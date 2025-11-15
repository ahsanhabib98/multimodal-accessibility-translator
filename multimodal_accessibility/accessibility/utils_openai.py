import base64
from io import BytesIO
from pathlib import Path
import os

from openai import OpenAI
from PyPDF2 import PdfReader
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from PIL import Image

client = OpenAI()  


def encode_image_as_data_url(image_path: Path) -> str:
    ext = image_path.suffix.lower()
    mime = "image/png" if ext == ".png" else "image/jpeg"
    data = image_path.read_bytes()
    b64 = base64.b64encode(data).decode("utf-8")
    return f"data:{mime};base64,{b64}"


def generate_image_description(image_path: Path, detail_level: str = "standard") -> str:
    data_url = encode_image_as_data_url(image_path)

    prompt = f"""
    You are an accessibility assistant generating image descriptions for blind and low-vision users.

    Follow these principles:
    - Be accurate and objective.
    - Include only important details.
    - Detail level: {detail_level.upper()}.

    Return ONLY the description text.
    """

    resp = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {"type": "input_image", "image_url": data_url},
                ],
            }
        ],
    )
    return resp.output_text


def text_to_speech(text: str, basename: str = "audio_description") -> str:
    """
    Generates an mp3 file from text and returns its relative media path.
    """
    media_dir = Path("media/audio")
    media_dir.mkdir(parents=True, exist_ok=True)
    out_path = media_dir / f"{basename}.mp3"

    response = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=text,
    )
    response.stream_to_file(out_path)
    return f"/media/audio/{basename}.mp3"


def generate_sign_language_description(text: str):
    """
    Returns dict with simplified English, ASL gloss, and notes.
    """
    system_prompt = """
    You are an American Sign Language (ASL) interpreter.

    Given English text:
    1. Rewrite it as simple English.
    2. Give an ASL GLOSS line in ALL CAPS.
    3. Provide brief notes on facial expression and body movement.

    Return JSON with keys:
    - simplified_english
    - asl_gloss
    - body_and_face_notes
    """

    resp = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ],
        text={"format": {"type": "json_object"}},
    )
    import json
    data = json.loads(resp.output_text)
    return {
        "simplified_english": data.get("simplified_english", text),
        "asl_gloss": data.get("asl_gloss", ""),
        "body_and_face_notes": data.get("body_and_face_notes", ""),
    }


def generate_visual_plan(text: str):
    """
    Converts complex text into a visual explanation plan.
    """
    system_prompt = """
    You are a teacher who explains complex ideas with simple diagrams.

    Given some complex text:
    1. Extract 3-7 key concepts.
    2. Describe ONE clear diagram (flowchart, layers, concept map, or timeline).
    3. Provide a simple explanation for non-experts.

    Return JSON:
    - short_title
    - diagram_description
    - labels_and_nodes
    - simple_explanation
    """

    resp = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ],
        text={"format": {"type": "json_object"}},
    )
    import json
    data = json.loads(resp.output_text)
    return {
        "short_title": data.get("short_title", "Visual Explanation"),
        "diagram_description": data.get("diagram_description", ""),
        "labels_and_nodes": data.get("labels_and_nodes", ""),
        "simple_explanation": data.get("simple_explanation", ""),
    }


def generate_diagram_image(prompt: str) -> str:
    """
    Generates a diagram image using GPT-Image and returns its media URL.
    """
    result = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1024",
        output_format="png",
    )

    b64 = result.data[0].b64_json
    image_bytes = base64.b64decode(b64)
    img = Image.open(BytesIO(image_bytes))

    media_dir = Path("media/diagrams")
    media_dir.mkdir(parents=True, exist_ok=True)
    out_path = media_dir / "diagram.png"
    img.save(out_path, format="PNG")

    return "/media/diagrams/diagram.png"


def extract_text_from_document(uploaded_file) -> str:
    """
    Very simple extractor:
    - If .txt: decode directly
    - If .pdf: use PyPDF2
    """
    name = uploaded_file.name.lower()
    content = uploaded_file.read()

    if name.endswith(".txt"):
        try:
            return content.decode("utf-8")
        except Exception:
            return content.decode("latin-1", errors="ignore")

    if name.endswith(".pdf"):
        tmp_path = default_storage.save("tmp_upload.pdf", ContentFile(content))
        full_path = Path(default_storage.path(tmp_path))
        reader = PdfReader(str(full_path))
        text = []
        for page in reader.pages[:5]:  
            text.append(page.extract_text() or "")
        full_path.unlink(missing_ok=True)
        return "\n".join(text)

    return "Unsupported document format or empty content."
    

def make_document_accessible(text: str):
    """
    Turns document text into multiple accessible formats.
    - simplified_text
    - bullet_points
    - alt_style_summary
    """
    prompt = """
    You are an accessibility assistant.

    Given the following document text:
    1. Produce a simplified version in plain language.
    2. Produce 5-8 key bullet points.
    3. Produce a short alt-text style summary (for screen readers).

    Return JSON:
    - simplified_text
    - bullet_points
    - alt_summary
    """

    resp = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": text},
        ],
        text={"format": {"type": "json_object"}},
    )
    import json
    data = json.loads(resp.output_text)
    return {
        "simplified_text": data.get("simplified_text", ""),
        "bullet_points": data.get("bullet_points", ""),
        "alt_summary": data.get("alt_summary", ""),
    }
