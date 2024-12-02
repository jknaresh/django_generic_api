import pytest
from fixtures.API import api_client
from django.core.cache import cache as cache1


@pytest.mark.django_db
class TestCaptchaAPI:

    def test_captcha_success(self, api_client):
        """
        Captcha success scenario.
        """

        captcha_response = api_client.get("/captcha/")

        captcha_id = captcha_response.headers.get("X-Captcha-ID")
        captcha_number = cache1.get(captcha_id)

        # captcha is an image
        assert captcha_response["Content-Type"] == "image/png"
        assert captcha_response.status_code == 200
        assert captcha_id is not None
        assert captcha_number is not None
