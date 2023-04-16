import sys
import time
import os
import string
from rapidfuzz import fuzz, process
#from TTS.api import TTS
from gtts.tts import gTTS
import pydub
from pydub import playback
import asyncio
import threading
import re
import whisper
import speech_recognition as sr

from EdgeGPT import Chatbot, ConversationStyle

recognizer = sr.Recognizer()
#List of the words that trigger the application
wake_sentence = "Hey Bing"

#Initialize TTS
#tts = TTS(model_name="tts_models/en/ljspeech/fast_pitch", model_path = ".cache/TTS/fast_pitch/model_file.pth", config_path = ".cache/TTS/fast_pitch/config.json", vocoder_path=".cache/TTS/vocoder_hifigan_v2/model_file.pth", vocoder_config_path=".cache/TTS/vocoder_hifigan_v2/config.json")

model = whisper.load_model("base", download_root = '.cache/whisper/')

#Creates an instance of Chatbot. Every time we need to start fresh (new topic), we have to create another instance of Chatbot.
bot = Chatbot(cookiePath='cookies.json')

def clean_str(text: str) -> str:
	text = strip_emojis(text)
	text = strip_punctuation(text)
	text= text.lstrip()
	text = text.rstrip()
	text = text.lower()
	return text

def get_wake_sentence(phrase: str) -> tuple:
	"""Checks the spoken phrase against wake_sentence.
	Returns the spoken phrase, if the assessment passes, so that later it can be used for prompting the bot without waiting."""
	
	if phrase == "": return None
	ratio = fuzz.ratio(wake_sentence, phrase[0:len(wake_sentence)])
	if ratio >= 70:
		return (phrase, ratio)
	else:
		speak("I heard, " + phrase +". Which is not a wake up word for me.")
		return ()

def strip_punctuation(text: str) -> str:
	"""Strips all punctuation symbols from the given string"""
	return text.translate(str.maketrans('', '', string.punctuation))

def strip_emojis(text: str) -> str:
	emoji_pattern = re.compile("["
		u"\U0001F600-\U0001F64F"  # emoticons
		u"\U0001F300-\U0001F5FF"  # symbols & pictographs
		u"\U0001F680-\U0001F6FF"  # transport & map symbols
		u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
		u"\U00002702-\U000027B0"
		u"\U000024C2-\U0001F251"
		"]", flags=re.UNICODE
	)
	text = emoji_pattern.sub(r'', text)
	return text

def is_question(text: str) -> bool:
	"""Checks to make sure the text ends with a question by removing all the emoji characters, then stripping the trailing white spaces."""
	text = strip_emojis(text)
	text = text.rstrip()
	return text.endswith("?")

def strip_wake_sentence(spoken_sentence: str) -> str:
	"""Strips wake_sentence from spoken_sentence and returns it"""
	
	spoken_sentence = spoken_sentence[len(wake_sentence):]
	spoken_sentence = spoken_sentence.lstrip()
	return spoken_sentence

def _load_play_audio(file: str):
	"""Loads and plays an audio file. Must be seprated from the `play_audio` function, so that both loading and playing procedure can be in one single thread. Otherwise, the none blocking mode will not work."""
	sounddata = pydub.AudioSegment.from_file(file, format=file.split(".")[-1])
	playback.play(sounddata)

def play_audio(file: str, blocking: bool = False):
	"""Plays an audio file.
	In order for the none blocking mode to work, the actual logic of loading and playing sounds is moved to the `_load_play_audio` function. If loading and playing of audio files are seprated in different threads, the none blocking mode will not work as expected"""
	if blocking:
		_load_play_audio(file)
	else:
		t = threading.Thread(target=_load_play_audio, args=[file])
		t.daemon = True
		t.start()

def speak(text: str, blocking: bool = True):
	#tts.tts_to_file(text, speed=2.0, file_path="tts_output.mp3")
	speech = gTTS(text=text, tld="ca")
	speech.save("tts_output.mp3")
	play_audio("tts_output.mp3", blocking=blocking)
	os.remove("tts_output.mp3")

async def get_trigger(source: sr.Microphone):
	global bot
	play_audio("sounds/get_trigger.mp3", True)
	while True:
		try:
			#speak("Say, Hay richard")
			#

			recognizer.energy_threshold = 1000
			try:
				audio = recognizer.listen(source, 4)
			except sr.exceptions.WaitTimeoutError:
				continue
			play_audio("sounds/processing.mp3")
			try:
				with open("audio.mp3", "wb") as f:
					f.write(audio.get_wav_data())
				
				result = model.transcribe("audio.mp3", initial_prompt = "Hey Richard")
				os.remove("audio.mp3")
				phrase = result["text"]


				try:
					spoken_sentence, ratio = get_wake_sentence(phrase=phrase)
				except (ValueError, TypeError):
					#Play the get trigger audio so the user knows they can speak
					play_audio("sounds/get_trigger.mp3")
					continue
				processed_sentence = clean_str(spoken_sentence)
				if processed_sentence != "":
					processed_sentence = strip_wake_sentence(processed_sentence)
					if processed_sentence == "":
						break
					elif fuzz.ratio(processed_sentence, "new topic") >= 70:
						bot = Chatbot(cookiePath="cookies.json")
						#Announce that there's going to be a new topic from now on so that user won't continue the last one.
						speak("New topic. What can I do for you?")
						break
					else:
						#Something is spoken after the wake up sentence, so we are going to ask about it from bing.
						spoken_sentence = strip_wake_sentence(spoken_sentence)
						response_params = process_response(await get_response(spoken_sentence))
						if response_params["question"]:
							#A question is asked, so move back to main to get a prompt.
							break
						else:
							#Play the get trigger audio so the user knows they can speak
							play_audio("sounds/get_trigger.mp3")
			except Exception as e:
				print("Error transcribing audio: {0}".format(e))
				continue
		except KeyboardInterrupt:
			await quit()

async def main():
	global bot
	with sr.Microphone() as source:
		recognizer.dynamic_energy_threshold = False
		await get_trigger(source=source)
		#recognizer.adjust_for_ambient_noise(source, 0.5)
		while True:
			try:
				#recognizer.energy_threshold = 300
				play_audio("sounds/prompt.mp3", True)
				
				try:
					audio = recognizer.listen(source, 5)
				except sr.exceptions.WaitTimeoutError:
					await get_trigger(source)
					continue

				play_audio("sounds/processing.mp3")
				try:
					with open("audio_prompt.mp3", "wb") as f:
						f.write(audio.get_wav_data())
					result = model.transcribe("audio_prompt.mp3")
					os.remove("audio_prompt.mp3")
					user_input = result["text"]
					if fuzz.ratio(user_input, "new topic") >= 70:
						bot = Chatbot(cookiePath="cookies.json")
						speak("New topic. What can I do for you?")
						continue
				except Exception as e:
					print("Error transcribing audio: {0}".format(e))
					continue
				response_params = process_response(await get_response(user_input=user_input))
				if not response_params["question"]:
					#No question is asked, so move on to waiting for the wake up sentence again.
					await get_trigger(source=source)
			except KeyboardInterrupt:
				await quit()

async def get_response(user_input: str) -> str:
	play_audio("sounds/requesting.mp3")
	response = await bot.ask(prompt=user_input, conversation_style=ConversationStyle.precise)
	for message in response["item"]["messages"]:
		if message["author"] == "bot":
			bot_response = message["text"]

	bot_response = re.sub('\[\^\d+\^\]', '', bot_response)

	"""
	bot = Chatbot(cookiePath='cookies.json')
	response = await bot.ask(prompt=user_input, conversation_style=ConversationStyle.creative)
	# Select only the bot response from the response dictionary
	for message in response["item"]["messages"]:
		if message["author"] == "bot":
			bot_response = message["text"]
	# Remove [^#^] citations in response
	bot_response = re.sub('\[\^\d+\^\]', '', bot_response)
	"""

	return bot_response

def process_response(response: str):
	speak(response)
	
	return {
		"question": is_question(response)
	}

async def quit():
	print("exiting...")
	await bot.close()
	sys.exit(0)

if __name__ == "__main__":
	asyncio.run(main())
