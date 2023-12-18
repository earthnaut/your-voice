from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("upload-media/", views.upload_media, name="upload_media"),
    path("select-language/", views.select_language, name="select_language"),
    path("loading/", views.loading, name="loading"),
    path("select-speaker/", views.select_speaker, name="select_speaker"),
    path("result-download/", views.result_download, name="result_download"),
    path(
        "upload-media/youtube/",
        views.download_youtube_link,
        name="download_youtube_link",
    ),
    path(
        "upload-media/attachment/",
        views.download_attachment,
        name="download_attachment",
    ),
    path("invalid-path/", views.invalid_path, name="invalid_path"),
]
