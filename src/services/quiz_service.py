import random
from datetime import datetime
from typing import Optional

from sqlalchemy .exc import IntegrityError
from src .models .question import TYPE_MULTIPLE, TYPE_SINGLE, TYPE_TEXT, Question, QuestionOption
from src .models .result import (
    STATUS_FINISHED,
    AttemptAnswer,
    AttemptAnswerOption,
    TestAttempt,
)
from src .models .test import Test
from src .repositories .result_repository import (
    AttemptAnswerOptionRepository,
    AttemptAnswerRepository,
    TestAttemptRepository,
)
from src .repositories .test_repository import TestRepository
from src .utils .text_match import matches_any, normalize_text
from src .utils .timer import compute_remaining_seconds

from src.utils.time import utcnow


class QuizService :
    def __init__ (
    self ,
    tests :TestRepository ,
    attempts :TestAttemptRepository ,
    attempt_answers :AttemptAnswerRepository ,
    attempt_answer_options :AttemptAnswerOptionRepository ,
    )->None :
        self ._tests =tests
        self ._attempts =attempts
        self ._answers =attempt_answers
        self ._answer_options =attempt_answer_options

    def list_tests (self )->list [Test ]:
        return self ._tests .list_published ()

    def get_test (self ,test_id :int )->Optional [Test ]:
        return self ._tests .get (test_id )

    def get_attempt (self ,attempt_id :int )->Optional [TestAttempt ]:
        return self ._attempts .get (attempt_id )

    def history_for (self ,user_id :int )->list [TestAttempt ]:
        return self ._attempts .list_for_user (user_id )

    def attempts_used (self ,user_id :int ,test_id :int )->int :
        return self ._attempts .count_for_user_test (user_id ,test_id )

    def can_start (self ,user_id :int ,test :Test )->bool :
        if not self .is_within_schedule (test ):
            return False
        if test .max_attempts is None :
            return True
        return self .attempts_used (user_id ,test .id )<test .max_attempts

    @staticmethod
    def can_view_result (test :Test ,now :Optional [datetime ]=None )->bool :
        if getattr (test ,"show_result_immediately",True ):
            return True
        end =getattr (test ,"availability_end",None )
        if end is None :
            return False
        current =now or utcnow ()
        return current >=end

    @staticmethod
    def is_within_schedule (test :Test ,now :Optional [datetime ]=None )->bool :
        current =now or utcnow ()
        start =getattr (test ,"availability_start",None )
        end =getattr (test ,"availability_end",None )
        if start and current <start :
            return False
        if end and current >end :
            return False
        return True

    def last_attempt (self ,user_id :int ,test_id :int )->Optional [TestAttempt ]:
        attempts =[
        a for a in self ._attempts .list_for_user (user_id )
        if a .test_id ==test_id
        ]
        if not attempts :
            return None
        return max (attempts ,key =lambda a :a .started_at )

    def start_attempt (self ,user_id :int ,test_id :int )->TestAttempt :
        test =self ._tests .get (test_id )
        if test is None :
            raise ValueError ("Test not found")
        if not self .is_within_schedule (test ):
            raise ValueError ("Test is not available at the moment")
        used =self .attempts_used (user_id ,test_id )
        limit =test .max_attempts
        if limit is not None and used >=limit :
            raise ValueError (
            f"Attempt limit for the test has been reached ({used } of {limit })"
            )
        attempt =TestAttempt (
        test_id =test_id ,
        student_id =user_id ,
        attempt_no =used +1 ,
        started_at =utcnow (),
        )
        try :
            return self ._attempts .add (attempt )
        except IntegrityError as exc :
            self ._attempts .db .rollback ()
            raise ValueError (
            "Failed to start the attempt, please try again"
            )from exc

    def ordered_questions (self ,attempt :TestAttempt ,test :Test )->list [Question ]:
        questions =list (test .questions )
        if not getattr (test ,"shuffle_questions",False ):
            return questions
        rng =random .Random (attempt .id )
        rng .shuffle (questions )
        return questions

    def remaining_seconds (self ,attempt :TestAttempt )->int :
        test =self ._tests .get (attempt .test_id )
        if test is None :
            return 0
        return compute_remaining_seconds (attempt .started_at ,test .time_limit_minutes )

    def _get_or_create_answer (
    self ,attempt :TestAttempt ,question :Question
    )->AttemptAnswer :
        answer =self ._answers .by_attempt_and_question (attempt .id ,question .id )
        if answer is None :
            answer =AttemptAnswer (
            attempt_id =attempt .id ,
            question_id =question .id ,
            question_order_shown =question .position ,
            )
            self ._answers .add (answer )
        return answer

    def save_answer (
    self ,
    attempt :TestAttempt ,
    question :Question ,
    option_index :Optional [int ]=None ,
    )->None :
        if option_index is None :
            self .save_multi_answer (attempt ,question ,[])
            return
        self .save_multi_answer (attempt ,question ,[option_index ])

    def save_multi_answer (
    self ,
    attempt :TestAttempt ,
    question :Question ,
    option_indexes :list [int ],
    )->None :
        if attempt .is_finished :
            return
        answer =self ._get_or_create_answer (attempt ,question )

        for prev in list (answer .selected_options ):
            answer .selected_options .remove (prev )

        valid_indexes =sorted ({
        i for i in option_indexes
        if isinstance (i ,int )and 0 <=i <len (question .options )
        })
        for idx in valid_indexes :
            opt :QuestionOption =question .options [idx ]
            answer .selected_options .append (AttemptAnswerOption (
            option_id =opt .id ,
            option_order_shown =opt .position ,
            ))
        self ._answers .db .flush ()

        is_correct ,awarded =self ._evaluate_choice (question ,valid_indexes )
        answer .is_correct =is_correct
        answer .awarded_points =awarded

    @staticmethod
    def _evaluate_choice (question :Question ,indexes :list [int ])->tuple [bool ,int ]:
        if not indexes :
            return False ,0
        correct_ids ={o .id for o in question .options if o .is_correct }
        picked_ids ={question .options [i ].id for i in indexes }
        if question .question_type ==TYPE_SINGLE :
            is_correct =picked_ids ==correct_ids
            return is_correct ,question .points if is_correct else 0
        if not correct_ids :
            return False ,0
        right =len (picked_ids &correct_ids )
        wrong =len (picked_ids -correct_ids )
        net =max (0 ,right -wrong )
        awarded =round (question .points *net /len (correct_ids ))
        is_correct =picked_ids ==correct_ids
        return is_correct ,awarded

    def save_text_answer (
    self ,attempt :TestAttempt ,question :Question ,text :str
    )->None :
        if attempt .is_finished :
            return
        if question .question_type !=TYPE_TEXT :
            return
        answer =self ._get_or_create_answer (attempt ,question )
        raw =(text or "").strip ()
        answer .text_answer_raw =raw
        answer .text_answer_normalized =normalize_text (raw )
        is_correct =self ._is_text_correct (question ,raw )
        answer .is_correct =is_correct
        answer .awarded_points =question .points if is_correct else 0

    @staticmethod
    def _is_text_correct (question :Question ,raw_answer :str )->bool :
        if not raw_answer :
            return False
        accepted =[a .accepted_answer for a in question .text_answers ]
        if not accepted :
            return True
        return matches_any (raw_answer ,accepted )

    def finish_attempt (self ,attempt :TestAttempt )->TestAttempt :
        if attempt .is_finished :
            return attempt
        test =self ._tests .get (attempt .test_id )
        if test is None :
            raise ValueError ("Test not found")
        finished_at =utcnow ()
        attempt .finished_at =finished_at
        attempt .status =STATUS_FINISHED
        attempt .time_spent_seconds =int (
        (finished_at -attempt .started_at ).total_seconds ()
        )

        correct =0
        total_points =0
        max_points =0
        for q in test .questions :
            max_points +=q .points
            ans =self ._answers .by_attempt_and_question (attempt .id ,q .id )
            if ans is None :
                continue
            is_correct ,awarded =self ._evaluate_answer (q ,ans )
            ans .is_correct =is_correct
            ans .awarded_points =awarded
            total_points +=awarded
            if is_correct :
                correct +=1

        attempt .correct_answers_count =correct
        attempt .score =total_points
        attempt .success_percent =(
        round (total_points /max_points *100 )if max_points else 0
        )
        return attempt

    def _evaluate_answer (self ,question :Question ,answer :AttemptAnswer )->tuple [bool ,int ]:
        if question .question_type in (TYPE_SINGLE ,TYPE_MULTIPLE ):
            id_to_index ={o .id :i for i ,o in enumerate (question .options )}
            indexes =[
            id_to_index [ao .option_id ]
            for ao in answer .selected_options
            if ao .option_id in id_to_index
            ]
            return self ._evaluate_choice (question ,indexes )

        if question .question_type ==TYPE_TEXT :
            is_correct =self ._is_text_correct (question ,answer .text_answer_raw or "")
            return is_correct ,question .points if is_correct else 0

        return False ,0
