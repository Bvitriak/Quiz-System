from src .models .test import Test 
from src.database import connection 
def _register_student (client ):
    return client .post ("/register",data ={
    "email":"stud@example.com",
    "password":"password123",
    "password_confirm":"password123",
    "full_name":"Student",
    "role":"student",
    })

def _register_teacher_and_publish_test (client ):
    client .post ("/register",data ={
    "email":"teach@example.com",
    "password":"password123",
    "password_confirm":"password123",
    "full_name":"Teacher",
    "role":"teacher",
    })
    response =client .post ("/teacher/tests/new",data ={
    "title":"Algebra",
    "time_limit_minutes":"20",
    "description":"",
    "action":"draft",
    },follow_redirects =False )
    with connection .SessionLocal ()as db :
        last =db .query (Test ).order_by (Test .id .desc ()).first ()
    connection .SessionLocal .remove ()
    test_id =last .id 
    client .post (f"/teacher/tests/{test_id }/questions/new",data ={
    "type":"single",
    "text":"2 + 2 = ?",
    "option":["3","4","5"],
    "correct":"1",
    })
    client .post (f"/teacher/tests/{test_id }/edit",data ={
    "title":"Algebra",
    "time_limit_minutes":"20",
    "description":"",
    "action":"publish",
    })
    client .get ("/logout")
    return test_id 

class TestStudentFlow :
    def test_tests_list_shows_published (self ,client ):
        _register_teacher_and_publish_test (client )
        _register_student (client )
        response =client .get ("/student")
        assert response .status_code ==200 
        assert "Algebra".encode ()in response .data 

    def test_full_pass (self ,client ):
        test_id =_register_teacher_and_publish_test (client )
        _register_student (client )

        response =client .post (f"/student/tests/{test_id }/start",follow_redirects =False )
        assert response .status_code ==302 
        assert "/question/1"in response .headers ["Location"]
        attempt_id =int (response .headers ["Location"].split ("/attempts/")[1 ].split ("/")[0 ])

        response =client .post (
        f"/student/attempts/{attempt_id }/question/1",
        data ={"option":"1"},
        follow_redirects =False ,
        )
        assert "/result"in response .headers ["Location"]

        response =client .get (f"/student/attempts/{attempt_id }/result")
        assert response .status_code ==200 
        assert b"100/100"in response .data 

    def test_history_lists_attempt (self ,client ):
        test_id =_register_teacher_and_publish_test (client )
        _register_student (client )
        response =client .post (f"/student/tests/{test_id }/start",follow_redirects =False )
        attempt_id =int (response .headers ["Location"].split ("/attempts/")[1 ].split ("/")[0 ])
        client .post (
        f"/student/attempts/{attempt_id }/question/1",data ={"option":"1"}
        )
        client .post (f"/student/attempts/{attempt_id }/finish")

        response =client .get ("/student/history")
        assert response .status_code ==200 
        assert "Algebra".encode ()in response .data 
