from datetime import datetime
from typing import Optional

from src .services .test_service import TestService


class TestController :

    def __init__ (self ,test_service :TestService )->None :
        self ._service =test_service

    def list_for_owner (self ,owner_id :int ):
        return self ._service .list_for_owner (owner_id )

    def get (self ,test_id :int ):
        return self ._service .get (test_id )

    def create (self ,*,owner_id :int ,title :str ,time_limit_minutes :int ,
    description :str ,randomize :bool ):
        return self ._service .create (
        owner_id =owner_id ,
        title =title ,
        time_limit_minutes =time_limit_minutes ,
        description =description ,
        randomize =randomize ,
        )

    def update_basics (self ,test ,*,title :str ,time_limit_minutes :int ,
    description :str ,randomize :bool )->None :
        self ._service .update_basics (
        test ,
        title =title ,
        time_limit_minutes =time_limit_minutes ,
        description =description ,
        randomize =randomize ,
        )

    def update_availability (
    self ,
    test ,
    *,
    start :Optional [datetime ],
    end :Optional [datetime ],
    max_attempts :Optional [int ],
    show_result_immediately :bool ,
    randomize :bool ,
    time_limit_minutes :Optional [int ]=None ,
    )->None :
        self ._service .update_availability (
        test ,
        start =start ,
        end =end ,
        max_attempts =max_attempts ,
        show_result_immediately =show_result_immediately ,
        randomize =randomize ,
        time_limit_minutes =time_limit_minutes ,
        )

    def publish (self ,test ,*,changed_by :Optional [int ]=None )->None :
        self ._service .publish (test ,changed_by =changed_by )

    def to_draft (self ,test ,*,changed_by :Optional [int ]=None )->None :
        self ._service .to_draft (test ,changed_by =changed_by )

    def add_question (self ,test ,*,qtype :str ,text :str ,
    options :list [str ],correct_indexes :list [int ],
    correct_text :str ="",points :int =1 ):
        return self ._service .add_question (
        test ,
        qtype =qtype ,
        text =text ,
        options =options ,
        correct_indexes =correct_indexes ,
        correct_text =correct_text ,
        points =points ,
        )

    def delete_question (self ,test ,question_id :int )->None :
        self ._service .delete_question (test ,question_id )

    def get_question (self ,test ,question_id :int ):
        return self ._service .get_question (test ,question_id )

    def update_question (self ,question ,*,text :str ,
    options :list [str ],correct_indexes :list [int ],
    correct_text :str ="",points :Optional [int ]=None )->None :
        self ._service .update_question (
        question ,
        text =text ,
        options =options ,
        correct_indexes =correct_indexes ,
        correct_text =correct_text ,
        points =points ,
        )

    def student_stats (self ,students ):
        return self ._service .student_stats (students )

    def delete (self ,test )->None :
        self ._service .delete (test )
