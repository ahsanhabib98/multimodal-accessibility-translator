from pathlib import Path
from typing import Literal

from . import client_singleton

client = client_singleton.client

VoiceName = Literal[
    "alloy",
    "coral",
    "sage",
    "nova",
    "verse",
    "ash",
    "ember",
    "spark",
    "breeze",
    "flow",
    "spectrum",
]


class AudioProducerAgent:
    """
    Converts text descriptions into spoken audio using the OpenAI TTS models.
    """

    def __init__(self, model: str = "gpt-4o-mini-tts", voice: VoiceName = "alloy", output_dir: str = "outputs/audio"):
        self.model = model
        self.voice = voice
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def synthesize(self, text: str, basename: str = "description", file_ext: str = "mp3"):
        """
        Generate an audio file from text and return the path.
        """
        output_path = self.output_dir / f"{basename}.{file_ext}"

        response = client.audio.speech.create(
            model=self.model,
            voice=self.voice,
            input=text,
        )

        response.stream_to_file(output_path)

        return output_path
