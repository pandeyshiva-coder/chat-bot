import speech_recognition as sr
import webbrowser
import pyttsx3
import musicLibrary
import requests
from gtts import gTTS
import pygame
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

recognizer = sr.Recognizer()
engine = pyttsx3.init() 
newsapi = os.getenv("GNEWS_API_KEY", "")

# Initialize Pygame mixer once at start
pygame.mixer.init()

def speak(text):
    tts = gTTS(text)
    tts.save('temp.mp3') 

    # Load the MP3 file
    pygame.mixer.music.load('temp.mp3')

    # Play the MP3 file
    pygame.mixer.music.play()

    # Keep the program running until the music stops playing
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    
    pygame.mixer.music.unload()
    pygame.mixer.music.unload()
    # On Windows, Pygame can take a moment to release the file handle, 
    # causing PermissionError. We safely overwrite it on the next speak() call anyway.
    pass

def processCommand(c):
    c_lower = c.lower()
    
    # Dictionary for websites
    websites = {
        "google": "https://google.com",
        "facebook": "https://facebook.com",
        "youtube": "https://youtube.com",
        "linkedin": "https://linkedin.com"
    }

    for site, url in websites.items():
        if f"open {site}" in c_lower:
            webbrowser.open(url)
            return

    if c_lower.startswith("play"):
        words = c_lower.split(" ")
        if len(words) > 1:
            song = words[1]
            link = musicLibrary.music.get(song)
            if link:
                webbrowser.open(link)
            else:
                speak("Sorry, I could not find this song in your library.")
        return

    elif "news" in c_lower:
        if not newsapi:
            speak("API key for news is missing.")
            return

        url = f"https://gnews.io/api/v4/top-headlines?country=in&max=5&lang=en&apikey={newsapi}"

        try:
            r = requests.get(url)
            if r.status_code == 200:
                data = r.json()
                articles = data.get("articles", [])

                if not articles:
                    speak("No news available right now.")
                else:
                    speak("Here are the latest headlines.")
                    for article in articles:
                        speak(article["title"])
            else:
                speak("Unable to fetch news right now.")
        except Exception as e:
            print("News error:", e)
            speak("There is a problem fetching news.")

    # If the command doesn't match any specific fixed command, pass it to Google Gemini API
    else:
        gemini_key = os.getenv("GEMINI_API_KEY", "")
        if not gemini_key or gemini_key == "your_gemini_api_key_here":
            speak("I heard your command, but my Gemini API key is missing. Please add it to the dot env file.")
            return
            
        from google import genai
        from google.genai import types
        try:
            client = genai.Client(api_key=gemini_key)
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=c,
                config=types.GenerateContentConfig(
                    system_instruction="You are a short-spoken virtual assistant named Jarvis skilled in general tasks. Always respond in 1 or 2 short sentences max.",
                )
            )
            print(f"Jarvis AI: {response.text}")
            speak(response.text)
        except Exception as e:
            print(f"Error communicating with Gemini: {e}")
            speak("Sorry, I am having trouble connecting to my AI brain.")


if __name__ == "__main__":
    speak("Initializing Jarvis....")
    while True:
        # Listen for the wake word "Jarvis"
        r = sr.Recognizer()
         
        print("recognizing...")
        try:
            with sr.Microphone() as source:
                print("Listening...")
                # Adjust for ambient noise for better accuracy
                r.adjust_for_ambient_noise(source, duration=0.5)
                # Listen without strict timeout limits
                audio = r.listen(source, timeout=5, phrase_time_limit=3)
            
            try:
                word = r.recognize_google(audio)
                print(f"Recognized word: {word}") # Debug output
            except sr.UnknownValueError:
                continue # Ignore unrecognized chatter
            except sr.RequestError as e:
                print(f"Could not request results; {e}")
                continue

            if word.lower() == "jarvis":
                speak("Yes, I am listening.")
                # Continuous Conversation Loop
                while True:
                    with sr.Microphone() as source:
                        print("Jarvis Active... waiting for your command")
                        try:
                            # Listen for command with reasonable timeouts
                            r.adjust_for_ambient_noise(source, duration=0.2)
                            audio = r.listen(source, timeout=10, phrase_time_limit=10)
                            command = r.recognize_google(audio).lower()
                            print(f"You said: {command}")
                            
                            # Check if user wants to stop the conversation
                            if command in ["stop", "exit", "quit", "bye", "goodbye"]:
                                speak("Goodbye! Call me if you need me.")
                                break # Exit the continuous loop and wait for wake word again
                                
                            processCommand(command)
                        except sr.UnknownValueError:
                            speak("Sorry, I didn't get that. Please say that again.")
                        except sr.WaitTimeoutError:
                            # If the user doesn't say anything for 10 seconds, go back to sleep
                            speak("I did not hear anything, going back to sleep.")
                            break
                        except sr.RequestError as e:
                            speak("Network error.")
                            break

        except sr.WaitTimeoutError:
            pass # Ignore read timeouts
        except Exception as e:
            print("Error: {0}".format(e))
