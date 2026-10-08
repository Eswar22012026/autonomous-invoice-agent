from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-6-luna",
    input="Explain what an AI agent is in one simple sentence."
)

print(response.output_text)