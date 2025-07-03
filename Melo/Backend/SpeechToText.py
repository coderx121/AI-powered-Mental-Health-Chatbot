import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import mtranslate as mt

# Load environment variables
env_vars = dotenv_values(".env")
InputLanguage = env_vars.get("InputLanguage", "en")

# HTML code as a triple-quoted string
HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
      <title>Speech Recognition</title>
</head>
<body>
      <button id="start" onclick="startRecognition()">Start Recognition</button>
      <button id="end" onclick="stopRecognition()">Stop Recognition</button>
      <p id="output"></p>

      <script>
            const output = document.getElementById('output');
            let recognition;

            function startRecognition() {
                  recognition = new webkitSpeechRecognition() || new SpeechRecognition();
                  recognition.lang = 'en-US';
                  recognition.continuous = true;

                  recognition.onresult = function(event) {
                        const transcript = event.results[event.results.length - 1][0].transcript; 
                        output.textContent += transcript;                       
                  };

                  recognition.onend = function() {
                        recognition.start();
                  };
                  recognition.start();
            }

            function stopRecognition() {
                  recognition.stop();
                  output.innerHTML = ""
            }
      </script>
</body>
</html>'''

# Replace language placeholder
HtmlCode = HtmlCode.replace("recognition.lang = 'en-US';", f"recognition.lang = '{InputLanguage}';")

# Save HTML file
os.makedirs("Data", exist_ok=True)
html_path = os.path.join("Data", "Voice.html")
with open(html_path, "w") as f:
    f.write(HtmlCode)

current_dir = os.getcwd()
Link = f"file:///{current_dir}/Data/Voice.html"

# Set up Chrome options
chrome_options = Options()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.142.86 Safari/537.36"
chrome_options.add_argument(f"user-agent={user_agent}")
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
# Comment this line during debugging to see the browser UI
chrome_options.add_argument("--headless=new")

# Set up WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Directory for temporary files
TempDirPath = os.path.join(current_dir, "Frontend", "Files")
os.makedirs(TempDirPath, exist_ok=True)

def SetAssistantStatus(Status):
    with open(os.path.join(TempDirPath, "Status.data"), "w", encoding="utf-8") as file:
        file.write(Status)

def QueryModifier(Query):
    Query = Query.strip()
    if Query[-1] not in ".?!":
        Query += "?" if any(Query.lower().startswith(word) for word in ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"]) else "."
    return Query.capitalize()

def UniversalTranslator(Text):
    english_translation = mt.translate(Text, "en", "auto")
    return english_translation.capitalize()

def SpeechRecognition():
    driver.get(Link)
    driver.find_element(By.ID, "start").click()

    while True:
        try:
            Text = driver.find_element(By.ID, "output").text
            if Text:
                driver.find_element(By.ID, "end").click()
                if "en" in InputLanguage.lower():
                    return QueryModifier(Text)
                else:
                    SetAssistantStatus("Translating...")
                    return QueryModifier(UniversalTranslator(Text))
        except Exception as e:
            print(f"Error: {e}")
            break

# Main execution block
if __name__ == "__main__":
    while True:
        result = SpeechRecognition()
        print(result)