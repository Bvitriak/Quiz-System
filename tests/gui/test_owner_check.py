from src .models .test import Test 
from src.database import connection 
def _register (client ,email :str ,role :str ):
    client .post ("/register",data ={
    "email":email ,
    "password":"password123",
    "password_confirm":"password123",
    "full_name":"User",
    "role":role ,
    })

def _create_test (client )->int :
    response =client .post ("/teacher/tests/new",data ={
    "title":"Other",
    "time_limit_minutes":"10",
    "description":"",
    "action":"draft",
    },follow_redirects =False )
    with connection .SessionLocal ()as db :
        last =db .query (Test ).order_by (Test .id .desc ()).first ()
    connection .SessionLocal .remove ()
    return last .id 

class TestOwnerEnforcement :
    def test_teacher_cannot_edit_other_teacher_test (self ,client ):
        _register (client ,"alice@example.com","teacher")
        test_id =_create_test (client )
        client .get ("/logout")

        _register (client ,"bob@example.com","teacher")
        response =client .get (f"/teacher/tests/{test_id }/edit")
        assert response .status_code ==404 

    def test_teacher_cannot_open_other_availability (self ,client ):
        _register (client ,"alice2@example.com","teacher")
        test_id =_create_test (client )
        client .get ("/logout")

        _register (client ,"bob2@example.com","teacher")
        response =client .get (f"/teacher/tests/{test_id }/availability")
        assert response .status_code ==404 

    def test_teacher_cannot_delete_other_question (self ,client ):
        _register (client ,"alice3@example.com","teacher")
        test_id =_create_test (client )
        client .post (f"/teacher/tests/{test_id }/questions/new",data ={
        "type":"single",
        "text":"?",
        "option":["a","b"],
        "correct":"0",
        "points":"1",
        })
        client .get ("/logout")

        _register (client ,"bob3@example.com","teacher")
        response =client .post (
        f"/teacher/tests/{test_id }/questions/1/delete",
        follow_redirects =False ,
        )
        assert response .status_code ==404 
