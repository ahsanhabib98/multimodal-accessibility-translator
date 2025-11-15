from django import forms


class ImageToAudioForm(forms.Form):
    image = forms.ImageField(label="Upload an image")
    detail_level = forms.ChoiceField(
        choices=[("brief", "Brief"), ("standard", "Standard"), ("detailed", "Detailed")],
        initial="standard",
    )


class ComplexTextForm(forms.Form):
    text = forms.CharField(
        label="Complex text",
        widget=forms.Textarea(attrs={"rows": 5}),
    )
    generate_diagram = forms.BooleanField(
        label="Generate a diagram image", required=False
    )


class SignLanguageForm(forms.Form):
    text = forms.CharField(
        label="Text to convert to sign language description",
        widget=forms.Textarea(attrs={"rows": 3}),
    )


class DocumentUploadForm(forms.Form):
    document = forms.FileField(
        label="Upload document (.txt or .pdf)"
    )
    generate_audio = forms.BooleanField(
        label="Also generate audio summary", required=False
    )
