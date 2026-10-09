
from google import genai

def main():
    try:
        client = genai.Client()

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents="Explain an AI agent in one simple sentence."
        )

        print("\nGemini response:")
        print(response.text)

    except Exception as error:
        print("\nGemini test failed.")
        print("Error type:", type(error).__name__)
        print("Error details:", error)

if __name__ == "__main__":
    main()
