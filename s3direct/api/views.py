from rest_framework.views import APIView

from ..api import serializers, utils


class S3DirectWrapper(APIView):
    """Custom s3direct `get_params` method.

    It calls s3direct functions.

    This view allows to get request params as JSON instead of form-data and add
    custom policy expiration time and key equal condition to policy.
    """

    def post(self, request):
        """Get parameters for upload to S3 bucket.

        Current endpoint returns all required for direct s3 upload data,
        which should be later sent to `form_action` as `form-data` url with
        'file'. Workflow: First, you make request to this endpoint. Then send
        response data to `form_action` via `POST`.

        """
        serializer = serializers.S3DirectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return utils.get_upload_params(request=request, **serializer.data)
