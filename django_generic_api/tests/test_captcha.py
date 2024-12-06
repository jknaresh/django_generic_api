import pytest
from fixtures.API import api_client
from django.core.cache import cache as cache1


@pytest.mark.django_db
class TestCaptchaAPI:

    def test_captcha_post_success(self, api_client):
        """
        Captcha success scenario using post method.
        """

        captcha_response = api_client.post("/captcha/")
        assert captcha_response.headers["Content-Type"] == "image/png"

        captcha_id = captcha_response.headers.get("X-Captcha-ID")
        captcha_number = cache1.get(captcha_id)

        # captcha is an image
        assert captcha_response["Content-Type"] == "image/png"
        assert captcha_response.status_code == 200
        assert captcha_id is not None
        assert captcha_number is not None

    def test_captcha_get_success(self, api_client):
        """
        Captcha success scenario using get method.
        """

        captcha_response = api_client.get("/captcha/")
        assert captcha_response.headers["Content-Type"] == "image/png"

        captcha_id = captcha_response.headers.get("X-Captcha-ID")
        captcha_number = cache1.get(captcha_id)

        # captcha is an image
        assert captcha_response["Content-Type"] == "image/png"
        assert captcha_response.status_code == 200
        assert captcha_id is not None
        assert captcha_number is not None
