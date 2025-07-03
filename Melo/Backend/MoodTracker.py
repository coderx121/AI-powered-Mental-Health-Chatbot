from datetime import datetime
import json
import os
from textblob import TextBlob
import matplotlib.pyplot as plt

class MoodTracker:
    def __init__(self, moodlog_path="Data/MoodLog.json"):
        self.moodlog_path = moodlog_path
        os.makedirs(os.path.dirname(moodlog_path), exist_ok=True)
        self.moods = self.load_moods()

    def load_moods(self):
        try:
            with open(self.moodlog_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_moods(self):
        with open(self.moodlog_path, "w") as f:
            json.dump(self.moods, f, indent=4)

    def log_mood(self, text, user_input_score=None):
        sentiment = TextBlob(text).sentiment.polarity
        score = user_input_score if user_input_score else sentiment
        entry = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "score": score,
            "text": text,
            "recommendations": self.get_recommendations(score)
        }
        self.moods.append(entry)
        self.save_moods()

    def get_recommendations(self, score):
        if score < -0.3:
            return [
                "Try a 5-minute guided meditation: https://www.youtube.com/watch?v=inpok4MKVLM",
                "Write down three things you're grateful for today.",
                "Reach out to a friend or family member for a chat."
            ]
        elif score < 0.3:
            return [
                "Take a short walk to clear your mind.",
                "Listen to calming music: https://www.youtube.com/watch?v=1zyhZpE28P8",
                "Practice deep breathing for 2 minutes."
            ]
        else:
            return [
                "Keep up the positive vibes! Share something positive with someone today.",
                "Set a small goal for the day and celebrate when you achieve it."
            ]

    def generate_trend_graph(self, output_path="Data/MoodTrend.png"):
        if not self.moods:
            return False
        dates = [entry["date"] for entry in self.moods]
        scores = [entry["score"] for entry in self.moods]
        plt.figure(figsize=(10, 5))
        plt.plot(dates, scores, marker='o', color='b', label='Mood Score')
        plt.title("Mood Trend Over Time")
        plt.xlabel("Date")
        plt.ylabel("Mood Score (-1 to 1)")
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
        return True

def enhanced_mood_logging(query):
    tracker = MoodTracker()
    user_score = None
    if "mood score" in query.lower():
        try:
            user_score = float(query.split("mood score")[-1].strip())
            if -1 <= user_score <= 1:
                tracker.log_mood(query, user_score)
            else:
                return "Mood score must be between -1 and 1."
        except ValueError:
            return "Please provide a valid mood score (e.g., 'mood score 0.5')."
    else:
        tracker.log_mood(query)
    tracker.generate_trend_graph()
    return f"Mood logged. Check your trend graph at Data/MoodTrend.png. Recommendations: {tracker.moods[-1]['recommendations']}"

if __name__ == "__main__":
    # Test case for standalone execution
    test_query = "I’m feeling great today"
    print(f"Testing MoodTracker with query: {test_query}")
    response = enhanced_mood_logging(test_query)
    print(response)
    print(f"Check Data/MoodLog.json and Data/MoodTrend.png for outputs.")