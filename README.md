# Bing-Voice-Assistant
This is a voice assistant, powered by Bing Chat and Google Bard!
For transcribing this program implements OpenAI Whisper locally, Text-to-speech is done with gtts.

## How To Run
- Open a console in the directory with access to pip where you cloned this repo, then type `pip install -r requirements.txt` to install the required modules for the application.
- For Bing Chat:
-- Install Cookie-Editor from [Chrome Web Store](https://chrome.google.com/webstore/detail/hlkenndednhfkekhgcdicdfddnkalmdm)
-- Click Cookie-Editor's icon on the side bar, click "Export", then "Export as JSON".
-- Create a file named "cookies.json" next to "main.py", then paste what Cookie-Editor copied to your clipboard in the previous step and save.
- For Google Bard:
-- Go to [bard.google.com](https://bard.google.com/)
-- Open developer tools, go to application>cookies and copy the value for _Secure_1PSID
-- Create a file named "bard.txt" next to "main.py", then paste what you copied in the previous step and save.
- Add the sound files mentioned in "sound_list.txt". Without them, the application simply won't work.
- Make sure you have a working microphone connected to your PC, and that it's set as the default recording device.
- In the console that you previously opened, type `python main.py` to run the application.

## How To Use
The app might take a few seconds to load. Once done, you will hear the get_trigger sound. This indicates that the app is waiting for the wake up sentence.
Go ahead and say "Hey Bing" for Bing chat or "Hey Bard" for Google Bard. Make sure that you are close enough to the microphone and that you speak clearly. If the app cannot understand you, go ahead and change the `energy_threshold` of the recognizer in the "main.py" file. An increased value means less sensetivity. You might need to decrease it if you don't hear the processing sound for a long time after saying the wake up sentence. This is because the sensetivity is too much for your microphone. So much so that it thinks that your background noise is actual speech.
To start a new topic, (Meaning to reset the conversation flow), if the app is waiting for the wake up sentence, say the wake up sentence instantly followed by "new topic". If it's asking for a prompt, just say "new topic".
Do note that only the service you were talking to will have its conversation reset. For instance, if you were talking to Bing, only Bing's conversation will be reset. Bard will be still at that point of conversation where it was previously.
You can also provide a prompt without waiting for the app to ask you for it. Just say your prompt instantly after saying the wake up sentence. For example: "Hey bing, what is 10+10+10". This will avoid the prompting part and instantly sends the prompt you provided to Bing.

## Credits
- This project was originally forked from [Ai-Austin/Bing-GPT-Voice-Assistant](https://github.com/Ai-Austin/Bing-GPT-Voice-Assistant)
- Further additions, improvements and enhancements, optimizations, removal and replacement of paid services with free alternatives has been done by [Sonorous Arts](https://github.com/sonorous-arts/).