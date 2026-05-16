from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy .orm import Mapped, mapped_column, relationship
from src .models .base import Base

from src.utils.time import utcnow

if TYPE_CHECKING :
    from src .models .question import Question

STATUS_DRAFT ="draft"
STATUS_PUBLISHED ="published"

class Test (Base ):
    __tablename__ ="tests"

    id :Mapped [int ]=mapped_column (BigInteger ,primary_key =True )
    teacher_id :Mapped [int ]=mapped_column (ForeignKey ("users.id"),nullable =False )
    title :Mapped [str ]=mapped_column (String (255 ),nullable =False )
    description :Mapped [Optional [str ]]=mapped_column (Text ,nullable =True ,default ="")
    time_limit_minutes :Mapped [int ]=mapped_column (Integer ,nullable =False )
    status :Mapped [str ]=mapped_column (String (255 ),nullable =False ,default =STATUS_DRAFT )
    shuffle_questions :Mapped [bool ]=mapped_column (Boolean ,nullable =False ,default =False )
    created_at :Mapped [datetime ]=mapped_column (DateTime ,nullable =False ,default =utcnow )
    published_at :Mapped [Optional [datetime ]]=mapped_column (DateTime ,nullable =True )
    max_attempts :Mapped [Optional [int ]]=mapped_column (Integer ,nullable =True )
    availability_start :Mapped [Optional [datetime ]]=mapped_column (DateTime ,nullable =True )
    availability_end :Mapped [Optional [datetime ]]=mapped_column (DateTime ,nullable =True )
    show_result_immediately :Mapped [bool ]=mapped_column (
    Boolean ,nullable =False ,default =True
    )

    questions :Mapped [list ["Question"]]=relationship (
    "Question",
    back_populates ="test",
    order_by ="Question.position",
    cascade ="all, delete-orphan",
    )

    @property
    def randomize (self )->bool :
        return self .shuffle_questions

    @property
    def is_published (self )->bool :
        return self .status ==STATUS_PUBLISHED

    @property
    def status_label (self )->str :
        return "Published"if self .is_published else "Draft"

    @property
    def question_count (self )->int :
        return len (self .questions )

    @property
    def deadline (self ):
        target =self .published_at or self .created_at
        return target .date ()

    @property
    def owner_id (self )->int :
        return self .teacher_id

class TestStatusHistory (Base ):
    __tablename__ ="test_status_history"

    id :Mapped [int ]=mapped_column (BigInteger ,primary_key =True )
    test_id :Mapped [int ]=mapped_column (ForeignKey ("tests.id"),nullable =False )
    changed_by :Mapped [int ]=mapped_column (ForeignKey ("users.id"),nullable =False )
    old_status :Mapped [str ]=mapped_column (String (255 ),nullable =False )
    new_status :Mapped [str ]=mapped_column (String (255 ),nullable =False )
    changed_at :Mapped [datetime ]=mapped_column (DateTime ,nullable =False ,default =utcnow )
