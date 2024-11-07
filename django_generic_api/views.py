import time
from symbol import raise_stmt
from urllib.parse import quote, unquote

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils.decorators import method_decorator
from pydantic import ValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .payload_models import (
    FetchPayload,
    SavePayload,
    GenericLoginPayload,
    GenericRegisterPayload,
)
from .services import (
    get_model_by_name,
    validate_access_token,
    handle_save_input,
    fetch_data,
    generate_token,
)
from .utils import (
    make_permission_str,
    registration_token,
    store_user_ip,
    is_valid_domain,
    CustomAPIError,
)


class GenericSaveAPIView(APIView):

    @method_decorator(validate_access_token)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, *args, **kwargs):

        payload = self.request.data.get("payload", {}).get("variables", {})

        saveInput = payload.get("saveInput", {})

        # Does not allow to save more than 10 records at once
        if len(saveInput) > 10:
            custom_error = CustomAPIError(
                error="Only 10 records at once.",
                code="DGA-V001",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
            return Response(
                {
                    "error": custom_error.error,
                    "code": custom_error.code,
                },
                status=custom_error.status_code,
            )

        try:
            # Validate the payload using the Pydantic model
            validated_payload_data = SavePayload(**payload)
        except ValidationError as e:
            custom_error = CustomAPIError(
                error=e.errors()[0]["msg"],
                code="DGA-V002",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
            return Response(
                {
                    "error": custom_error.error,
                    "code": custom_error.code,
                },
                status=custom_error.status_code,
            )

        # Proceed with saving the data using validated_payload_data
        model_name = validated_payload_data.modelName
        save_input = validated_payload_data.saveInput
        record_id = validated_payload_data.id

        try:
            model = get_model_by_name(model_name)
        except CustomAPIError as e:
            return Response(
                {
                    "error": e.error,
                    "code": e.code,
                },
                status=e.status_code,
            )

        action = "save" if not record_id else "edit"
        # checks if user has permission to add or change the data
        if not self.request.user.has_perm(make_permission_str(model, action)):
            custom_error = CustomAPIError(
                error="Something went wrong!!! Please contact the administrator.",
                code="DGA-V003",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
            return Response(
                {
                    "error": custom_error.error,
                    "code": custom_error.code,
                },
                status=custom_error.status_code,
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
        except CustomAPIError as e:
            return Response(
                {"error": e.error, "code": e.code}, status=e.status_code
            )


class GenericFetchAPIView(APIView):

    # authenticates user by token
    @method_decorator(validate_access_token)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, *args, **kwargs):

        payload = self.request.data.get("payload", {}).get("variables", {})

        try:
            # Validate the payload using the Pydantic model
            validated_payload_data = FetchPayload(**payload)
        except ValidationError as e:
            custom_error = CustomAPIError(
                error=e.errors()[0]["msg"],
                code="DGA-V004",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
            return Response(
                {"error": custom_error.error, "code": custom_error.code},
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

        try:
            model = get_model_by_name(model_name)
        except CustomAPIError as e:
            return Response(
                {
                    "error": e.error,
                    "code": e.code,
                },
                status=e.status_code,
            )

        # check if user has permission to view the data.
        if not self.request.user.has_perm(make_permission_str(model, "fetch")):
            custom_error = CustomAPIError(
                error="Something went wrong!!! Please contact the administrator.",
                code="DGA-V005",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
            return Response(
                {
                    "error": custom_error.error,
                    "code": custom_error.code,
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
        except CustomAPIError as e:
            return Response(
                {"error": e.error, "code": e.code},
                status=e.status_code,
            )


class GenericLoginAPIView(APIView):

    def post(self, *args, **kwargs):
        payload = self.request.data.get("payload", {}).get("variables", {})
        try:
            validated_userdata = GenericLoginPayload(**payload)
        except ValidationError as e:
            custom_error = CustomAPIError(
                error=e.errors()[0]["msg"],
                code="DGA-V006",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
            return Response(
                {"error": custom_error.error, "code": custom_error.code},
                status=custom_error.status_code,
            )

        username = validated_userdata.email
        password = validated_userdata.password.get_secret_value()

        user_model = get_user_model()
        try:
            user = user_model.objects.get(username=username)
        except user_model.DoesNotExist:
            custom_error = CustomAPIError(
                error="Username not found",
                code="DGA-V007",
                status_code=status.HTTP_404_NOT_FOUND,
            )
            return Response(
                {"error": custom_error.error, "code": custom_error.code},
                status=custom_error.status_code,
            )

        auth_user = user.check_password(password)
        if not auth_user:
            custom_error = CustomAPIError(
                error="Invalid password",
                code="DGA-V008",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
            return Response(
                {"error": custom_error.error, "code": custom_error.code},
                status=custom_error.status_code,
            )

        if auth_user:
            # info: Users cannot generate tokens via AJAX. Token generation
            # is only allowed through tools like Postman.
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
                custom_error = CustomAPIError(
                    error="Token generation not allowed.",
                    code="DGA-V009",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
                return Response(
                    {
                        "error": custom_error.error,
                        "code": custom_error.code,
                    },
                    status=custom_error.status_code,
                )


class GenericRegisterAPIView(APIView):

    def post(self, *args, **kwargs):
        payload = self.request.data.get("payload", {}).get("variables", {})
        try:
            validate_register_data = GenericRegisterPayload(**payload)
        except ValidationError as e:
            custom_error = CustomAPIError(
                error=e.errors()[0]["msg"],
                code="DGA-V010",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
            return Response(
                {"error": custom_error.error, "code": custom_error.code},
                status=custom_error.status_code,
            )

        email = validate_register_data.email
        # todo: password strength
        password = validate_register_data.password.get_secret_value()
        password1 = validate_register_data.password1.get_secret_value()

        if not password == password1:
            custom_error = CustomAPIError(
                error="Passwords does not match",
                code="DGA-V011",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
            return Response(
                {"error": custom_error.error, "code": custom_error.code},
                status=custom_error.status_code,
            )

        email_domain = email.split("@")[-1]
        if not is_valid_domain(email_domain):
            custom_error = CustomAPIError(
                error="Invalid email domain",
                code="DGA-V012",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
            return Response(
                {"error": custom_error.error, "code": custom_error.code},
                status=custom_error.status_code,
            )

        user = User.objects.filter(username=email).exists()
        if user:
            custom_error = CustomAPIError(
                error="Account already exists with this email.",
                code="DGA-V013",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
            return Response(
                {
                    "error": custom_error.error,
                    "code": custom_error.code,
                },
                status=custom_error.status_code,
            )
        else:
            new_user = User(
                username=email,
                email=email,
                is_active=False,
            )
            new_user.set_password(password)
            new_user.save()

            token = registration_token(new_user.id)
            encoded_token = quote(token)
            email_verify = (
                f"{settings.BASE_URL}/api/activate/" f"{encoded_token}/"
            )  # todo: throw error if no
            # base url

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
                custom_error = CustomAPIError(
                    error=str(e),
                    code="DGA-V014",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
                return Response(
                    {"error": custom_error.error, "code": custom_error.code},
                    status=custom_error.status_code,
                )


class GenericForgotPasswordAPIView(APIView):
    # WIP: continue process
    def post(self, *args, **kwargs):
        payload = self.request.data.get("payload", {}).get("variables", {})
        try:
            validated_email = ForgotPasswordPayload(**payload)
        except ValidationError as e:
            custom_error = CustomAPIError(
                error=e.errors()[0]["msg"],
                code="DGA-V015",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
            return Response(
                {"error": custom_error.error, "code": custom_error.code},
                status=custom_error.status_code,
            )


class LogoutAPIView(APIView):

    def post(self, *args, **kwargs):
        logout(self.request)
        return Response(
            {"message": "Successfully logged out."}, status=status.HTTP_200_OK
        )


class AccountActivateAPIView(APIView):

    def get(self, request, encoded_token, *args, **kwargs):
        try:
            # Decode token and get the user ID
            token = unquote(encoded_token)
            user_id, timestamp = token.split(":")

            # todo: set as user customizable time
            if int(time.time()) - int(timestamp) > 24 * 3600:
                custom_error = CustomAPIError(
                    error="The activation link has expired.",
                    code="DGA-V016",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
                return Response(
                    {
                        "error": custom_error.error,
                        "code": custom_error.code,
                    },
                    status=custom_error.status_code,
                )

            if User.DoesNotExist:
                raise CustomAPIError(
                    error="User not found.",
                    code="DGA-V017",
                    status_code=status.HTTP_404_NOT_FOUND,
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

        except CustomAPIError as e:
            return Response(
                {"error": e.error, "code": e.code},
                status=e.status_code,
            )

        except Exception as e:
            custom_error = CustomAPIError(
                error=str(e),
                code="DGA-V018",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
            return Response(
                {"error": custom_error.error, "code": custom_error.code},
                status=custom_error.status_code,
            )
