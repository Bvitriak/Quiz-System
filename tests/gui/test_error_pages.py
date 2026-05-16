class TestErrorPages:
    def test_404(self, client):
        response = client.get("/nonexistent-page-xyz")
        assert response.status_code == 404
        assert b"404" in response.data

    def test_405_get_on_post_only(self, client):
        response = client.get("/student/tests/1/start")
        assert response.status_code in (405, 302)
