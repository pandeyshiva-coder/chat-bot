import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI Client using the key from .env file
client = OpenAI(
  api_key=os.getenv("OPENAI_API_KEY", ""),
)

try:
    completion = client.chat.completions.create(
      model="gpt-3.5-turbo",
      messages=[
        {"role": "system", "content": "You are a virtual assistant named jarvis skilled in general tasks like Alexa and Google Cloud"},
        {"role": "user", "content": "what is coding"}
      ]
    )
    print(completion.choices[0].message.content)
except Exception as e:
    print(f"Error communicating with OpenAI: {e}")