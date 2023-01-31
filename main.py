import sys

if sys.version_info.major == 3 and sys.version_info.minor >= 10:
    import collections
    import collections.abc as abc
    setattr(collections, "MutableMapping", abc.MutableMapping)

import speech_recognition as sr
import dronekit
import dronekit_sitl
import time

voice_rec = sr.Recognizer()
voice_input = sr.Microphone()

vehicle_exit = False

drone_sim = dronekit_sitl.start_default()

vehicle = dronekit.connect(
	drone_sim.connection_string(),
	wait_ready = True,
	# baud=57600
)

if not vehicle:
	print("Could not connect to FlightController!")
	exit(1)
	
def arm_drone():
	is_armable = vehicle.is_armable
	print(f"Drone armable status: {is_armable}")
	if is_armable == True:
		vehicle.arm()

drone_command_map = {
	"arm": arm_drone
}

while vehicle_exit == False:
	try:
		# with voice_input as mic:
		# 	voice_rec.adjust_for_ambient_noise(mic)
		# 	audio_clip = voice_rec.listen(mic, phrase_time_limit = 0.5)
		
		# 	recognized_audio = voice_rec.recognize_sphinx(audio_clip)
		# 	print(recognized_audio)
		in_command = input("Drone command: ")
		for command in drone_command_map:
			if command.lower() in in_command.lower():
				mapped_command = drone_command_map[command]
				mapped_command()
				break

	except sr.UnknownValueError:
		print("Could not recognize audio")
	time.sleep(2)	