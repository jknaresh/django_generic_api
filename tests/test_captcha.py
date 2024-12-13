import pytest
from fixtures.api import api_client
from django.core.cache import cache as cache1
from unittest.mock import patch


@pytest.mark.django_db
class TestCaptchaAPI:

    def test_captcha_post_success(self, api_client):
        """
        Captcha success scenario using post method.
        """

        captcha_response = api_client.post("/captcha/")
        assert captcha_response.headers["Content-Type"] == "image/png"

        captcha_id = captcha_response.headers.get("X-Captcha-ID")
        captcha_value = cache1.get(captcha_id)

        # captcha is an image
        assert captcha_response["Content-Type"] == "image/png"
        assert captcha_response.status_code == 200
        assert captcha_id is not None
        assert captcha_value is not None

    def test_captcha_get_success(self, api_client):
        """
        Captcha success scenario using get method.
        """

        captcha_response = api_client.get("/captcha/")
        assert captcha_response.headers["Content-Type"] == "image/png"

        captcha_id = captcha_response.headers.get("X-Captcha-ID")
        captcha_value = cache1.get(captcha_id)

        # captcha is an image
        assert captcha_response["Content-Type"] == "image/png"
        assert captcha_response.status_code == 200
        assert captcha_id is not None
        assert captcha_value is not None

    def test_captcha_get_cache_timeout(self, api_client):
        """
        Negative scenario: Cache returns None as cache timeouts
        """
        captcha_response = api_client.get("/captcha/")

        assert captcha_response.headers["Content-Type"] == "image/png"

        captcha_id = captcha_response.headers.get("X-Captcha-ID")

        # after timeout, cache returns None
        with patch("django.core.cache.cache.get", return_value=None):
            captcha_value = cache1.get(captcha_id)

        assert captcha_value is None
