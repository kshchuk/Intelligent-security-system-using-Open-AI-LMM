import base64

from openai import OpenAI

class AIAnalyzer:
    """
    Uses OpenAI to analyze image and return a description.
    """
    def __init__(self):
        self.client = OpenAI()

    def analyze(self, image_path: str) -> str:
        # Prepare prompt
        prompt = (
            "It's an image from security camera. Movement detected via sensors. "
            "Please provide a detailed description of the cause and appearance."
        )
        base64_image = self._encode_image(image_path)

        response = self.client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {"role": "user", "content": [
                    {"type": "input_text", "text": prompt},
                    {"type": "input_image", "image_url": f"data:image/jpeg;base64,{base64_image}"},
                ]}
            ],
        )
        return response.output_text

    def _encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
