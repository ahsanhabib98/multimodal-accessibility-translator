from pathlib import Path
from typing import Dict, Optional

import base64
from io import BytesIO

from PIL import Image

from . import client_singleton

client = client_singleton.client


class VisualSimplifierAgent:
    """
    Converts complex text into a diagram concept plus an optional generated image.
    """

    def __init__(self, text_model: str = "gpt-4.1-mini", image_model: str = "gpt-image-1", output_dir: str = "outputs/visuals"):
        self.text_model = text_model
        self.image_model = image_model
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def plan_diagram(self, text: str):
        """
        Returns a dict:
        - 'short_title'
        - 'diagram_description'    (what to draw)
        - 'labels_and_nodes'       (bullet list / ascii layout)
        - 'simple_explanation'     (explain to non-expert)
        """
        system_prompt = """
        You are a teacher who explains complex ideas using simple diagrams.

        Given some complex text:
        1. Extract 3–7 key concepts.
        2. Describe ONE clear diagram to explain it:
        - type: flowchart, timeline, layers, or concept map.
        - list of nodes and arrows.
        3. Explain it in very simple English for a high-school student.

        Return a short JSON object with:
        - short_title
        - diagram_description
        - labels_and_nodes
        - simple_explanation
        """

        response = client.responses.create(
            model=self.text_model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            text={"format": {"type": "json_object"}},
        )

        raw = response.output_text
        import json

        data = json.loads(raw)
        return {
            "short_title": data.get("short_title", "Visual Summary"),
            "diagram_description": data.get("diagram_description", ""),
            "labels_and_nodes": data.get("labels_and_nodes", ""),
            "simple_explanation": data.get("simple_explanation", ""),
        }

    def generate_diagram_image(self, prompt: str, filename: str = "diagram.png", size: str = "1024x1024"):
        """
        Uses GPT Image to generate a simple diagram / infographic. :contentReference[oaicite:9]{index=9}
        """
        img_path = self.output_dir / filename

        result = client.images.generate(
            model=self.image_model,
            prompt=prompt,
            size=size,
            quality="low",
            output_format="png",
        )

        b64 = result.data[0].b64_json
        image_bytes = base64.b64decode(b64)

        image = Image.open(BytesIO(image_bytes))
        image.save(img_path, format="PNG")

        return img_path
