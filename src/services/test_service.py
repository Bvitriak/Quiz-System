from datetime import datetime
from typing import Optional

from src .models .question import (
    TYPE_MULTIPLE,
    TYPE_SINGLE,
    TYPE_TEXT,
    Question,
    QuestionOption,
    QuestionTextAnswer,
)
from src .models .test import STATUS_DRAFT, STATUS_PUBLISHED, Test, TestStatusHistory
from src .models .user import User
from src .repositories .result_repository import TestAttemptRepository
from src .repositories .test_repository import (
    QuestionRepository,
    TestRepository,
)
from src .utils .text_match import normalize_text

from src.utils.time import utcnow

QUESTION_TYPES =(TYPE_SINGLE ,TYPE_MULTIPLE ,TYPE_TEXT )

class TestService :

    def __init__ (
    self ,
    tests :TestRepository ,
    questions :QuestionRepository ,
    attempts :TestAttemptRepository ,
    )->None :
        self ._tests =tests
        self ._questions =questions
        self ._attempts =attempts

    def list_for_owner (self ,owner_id :int )->list [Test ]:
        return self ._tests .list_for_owner (owner_id )

    def get (self ,test_id :int )->Optional [Test ]:
        return self ._tests .get (test_id )

    def create (self ,owner_id :int ,title :str ,time_limit_minutes :int ,
    description :str ,randomize :bool )->Test :
        title =(title or "").strip ()
        if not title :
            raise ValueError ("Enter a test title")
        if time_limit_minutes <=0 :
            raise ValueError ("Time limit must be greater than zero")
        test =Test (
        teacher_id =owner_id ,
        title =title ,
        description =(description or "").strip ()or None ,
        time_limit_minutes =time_limit_minutes ,
        shuffle_questions =randomize ,
        status =STATUS_DRAFT ,
        )
        return self ._tests .add (test )

    @staticmethod
    def _ensure_editable (test :Test )->None :
        if test .status ==STATUS_PUBLISHED :
            raise ValueError (
            "Test is published. Unpublish it to make changes."
            )

    def update_basics (self ,test :Test ,*,title :str ,time_limit_minutes :int ,
    description :str ,randomize :bool )->None :
        self ._ensure_editable (test )
        title =(title or "").strip ()
        if not title :
            raise ValueError ("Enter a test title")
        if time_limit_minutes <=0 :
            raise ValueError ("Time limit must be greater than zero")
        test .title =title
        test .time_limit_minutes =time_limit_minutes
        test .description =(description or "").strip ()or None
        test .shuffle_questions =randomize

    def update_availability (
    self ,
    test :Test ,
    *,
    start :Optional [datetime ],
    end :Optional [datetime ],
    max_attempts :Optional [int ],
    show_result_immediately :bool ,
    randomize :bool ,
    time_limit_minutes :Optional [int ]=None ,
    )->None :
        self ._ensure_editable (test )
        if start and end and end <=start :
            raise ValueError ("End date must be later than start date")
        if max_attempts is not None and max_attempts <=0 :
            raise ValueError ("Number of attempts must be greater than zero")
        if time_limit_minutes is not None :
            if time_limit_minutes <=0 :
                raise ValueError ("Time limit must be greater than zero")
            test .time_limit_minutes =time_limit_minutes
        test .availability_start =start
        test .availability_end =end
        test .show_result_immediately =show_result_immediately
        test .max_attempts =max_attempts
        test .shuffle_questions =randomize

    def publish (self ,test :Test ,*,changed_by :Optional [int ]=None )->None :
        if not test .questions :
            raise ValueError ("Cannot publish a test without questions")
        old_status =test .status
        test .status =STATUS_PUBLISHED
        test .published_at =utcnow ()
        self ._record_status_change (test ,old_status ,STATUS_PUBLISHED ,changed_by )

    def to_draft (self ,test :Test ,*,changed_by :Optional [int ]=None )->None :
        old_status =test .status
        test .status =STATUS_DRAFT
        self ._record_status_change (test ,old_status ,STATUS_DRAFT ,changed_by )

    def _record_status_change (
    self ,test :Test ,old_status :str ,new_status :str ,
    changed_by :Optional [int ],
    )->None :
        if old_status ==new_status :
            return
        actor =changed_by if changed_by is not None else test .teacher_id
        self ._tests .add_status_history (TestStatusHistory (
        test_id =test .id ,
        changed_by =actor ,
        old_status =old_status ,
        new_status =new_status ,
        ))

    def delete (self ,test :Test )->None :
        active =self ._attempts .count_active_for_test (test .id )
        if active >0 :
            raise ValueError (
            f"Cannot delete test: there are unfinished attempts ({active })"
            )
        for attempt in self ._attempts .list_for_test (test .id ):
            self ._attempts .delete (attempt )
        self ._tests .delete (test )

    def add_question (self ,test :Test ,*,qtype :str ,text :str ,
    options :list [str ],correct_indexes :list [int ],
    correct_text :str ="",points :int =1 )->Question :
        self ._ensure_editable (test )
        if qtype not in QUESTION_TYPES :
            raise ValueError ("Unknown question type")
        text =(text or "").strip ()
        if not text :
            raise ValueError ("Enter the question text")
        points =self ._validate_points (points )

        question =Question (
        test_id =test .id ,
        question_type =qtype ,
        text =text ,
        points =points ,
        position =self ._questions .next_position (test .id ),
        )
        self ._questions .add (question )

        if qtype in (TYPE_SINGLE ,TYPE_MULTIPLE ):
            self ._fill_options (question ,qtype ,options ,correct_indexes )
        elif qtype ==TYPE_TEXT :
            self ._fill_text_answer (question ,correct_text )

        return question

    @staticmethod
    def _validate_points (points :int )->int :
        try :
            value =int (points )
        except (TypeError ,ValueError )as exc :
            raise ValueError ("Score must be an integer")from exc
        if value <=0 :
            raise ValueError ("Score must be greater than zero")
        return value

    @staticmethod
    def _fill_options (question :Question ,qtype :str ,
    options :list [str ],correct_indexes :list [int ])->None :
        clean =[o .strip ()for o in options if o and o .strip ()]
        if len (clean )<2 :
            raise ValueError ("Add at least two answer options")
        if not correct_indexes :
            raise ValueError ("Mark the correct answer")
        if qtype ==TYPE_SINGLE and len (correct_indexes )!=1 :
            raise ValueError ("Single choice requires exactly one correct answer")
        for i in correct_indexes :
            if not 0 <=i <len (clean ):
                raise ValueError ("Invalid correct answer index")
        question .options .clear ()
        for i ,text_opt in enumerate (clean ):
            question .options .append (QuestionOption (
            option_text =text_opt ,
            is_correct =i in correct_indexes ,
            position =i ,
            ))

    @staticmethod
    def _fill_text_answer (question :Question ,correct_text :str )->None :
        question .text_answers .clear ()
        accepted =(correct_text or "").strip ()
        if not accepted :
            return
        question .text_answers .append (QuestionTextAnswer (
        accepted_answer =accepted ,
        normalized_answer =normalize_text (accepted ),
        ))

    def delete_question (self ,test :Test ,question_id :int )->None :
        self ._ensure_editable (test )
        for q in list (test .questions ):
            if q .id ==question_id :
                test .questions .remove (q )
                break

    def get_question (self ,test :Test ,question_id :int )->Optional [Question ]:
        for q in test .questions :
            if q .id ==question_id :
                return q
        return None

    def update_question (self ,question :Question ,*,text :str ,
    options :list [str ],correct_indexes :list [int ],
    correct_text :str ="",points :Optional [int ]=None )->None :
        if question .test is not None :
            self ._ensure_editable (question .test )
        text =(text or "").strip ()
        if not text :
            raise ValueError ("Enter the question text")
        question .text =text
        if points is not None :
            question .points =self ._validate_points (points )

        if question .question_type in (TYPE_SINGLE ,TYPE_MULTIPLE ):
            self ._fill_options (
            question ,question .question_type ,options ,correct_indexes
            )
        else :
            self ._fill_text_answer (question ,correct_text )

    def student_stats (self ,students :list [User ])->list [dict ]:
        by_student =self ._attempts .list_finished_for_users ([s .id for s in students ])
        rows =[]
        for s in students :
            attempts =by_student .get (s .id ,[])
            avg =(
            round (sum (a .success_percent for a in attempts )/len (attempts ))
            if attempts else 0
            )
            last =max (
            attempts ,
            key =lambda a :a .finished_at or datetime .min ,
            default =None ,
            )

            by_test :dict [int ,list ]={}
            for a in attempts :
                by_test .setdefault (a .test_id ,[]).append (a )

            per_test =[]
            for test_id ,items in by_test .items ():
                test =self ._tests .get (test_id )
                last_item =max (
                items ,
                key =lambda x :x .finished_at or datetime .min ,
                )
                best =max (items ,key =lambda x :x .success_percent )
                per_test .append ({
                "test":test ,
                "test_title":test .title if test else f"Test #{test_id }",
                "attempts_count":len (items ),
                "best_score":best .success_percent ,
                "last_attempt":last_item ,
                })
            per_test .sort (
            key =lambda r :r ["last_attempt"].finished_at or datetime .min ,
            reverse =True ,
            )

            rows .append ({
            "student":s ,
            "attempts_count":len (attempts ),
            "avg_score":avg ,
            "last_attempt":last ,
            "per_test":per_test ,
            })
        return rows
