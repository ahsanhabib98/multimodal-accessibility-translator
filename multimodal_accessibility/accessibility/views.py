from pathlib import Path

from django.shortcuts import render
from django.conf import settings

from .forms import (
    ImageToAudioForm,
    ComplexTextForm,
    SignLanguageForm,
    DocumentUploadForm,
)
from . import utils_openai as uai


def index(request):
    context = {
        "image_form": ImageToAudioForm(),
        "complex_form": ComplexTextForm(),
        "sign_form": SignLanguageForm(),
        "doc_form": DocumentUploadForm(),
    }
    return render(request, "accessibility/index.html", context)


def image_to_audio_view(request):
    context = {}
    if request.method == "POST":
        form = ImageToAudioForm(request.POST, request.FILES)
        if form.is_valid():
            image_file = form.cleaned_data["image"]
            detail_level = form.cleaned_data["detail_level"]

            media_dir = Path(settings.MEDIA_ROOT) / "uploads"
            media_dir.mkdir(parents=True, exist_ok=True)
            img_path = media_dir / image_file.name
            with open(img_path, "wb+") as f:
                for chunk in image_file.chunks():
                    f.write(chunk)

            description = uai.generate_image_description(img_path, detail_level)
            audio_url = uai.text_to_speech(description, basename="image_description")

            context["image_description"] = description
            context["image_audio_url"] = audio_url
    else:
        form = ImageToAudioForm()

    context.setdefault("image_form", form)
    context.setdefault("complex_form", ComplexTextForm())
    context.setdefault("sign_form", SignLanguageForm())
    context.setdefault("doc_form", DocumentUploadForm())

    return render(request, "accessibility/index.html", context)


def complex_text_view(request):
    context = {}
    if request.method == "POST":
        form = ComplexTextForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data["text"]
            generate_diagram = form.cleaned_data["generate_diagram"]

            plan = uai.generate_visual_plan(text)
            context["visual_plan"] = plan

            if generate_diagram:
                img_url = uai.generate_diagram_image(plan["diagram_description"])
                context["diagram_image_url"] = img_url
    else:
        form = ComplexTextForm()

    context.setdefault("image_form", ImageToAudioForm())
    context.setdefault("complex_form", form)
    context.setdefault("sign_form", SignLanguageForm())
    context.setdefault("doc_form", DocumentUploadForm())
    return render(request, "accessibility/index.html", context)


def sign_language_view(request):
    context = {}
    if request.method == "POST":
        form = SignLanguageForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data["text"]
            result = uai.generate_sign_language_description(text)
            context["sign_result"] = result
    else:
        form = SignLanguageForm()

    context.setdefault("image_form", ImageToAudioForm())
    context.setdefault("complex_form", ComplexTextForm())
    context.setdefault("sign_form", form)
    context.setdefault("doc_form", DocumentUploadForm())
    return render(request, "accessibility/index.html", context)


def document_accessible_view(request):
    context = {}
    if request.method == "POST":
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_doc = form.cleaned_data["document"]
            generate_audio = form.cleaned_data["generate_audio"]

            raw_text = uai.extract_text_from_document(uploaded_doc)
            acc = uai.make_document_accessible(raw_text)

            context["doc_accessible"] = acc

            if generate_audio and acc.get("alt_summary"):
                audio_url = uai.text_to_speech(acc["alt_summary"], basename="doc_summary")
                context["doc_audio_url"] = audio_url
    else:
        form = DocumentUploadForm()

    context.setdefault("image_form", ImageToAudioForm())
    context.setdefault("complex_form", ComplexTextForm())
    context.setdefault("sign_form", SignLanguageForm())
    context.setdefault("doc_form", form)
    return render(request, "accessibility/index.html", context)
