from pydantic import ValidationError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .payload_models import FetchPayload, SavePayload
from .services import (
    get_model_by_name,
    handle_save_input,
    fetch_data,
)


class GenericFetchAPIView(APIView):

    def post(self, *args, **kwargs):
        payload = self.request.data.get("payload", {}).get("variables", {})
        try:
            # Validate the payload using the Pydantic model
            validated_data = FetchPayload(**payload)
        except ValidationError as e:
            return Response({"error": e.errors()}, status=400)

        model_name = validated_data.modelName
        fields = validated_data.fields
        filters = validated_data.filters

        # Default values
        page_number = getattr(validated_data, "pageNumber")
        page_size = getattr(validated_data, "pageSize")
        sort = validated_data.sort

        try:
            data = fetch_data(
                model_name, filters, fields, page_number, page_size, sort
            )
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )


class GenericSaveAPIView(APIView):

    def post(self, *args, **kwargs):
        payload = self.request.data.get("payload", {}).get("variables", {})

        payload.get("saveInput", {}).pop("csrfmiddlewaretoken", "")

        try:
            # Validate the payload using the Pydantic model
            validated_data = SavePayload(**payload)
        except ValidationError as e:
            return Response({"error": e.errors()}, status=400)

        # Proceed with saving the data using validated_data
        model_name = validated_data.modelName
        save_input = validated_data.saveInput
        record_id = validated_data.id

        model = get_model_by_name(model_name)
        if not model:
            return Response(
                {"error": "Model not found"},
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
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )