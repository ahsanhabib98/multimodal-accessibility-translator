from typing import Dict

from . import client_singleton

client = client_singleton.client


class QualityCheckerAgent:
    """
    Gives a quick accessibility/readability review for outputs.
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model

    def review_description(self, description: str):
        """
        Returns:
        - readability_level
        - issues
        - suggestions
        """
        system_prompt = """
        You are an accessibility and plain-language reviewer.

        Given an image description:
        1. Estimate the reading level (e.g., "Grade 6–8", "College").
        2. List any accessibility issues (too long, too vague, too visual-only, etc.).
        3. Suggest 2–3 concrete improvements.

        Return JSON with:
        - readability_level
        - issues
        - suggestions
        """

        response = client.responses.create(
            model=self.model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": description},
            ],
            text={"format": {"type": "json_object"}},
        )

        import json

        data = json.loads(response.output_text)
        return {
            "readability_level": data.get("readability_level", ""),
            "issues": data.get("issues", ""),
            "suggestions": data.get("suggestions", ""),
        }
