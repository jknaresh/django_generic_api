import time
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
            return Response(
                {"error": "Only 10 records at once.", "code": "DGA-V001"},
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
        except ValueError:
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
        except Exception as e:
            return Response(
                {"error": str(e), "code": "DGA-V007"},
                status=status.HTTP_404_NOT_FOUND,
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

    def post(self, *args, **kwargs):
        payload = self.request.data.get("payload", {}).get("variables", {})
        try:
            validated_userdata = GenericLoginPayload(**payload)
        except ValidationError as e:
            return Response(
                {"error": e.errors()[0].get("msg"), "code": "DGA-V010"},
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

    def post(self, *args, **kwargs):
        payload = self.request.data.get("payload", {}).get("variables", {})
        try:
            validate_register_data = GenericRegisterPayload(**payload)
        except ValidationError as e:
            return Response(
                {"error": e.errors()[0].get("msg"), "code": "DGA-V013"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = validate_register_data.email
        password = validate_register_data.password.get_secret_value()
        password1 = validate_register_data.password1.get_secret_value()

        if not password == password1:
            return Response(
                {"error": "passwords does not match", "code": "DGA-V014"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(username=email).exists()
        if user:
            return Response(
                {
                    "error": "Account already exists with this email.",
                    "code": "DGA-V015",
                },
                status=status.HTTP_400_BAD_REQUEST,
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
            email_verify = f"{settings.BASE_URL}/api/activate/{encoded_token}/"

            try:
                subject = "Verify your email address for SignUp"
                message = (
                    f"Please click the link below to verify your "
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
                # todo: Remove "email_verify' variable after whole process.
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

    def post(self, *args, **kwargs):
        payload = self.request.data.get("payload", {}).get("variables", {})
        try:
            validated_email = ForgotPasswordPayload(**payload)
        except ValidationError as e:
            return Response(
                {"error": e.errors()[0].get("msg"), "code": "DGA-V017"},
                status=status.HTTP_400_BAD_REQUEST,
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

            # Token expires after 24 hours
            if int(time.time()) - int(timestamp) > 24 * 3600:
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
