# Bing-Voice-Assistant
This is a voice assistant, powered by Bing Chat.
For transcribing this program implements OpenAI Whisper locally, Text-to-speech is done with pyttsx3.

## How To Run
Please note that pytorch and openai-whisper are not compatible with python3.11, therefore neither is this project. The highest version that this project supports is python3.10.
- Open a console in the directory with access to pip where you cloned this repo, then type `pip install -r requirements.txt` to install the required modules for the application.
- Add the sound files mentioned in "sound_list.txt". Without them, it simply won't work.
- Make sure you have a microphone connected to your PC, and that it's set as the default recording device.
- In the console that you previously opened, type `python main.py` to run the application.

## Credits
- This project was originally froked from [Ai-Austin/Bing-GPT-Voice-Assistant](https://github.com/Ai-Austin/Bing-GPT-Voice-Assistant)
- Further additions, improvements and enhancements, optimizations, removal and replacement of paid services with free alternatives has been my work.