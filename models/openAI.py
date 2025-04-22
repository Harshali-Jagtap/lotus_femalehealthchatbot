# ===== OpenAI Fallback Assistant Wrapper =====
from openai import OpenAI
import os


class OpenAIAssistant:
    def __init__(self):
        """
        Initialize OpenAI client using an environment variable.
        Throws error if an API key is not configured.
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        self.client = OpenAI(api_key=api_key)

    def get_safe_response(self, user_input):
        """
        Query OpenAI GPT-3.5 to simplify or rephrase a user input in friendly, plain English.

        :param user_input: raw user message
        :return: simplified or helpful AI response string
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "user",
                    "content": f"Explain in simple terms: {user_input}"
                }],
                max_tokens=150
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI Error: {str(e)}")
            return None
