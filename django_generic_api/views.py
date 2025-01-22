import base64
import time
from urllib.parse import quote, unquote

from captcha.helpers import captcha_image_url
from captcha.models import CaptchaStore
from django.conf import settings
from django.contrib.auth import get_user_model, logout, password_validation
from django.core.cache import cache
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.mail import send_mail
from pydantic import ValidationError
from rest_framework import status
from rest_framework.views import APIView

from .config import create_batch_size, expiry_hours
from .payload_models import (
    FetchPayload,
    SavePayload,
    GenericLoginPayload,
    GenericRegisterPayload,
    GenericForgotPasswordPayload,
    GenericNewPasswordPayload,
    GenericUserUpdatePayload,
)
from .services import (
    get_model_by_name,
    handle_save_input,
    fetch_data,
    generate_token,
    handle_user_info_update,
    read_user_info,
)
from .utils import (
    make_permission_str,
    registration_token,
    store_user_ip,
    is_valid_email_domain,
    error_response,
    success_response,
)


class GenericSaveAPIView(APIView):
    """
    Save API.
    - Length of payload if checked.
    - Strict typing is enabled for payload.
    - Checks if model exists or not.
    - Checks if user has 'add' or 'change' permission.
    - Save functionality.

    """

    def post(self, *args, **kwargs):

        payload = self.request.data.get("payload", {}).get("variables", {})

        save_input = payload.get("saveInput", [])

        # Does not allow saving more than the customized number of records
        # at once.
        if len(save_input) > create_batch_size:
            return error_response(
                error=f"Only {create_batch_size} records at once.",
                code="DGA-V001",
            )

        try:
            # Validate the payload using the Pydantic model
            validated_payload_data = SavePayload(**payload)
        except ValidationError as e:
            return error_response(
                error=e.errors()[0].get("msg"),
                code="DGA-V002",
            )

        # Proceed with saving the data using validated_payload_data
        model_name = validated_payload_data.modelName
        save_input = validated_payload_data.saveInput
        record_id = validated_payload_data.id

        try:
            model = get_model_by_name(model_name)

        except Exception as e:
            return error_response(
                error=e.args[0]["error"],
                code=e.args[0]["code"],
                http_status=e.args[0]["http_status"],
            )

        status_code = (
            status.HTTP_201_CREATED if not record_id else status.HTTP_200_OK
        )
        action = "save" if not record_id else "edit"
        # checks if user has permission to add or change the data
        if not self.request.user.has_perm(make_permission_str(model, action)):
            return error_response(
                error="Something went wrong!!! Please contact the "
                "administrator.",
                code="DGA-V004",
                http_status=status.HTTP_404_NOT_FOUND,
            )

        try:
            instances, message = handle_save_input(
                model, record_id, save_input
            )
            instance_ids = [instance.id for instance in instances]
            return success_response(
                data=[{"id": instance_ids}],
                message=message,
                http_status=status_code,
            )
        except Exception as e:
            return error_response(
                error=e.args[0]["error"], code=e.args[0]["code"]
            )


class GenericFetchAPIView(APIView):
    """
    Fetch API
    - Strict typing is enabled for payload.
    - Checks if model exists or not.
    - Checks if user has 'view' permission.
    - Fetch functionality.
    """

    def post(self, *args, **kwargs):

        payload = self.request.data.get("payload", {}).get("variables", {})
        try:
            # Validate the payload using the Pydantic model
            validated_payload_data = FetchPayload(**payload)
        except ValidationError as e:
            error_msg = e.errors()[0].get("msg")
            error_loc = e.errors()[0].get("loc")
            error = f"{error_msg}{error_loc}"

            return error_response(error=error, code="DGA-V005")

        model_name = validated_payload_data.modelName
        fields = validated_payload_data.fields
        filters = validated_payload_data.filters

        # Default values
        page_number = validated_payload_data.pageNumber
        page_size = validated_payload_data.pageSize
        sort = validated_payload_data.sort
        distinct = validated_payload_data.distinct

        # check if user has permission to view the data.
        try:
            model = get_model_by_name(model_name)
        except Exception as e:
            return error_response(
                error=e.args[0]["error"],
                code=e.args[0]["code"],
                http_status=e.args[0]["http_status"],
            )

        if not self.request.user.has_perm(make_permission_str(model, "fetch")):
            return error_response(
                error="Something went wrong!!! Please contact the "
                "administrator.",
                code="DGA-V007",
                http_status=status.HTTP_404_NOT_FOUND,
            )
        try:
            data = fetch_data(
                model,
                filters,
                fields,
                page_number,
                page_size,
                sort,
                distinct,
            )
            return success_response(
                data=data,
                message="Completed.",
            )
        except Exception as e:
            return error_response(**e.args[0])


class GenericLoginAPIView(APIView):
    """
    Login API
    - Strict typing for payload is done.
    - Checks if user exists or not.
    - Validates user's password.
    - Generates token if user is not session based.
    """

    def post(self, *args, **kwargs):
        payload = self.request.data.get("payload", {}).get("variables", {})
        try:
            validated_userdata = GenericLoginPayload(**payload)
        except ValidationError as e:
            return error_response(
                error=e.errors()[0].get("msg"), code="DGA-V008"
            )

        captcha_required = getattr(settings, "CAPTCHA_REQUIRED", False)

        # If CAPTCHA_REQUIRED is True, validate the captcha
        if captcha_required:
            captcha_key = validated_userdata.captcha_key
            captcha_value = validated_userdata.captcha_value

            try:
                # Validate the captcha response
                captcha = CaptchaStore.objects.get(hashkey=captcha_key)
                if captcha.challenge == captcha_value:
                    captcha.delete()  # Clean up after successful validation
                else:
                    return error_response(
                        error="Invalid captcha response.",
                        code="DGA-V009",
                    )
            except CaptchaStore.DoesNotExist:
                return error_response(
                    error="Invalid or expired captcha key.", code="DGA-V010"
                )

        username = validated_userdata.email
        password = validated_userdata.password.get_secret_value()

        user_model = get_user_model()
        try:
            user = user_model.objects.get(username=username)
        except user_model.DoesNotExist:
            return error_response(
                error="Username not found",
                code="DGA-V011",
                http_status=status.HTTP_404_NOT_FOUND,
            )

        auth_user = user.check_password(password)
        if not auth_user:
            return error_response(
                error="Invalid password",
                code="DGA-V012",
                http_status=status.HTTP_401_UNAUTHORIZED,
            )

        if auth_user:
            if (
                not self.request.headers.get("X-Requested-With")
                == "XMLHttpRequest"
            ):
                token = generate_token(user)
                return success_response(
                    data=token, message="Tokens are generated."
                )
            else:
                return error_response(
                    error="Token generation not allowed.", code="DGA-V013"
                )


class GenericRegisterAPIView(APIView):
    """
    Register API
    - Strict typing of payload is enabled.
    - Captcha is validated.
    - Checks is email already exists or not.
    - Passwords are validated.
    - Email domain validation is done.
    - Creates a inactive user.
    - Sends a user activation email.
    """

    def post(self, *args, **kwargs):
        payload = self.request.data.get("payload", {}).get("variables", {})
        try:
            validate_register_data = GenericRegisterPayload(**payload)
        except ValidationError as e:
            return error_response(
                error=e.errors()[0].get("msg"), code="DGA-V014"
            )

        captcha_required = getattr(settings, "CAPTCHA_REQUIRED", False)

        # If CAPTCHA_REQUIRED is True, validate the captcha
        if captcha_required:
            captcha_key = validate_register_data.captcha_key
            captcha_value = validate_register_data.captcha_value

            try:
                # Validate the captcha response
                captcha = CaptchaStore.objects.get(hashkey=captcha_key)
                if captcha.challenge == captcha_value:
                    captcha.delete()  # Clean up after successful validation
                else:
                    return error_response(
                        error="Invalid captcha response.", code="DGA-V015"
                    )
            except CaptchaStore.DoesNotExist:
                return error_response(
                    error="Invalid or expired captcha key.", code="DGA-V016"
                )

        email = validate_register_data.email

        user_model = get_user_model()

        user = user_model.objects.filter(username=email).exists()
        if user:
            return error_response(
                error="Account already exists with this email.",
                code="DGA-V017",
            )

        password = validate_register_data.password.get_secret_value()
        password1 = validate_register_data.password1.get_secret_value()

        if not password == password1:
            return error_response(
                error="passwords does not match", code="DGA-V018"
            )

        # info: Checks password strength if password validators are
        # configured in settings.
        if getattr(settings, "AUTH_PASSWORD_VALIDATORS"):
            try:
                password_validation.validate_password(password)
            except DjangoValidationError:
                return error_response(
                    error=[
                        "1. Password must contain at least 8 characters.",
                        "2. Password must not be too common.",
                        "3. Password must not be entirely numeric.",
                    ],
                    code="DGA-V019",
                )

        email_domain = email.split("@")[-1]
        if not is_valid_email_domain(email_domain):
            return error_response(
                error="Invalid email domain", code="DGA-V020"
            )

        if not getattr(settings, "BASE_URL", None):
            return error_response(
                error="Configure BASE_URL before registration.",
                code="DGA-V021",
            )

        new_user = user_model(
            username=email,
            email=email,
            is_active=False,
        )
        new_user.set_password(password)
        new_user.save()

        token = registration_token(new_user.id)
        encoded_token = quote(token)
        email_verify = f"{settings.BASE_URL}/api/v1/activate/{encoded_token}/"

        # todo : throw error if email settings arent setup
        try:
            subject = "Verify your email address for SignUp"
            message = (
                "Please click the link below to verify your "
                f"account:\n\n{email_verify}"
            )
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [email]

            send_mail(
                subject,
                message,
                from_email,
                recipient_list,
                fail_silently=False,
            )
            # todo: Remove "email_verify' variable after whole process,
            #  only for dev, remove in prod.
            return success_response(
                message=f"Email sent successfully. {email_verify}",
                data="Registration initiated.",
            )
        except Exception as e:
            return error_response(error=str(e), code="DGA-V022")


class GenericForgotPasswordAPIView(APIView):
    """
    Forgot Password API
    - Strict typing of payload is enabled.
    - Captcha is validated.
    - Checks if user exists or not.
    - New password generation email is sent.
    """

    def post(self, *args, **kwargs):
        payload = self.request.data.get("payload", {}).get("variables", {})
        try:
            validated_userdata = GenericForgotPasswordPayload(**payload)
        except ValidationError as e:
            return error_response(
                error=e.errors()[0].get("msg"), code="DGA-V023"
            )

        captcha_required = getattr(settings, "CAPTCHA_REQUIRED", False)

        # If CAPTCHA_REQUIRED is True, validate the captcha
        if captcha_required:
            captcha_key = validated_userdata.captcha_key
            captcha_value = validated_userdata.captcha_value

            try:
                # Validate the captcha response
                captcha = CaptchaStore.objects.get(hashkey=captcha_key)
                if captcha.challenge == captcha_value:
                    captcha.delete()  # Clean up after successful validation
                else:
                    return error_response(
                        error="Invalid captcha response.", code="DGA-V024"
                    )
            except CaptchaStore.DoesNotExist:
                return error_response(
                    error="Invalid or expired captcha key.", code="DGA-V025"
                )

        username = validated_userdata.email
        user_model = get_user_model()

        try:
            user = user_model.objects.get(username=username)
        except user_model.DoesNotExist:
            return error_response(
                error="User not found",
                code="DGA-V026",
                http_status=status.HTTP_404_NOT_FOUND,
            )

        token = registration_token(user.id)
        encoded_token = quote(token)
        new_password_link = (
            f"{settings.BASE_URL}/api/v1/newpassword/{encoded_token}/"
        )

        try:
            subject = "Change your password"
            message = (
                f"This link is to generate a new password: \n\n"
                f"{new_password_link}, "
                "\n\nSend a POST request to this link with defined payload "
                "to generate a new password."
            )
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [username]

            send_mail(
                subject,
                message,
                from_email,
                recipient_list,
                fail_silently=False,
            )
            # todo: Remove "new_password_link' variable after whole process,
            #  only for dev, remove in prod.
            return success_response(
                message=f"Email sent successfully. {new_password_link}",
                data="Password reset initiated.",
            )
        except Exception as e:
            return error_response(error=str(e), code="DGA-V027")


class LogoutAPIView(APIView):
    """
    Logout API.
    """

    def post(self, *args, **kwargs):
        logout(self.request)
        return success_response(
            message="Successfully logged out.", data="Bye."
        )


class AccountActivateAPIView(APIView):
    """
    Account activation API
    - Decodes the token.
    - Checks if user is already active.
    - Activates user account and stores User's IP address.
    """

    def get(self, *args, **kwargs):
        # Fetch user by ID
        user_model = get_user_model()
        try:
            # Decode token and get the user ID
            encode_token = kwargs.get("encoded_token")
            token = unquote(encode_token)
            decoded_token = base64.urlsafe_b64decode(token.encode()).decode()
            user_id, timestamp = decoded_token.split(":")

            # info: set as user customizable time
            if int(time.time()) - int(timestamp) > expiry_hours * 3600:
                return error_response(
                    error="The activation link has expired.", code="DGA-V028"
                )

            user = user_model.objects.get(id=user_id)
            if user.is_active:
                return success_response(
                    message="Account is already active.", data="User exists."
                )

            # Activate user account
            user.is_active = True
            user.save()

            # info : store user's IP address when email is activated
            user_ip = self.request.META.get("REMOTE_ADDR")
            store_user_ip(user_id, user_ip)

            return success_response(
                message="Your account has been activated successfully.",
                data="Registration completed.",
                http_status=status.HTTP_201_CREATED,
            )
        except user_model.DoesNotExist:
            return error_response(error="User not found.", code="DGA-V029")
        except Exception as e:
            return error_response(error=str(e), code="DGA-V030")


class CaptchaServiceAPIView(APIView):
    """
    Captcha Service API
    - Post and Get method are used to generate captcha key and image.
    """

    # post method
    def post(self, request, *args, **kwargs):
        # Every 10 minutes expecting to clean captcha data.
        try:
            captcha_timeout = getattr(settings, "CAPTCHA_TIMEOUT", 5)

            if not cache.get("CLEAN_CAPTCHA"):
                CaptchaStore.remove_expired()
                cache.set("CLEAN_CAPTCHA", 1, captcha_timeout + 1)
        except Exception as e:
            pass

        try:
            # Generate a new captcha key
            captcha_key = CaptchaStore.generate_key()
            # Generate the image URL
            image_url = captcha_image_url(captcha_key)

            return success_response(
                data={
                    "captcha_key": captcha_key,
                    "captcha_url": request.build_absolute_uri(image_url),
                },
                message="Captcha Generated.",
            )
        except Exception as e:
            return error_response(error=str(e), code="DGA-V031")


class NewPasswordAPIView(APIView):
    """
    New Password API
    - Decodes the token.
    - Strict typing of payload is enabled.
    - Checks if user exists or not.
    - Password validation is done.
    - User's password is updated and user is activated.
    """

    def post(self, request, *args, **kwargs):

        # Decode token and get the user ID
        encoded_token = kwargs.get("encoded_token")
        try:
            token = unquote(encoded_token)
            decoded_token = base64.urlsafe_b64decode(token.encode()).decode()
            user_id, timestamp = decoded_token.split(":")
        except (ValueError, base64.binascii.Error):
            return error_response(
                error="Invalid token format.", code="DGA-V032"
            )

        # todo: set as user customizable time
        if int(time.time()) - int(timestamp) > 24 * 3600:
            return error_response(
                error="The password reset link has expired.", code="DGA-V033"
            )

        payload = self.request.data.get("payload", {}).get("variables", {})
        try:
            validated_userdata = GenericNewPasswordPayload(**payload)
        except ValidationError as e:
            return error_response(
                error=e.errors()[0].get("msg"), code="DGA-V034"
            )

        user_model = get_user_model()
        try:
            user = user_model.objects.get(id=user_id)

            password = validated_userdata.password.get_secret_value()
            password1 = validated_userdata.password1.get_secret_value()

            if not password == password1:
                return error_response(
                    error="passwords does not match", code="DGA-V035"
                )

            if getattr(settings, "AUTH_PASSWORD_VALIDATORS"):
                try:
                    password_validation.validate_password(password)
                except DjangoValidationError:
                    return error_response(
                        error=[
                            "1. Password must contain at least 8 characters.",
                            "2. Password must not be too common.",
                            "3. Password must not be entirely numeric.",
                        ],
                        code="DGA-V036",
                    )

            user.set_password(password)
            user.is_active = True
            user.save()

            return success_response(
                message="Your password has been reset.",
                data="Password reset success",
            )
        except user_model.DoesNotExist:
            return error_response(
                error="User not found.",
                code="DGA-040",
                http_status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return error_response(error=str(e), code="DGA-V041")


class UserInfoAPIView(APIView):
    """
    User Info API.
    -  This API is used to get details of user in case of non session
    authentication methods
    """

    def post(self, *args, **kwargs):

        # checks if user has valid authorization header.
        if not self.request.user.is_authenticated:
            return error_response(
                error="User not authenticated.", code="DGA-V037"
            )

        try:
            user_info = read_user_info(user=self.request.user)
            return success_response(data=user_info, message="Completed.")
        except Exception as e:
            return error_response(
                error=e.args[0]["error"], code=e.args[0]["code"]
            )

    def put(self, *args, **kwargs):

        # checks if user has valid authorization header.
        if not self.request.user.is_authenticated:
            return error_response(
                error="User not authenticated.", code="DGA-V038"
            )

        payload = self.request.data.get("payload", {}).get("variables", {})

        try:
            # Validate the payload using the Pydantic model
            validated_payload_data = GenericUserUpdatePayload(**payload)
        except ValidationError as e:
            return error_response(
                error=e.errors()[0].get("msg"), code="DGA-V039"
            )

        save_input = validated_payload_data.saveInput

        user_id = self.request.user.id
        try:
            message = handle_user_info_update(save_input, user_id)
            return success_response(
                data=[{"id": user_id}],
                message=message,
                http_status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return error_response(
                error=e.args[0]["error"], code=e.args[0]["code"]
            )
