from typing import Dict

from . import client_singleton

client = client_singleton.client


class SignLanguageAgent:
    """
    Converts written English text into an ASL-style sign sequence description.

    This is a *linguistic* translator, not a video generator.
    Output can later be fed into avatar tools.
    """

    def __init__(self, model: str = "gpt-4.1-mini"):
        self.model = model

    def text_to_sign_description(self, text: str):
        """
        Returns a dict with:
        - 'simplified_english'
        - 'asl_gloss'
        - 'body_and_face_notes'
        """
        system_prompt = """
        You are an expert American Sign Language (ASL) interpreter.

        Given English text:
        1. Rewrite it as SIMPLE ENGLISH that preserves meaning.
        2. Convert it to an ASL GLOSS line:
        - ALL CAPS for each sign, separated by spaces.
        - Drop articles (a, an, the) and unnecessary words.
        - Use ASL word order when possible (TOPIC first).
        3. Provide short notes about facial expression and body movement.

        Return a json object with:
        - simplified_english
        - asl_gloss
        - body_and_face_notes
        """

        response = client.responses.create(
            model=self.model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            text={"format": {"type": "json_object"}},
        )

        raw = response.output[0].content[0].text

        import json
        data = json.loads(raw)

        return {
            "simplified_english": data.get("simplified_english", text),
            "asl_gloss": data.get("asl_gloss", ""),
            "body_and_face_notes": data.get("body_and_face_notes", ""),
        }
