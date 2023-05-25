import socket
import sys

if sys.version_info.major == 3 and sys.version_info.minor >= 10:
    import collections
    import collections.abc as abc
    setattr(collections, "MutableMapping", abc.MutableMapping)

import dronekit
import time


server_sock = socket.socket(
	socket.AF_INET,
	socket.SOCK_STREAM,
)

server_sock.bind(
	('', 57600)
)

server_sock.listen()

print("Waiting for inbound connection!")

(client, addr) = server_sock.accept()
print(f"Found inbound connection from {addr}")

vehicle_exit = False

#drone_sim = dronekit_sitl.start_default()

vehicle = dronekit.connect(
	'/dev/ttyAMA0',
	wait_ready = True,
    baud=921600
)

if not vehicle:
	print("Could not connect to FlightController!")
	exit(1)
	

def send_ned_velocity(velocity_x, velocity_y, velocity_z):
    """
    Move vehicle in direction based on specified velocity vectors.
    """
    msg = vehicle.message_factory.set_position_target_local_ned_encode(
        0,       # time_boot_ms (not used)
        0, 0,    # target system, target component
        dronekit.mavutil.mavlink.MAV_FRAME_LOCAL_NED, # frame
        0b0000111111000111, # type_mask (only speeds enabled)
        0, 0, 0, # x, y, z positions (not used)
        velocity_x, velocity_y, velocity_z, # x, y, z velocity in m/s
        0, 0, 0, # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
        0, 0
	)    # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)

def arm_drone():
	#while vehicle.is_armable == False:
	#	print(f"Drone armable status: {vehicle.is_armable}")
	#	time.sleep(1)

	#vehicle.mode = dronekit.VehicleMode("GUIDED")
	#while vehicle.mode != "GUIDED":
	#	print("Waiting for mode: ", vehicle.mode)
	#	time.sleep(1)

	#print("Mode: ", vehicle.mode)
	vehicle.armed = True

def disarm_drone():
	#vehicle.mode = dronekit.VehicleMode("AUTO")
	#while vehicle.mode != "AUTO":
	#	print("Waiting for auto mode")
	
	vehicle.disarm()
	print("Drone disarmed")

def drone_ascend():
	# Set up velocity mappings
	# velocity_x > 0 => fly North
	# velocity_x < 0 => fly South
	# velocity_y > 0 => fly East
	# velocity_y < 0 => fly West
	# velocity_z < 0 => ascend
	# velocity_z > 0 => descend

	#vel_x = 0
	#vel_y = 0
	#vel_z = 20
	#for _ in range(5):
	#	time.sleep(1)
	#	send_ned_velocity(vel_x, vel_y, vel_z)

	#send_ned_velocity(0, 0, 0)
	vehicle.simple_takeoff(5)

def drone_north():
	vel_x = 0.5
	vel_y = 0
	vel_z = 0
	send_ned_velocity(vel_x, vel_y, vel_z)

def drone_exit():
	vehicle_exit = True
	disarm_drone()
	client.close()
	server_sock.close()

def handle_drone_command(command_str):
	for command in drone_command_map:
		if command.lower() in command_str.lower():
			mapped_command = drone_command_map[command]
			mapped_command()
			print("Executing command :", command)

drone_command_map = {
	"start": arm_drone,
	"disarm": disarm_drone,
	"up": drone_ascend,
	"north": drone_north,
	"exit": drone_exit
}


while vehicle_exit == False:
	try:
		data = client.recv(1024)
		inbound_data = data.decode()
		# inbound_data = input("Command")
		print(f"Inbound data : {inbound_data}")

		handle_drone_command(inbound_data)
	except KeyboardInterrupt:
		drone_exit()

print("Clean exit!")	
