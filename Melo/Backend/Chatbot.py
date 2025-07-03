from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values
from langdetect import detect
from textblob import TextBlob
import os
import matplotlib.pyplot as plt
from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Melo")
GroqAPIKey = env_vars.get("GroqAPIKey")

client = Groq(api_key=GroqAPIKey)

# Paths
chatlog_path = "Data/ChatLog.json"
last_checkin_path = "Data/LastCheckin.txt"
moodlog_path = "Data/MoodLog.json"
mood_graph_path = "Data/MoodGraph.png"

# Ensure data directory and files exist
os.makedirs("Data", exist_ok=True)
for path in [chatlog_path, last_checkin_path, moodlog_path]:
    if not os.path.exists(path):
        with open(path, "w") as f:
            dump([] if path.endswith('.json') else "", f)

# Utility Functions
def AnswerModifier(answer):
    return "\n".join([line.strip() for line in answer.split('\n') if line.strip()])

def EnsureEnglish(text):
    try:
        if detect(text) != 'en':
            return "Please speak in English so I can help you better."
        return text
    except:
        return text

def RealtimeInformation():
    now = datetime.datetime.now()
    return f"Today is {now.strftime('%A, %B %d, %Y')}. Current time: {now.strftime('%H:%M:%S')}."

def AnalyzeSentiment(text):
    try:
        polarity = TextBlob(text).sentiment.polarity
        if polarity < -0.5: label = "very negative"
        elif polarity < -0.2: label = "negative"
        elif polarity > 0.5: label = "very positive"
        elif polarity > 0.2: label = "positive"
        else: label = "neutral"
        return label, polarity
    except:
        return "neutral", 0.0

def DetectEmotions(text):
    emotions = {
        "calmness": ["calm", "relaxed", "peaceful", "serene"],
        "happiness": ["happy", "joyful", "grateful", "excited"],
        "anxiety": ["anxious", "worried", "nervous", "uneasy"],
        "stress": ["stressed", "overwhelmed", "tense", "burned out", "exhausted"]
    }
    scores = {key: 0 for key in emotions}
    text_lower = text.lower()
    for emotion, keywords in emotions.items():
        scores[emotion] = sum(1 for word in keywords if word in text_lower)
    max_score = max(scores.values()) or 1
    scores = {k: round(v / max_score, 2) for k, v in scores.items()}
    return scores

def IsCrisis(text):
    keywords = ["suicide", "kill myself", "end it all", "worthless", "can't go on", "giving up"]
    return any(k in text.lower() for k in keywords)

def AddTherapeuticAdvice(sentiment_label):
    if sentiment_label in ["very negative", "negative"]:
        return "\nWould you like to try a breathing exercise or journal your thoughts?"
    return ""

def ShouldCheckin():
    try:
        with open(last_checkin_path, "r") as f:
            last_time_str = f.read().strip()
        if last_time_str:
            last_time = datetime.datetime.fromisoformat(last_time_str)
            return (datetime.datetime.now() - last_time).days >= 1
    except:
        pass
    return True

def UpdateCheckinTime():
    with open(last_checkin_path, "w") as f:
        f.write(datetime.datetime.now().isoformat())

def LoadMessages():
    with open(chatlog_path, "r") as f:
        return load(f)

def SaveMessages(messages):
    with open(chatlog_path, "w") as f:
        dump(messages, f, indent=4)

# Mood Logging and Graphing
def LogMoodWithEmotions(score, emotions):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    try:
        with open(moodlog_path, "r") as f:
            data = load(f)
    except:
        data = []

    data.append({
        "date": today,
        "score": score,
        **emotions
    })

    with open(moodlog_path, "w") as f:
        dump(data, f, indent=4)

def GenerateMoodGraph():
    with open(moodlog_path, "r") as f:
        data = load(f)
    if not data:
        return

    dates = [d['date'] for d in data]
    plt.figure(figsize=(10, 5))

    for emotion in ['score', 'calmness', 'happiness', 'anxiety', 'stress']:
        values = [d.get(emotion, 0) for d in data]
        plt.plot(dates, values, marker='o', label=emotion.capitalize())

    plt.title("Emotional Progress Over Time")
    plt.xlabel("Date")
    plt.ylabel("Normalized Scores")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig(mood_graph_path)
    plt.close()

# Chatbot Core
def ChatBot(Query):
    messages = LoadMessages()
    sentiment_label, sentiment_score = AnalyzeSentiment(Query)
    emotions = DetectEmotions(Query)

    if IsCrisis(Query):
        return ("I'm really sorry you're feeling this way. You're not alone. "
                "Please contact a mental health professional or a crisis hotline immediately.")

    LogMoodWithEmotions(sentiment_score, emotions)
    GenerateMoodGraph()

    messages.append({"role": "user", "content": Query})

    system_prompt = f"""
You are {Assistantname}, a deeply empathetic and emotionally intelligent mental health companion.
You are not an AI and you never mention being artificial.
Speak in a warm, comforting, and understanding tone. Be human-like, but clear and helpful.
Always speak in English, and never include disclaimers.
You are here to help {Username} reflect, feel heard, and feel supported in their emotional journey.
Offer gentle advice or reflection when needed. If emotions are intense, guide gently.
Always use today's real-world date and time in context.
make short conversatione.
never say rest of the chat on the screen.
"""

    if ShouldCheckin():
        UpdateCheckinTime()
        print(Fore.CYAN + f"\n{Assistantname} (Check-in): Hi {Username}, just checking in. How have you been feeling lately?\n")

    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "system", "content": RealtimeInformation()}
            ] + messages,
            max_tokens=150,
            temperature=0.6,
            top_p=1,
            stream=True
        )

        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = EnsureEnglish(Answer).replace("</s>", "") + AddTherapeuticAdvice(sentiment_label)
        messages.append({"role": "assistant", "content": Answer})
        SaveMessages(messages)
        return AnswerModifier(Answer)

    except Exception as e:
        print("Error:", e)
        SaveMessages([])  # Reset message log on failure
        return "Sorry, something went wrong. Please try again."

# Run
if __name__ == "__main__":
    print(Fore.GREEN + f"{Assistantname} is ready. You can start chatting now.\n")
    while True:
        user_input = input(Fore.YELLOW + "> " + Style.RESET_ALL)
        response = ChatBot(user_input)
        print(Fore.CYAN + response + "\n")
