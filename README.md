Mental Health Chatbot - AI-Powered Virtual Assistant
-----------------------------------------------------

Project Overview:
------------------
This project is an AI-powered Mental Health Chatbot designed to provide mood tracking, emotional analysis, and interactive mental health support. The application features a simple graphical interface and uses voice/text-based interaction to help users track their mental well-being.

The project follows a clean structure divided into:
1. Frontend - GUI for user interaction  
2. Backend - Core logic for mood analysis and chatbot responses  
3. Main - Entry point to run the complete application  

Project Structure:
-------------------
/frontend/       → All GUI components (Tkinter-based interface)  
/backend/        → Mood analysis, sentiment detection, chatbot logic  
/main.py         → Main application file to run the chatbot  
/requirements.txt → List of required dependencies  
/readme.txt      → Project documentation (this file)  

Key Features:
--------------
✔ Voice & text-based mental health chatbot  
✔ Mood tracking with graphical trend visualization  
✔ Sentiment analysis using NLP techniques  
✔ User-friendly GUI built with Tkinter  
✔ Modular structure for easy maintenance and expansion  
✔ Offline functionality for privacy  

Technologies Used:
-------------------
- Python  
- Tkinter (Frontend GUI)  
- SpeechRecognition & Pyttsx3 (Voice interaction)  
- Matplotlib (Mood trend graphs)  
- Scikit-learn & NLTK (Sentiment & mood analysis)  

Setup Instructions:
--------------------
1. Install dependencies:  
   `pip install -r requirements.txt`  

2. Run the application:  
   `python main.py`  

3. Follow the on-screen instructions to interact with the chatbot.  

Folder Details:
----------------
/frontend/ contains:  
    - `gui.py` → Main GUI window  
    - `widgets.py` → Custom widgets/components  

/backend/ contains:  
    - `mood_tracker.py` → Mood analysis & trend graph generation  
    - `chatbot_logic.py` → Chatbot response logic & sentiment analysis  
    - `speech_module.py` → Voice recognition & text-to-speech  

/main.py → Launches the complete application with frontend and backend integration  

Future Improvements:
---------------------
- Real-time emotion detection through voice tone analysis  
- Integration with professional mental health resources  
- User authentication and secure mood data storage  
- LLM-based advanced conversation (ChatGPT-like responses)  
- Multi-language support  

Disclaimer:
------------
This chatbot is intended for general mental health awareness and mood tracking only. It is not a substitute for professional mental health services. If experiencing severe distress, please consult a licensed therapist.


