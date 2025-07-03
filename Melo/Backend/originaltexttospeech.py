import pygame  # For audio playback
import random  # For random responses
import asyncio  # For async TTS operations
import edge_tts  # For text-to-speech functionality
import os  # For file handling
from dotenv import dotenv_values  # For loading environment variables

# Load environment variables
env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice") or "en-US-AriaNeural"  # Default voice if not set

# Debugging: Print the loaded voice
print(f"Loaded AssistantVoice: {AssistantVoice}")


async def TextToAudioFile(text) -> None:
    """
    Converts text to speech and saves it as an audio file.
    """
    file_path = r"Data\speech.mp3"
    # Remove the existing audio file if it exists
    if os.path.exists(file_path):
        os.remove(file_path)

    # Generate speech and save to file
    communicate = edge_tts.Communicate(text, AssistantVoice, pitch='+5Hz', rate='+13%')
    await communicate.save(file_path)


def TTS(text, func=lambda r=None: True):
    """
    Converts text to speech and plays it using pygame.
    """
    try:
        # Convert text to an audio file asynchronously
        asyncio.run(TextToAudioFile(text))

        # Initialize pygame mixer
        pygame.mixer.init()

        # Load the generated audio file
        pygame.mixer.music.load(r"Data\speech.mp3")

        # Play the audio
        pygame.mixer.music.play()

        # Wait for playback to complete or external function to stop it
        while pygame.mixer.music.get_busy():
            if func() is False:  # If external function returns False
                break
            pygame.time.Clock().tick(10)  # Limit loop speed

        return True

    except Exception as e:
        print(f"Error in TTS: {e}")

    finally:
        try:
            func(False)  # Notify external function
            if pygame.mixer.get_init():  # Ensure mixer is initialized before stopping
                pygame.mixer.music.stop()
                pygame.mixer.quit()
        except Exception as e:
            print(f"Error in finally block: {e}")


def TextToSpeech(text, func=lambda r=None: True):
    """
    Handles text-to-speech for short and long texts.
    Splits long texts and provides predefined responses.
    """
    Data = str(text).split(".")  # Split text by sentences
    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out, sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, sir.",
    ]

    # If the text is very long, play only the first part with a response
    if len(Data) > 4 and len(text) >= 250:
        TTS(" ".join(text.split(".")[0:2]) + ". " + random.choice(responses), func)
    else:
        # Play the whole text for shorter input
        TTS(text, func)


if __name__ == "__main__":
    # Ensure Data folder exists
    os.makedirs("Data", exist_ok=True)

    try:
        while True:
            # Get user input
            user_input = input("Enter the text (or type 'exit' to quit): ").strip()
            if user_input.lower() == "exit":
                print("Exiting the program. Goodbye!")
                break  # Exit loop
            TextToSpeech(user_input)

    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Exiting...")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
