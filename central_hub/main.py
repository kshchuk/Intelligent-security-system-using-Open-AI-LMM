from openai import OpenAI

client = OpenAI()

request = ("It's image from security camera. Some movement was detected via movement sensors. "
           "Please provide a detailed description of the reason for the move. (if human, it's detailed appearance, if cat it's colour etc.)")

response = client.responses.create(
    model="gpt-4.1-mini",
    input=[{
        "role": "user",
        "content": [
            {"type": "input_text", "text": request },
            {
                "type": "input_image",
                "image_url": "https://www.security.org/app/uploads/2020/05/Vivint-Outdoor-Cam-Pro-Night-Vision.jpg",
            },
        ],
    }],
)

print(response.output_text)