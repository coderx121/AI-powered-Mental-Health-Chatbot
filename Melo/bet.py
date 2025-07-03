import tkinter as tk
from tkinter import ttk
import webbrowser

try:
    import pyperclip
except ImportError:
    pyperclip = None  # Handle missing module gracefully

# --- Free Mental Health Resources ---

books = [
    ("Maybe you should talk to someone ",
     "https://fliphtml5.com/pezzr/shai/basic"),
    ("The Body Keeps the Score: Brain",
     "https://ia601604.us.archive.org/35/items/the-body-keeps-the-score-pdf/The-Body-Keeps-the-Score-PDF.pdf"),
    ("An Unquiet Mind",
     "https://ia802906.us.archive.org/26/items/an-unquiet-mind/An%20Unquiet%20Mind.pdf"),
]

exercises = [
    ("5-Minute Breathing Meditation (YouTube)",
     "https://www.youtube.com/watch?v=inpok4MKVLM"),
    ("Mindfulness Exercises - Free Library",
     "https://mindfulnessexercises.com/free-mindfulness-exercises/"),
    ("UCLA Guided Meditations",
     "https://www.uclahealth.org/programs/marc/mindful-meditations"),
    ("Gratitude Journal Template",
     "https://positivepsychology.com/gratitude-journal-pdf/"),
]

therapists_by_country = {
    "USA": [("National Suicide Prevention Lifeline", "1-800-273-8255"),
            ("Crisis Text Line", "Text HOME to 741741")],
    "UK": [("Samaritans", "116 123"), ("Mind InfoLine", "0300 123 3393")],
    "Pakistan": [("Umang Mental Health Hotline", "0311-7786264")],
    "Canada": [("Talk Suicide Canada", "1-833-456-4566")],
    "Australia": [("Lifeline Australia", "13 11 14")],
}

# --- App Class ---

class ResourceHubApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Free Mental Health Resource Hub")
        self.root.state('zoomed')  # Full screen mode
        self.root.configure(bg="#f0f8ff")

        self.selected_country = tk.StringVar()
        self.search_query = tk.StringVar()

        self.create_sidebar()
        self.create_main_area()
        self.display_resources()

    def create_sidebar(self):
        sidebar = tk.Frame(self.root, width=250, bg="#4f97a3", relief="solid", padx=10)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(sidebar, text="Filters", font=("Helvetica", 16, "bold"), fg="white", bg="#4f97a3").pack(pady=15)

        countries = list(therapists_by_country.keys())
        self.country_combo = ttk.Combobox(sidebar, values=countries, textvariable=self.selected_country, state="readonly", width=20)
        self.country_combo.set("Select Country")
        self.country_combo.pack(pady=10)
        self.country_combo.bind("<<ComboboxSelected>>", lambda e: self.display_resources())

        search_entry = tk.Entry(sidebar, textvariable=self.search_query, font=("Helvetica", 12), bd=2, relief="solid")
        search_entry.pack(pady=10, padx=10, fill=tk.X)
        tk.Button(sidebar, text="Search", command=self.display_resources, bg="#f4a261", fg="white", relief="solid", width=20).pack(pady=10)

    def create_main_area(self):
        self.main_area = tk.Frame(self.root, bg="#f0f8ff")
        self.main_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.canvas = tk.Canvas(self.main_area)
        self.scrollbar = ttk.Scrollbar(self.main_area, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#f0f8ff")

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.scrollable_frame.bind(
            "<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

    def display_resources(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        query = self.search_query.get().lower()

        # Books Section
        filtered_books = [b for b in books if query in b[0].lower()] if query else books
        self.create_section("📚 Free Books", filtered_books, self.display_book)

        # Exercises Section
        filtered_exercises = [e for e in exercises if query in e[0].lower()] if query else exercises
        self.create_section("🧘 Free Exercises & Tools", filtered_exercises, self.display_exercise)

        # Therapists Section
        self.create_section("📞 Free Hotlines", self.get_therapists(), self.display_therapist)

    def create_section(self, title, data, display_func):
        tk.Label(self.scrollable_frame, text=title, font=("Helvetica", 18, "bold"), bg="#f0f8ff", fg="#4f97a3").pack(pady=15, anchor="w")
        if not data:
            tk.Label(self.scrollable_frame, text="No resources found.", font=("Helvetica", 12), bg="#f0f8ff").pack(anchor="w", padx=10)
        for item in data:
            display_func(item)

    def display_book(self, book):
        title, link = book
        card = tk.Frame(self.scrollable_frame, bg="#94d2bd", relief="groove", padx=15, pady=15, bd=2)
        card.pack(pady=10, fill="x", anchor="w", padx=10)
        tk.Label(card, text=title, font=("Helvetica", 14, "bold"), bg="#94d2bd").pack(anchor="w")
        tk.Button(card, text="Read", command=lambda l=link: webbrowser.open(l), bg="#264653", fg="white", relief="solid").pack(pady=5)

    def display_exercise(self, exercise):
        name, link = exercise
        card = tk.Frame(self.scrollable_frame, bg="#e9d8a6", relief="groove", padx=15, pady=15, bd=2)
        card.pack(pady=10, fill="x", anchor="w", padx=10)
        tk.Label(card, text=name, font=("Helvetica", 14, "bold"), bg="#e9d8a6").pack(anchor="w")
        tk.Button(card, text="Try", command=lambda l=link: webbrowser.open(l), bg="#264653", fg="white", relief="solid").pack(pady=5)

    def display_therapist(self, therapist):
        name, contact = therapist
        card = tk.Frame(self.scrollable_frame, bg="#f4a261", relief="groove", padx=15, pady=15, bd=2)
        card.pack(pady=10, fill="x", anchor="w", padx=10)
        tk.Label(card, text=f"{name}: {contact}", font=("Helvetica", 14), bg="#f4a261").pack(anchor="w")
        if pyperclip:
            tk.Button(card, text="Copy", command=lambda c=contact: pyperclip.copy(c), bg="#264653", fg="white", relief="solid").pack(side=tk.RIGHT, padx=10)

    def get_therapists(self):
        country = self.selected_country.get()
        return therapists_by_country.get(country, [])


# --- Launch App ---
if __name__ == "__main__":
    root = tk.Tk()
    app = ResourceHubApp(root)
    root.mainloop()
