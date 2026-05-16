from unittest .mock import patch 

import pytest 
from sqlalchemy .exc import SQLAlchemyError 

class BrokenSession :
    def __enter__ (self ):
        return self 

    def __exit__ (self ,*args ):
        return False 

    def execute (self ,*args ,**kwargs ):
        raise SQLAlchemyError ("connection refused")

    def commit (self ):
        pass 

    def rollback (self ):
        pass 

    def close (self ):
        pass 

@pytest .fixture 
def csrf_app (engine ):
    from src .main import create_app 
    flask_app =create_app ()
    flask_app .config ["TESTING"]=True 
    flask_app .config ["WTF_CSRF_ENABLED"]=True 
    yield flask_app 

@pytest .fixture 
def csrf_client (csrf_app ):
    return csrf_app .test_client ()

@pytest .fixture 
def rate_limited_app (engine ):
    from src .main import create_app 
    from src .utils .rate_limit import limiter 
    limiter .reset ()
    flask_app =create_app ()
    flask_app .config ["TESTING"]=True 
    flask_app .config ["WTF_CSRF_ENABLED"]=False 
    yield flask_app 
    limiter .reset ()

@pytest .fixture 
def rate_limited_client (rate_limited_app ):
    return rate_limited_app .test_client ()

class TestCsrfEnforcement :
    def test_post_without_token_rejected (self ,csrf_client ):
        response =csrf_client .post ("/register",data ={
        "email":"x@y.io",
        "password":"password123",
        "password_confirm":"password123",
        "full_name":"X",
        "role":"student",
        })
        assert response .status_code ==400 

class TestSecurityHeaders :
    def test_basic_headers_present (self ,client ):
        response =client .get ("/")
        assert response .headers .get ("X-Frame-Options")=="DENY"
        assert response .headers .get ("X-Content-Type-Options")=="nosniff"
        assert "Content-Security-Policy"in response .headers 
        assert "default-src 'self'"in response .headers ["Content-Security-Policy"]

class TestHealthz :
    def test_healthz_ok (self ,client ):
        response =client .get ("/healthz")
        assert response .status_code ==200 
        assert response .json ["status"]=="ok"

    def test_healthz_db_down (self ,client ):
        import src .main as main_mod 
        broken_factory =type ("Factory",(),{
        "__call__":lambda self :BrokenSession (),
        "remove":lambda self :None ,
        })()
        with patch .object (main_mod ,"SessionLocal",broken_factory ):
            response =client .get ("/healthz")
        assert response .status_code ==503 
        assert response .json ["status"]=="db_error"

class TestLoginRateLimit :
    def test_429_after_too_many_attempts (self ,rate_limited_client ):
        for _ in range (5 ):
            rate_limited_client .post ("/login",data ={
            "email":"nobody@x.io",
            "password":"password123",
            })
        response =rate_limited_client .post ("/login",data ={
        "email":"nobody@x.io",
        "password":"password123",
        })
        assert response .status_code ==429 

class TestForgotPassword :
    def test_renders_with_admin_contact (self ,client ):
        response =client .get ("/forgot-password")
        assert response .status_code ==200 
        assert b"admin@example.com"in response .data or b"mailto:"in response .data 

    def test_rate_limited (self ,rate_limited_client ):
        for _ in range (20 ):
            rate_limited_client .get ("/forgot-password")
        response =rate_limited_client .get ("/forgot-password")
        assert response .status_code ==429 
