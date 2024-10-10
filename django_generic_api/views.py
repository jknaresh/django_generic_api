from django.contrib.auth import authenticate, logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from pydantic import ValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.core.mail import send_mail
from django.conf import settings
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
from .utils import make_permission_str, registration_token
from django.utils import timezone
import hashlib
import time
from django.urls import reverse
from django.utils.http import urlencode


class GenericSaveAPIView(APIView):

    @method_decorator(validate_access_token)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, *args, **kwargs):
        payload = self.request.data.get("payload", {}).get("variables", {})

        record_count = payload.get("saveInput", {})

        # Does not allow to save more than 10 records at once
        if len(record_count) > 10:
            return Response(
                {"error": "Only 10 records at once.", "code": "DGA-0A"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Validate the payload using the Pydantic model
            validated_data = SavePayload(**payload)
        except ValidationError as e:
            return Response(
                {"error": e.errors()[0].get("msg"), "code": "DGA-0B"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Proceed with saving the data using validated_data
        model_name = validated_data.modelName
        save_input = validated_data.saveInput
        record_id = validated_data.id

        try:
            model = get_model_by_name(model_name)
        except ValueError:
            return Response(
                {"error": "Model not found", "code": "DGA-0C"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        action = "save" if not record_id else "edit"
        # checks if user has permission to add or change the data
        if not self.request.user.has_perm(make_permission_str(model, action)):
            return Response(
                {
                    "error": "Something went wrong!!! Please contact the "
                    "administrator.",
                    "code": "DGA-0D",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            instances, message = handle_save_input(
                model, record_id, save_input
            )
            instance_ids = [{"id": instance.id} for instance in instances]
            return Response(
                {"data": [{"id": instance_ids}], "message": message},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": str(e), "code": "DGA-0E"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class GenericFetchAPIView(APIView):

    @method_decorator(validate_access_token)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, *args, **kwargs):
        payload = self.request.data.get("payload", {}).get("variables", {})
        try:
            # Validate the payload using the Pydantic model
            validated_data = FetchPayload(**payload)
        except ValidationError as e:
            error_msg = e.errors()[0].get("msg")
            error_loc = e.errors()[0].get("loc")
            error = f"{error_msg}{error_loc}"

            return Response(
                {"error": error, "code": "DGA-0F"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        model_name = validated_data.modelName
        fields = validated_data.fields
        filters = validated_data.filters

        # Default values
        page_number = validated_data.pageNumber
        page_size = validated_data.pageSize
        sort = validated_data.sort
        distinct = validated_data.distinct

        # check if user has permission to view the data.
        try:
            model = get_model_by_name(model_name)
        except Exception as e:
            return Response(
                {"error": str(e), "code": "DGA-0G"},
                status=status.HTTP_404_NOT_FOUND,
            )
        if not self.request.user.has_perm(make_permission_str(model, "fetch")):
            return Response(
                {
                    "error": "Something went wrong!!! Please contact the "
                    "administrator.",
                    "code": "DGA-0H",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        data = fetch_data(
            model,
            filters,
            fields,
            page_number,
            page_size,
            sort,
            distinct,
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
                {"error": str(e), "code": "DGA-0I"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class GenericLoginAPIView(APIView):
    def post(self, *args, **kwargs):
        payload = self.request.data.get("payload", {}).get("variables", {})
        try:
            validated_userdata = GenericLoginPayload(**payload)
        except ValidationError as e:
            return Response(
                {"error": e.errors()[0].get("msg"), "code": "DGA-0J"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        username = validated_userdata.email
        password = validated_userdata.password.get_secret_value()

        user = authenticate(username=username, password=password)
        if user:
            token = generate_token(user)
            return Response(
                {"data": token},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "Invalid credentials", "code": "DGA-0K"},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class GenericRegisterAPIView(APIView):
    def post(self, *args, **kwargs):
        payload = self.request.data.get("payload", {}).get("variables", {})
        try:
            validate_register_data = GenericRegisterPayload(**payload)
        except ValidationError as e:
            return Response(
                {"error": e.errors()[0].get("msg"), "code": "DGA-0L"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = validate_register_data.email
        password = validate_register_data.password.get_secret_value()
        password1 = validate_register_data.password1.get_secret_value()

        if not password == password1:
            return Response(
                {"error": "passwords does not match", "code": "DGA-0M"},
                status=status.HTTP_200_OK,
            )

        user = User.objects.filter(username=email).exists()
        if user:
            return Response(
                {
                    "error": "Account already exists with this email.",
                    "code": "DGA-0N",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            new_user = User(
                username=email,
                email=email,
            )
            new_user.set_password(password)
            new_user.is_active = False
            new_user.save()

            token = registration_token(new_user.id)

            try:
                subject = "Verify your email address for SignUp"
                message = f"Your verification link is {token}"
                from_email = settings.EMAIL_HOST_USER
                recipient_list = [email]
                fail_silently = False

                send_mail(
                    subject, message, from_email, recipient_list, fail_silently
                )
                return Response(
                    {"message": "Email sent successfully."},
                    status=status.HTTP_200_OK,
                )
            except Exception as e:
                return Response(
                    {"error": str(e), "code": "DGA-0O"},
                    status=status.HTTP_400_BAD_REQUEST,
                )


class GenericForgotPasswordAPIView(APIView):
    def post(self, *args, **kwargs):
        payload = self.request.data.get("payload", {}).get("variables", {})
        try:
            validated_email = ForgotPasswordPayload(**payload)
        except ValidationError as e:
            return Response(
                {"error": e.errors()[0].get("msg"), "code": "DGA-0P"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class LogoutAPIView(APIView):
    def post(self, *args, **kwargs):
        logout(self.request)
        return Response(
            {"status": "Successfully logged out."}, status=status.HTTP_200_OK
        )
