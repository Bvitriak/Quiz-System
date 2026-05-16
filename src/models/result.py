from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy .orm import Mapped, mapped_column, relationship
from src .models .base import Base

from src.utils.time import utcnow

if TYPE_CHECKING :
    from src .models .question import QuestionOption

STATUS_IN_PROGRESS ="in_progress"
STATUS_FINISHED ="finished"

class TestAttempt (Base ):
    __tablename__ ="test_attempts"
    __table_args__ =(
    UniqueConstraint (
    "test_id","student_id","attempt_no",
    name ="uq_test_attempts_student_attempt",
    ),
    )

    id :Mapped [int ]=mapped_column (BigInteger ,primary_key =True )
    test_id :Mapped [int ]=mapped_column (
    ForeignKey ("tests.id",ondelete ="CASCADE"),nullable =False
    )
    student_id :Mapped [int ]=mapped_column (ForeignKey ("users.id"),nullable =False )
    attempt_no :Mapped [int ]=mapped_column (Integer ,nullable =False )
    status :Mapped [str ]=mapped_column (
        String (255 ),nullable =False ,default =STATUS_IN_PROGRESS
    )
    started_at :Mapped [datetime ]=mapped_column (DateTime ,nullable =False ,default =utcnow )
    finished_at :Mapped [Optional [datetime ]]=mapped_column (DateTime ,nullable =True )
    time_spent_seconds :Mapped [int ]=mapped_column (Integer ,nullable =False ,default =0 )
    score :Mapped [int ]=mapped_column (Integer ,nullable =False ,default =0 )
    success_percent :Mapped [int ]=mapped_column (Integer ,nullable =False ,default =0 )
    correct_answers_count :Mapped [int ]=mapped_column (Integer ,nullable =False ,default =0 )

    answers_rel :Mapped [list ["AttemptAnswer"]]=relationship (
    "AttemptAnswer",
    back_populates ="attempt",
    cascade ="all, delete-orphan",
    )

    @property
    def user_id (self )->int :
        return self .student_id

    @property
    def attempt_number (self )->int :
        return self .attempt_no

    @property
    def correct_count (self )->int :
        return self .correct_answers_count

    @property
    def is_finished (self )->bool :
        return self .finished_at is not None

    @property
    def duration_seconds (self )->int :
        return self .time_spent_seconds

    @property
    def answers (self )->dict [int ,int ]:
        result :dict [int ,int ]={}
        for ans in self .answers_rel :
            if ans .selected_options :
                opt =ans .selected_options [0 ].option
                if opt is not None :
                    result [ans .question_id ]=opt .position
        return result

class AttemptAnswer (Base ):
    __tablename__ ="attempt_answers"

    id :Mapped [int ]=mapped_column (BigInteger ,primary_key =True )
    attempt_id :Mapped [int ]=mapped_column (ForeignKey ("test_attempts.id"),nullable =False )
    question_id :Mapped [int ]=mapped_column (
    ForeignKey ("questions.id",ondelete ="CASCADE"),nullable =False
    )
    question_order_shown :Mapped [int ]=mapped_column (Integer ,nullable =False ,default =0 )
    text_answer_raw :Mapped [str ]=mapped_column (String (255 ),nullable =False ,default ="")
    text_answer_normalized :Mapped [str ]=mapped_column (String (255 ),nullable =False ,default ="")
    is_correct :Mapped [bool ]=mapped_column (Boolean ,nullable =False ,default =False )
    awarded_points :Mapped [int ]=mapped_column (Integer ,nullable =False ,default =0 )

    attempt :Mapped ["TestAttempt"]=relationship ("TestAttempt",back_populates ="answers_rel")
    selected_options :Mapped [list ["AttemptAnswerOption"]]=relationship (
    "AttemptAnswerOption",
    back_populates ="answer",
    cascade ="all, delete-orphan",
    )

class AttemptAnswerOption (Base ):
    __tablename__ ="attempt_answer_options"

    id :Mapped [int ]=mapped_column (BigInteger ,primary_key =True )
    attempt_answer_id :Mapped [int ]=mapped_column (
    ForeignKey ("attempt_answers.id"),nullable =False
    )
    option_id :Mapped [int ]=mapped_column (ForeignKey ("question_options.id"),nullable =False )
    option_order_shown :Mapped [int ]=mapped_column (Integer ,nullable =False ,default =0 )

    answer :Mapped ["AttemptAnswer"]=relationship (
    "AttemptAnswer",back_populates ="selected_options"
    )
    option :Mapped ["QuestionOption"]=relationship ("QuestionOption",lazy ="joined")
