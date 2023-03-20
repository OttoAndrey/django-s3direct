from urllib.parse import unquote, unquote_plus, urlparse

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.validators import URLValidator
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.settings import api_settings

from botocore.exceptions import ParamValidationError


class S3DirectUploadURLField(serializers.URLField):
    """Special URL serializer field for S3.

    This field allows to save file from its link without domain.

    """
    def __init__(self, **kwargs):
        """Custom initialization.

        Add URLValidator to self, but don't add it to self.validators, because
        now validation is called after `to_internal_value`. So it provides
        validation before `to_internal_value`.

        """
        super(serializers.URLField, self).__init__(**kwargs)
        self.validator = URLValidator(message=self.error_messages['invalid'])

    def to_internal_value(self, data):
        """Validate `data` and convert it to internal value.

        Cut domain from url to save it in file field.

        """
        if not isinstance(data, str):
            self.fail('invalid')
        self.validator(data)

        # Crop server domain and port and get relative path to avatar
        file_url = urlparse(data).path

        if file_url.startswith(settings.MEDIA_URL):
            # In case of local storing crop the media prefix
            file_url = file_url[len(settings.MEDIA_URL):]

        elif (getattr(settings, 'AWS_STORAGE_BUCKET_NAME') and
              settings.AWS_STORAGE_BUCKET_NAME in file_url):
            # In case of S3 upload crop S3 bucket name
            file_url = file_url.split(
                f'{settings.AWS_STORAGE_BUCKET_NAME}/'
            )[-1]

        # Normalize URL
        is_minio = getattr(settings, 'AWS_IS_MINIO', False)
        if is_minio:
            file_url = unquote(unquote(file_url))
        else:
            file_url = unquote_plus(file_url)

        # If url comes not from s3, then botocore on url validation will
        # raise ParamValidationError
        try:
            if not default_storage.exists(file_url):
                raise serializers.ValidationError(
                    _("File does not exist."),
                )
        except ParamValidationError as error:
            raise serializers.ValidationError(error) from error

        return file_url

    def to_representation(self, value):
        """Return full file url."""
        if not value:
            return None

        use_url = getattr(self, 'use_url', api_settings.UPLOADED_FILES_USE_URL)

        if use_url:
            if not getattr(value, 'url', None):
                # If the file has not been saved it may not have a URL.
                return None
            url = value.url
            request = self.context.get('request', None)
            if request is not None:
                return request.build_absolute_uri(url)
            return url
        return value.name
