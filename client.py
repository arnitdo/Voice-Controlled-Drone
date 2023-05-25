import speech_recognition as sr
import socket

voice_rec = sr.Recognizer()
for pair in enumerate(sr.Microphone.list_microphone_names()):
	print(pair)

voice_input = sr.Microphone()

server_addr = input("Enter server address or hostname : ")

client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_sock.connect((server_addr, 57600))

client_side_exit = False

with voice_input as mic:
	while client_side_exit == False:
		try:
			audio_clip = voice_rec.listen(mic, phrase_time_limit = 1)
		
			recognized_audio = voice_rec.recognize_google_cloud(audio_clip, language = 'en-IN', credentials_json="credentials.json")

			print("Recognized audio :", recognized_audio)

			if (len(recognized_audio) > 1023):
				print("Audio clip too long!")
			else:
				client_sock.sendall(
					bytes(recognized_audio, "utf-8")
				)
				if "exit" in recognized_audio:
					client_side_exit = True

		except sr.UnknownValueError:
			print("Could not recognize audio")