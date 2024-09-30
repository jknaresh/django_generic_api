from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
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


class LoginAPIView(APIView):
    def post(self, *args, **kwargs):
        username = self.request.data.get("username")
        password = self.request.data.get("password")

        user = authenticate(username=username, password=password)
        if user:
            login(self.request, user)
            token = generate_token(user)
            return Response(
                {"token": token},
                status=status.HTTP_200_OK,
            )
        if not User.objects.filter(username=username).exists():
            message = "Account with {" + username + "} email does not exist."
            return Response(message, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class RegisterAPIView(APIView):
    def post(self, *args, **kwargs):
        username = self.request.POST["username"]
        email = self.request.POST["email"]
        firstname = self.request.POST["firstname"]
        lastname = self.request.POST["lastname"]
        password = self.request.POST["password"]

        user = User.objects.filter(email=email).exists()
        if user:
            return HttpResponse("Account already exists with this email.")
        else:
            new_user = User.objects.create_user(
                username=username,
                email=email,
                password=make_password(password),
                firstname=firstname,
                lastname=lastname,
            )
            new_user.save()
            success = "User " + email + " created successfully."
            return HttpResponse(success, status=status.HTTP_200_OK)


class LogoutAPIView(APIView):
    def post(self, request):
        logout(request)
        return Response(
            {"status": "Successfully logged out."}, status=status.HTTP_200_OK
        )


class ForgotPasswordAPIView(APIView):
    def post(self):
        username = self.request.POST.get("username")
        password = self.request.POST.get("password")
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
