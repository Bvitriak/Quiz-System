from src .models .test import Test 
from src.database import connection 
def _register_teacher (client ):
    return client .post ("/register",data ={
    "email":"t@example.com",
    "password":"password123",
    "password_confirm":"password123",
    "full_name":"Teacher",
    "role":"teacher",
    })

class TestTeacherDashboard :
    def test_my_tests_page (self ,client ):
        _register_teacher (client )
        response =client .get ("/teacher")
        assert response .status_code ==200 

    def test_students_tab (self ,client ):
        _register_teacher (client )
        response =client .get ("/teacher/students")
        assert response .status_code ==200 

    def test_create_test_form (self ,client ):
        _register_teacher (client )
        response =client .get ("/teacher/tests/new")
        assert response .status_code ==200 

class TestCreateTest :
    def test_creates_redirects_to_tests (self ,client ):
        _register_teacher (client )
        response =client .post ("/teacher/tests/new",data ={
        "title":"Physics",
        "time_limit_minutes":"30",
        "description":"mechanics",
        "action":"draft",
        },follow_redirects =False )
        assert response .status_code ==302 
        assert response .headers ["Location"].rstrip ("/").endswith ("/teacher")

    def test_invalid_time_limit_renders_error (self ,client ):
        _register_teacher (client )
        response =client .post ("/teacher/tests/new",data ={
        "title":"Physics",
        "time_limit_minutes":"0",
        "description":"",
        "action":"draft",
        })
        assert response .status_code ==200 
        assert b"alert"in response .data 

class TestAddQuestion :
    def test_add_single_question (self ,client ):
        _register_teacher (client )
        response =client .post ("/teacher/tests/new",data ={
        "title":"Q",
        "time_limit_minutes":"10",
        "description":"",
        "action":"draft",
        },follow_redirects =False )
        with connection .SessionLocal ()as db :
            last =db .query (Test ).order_by (Test .id .desc ()).first ()
        connection .SessionLocal .remove ()
        test_id =last .id 
        response =client .post (f"/teacher/tests/{test_id }/questions/new",data ={
        "type":"single",
        "text":"Question?",
        "option":["a","b"],
        "correct":"0",
        },follow_redirects =False )
        assert response .status_code ==302 
        assert "/edit"in response .headers ["Location"]

    def test_text_question_no_reference_needed (self ,client ):
        _register_teacher (client )
        response =client .post ("/teacher/tests/new",data ={
        "title":"T",
        "time_limit_minutes":"10",
        "description":"",
        "action":"draft",
        },follow_redirects =False )
        with connection .SessionLocal ()as db :
            last =db .query (Test ).order_by (Test .id .desc ()).first ()
        connection .SessionLocal .remove ()
        test_id =last .id 
        response =client .post (f"/teacher/tests/{test_id }/questions/new",data ={
        "type":"text",
        "text":"Long-form question",
        },follow_redirects =False )
        assert response .status_code ==302 
