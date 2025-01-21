from unittest.mock import patch

import pytest

from fixtures.api import api_client


@pytest.mark.django_db
class TestCaptchaAPI:

    def test_captcha_post_success(self, api_client):
        """
        Captcha success scenario using post method.
        """

        captcha_response = api_client.post("/v1/generate-captcha/")

        # captcha is an image
        assert captcha_response["Content-Type"] == "application/json"
        assert captcha_response.status_code == 200
        assert "captcha_key" in captcha_response.data["data"]
        assert "captcha_url" in captcha_response.data["data"]
        assert captcha_response.data["message"] == "Captcha Generated."

    def test_captcha_post_failure(self, api_client):
        """
        Test Captcha API failure scenario when CaptchaStore.generate_key fails.
        """

        # Mock CaptchaStore.generate_key to raise an exception
        with patch(
            "captcha.models.CaptchaStore.generate_key"
        ) as mock_generate_key:
            mock_generate_key.side_effect = Exception(
                "Failed to generate captcha key"
            )

            # Make a POST request to the captcha endpoint
            captcha_response = api_client.post("/v1/generate-captcha/")

            # Assertions
            assert (
                captcha_response.data["error"]
                == "Failed to generate captcha key"
            )
            assert captcha_response.data["code"] == "DGA-V031"
            assert captcha_response.status_code == 400
