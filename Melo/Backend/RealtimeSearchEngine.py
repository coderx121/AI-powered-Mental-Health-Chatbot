from googlesearch import search
from groq import Groq
from json import load, dump
from pathlib import Path
import datetime
from dotenv import dotenv_values

# Load environment variables with fallbacks
env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Assistant")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize Groq client
client = Groq(api_key=GroqAPIKey)

# System message template
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI mental health chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

# Ensure data directory exists
data_dir = Path("Data")
data_dir.mkdir(exist_ok=True)
chatlog_path = data_dir / "ChatLog.json"

# Load or initialize chat log
if chatlog_path.exists():
    with open(chatlog_path, "r") as f:
        messages = load(f)
else:
    messages = []
    with open(chatlog_path, "w") as f:
        dump(messages, f)

# Perform Google search and return top 5 links
def GoogleSearch(query):
    results = []
    for url in search(query, stop=5):  # 'stop=5' gets 5 results
        results.append(url)

    Answer = f"The search results for '{query}' are:\n[start]\n"
    for i, url in enumerate(results, 1):
        Answer += f"Result {i}: {url}\n\n"
    Answer += "[end]"
    return Answer

# Clean up the answer by removing extra blank lines
def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

# Real-time date and time info
def Information():
    now = datetime.datetime.now()
    return (
        f"Please use this real-time information if needed.\n"
        f"Day: {now.strftime('%A')}\n"
        f"Date: {now.strftime('%d')}\n"
        f"Month: {now.strftime('%B')}\n"
        f"Year: {now.strftime('%Y')}\n"
        f"Time: {now.strftime('%H')} hours {now.strftime('%M')} minutes {now.strftime('%S')} seconds.\n"
    )

# Real-time search + chat response
def RealtimeSearchEngine(prompt):
    global messages

    # Build a fresh conversation for each prompt
    conversation = [
        {"role": "system", "content": System},
        {"role": "user", "content": "Hi"},
        {"role": "assistant", "content": "Hello, how can I help you?"},
        {"role": "system", "content": GoogleSearch(prompt)},
        {"role": "system", "content": Information()},
        {"role": "user", "content": prompt}
    ]

    # Get response from Groq
    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=conversation,
        temperature=0.7,
        max_tokens=2048,
        top_p=1,
        stream=True,
    )

    Answer = ""
    for chunk in completion:
        delta = chunk.choices[0].delta.content
        if delta:
            Answer += delta

    Answer = Answer.replace("</s>", "").strip()

    # Save interaction to log
    messages.append({"role": "user", "content": prompt})
    messages.append({"role": "assistant", "content": Answer})

    with open(chatlog_path, "w") as f:
        dump(messages, f, indent=4)

    return AnswerModifier(Answer)

# Command-line interface
if __name__ == "__main__":
    while True:
        try:
            prompt = input("Enter your query: ")
            if prompt.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break
            print("\n" + RealtimeSearchEngine(prompt) + "\n")
        except KeyboardInterrupt:
            print("\nExiting...")
            break
