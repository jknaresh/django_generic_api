from django.contrib.auth import authenticate, logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from pydantic import ValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .payload_models import FetchPayload, SavePayload
from .services import (
    get_model_by_name,
    validate_access_token,
    handle_save_input,
    fetch_data,
    generate_token,
)
from .utils import make_permission_str


class LoginAPIView(APIView):
    def post(self, *args, **kwargs):
        username = self.request.data.get("username")
        password = self.request.data.get("password")

        user = authenticate(username=username, password=password)
        if user:
            # login(self.request, user)
            token = generate_token(user)
            return Response(
                {"token": token},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class RegisterAPIView(APIView):
    def post(self, *args, **kwargs):
        email = self.request.POST["email"]
        password = self.request.POST["password"]
        password1 = self.request.POST["password1"]
        password = password.strip()

        if not password == password1:
            return Response(
                {"error": "password does not match"},
                status=status.HTTP_200_OK,
            )

        user = User.objects.filter(username=email).exists()
        if user:
            return Response(
                {"error": "Account already exists with this email."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        else:
            new_user = User(
                username=email,
                email=email,
            )
            new_user.set_password(password)
            new_user.save()
            success = "User " + email + " created successfully."
            return Response(
                {"status": success},
                status=status.HTTP_201_CREATED,
            )


class LogoutAPIView(APIView):
    def post(self, *args, **kwargs):
        logout(self.request)
        return Response(
            {"status": "Successfully logged out."}, status=status.HTTP_200_OK
        )


class ForgotPasswordAPIView(APIView):
    def post(self):
        username = self.request.POST.get("email")
        password = self.request.POST.get("password")
        password1 = self.request.POST.get("password1")
        if not password == password1:
            return Response(
                {"error": "password does not match"},
                status=status.HTTP_200_OK,
            )

        u = User.objects.get(username=username)
        u.set_password(password)
        u.save()
        return HttpResponse(
            {"status": "Password has been updated."},
            status=status.HTTP_200_OK,
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
            return Response(
                {"error": e.errors(), "code": "DGA-0E"},
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
                {"error": str(e), "code": "DGA-0M"},
                status=status.HTTP_404_NOT_FOUND,
            )
        if not self.request.user.has_perm(make_permission_str(model, "fetch")):
            return Response(
                {
                    "error": "Something went wrong!!! Please contact the "
                    "administrator.",
                    "code": "DGA-0R",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            data = fetch_data(
                model_name,
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
                {"error": str(e), "code": "DGA-0D"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class GenericSaveAPIView(APIView):

    @method_decorator(validate_access_token)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, *args, **kwargs):
        payload = self.request.data.get("payload", {}).get("variables", {})

        payload.get("saveInput", {}).pop("csrfmiddlewaretoken", "")

        try:
            # Validate the payload using the Pydantic model
            validated_data = SavePayload(**payload)
        except ValidationError as e:
            return Response(
                {"error": e.errors(), "code": "DGA-0A"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Proceed with saving the data using validated_data
        model_name = validated_data.modelName
        save_input = validated_data.saveInput
        record_id = validated_data.id
        model = get_model_by_name(model_name)
        if not model:
            return Response(
                {"error": "Model not found", "code": "DGA-0B"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        action = "save" if not record_id else "edit"
        # checks if user has permission to add or change the data
        if not self.request.user.has_perm(make_permission_str(model, action)):
            return Response(
                {
                    "error": "Something went wrong!!! Please contact the "
                    "administrator.",
                    "code": "DGA-0S",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            instance, message = handle_save_input(model, record_id, save_input)
            return Response(
                {"status": "success", "data": instance.id, "message": message},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": str(e), "code": "DGA-0C"},
                status=status.HTTP_400_BAD_REQUEST,
            )
