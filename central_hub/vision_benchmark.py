import os
import time
import base64
import requests
from openai import OpenAI, OpenAIError

class VisionBenchmark:
    """
    Benchmarks round-trip latency for a list of OpenAI Vision models.
    Each iteration downloads a sample image from the internet, encodes it,
    sends it to the model, and measures the elapsed time.
    """

    def __init__(self, api_key: str, models: list[str], image_url: str):
        """
        :param api_key: Your OpenAI API key
        :param models: List of OpenAI Vision-capable model names to benchmark
        :param image_url: URL of a publicly accessible JPEG/PNG image
        """
        self.client = OpenAI(api_key=api_key)
        self.models = models
        self.image_url = image_url

        # A fixed prompt to accompany every image request:
        self.prompt_text = (
            "This is from a security camera. Motion was detected via sensors. "
            "Please provide a detailed description of the cause and appearance."
        )

    def _download_and_encode(self) -> str:
        """
        Downloads the image at self.image_url and returns its Base64-encoded contents.
        """
        response = requests.get(self.image_url, timeout=10)
        response.raise_for_status()
        image_bytes = response.content
        encoded = base64.b64encode(image_bytes).decode("utf-8")
        return encoded

    def benchmark_once(self, model: str, encoded_image: str) -> float:
        """
        Sends a single request to the specified model with the encoded_image + prompt,
        measures, and returns the elapsed time in seconds.

        :param model: OpenAI model name
        :param encoded_image: Base64-encoded JPEG/PNG string (no "data:" prefix)
        :return: elapsed time in seconds
        """
        # Wrap into the same format as your existing code but with minimal overhead
        payload = [
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": self.prompt_text},
                    {"type": "input_image", "image_url": f"data:image/jpeg;base64,{encoded_image}"}
                ]
            }
        ]

        start = time.time()
        try:
            _ = self.client.responses.create(model=model, input=payload)
        except OpenAIError as e:
            # If the request fails (e.g., model not enabled), we re-raise or handle accordingly
            raise RuntimeError(f"Request to model {model} failed: {e}") from e
        end = time.time()
        return end - start

    def run_all(self, repeat: int = 1) -> None:
        """
        For each model in self.models, runs `self.benchmark_once` `repeat` times and prints the average time.
        """
        # Download & encode once (so we are only measuring network+inference, not repeated download)
        print(f"Downloading image from URL: {self.image_url}")
        encoded_image = self._download_and_encode()
        print("Image downloaded and encoded.\n")

        for model in self.models:
            print(f"=== Benchmarking model: {model} ===")
            timings = []
            for i in range(repeat):
                try:
                    elapsed = self.benchmark_once(model, encoded_image)
                    timings.append(elapsed)
                    print(f"  Run #{i+1}: {elapsed:.3f} seconds")
                except RuntimeError as e:
                    print(f"  ❌ Error on run #{i+1}: {e}")
                    # If you want to skip further attempts for this model, break here:
                    break

            if timings:
                avg = sum(timings) / len(timings)
                print(f"  → Average over {len(timings)} run(s): {avg:.3f} seconds\n")
            else:
                print(f"  → No successful runs for model {model}\n")


if __name__ == "__main__":
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Please set the OPENAI_API_KEY environment variable.")

    vision_models = [
        "o4-mini",
        "gpt-4.1-nano",
        "gpt-4.1-mini"
    ]

    sample_image_url = "https://i.reddituploads.com/aaf2fe36806744fbb33931bfa7a49522?fit=max&h=1536&w=1536&s=fe1252bc2c0ab3a4fb1ace5f34e541ae"

    runs_per_model = 3

    bench = VisionBenchmark(api_key=api_key, models=vision_models, image_url=sample_image_url)
    bench.run_all(repeat=runs_per_model)
