class TestPublicPages:
    def test_index(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "Quiz System".encode() in response.data

    def test_login_page(self, client):
        response = client.get("/login")
        assert response.status_code == 200
        assert b"<form" in response.data

    def test_register_page(self, client):
        response = client.get("/register")
        assert response.status_code == 200

class TestRegisterFlow:
    def test_register_student_redirects_to_student_area(self, client):
        response = client.post("/register", data={
            "email": "newstud@example.com",
            "password": "password123",
            "password_confirm": "password123",
            "full_name": "New Student",
            "role": "student",
        }, follow_redirects=False)
        assert response.status_code == 302
        assert "/student" in response.headers["Location"]

    def test_register_teacher_redirects_to_teacher_area(self, client):
        response = client.post("/register", data={
            "email": "newteach@example.com",
            "password": "password123",
            "password_confirm": "password123",
            "full_name": "New Teacher",
            "role": "teacher",
        }, follow_redirects=False)
        assert response.status_code == 302
        assert "/teacher" in response.headers["Location"]

    def test_register_password_mismatch_renders_error(self, client):
        response = client.post("/register", data={
            "email": "x@example.com",
            "password": "password123",
            "password_confirm": "different456",
            "full_name": "X",
            "role": "student",
        })
        assert response.status_code == 200
        assert b"alert" in response.data

class TestLoginFlow:
    def test_login_then_logout(self, client):
        client.post("/register", data={
            "email": "logme@example.com",
            "password": "password123",
            "password_confirm": "password123",
            "full_name": "Lou",
            "role": "student",
        })
        client.get("/logout")
        response = client.post("/login", data={
            "email": "logme@example.com",
            "password": "password123",
        })
        assert response.status_code == 302
        assert "/student" in response.headers["Location"]

    def test_login_bad_credentials(self, client):
        response = client.post("/login", data={
            "email": "noone@example.com",
            "password": "password123",
        })
        assert response.status_code == 200
        assert b"alert" in response.data

class TestGuards:
    def test_student_page_requires_login(self, client):
        response = client.get("/student", follow_redirects=False)
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]

    def test_teacher_page_requires_login(self, client):
        response = client.get("/teacher", follow_redirects=False)
        assert response.status_code == 302

    def test_student_cant_access_teacher(self, client):
        client.post("/register", data={
            "email": "s1@example.com",
            "password": "password123",
            "password_confirm": "password123",
            "full_name": "S",
            "role": "student",
        })
        response = client.get("/teacher", follow_redirects=False)
        assert response.status_code == 302
