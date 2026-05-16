from src .models .test import Test 
from src.database import connection 
def _register (client ,email :str ,role :str ="teacher"):
    client .post ("/register",data ={
    "email":email ,"password":"password123",
    "password_confirm":"password123",
    "full_name":"T","role":role ,
    })

def _create_published_test (client )->int :
    response =client .post ("/teacher/tests/new",data ={
    "title":"Pub","time_limit_minutes":"10",
    "description":"","action":"draft",
    },follow_redirects =False )
    with connection .SessionLocal ()as db :
        last =db .query (Test ).order_by (Test .id .desc ()).first ()
    connection .SessionLocal .remove ()
    test_id =last .id 
    client .post (f"/teacher/tests/{test_id }/questions/new",data ={
    "type":"single","text":"?",
    "option":["a","b"],"correct":"0","points":"1",
    })
    client .post (f"/teacher/tests/{test_id }/edit",data ={
    "title":"Pub","time_limit_minutes":"10",
    "description":"","action":"publish",
    })
    return test_id 

class TestPublishedEditBlocked :
    def test_edit_basics_rejected (self ,client ):
        _register (client ,"pub1@example.com")
        test_id =_create_published_test (client )
        response =client .post (f"/teacher/tests/{test_id }/edit",data ={
        "title":"Changed","time_limit_minutes":"20",
        "description":"","action":"save",
        })
        assert response .status_code ==200 
        assert "Unpublish".encode ()in response .data 

    def test_add_question_rejected (self ,client ):
        _register (client ,"pub2@example.com")
        test_id =_create_published_test (client )
        response =client .post (f"/teacher/tests/{test_id }/questions/new",data ={
        "type":"single","text":"new",
        "option":["a","b"],"correct":"0","points":"1",
        })
        assert response .status_code ==200 
        assert "Unpublish".encode ()in response .data 

    def test_to_draft_then_edit_works (self ,client ):
        _register (client ,"pub3@example.com")
        test_id =_create_published_test (client )
        response =client .post (f"/teacher/tests/{test_id }/edit",data ={
        "title":"Pub","time_limit_minutes":"10",
        "description":"","action":"draft",
        },follow_redirects =False )
        assert response .status_code ==302 
        response =client .post (f"/teacher/tests/{test_id }/edit",data ={
        "title":"New","time_limit_minutes":"15",
        "description":"","action":"save",
        },follow_redirects =False )
        assert response .status_code ==302 
