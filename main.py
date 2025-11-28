import pyttsx3 
import speech_recognition as sr 
import datetime
import wikipedia 
import webbrowser
import os
import smtplib
import subprocess
import pyjokes
import pywhatkit
import requests
import pyautogui
import feedparser


engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
# print(voices[1].id)
engine.setProperty('voice', voices[0].id)


def speak(audio):
    engine.say(audio)
    engine.runAndWait()


def wishMe():
    hour = int(datetime.datetime.now().hour)
    if hour>=0 and hour<12:
        speak("Good Morning!")

    elif hour>=12 and hour<18:
        speak("Good Afternoon!")   

    else:
        speak("Good Evening!")  

    speak(" i am shivaJi          cool,   tell me what u want")       

def takeCommand():
    #It takes microphone input from the user and returns string output

    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Recognizing...")    
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")

    except Exception as e:
        # print(e)    
        print("Say that again please...")  
        return "None"
    return query

def sendEmail(to, content):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login('viveksinghchauhan96005@gmail.com', 'yehmerafakeemailhai6969')
    server.sendmail('viveksingh96005@gmail.com', to, content)
    server.close()
    
def get_weather(city="New Delhi"):
    api_key = "YOUR_OPENWEATHER_API_KEY"  # <- Create free API key at openweathermap.org
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    weather = response.json()
    
    if weather["cod"] != "404":
        temp = weather["main"]["temp"]
        description = weather["weather"][0]["description"]
        speak(f"The temperature in {city} is {temp} degrees Celsius with {description}.")
    else:
        speak("City not found.")



def get_news_by_category(category="top"):
    category = category.lower()
    if category == "technology":
        url = "https://news.google.com/rss/search?q=technology&hl=en-IN&gl=IN&ceid=IN:en"
    elif category == "sports":
        url = "https://news.google.com/rss/search?q=sports&hl=en-IN&gl=IN&ceid=IN:en"
    elif category == "business":
        url = "https://news.google.com/rss/search?q=business&hl=en-IN&gl=IN&ceid=IN:en"
    elif category == "world":
        url = "https://news.google.com/rss/search?q=world&hl=en-IN&gl=IN&ceid=IN:en"
    else:
        url = "https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en" 

    news_feed = feedparser.parse(url)
    
    if not news_feed.entries:
        speak("Sorry, I couldn't fetch the news.")
        return

    speak(f"Here are the top 5 {category} news headlines:")
    print(f"\n---- {category.capitalize()} News ----")

    for entry in news_feed.entries[:5]:
        print(f"Title: {entry.title}")
        print(f"Link: {entry.link}\n")
        speak(entry.title)

    
def take_screenshot():
    screenshot = pyautogui.screenshot()
    screenshot.save("screenshot.png")
    speak("Screenshot taken and saved successfully.")


def listen_and_respond():
    wishMe()
    last_command = ""
    while True:
        query = takeCommand().lower()
        if query not in ["repeat", "again", "do that again"]:
            last_command = query

        if 'wikipedia' in query:
            speak('Searching Wikipedia...')
            query = query.replace("wikipedia", "")
            results = wikipedia.summary(query, sentences=2)
            speak("According to Wikipedia")
            print(results)
            speak(results)

        elif 'open youtube' in query:
            webbrowser.open("youtube.com")

        elif 'open google' in query:
            webbrowser.open("google.com")

        elif 'open whatsapp' in query:
            webbrowser.open("whatsapp.com")

        elif 'time' in query:
            strTime = datetime.datetime.now().strftime("%H:%M:%S")
            speak(f"Sir, the time is {strTime}")

        elif 'open code' in query:
            codePath = r'C:\Users\Parixit Singh\AppData\Local\Programs\Microsoft VS Code\Code.exe'
            if os.path.exists(codePath):
                os.startfile(codePath)
            else:
                speak("Code editor not found!")

        elif 'write email' in query:
            try:
                speak("What should I say?")
                content = takeCommand()
                to = "recipient_email@gmail.com"
                sendEmail(to, content)
                speak("Email has been sent!")
            except Exception as e:
                print(e)
                speak("Sorry, email failed.")

        elif 'open canvas' in query:
            speak("Opening Cal Canvas. Please wait.")
            subprocess.Popen(["python", "clacanvas_with_voice.py"])

        elif 'joke' in query:
            joke = pyjokes.get_joke()
            print(joke)
            speak(joke)

        elif 'play video on youtube' in query:
            speak("What should I play?")
            song = takeCommand().lower()
            pywhatkit.playonyt(song)

        elif 'search on google' in query:
            speak("What should I search?")
            search_query = takeCommand().lower()
            webbrowser.open(f"https://www.google.com/search?q={search_query}")

        elif query in ["repeat", "again", "do that again", "another one"]:
            if last_command:
                speak(f"Repeating your last command: {last_command}")
                query = last_command
                continue
            else:
                speak("Nothing to repeat yet.")

        elif 'weather' in query:
            speak("Checking weather.")
            get_weather()

        elif 'news' in query:
            speak("Which category news would you like to listen to sir ?      You can say technology, sports, world or business.   or you can say Random")
            print("Waiting for your category choice...")
            category_query = takeCommand().lower()
            if 'technology' in category_query:
                get_news_by_category('technology')
            elif 'sports' in category_query:
                get_news_by_category('sports')
            elif 'business' in category_query:
                get_news_by_category('business')
            elif 'world' in category_query:
                get_news_by_category('world')
            else:
                get_news_by_category()

        elif 'take screenshot' in query:
            speak("Taking screenshot.")
            take_screenshot()

        elif 'exit' in query or 'quit' in query or 'bye' in query:
            speak("Goodbye sir, shutting down.")
            break
        elif 'hello' in query or 'hi' in query:
            speak("Hello      sir ! How can I assist you today?")


if __name__ == "__main__":
    listen_and_respond()
