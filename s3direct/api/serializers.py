from django.conf import settings
from rest_framework import serializers

DESTINATION_CHOICES = [
    (destination, destination) for destination in
    settings.S3DIRECT_DESTINATIONS.keys()
]


class S3DirectSerializer(serializers.Serializer):
    """Serializer for validation s3direct uploading fields."""
    dest = serializers.ChoiceField(
        choices=DESTINATION_CHOICES,
        default=settings.DEFAULT_DESTINATION
    )
    filename = serializers.CharField(required=False, allow_null=True)
    content_type = serializers.CharField(
        required=False, allow_null=True, allow_blank=True
    )


class S3UploadSerializer(serializers.Serializer):
    """Serializer for S3DirectWrapper auto swagger documentation.

    This serializer used just for drf-yasg package, so that front-end team
    could see specs for response for S3DirectWrapper view.

    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        fields = (
            'policy',
            'success_action_status',
            'x-amz-credential',
            'x-amz-date',
            'x-amz-signature',
            'x-amz-algorithm',
            'form_action',
            'key',
            'acl',
            'x-amz-security-token',
            'content-type',
            'Cache-Control',
            'Content-Disposition',
        )
        for field in fields:
            self.fields[field] = serializers.CharField(
                label=field,
                required=False,
            )
