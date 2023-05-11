import json
from time import sleep
import paho.mqtt.client as mqtt


# The callback function of connection
def on_connect(client, userdata, flags, return_code):
    if return_code != 0:
        print(f"Could not connect with broker {return_code}")
    print(f"Connected successfully with broker")
    client.subscribe("In/Kitchen_1/Spice_Dispenser_X")


# The callback function for received message
def on_message(client, userdata, msg):
    input_data = json.loads(msg.payload.decode("utf-8"))
    print(input_data)
    sid = input_data["Spot_Id"]
    output_data = json.dumps({"Spot_Id": sid, "Status": "success"})
    client.publish("Kitchen_1/In/Robot_Status", "busy", 2)
    sleep(10)
    client.publish("Out/Kitchen_1/Spice_Dispenser_X", output_data, 2)


client = mqtt.Client("IngredientsProcess", clean_session=False)

# Specify callback functions
client.on_connect = on_connect
client.on_message = on_message

# Establish a connection with broker using username and password
client.username_pw_set(username="admin", password="Shakes2018")
client.connect("188.80.94.190", 1883)

try:
    client.loop_forever()
except KeyboardInterrupt:
    client.disconnect()
    exit(0)
