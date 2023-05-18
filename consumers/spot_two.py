import json
from time import sleep
import paho.mqtt.client as mqtt


# when connection is established, on_connect is called
def on_connect(client, userdata, flags, return_code):
    if return_code != 0:
        print(f"Could not connect with broker {return_code}")
    print(f"Connected successfully with broker")
    client.subscribe("Kitchen_1/In/Cooking_Station/02", 2)


# when data is published, on_message is called by default
def on_message(client, userdata, msg):
    # convert binary data to python dictionary
    data = json.loads(msg.payload.decode("utf-8"))
    print(data)
    res_data = json.dumps({"Req_Id": data["Req_Id"], "Status": "success"})
    sleep(data["Duration"])  # put on sleep mode
    # return spot number and status of the process
    topic = f"Kitchen_1/Out/Cooking_Station/02"
    client.publish(topic=topic, payload=res_data, qos=2)


# create a new client instance with name and clean session
client = mqtt.Client("SpotTwoAction", clean_session=False)

# specify callback functions
client.on_connect = on_connect
client.on_message = on_message

# establish a connection with broker using username and password
client.username_pw_set(username="admin", password="Shakes2018")
client.connect("188.80.94.190", 1883)

# start separate blocking thread
try:
    client.loop_forever()
except KeyboardInterrupt:
    client.disconnect()
    exit(0)
