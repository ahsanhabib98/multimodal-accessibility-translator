from typing import Literal, Dict, Any

from . import client_singleton

client = client_singleton.client

ContentType = Literal["image", "text", "unknown"]


class ContentAnalyzerAgent:
    """
    Decides what kind of content we have and what transformations are appropriate.
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model

    def analyze(self, user_goal: str, has_image: bool = False, has_text: bool = False):
        """
        Returns:
        - content_type
        - recommended_pipelines: list like ["image_to_audio", "text_to_sign"]
        - notes
        """
        description = f"""
        User goal: {user_goal}

        Available input:
        - image: {has_image}
        - text: {has_text}
        """

        system_prompt = """
        You are an accessibility planner for a multimodal assistant.

        Given the user's goal and available input, choose which pipelines to run:
        - image_to_audio
        - text_to_sign
        - text_to_visual

        Return JSON with:
        - content_type: "image", "text", or "unknown"
        - recommended_pipelines: list of strings
        - notes: short explanation
        """

        response = client.responses.create(
            model=self.model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": description},
            ],
            text={"format": {"type": "json"}},
        )

        import json

        data = json.loads(response.output_text)

        ct: ContentType = data.get("content_type", "unknown")
        rec = data.get("recommended_pipelines", [])
        notes = data.get("notes", "")

        return {
            "content_type": ct,
            "recommended_pipelines": rec,
            "notes": notes,
        }
