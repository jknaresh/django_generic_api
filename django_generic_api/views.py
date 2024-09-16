from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import get_model_by_name, apply_filters, handle_save_input


class GenericFetchAPIView(APIView):

    def post(self, request, *args, **kwargs):
        payload = request.data.get("payload", {}).get("variables", {})
        model_name = payload.get("modelName")
        fields = payload.get("fields", [])
        filters = payload.get("filters", [])

        model = get_model_by_name(model_name)
        if not model:
            return Response(
                {"error": "Model not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        query_filters = apply_filters(filters)

        try:
            queryset = model.objects.filter(query_filters).values(*fields)
            return Response(
                {"data": list(queryset)}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )


class GenericSaveAPIView(APIView):

    def post(self, request, *args, **kwargs):
        payload = request.data.get("payload", {}).get("variables", {})
        model_name = payload.get("modelName")
        save_input = payload.get("saveInput", {})
        record_id = payload.get("id", None)

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
