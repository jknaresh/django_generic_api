import base64
import time
from urllib.parse import quote, unquote

from captcha.helpers import captcha_image_url
from captcha.models import CaptchaStore
from django.conf import settings
from django.contrib.auth import get_user_model, logout, password_validation
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from pydantic import ValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .config import create_batch_size, expiry_hours
from .payload_models import (
    FetchPayload,
    SavePayload,
    GenericLoginPayload,
    GenericRegisterPayload,
    GenericForgotPasswordPayload,
    GenericNewPasswordPayload,
)
from .services import (
    get_model_by_name,
    handle_save_input,
    fetch_data,
    generate_token,
)
from .utils import (
    make_permission_str,
    registration_token,
    store_user_ip,
    is_valid_email_domain,
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

        saveInput = payload.get("saveInput", {})

        # Does not allow saving more than the customized number of records
        # at once.
        if len(saveInput) > create_batch_size:
            return Response(
                {
                    "error": f"Only {create_batch_size} records at once.",
                    "code": "DGA-V001",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Validate the payload using the Pydantic model
            validated_payload_data = SavePayload(**payload)
        except ValidationError as e:
            return Response(
                {"error": e.errors()[0].get("msg"), "code": "DGA-V002"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Proceed with saving the data using validated_payload_data
        model_name = validated_payload_data.modelName
        save_input = validated_payload_data.saveInput
        record_id = validated_payload_data.id

        try:
            model = get_model_by_name(model_name)
        except (ValueError, LookupError) as e:
            return Response(
                {"error": "Model not found", "code": "DGA-V003"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        action = "save" if not record_id else "edit"
        # checks if user has permission to add or change the data
        if not self.request.user.has_perm(make_permission_str(model, action)):
            return Response(
                {
                    "error": "Something went wrong!!! Please contact the "
                    "administrator.",
                    "code": "DGA-V004",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            instances, message = handle_save_input(
                model, record_id, save_input
            )
            instance_ids = [instance.id for instance in instances]
            return Response(
                {"data": [{"id": instance_ids}], "message": message},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {"error": str(e), "code": "DGA-V005"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class GenericFetchAPIView(APIView):
    """
    Fetch API
    - Strict typing is enabled for payload.
    - Checks if model exists or not.
    - Checks if user has 'view' permission.
    - Fetch fuctionality.
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

            return Response(
                {"error": error, "code": "DGA-V006"},
                status=status.HTTP_400_BAD_REQUEST,
            )

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
        except (ValueError, LookupError) as e:
            return Response(
                {"error": "Model not found", "code": "DGA-V007"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not self.request.user.has_perm(make_permission_str(model, "fetch")):
            return Response(
                {
                    "error": "Something went wrong!!! Please contact the "
                    "administrator.",
                    "code": "DGA-V008",
                },
                status=status.HTTP_404_NOT_FOUND,
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
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e), "code": "DGA-V009"},
                status=status.HTTP_400_BAD_REQUEST,
            )


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
            return Response(
                {"error": e.errors()[0].get("msg"), "code": "DGA-V010"},
                status=status.HTTP_400_BAD_REQUEST,
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
                    return Response(
                        {
                            "error": "Invalid captcha response.",
                            "code": "DGA-V025",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            except CaptchaStore.DoesNotExist:
                return Response(
                    {
                        "error": "Invalid or expired captcha key.",
                        "code": "DGA-V027",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        username = validated_userdata.email
        password = validated_userdata.password.get_secret_value()

        user_model = get_user_model()
        try:
            user = user_model.objects.get(username=username)
        except user_model.DoesNotExist:
            return Response(
                {"error": "Username not found", "code": "DGA-V011"},
                status=status.HTTP_404_NOT_FOUND,
            )

        auth_user = user.check_password(password)
        if not auth_user:
            return Response(
                {"error": "Invalid password", "code": "DGA-V012"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if auth_user:
            if (
                not self.request.headers.get("X-Requested-With")
                == "XMLHttpRequest"
            ):
                token = generate_token(user)
                return Response(
                    {"data": token},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {
                        "error": "Token generation not allowed.",
                        "code": "DGA-V021",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
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
            return Response(
                {"error": e.errors()[0].get("msg"), "code": "DGA-V013"},
                status=status.HTTP_400_BAD_REQUEST,
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
                    return Response(
                        {
                            "error": "Invalid captcha response.",
                            "code": "DGA-V025",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            except CaptchaStore.DoesNotExist:
                return Response(
                    {
                        "error": "Invalid or expired captcha key.",
                        "code": "DGA-V027",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        email = validate_register_data.email

        user = User.objects.filter(username=email).exists()
        if user:
            return Response(
                {
                    "error": "Account already exists with this email.",
                    "code": "DGA-V015",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        password = validate_register_data.password.get_secret_value()
        password1 = validate_register_data.password1.get_secret_value()

        if not password == password1:
            return Response(
                {"error": "passwords does not match", "code": "DGA-V014"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # info: Checks password strength if password validators are
        # configured in settings.
        if getattr(settings, "AUTH_PASSWORD_VALIDATORS"):
            try:
                password_validation.validate_password(password)
            except DjangoValidationError:
                return Response(
                    {
                        "error": [
                            "1. Password must contain at least 8 characters.",
                            "2. Password must not be too common.",
                            "3. Password must not be entirely numeric.",
                        ],
                        "code": "DGA-V024",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        email_domain = email.split("@")[-1]
        if not is_valid_email_domain(email_domain):
            return Response(
                {"error": "Invalid email domain", "code": "DGA-V022"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not getattr(settings, "BASE_URL", None):
            return Response(
                {
                    "error": "Configure BASE_URL before registration.",
                    "code": "DGA-V023",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        new_user = User(
            username=email,
            email=email,
            is_active=False,
        )
        new_user.set_password(password)
        new_user.save()

        token = registration_token(new_user.id)
        encoded_token = quote(token)
        email_verify = f"{settings.BASE_URL}/api/activate/" f"{encoded_token}/"

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
            return Response(
                {"message": f"Email sent successfully. {email_verify}"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": str(e), "code": "DGA-V016"},
                status=status.HTTP_400_BAD_REQUEST,
            )


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
            return Response(
                {"error": e.errors()[0].get("msg"), "code": "DGA-V017"},
                status=status.HTTP_400_BAD_REQUEST,
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
                    return Response(
                        {
                            "error": "Invalid captcha response.",
                            "code": "DGA-V026",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            except CaptchaStore.DoesNotExist:
                return Response(
                    {
                        "error": "Invalid or expired captcha key.",
                        "code": "DGA-V036",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        username = validated_userdata.email
        user_model = get_user_model()

        try:
            user = user_model.objects.get(username=username)
        except user_model.DoesNotExist:
            return Response(
                {"error": "User not found", "code": "DGA-V037"},
                status=status.HTTP_404_NOT_FOUND,
            )

        token = registration_token(user.id)
        encoded_token = quote(token)
        new_password_link = (
            f"{settings.BASE_URL}/api/newpassword/" f"{encoded_token}/"
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
            return Response(
                {"message": f"Email sent successfully. {new_password_link}"},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": str(e), "code": "DGA-V028"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class LogoutAPIView(APIView):
    """
    Logout API.
    """

    def post(self, *args, **kwargs):
        logout(self.request)
        return Response(
            {"message": "Successfully logged out."}, status=status.HTTP_200_OK
        )


class AccountActivateAPIView(APIView):
    """
    Account activation API
    - Decodes the token.
    - Checks if user is already active.
    - Activates user account and stores User's IP address.
    """

    def get(self, request, encoded_token, *args, **kwargs):
        try:
            # Decode token and get the user ID
            token = unquote(encoded_token)
            decoded_token = base64.urlsafe_b64decode(token.encode()).decode()
            user_id, timestamp = decoded_token.split(":")

            # info: set as user customizable time
            if int(time.time()) - int(timestamp) > expiry_hours * 3600:
                return Response(
                    {
                        "error": "The activation link has expired.",
                        "code": "DGA-V018",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Fetch user by ID
            user = User.objects.get(id=user_id)
            if user.is_active:
                return Response(
                    {"message": "Account is already active."},
                    status=status.HTTP_200_OK,
                )

            # Activate user account
            user.is_active = True
            user.save()

            # info : store user's IP address when email is activated
            user_ip = request.META.get("REMOTE_ADDR")
            store_user_ip(user_id, user_ip)

            return Response(
                {"message": "Your account has been activated successfully."},
                status=status.HTTP_201_CREATED,
            )
        except User.DoesNotExist:
            return Response(
                {"error": "User not found.", "code": "DGA-V019"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": str(e), "code": "DGA-V020"},
                status=status.HTTP_400_BAD_REQUEST,
            )


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

            return Response(
                {
                    "captcha_key": captcha_key,
                    "captcha_url": request.build_absolute_uri(image_url),
                }
            )
        except Exception as e:
            return Response(
                {"error": str(e), "code": "DGA-V029"},
                status=status.HTTP_400_BAD_REQUEST,
            )


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
            return Response(
                {"error": "Invalid token format.", "code": "DGA-V035"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # todo: set as user customizable time
        if int(time.time()) - int(timestamp) > 24 * 3600:
            return Response(
                {
                    "error": "The password reset link has expired.",
                    "code": "DGA-V031",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        payload = self.request.data.get("payload", {}).get("variables", {})
        try:
            validated_userdata = GenericNewPasswordPayload(**payload)
        except ValidationError as e:
            return Response(
                {"error": e.errors()[0].get("msg"), "code": "DGA-V032"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = get_object_or_404(User, id=user_id)

        password = validated_userdata.password.get_secret_value()
        password1 = validated_userdata.password1.get_secret_value()

        if not password == password1:
            return Response(
                {"error": "passwords does not match", "code": "DGA-V033"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if getattr(settings, "AUTH_PASSWORD_VALIDATORS"):
            try:
                password_validation.validate_password(password)
            except DjangoValidationError:
                return Response(
                    {
                        "error": [
                            "1. Password must contain at least 8 characters.",
                            "2. Password must not be too common.",
                            "3. Password must not be entirely numeric.",
                        ],
                        "code": "DGA-V034",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        user.set_password(password)
        user.is_active = True
        user.save()

        return Response(
            {"message": "Your password has been reset."},
            status=status.HTTP_200_OK,
        )


class UserInfoAPIView(APIView):
    """
    User Info API.
    -  This API is used to get details of user in case of non session authentication methods
    """

    def post(self, *args, **kwargs):

        if not self.request.user.is_authenticated:
            return Response(
                {"error": "User not authenticated.", "code": "DGA-V030"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {
                "data": [
                    {
                        "email": self.request.user.email,
                        "first_name": self.request.user.first_name,
                        "last_name": self.request.user.last_name,
                    }
                ]
            },
            status=status.HTTP_200_OK,
        )
