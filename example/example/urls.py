from django.conf.urls import include, url
from django.contrib import admin

from s3direct.api.views import S3DirectWrapper

admin.autodiscover()


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^s3direct/', include('s3direct.urls')),
    url(r'^form/', include('cat.urls')),
    url(
        '^api/v1/s3direct/get_params/',
        S3DirectWrapper.as_view(),
        name='s3direct'
    ),
]
