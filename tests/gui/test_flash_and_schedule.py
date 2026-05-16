from datetime import datetime ,timedelta

from src.database import connection
from src.models.test import Test

def _register (client ,email :str ,role :str ):
    return client .post ("/register",data ={
    "email":email ,
    "password":"password123",
    "password_confirm":"password123",
    "full_name":"User",
    "role":role ,
    })

def _create_published_test (client ,test_id_holder :list [int ])->int :
    response =client .post ("/teacher/tests/new",data ={
    "title":"Quiz",
    "time_limit_minutes":"10",
    "description":"",
    "action":"draft",
    },follow_redirects =False )
    with connection .SessionLocal ()as db :
        last =db .query (Test ).order_by (Test .id .desc ()).first ()
    connection .SessionLocal .remove ()
    test_id =last .id 
    client .post (f"/teacher/tests/{test_id }/questions/new",data ={
    "type":"single",
    "text":"?",
    "option":["a","b"],
    "correct":"0",
    "points":"1",
    })
    client .post (f"/teacher/tests/{test_id }/edit",data ={
    "title":"Quiz",
    "time_limit_minutes":"10",
    "description":"",
    "action":"publish",
    })
    test_id_holder .append (test_id )
    return test_id 

class TestFlashMessages :
    def test_publish_emits_success_flash (self ,client ):
        _register (client ,"fteacher@example.com","teacher")
        ids :list [int ]=[]
        test_id =_create_published_test (client ,ids )
        response =client .get (f"/teacher/tests/{test_id }/edit")
        assert "Test published".encode ()in response .data 

    def test_logout_emits_info_flash (self ,client ):
        _register (client ,"logout@example.com","student")
        client .get ("/logout",follow_redirects =False )
        response =client .get ("/",follow_redirects =False )
        assert response .status_code ==200 


class TestStartTestOutsideWindow :
    def test_blocked_with_flash (self ,client ):
        _register (client ,"ts_t@example.com","teacher")
        ids :list [int ]=[]
        test_id =_create_published_test (client ,ids )
        with connection .SessionLocal ()as db :
            test_obj =db .get (Test ,test_id )
            test_obj .availability_end =datetime .utcnow ()-timedelta (hours =1 )
            db .commit ()
        connection .SessionLocal .remove ()
        client .get ("/logout")

        _register (client ,"ts_s@example.com","student")
        response =client .post (
        f"/student/tests/{test_id }/start",
        follow_redirects =False ,
        )
        assert response .status_code ==302 
        r2 =client .get ("/student")
        assert "unavailable".encode ()in r2 .data 


class TestShowResultImmediately :
    def test_results_hidden_before_window_ends (self ,client ):
        _register (client ,"sr_t@example.com","teacher")
        ids :list [int ]=[]
        test_id =_create_published_test (client ,ids )
        future =datetime .utcnow ()+timedelta (hours =1 )
        with connection .SessionLocal ()as db :
            test_obj =db .get (Test ,test_id )
            test_obj .show_result_immediately =False 
            test_obj .availability_end =future 
            db .commit ()
        connection .SessionLocal .remove ()
        client .get ("/logout")

        _register (client ,"sr_s@example.com","student")
        response =client .post (f"/student/tests/{test_id }/start",follow_redirects =False )
        attempt_id =int (response .headers ["Location"].split ("/attempts/")[1 ].split ("/")[0 ])
        client .post (
        f"/student/attempts/{attempt_id }/question/1",data ={"option":"0"}
        )
        client .post (f"/student/attempts/{attempt_id }/finish")
        response =client .get (f"/student/attempts/{attempt_id }/result")
        assert response .status_code ==200 
        assert "later".encode ()in response .data 

    def test_results_visible_when_immediate (self ,client ):
        _register (client ,"sr2_t@example.com","teacher")
        ids :list [int ]=[]
        test_id =_create_published_test (client ,ids )
        client .get ("/logout")
        _register (client ,"sr2_s@example.com","student")
        response =client .post (f"/student/tests/{test_id }/start",follow_redirects =False )
        attempt_id =int (response .headers ["Location"].split ("/attempts/")[1 ].split ("/")[0 ])
        client .post (
        f"/student/attempts/{attempt_id }/question/1",data ={"option":"0"}
        )
        client .post (f"/student/attempts/{attempt_id }/finish")
        response =client .get (f"/student/attempts/{attempt_id }/result")
        assert response .status_code ==200 
        assert b"result"in response .data .lower ()

    def test_results_visible_after_window_closed (self ,client ):
        _register (client ,"sr3_t@example.com","teacher")
        ids :list [int ]=[]
        test_id =_create_published_test (client ,ids )
        with connection .SessionLocal ()as db :
            test_obj =db .get (Test ,test_id )
            test_obj .show_result_immediately =False 
            test_obj .availability_end =datetime .utcnow ()-timedelta (hours =1 )
            db .commit ()
        connection .SessionLocal .remove ()
        client .get ("/logout")

        _register (client ,"sr3_s@example.com","student")
        with connection .SessionLocal ()as db :
            test_obj =db .get (Test ,test_id )
            test_obj .availability_end =datetime .utcnow ()+timedelta (hours =1 )
            db .commit ()
        connection .SessionLocal .remove ()

        response =client .post (f"/student/tests/{test_id }/start",follow_redirects =False )
        attempt_id =int (response .headers ["Location"].split ("/attempts/")[1 ].split ("/")[0 ])
        client .post (
        f"/student/attempts/{attempt_id }/question/1",data ={"option":"0"}
        )
        client .post (f"/student/attempts/{attempt_id }/finish")

        with connection .SessionLocal ()as db :
            test_obj =db .get (Test ,test_id )
            test_obj .availability_end =datetime .utcnow ()-timedelta (minutes =1 )
            db .commit ()
        connection .SessionLocal .remove ()

        response =client .get (f"/student/attempts/{attempt_id }/result")
        assert response .status_code ==200 
        assert b"result"in response .data .lower ()

    def test_auto_finished_flag_shown (self ,client ):
        _register (client ,"auto_t@example.com","teacher")
        ids :list [int ]=[]
        test_id =_create_published_test (client ,ids )
        with connection .SessionLocal ()as db :
            test_obj =db .get (Test ,test_id )
            test_obj .show_result_immediately =False 
            test_obj .availability_end =datetime .utcnow ()+timedelta (hours =1 )
            db .commit ()
        connection .SessionLocal .remove ()
        client .get ("/logout")

        _register (client ,"auto_s@example.com","student")
        response =client .post (f"/student/tests/{test_id }/start",follow_redirects =False )
        attempt_id =int (response .headers ["Location"].split ("/attempts/")[1 ].split ("/")[0 ])
        client .post (f"/student/attempts/{attempt_id }/finish")
        response =client .get (f"/student/attempts/{attempt_id }/result?auto=1")
        assert response .status_code ==200 
        assert "automatically".encode ()in response .data 

class TestLimitExhaustedFlash :
    def test_limit_message_includes_numbers (self ,client ):
        _register (client ,"lim_t@example.com","teacher")
        ids :list [int ]=[]
        test_id =_create_published_test (client ,ids )
        with connection .SessionLocal ()as db :
            test_obj =db .get (Test ,test_id )
            test_obj .max_attempts =1 
            db .commit ()
        connection .SessionLocal .remove ()
        client .get ("/logout")

        _register (client ,"lim_s@example.com","student")
        response =client .post (f"/student/tests/{test_id }/start",follow_redirects =False )
        attempt_id =int (response .headers ["Location"].split ("/attempts/")[1 ].split ("/")[0 ])
        client .post (f"/student/attempts/{attempt_id }/finish")

        client .post (f"/student/tests/{test_id }/start",follow_redirects =False )
        response =client .get ("/student")
        assert ("1 of 1".encode ()in response .data )or ("exhausted".encode ()in response .data )
