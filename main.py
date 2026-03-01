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
    try:
        os.remove("temp.mp3") 
    except Exception as e:
        print(f"Failed to remove temp.mp3: {e}")

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


if __name__ == "__main__":
    speak("Initializing Jarvis....")
    while True:
        # Listen for the wake word "Jarvis"
        r = sr.Recognizer()
         
        print("recognizing...")
        try:
            with sr.Microphone() as source:
                print("Listening...")
                audio = r.listen(source, timeout=2, phrase_time_limit=1)
            
            try:
                word = r.recognize_google(audio)
            except sr.UnknownValueError:
                continue # Ignore unrecognized chatter
            except sr.RequestError as e:
                print(f"Could not request results; {e}")
                continue

            if word.lower() == "jarvis":
                speak("Ya")
                # Listen for command
                with sr.Microphone() as source:
                    print("Jarvis Active...")
                    try:
                        audio = r.listen(source, timeout=5, phrase_time_limit=5)
                        command = r.recognize_google(audio)
                        processCommand(command)
                    except sr.UnknownValueError:
                        speak("Sorry, I didn't get that.")
                    except sr.RequestError as e:
                        speak("Network error.")

        except sr.WaitTimeoutError:
            pass # Ignore read timeouts
        except Exception as e:
            print("Error: {0}".format(e))
