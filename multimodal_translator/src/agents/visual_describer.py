import base64
from pathlib import Path
from typing import Literal

from . import client_singleton

DetailLevel = Literal["brief", "standard", "detailed"]

client = client_singleton.client


def _encode_image_as_data_url(image_path: str):
    """
    Encodes a local image as a base64 data URL suitable for OpenAI multimodal input.
    """
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    mime = "image/png" if path.suffix.lower() in {".png"} else "image/jpeg"
    data = path.read_bytes()
    b64 = base64.b64encode(data).decode("utf-8")
    return f"data:{mime};base64,{b64}"


class VisualDescriberAgent:
    """
    Generates accessibility-friendly image descriptions at multiple detail levels,
    following W3C WAI guidance (concise, relevant, no over-explaining). :contentReference[oaicite:3]{index=3}
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model

    def describe_image(self, image_path: str, detail_level: DetailLevel = "standard"):
        data_url = _encode_image_as_data_url(image_path)

        prompt = f"""
        You are an accessibility assistant generating image descriptions for blind and low-vision users.

        Follow these principles:
        - Be accurate, concise, and objective.
        - Mention only what is important for understanding the image.
        - Avoid guessing about things that aren't clear.

        Detail level required: {detail_level.upper()}.

        Return ONLY the description text, no headings or bullets.
        """

        response = client.responses.create(
            model=self.model,
            input=[
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": prompt},
                        {
                            "type": "input_image",
                            "image_url": data_url,
                        },
                    ],
                }
            ],
        )
        return response.output_text
