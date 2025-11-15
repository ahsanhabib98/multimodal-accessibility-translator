from django.urls import path
from . import views

app_name = "accessibility"

urlpatterns = [
    path("", views.index, name="index"),
    path("image-to-audio/", views.image_to_audio_view, name="image_to_audio"),
    path("text-to-visual/", views.complex_text_view, name="text_to_visual"),
    path("text-to-sign/", views.sign_language_view, name="text_to_sign"),
    path("document-accessible/", views.document_accessible_view, name="document_accessible"),
]
