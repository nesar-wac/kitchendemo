import json
from threading import Thread, current_thread
from time import sleep

from paho.mqtt import client as mqtt


def on_connect(client, userdata, flags, return_code):
    if return_code != 0:
        print("connection isn't established with broker.")


client = mqtt.Client("ShopAveiroOne")
client.on_connect = on_connect

client.username_pw_set(username="admin", password="Shakes2018")
client.connect("188.80.94.190", 1883)


def process_steps(recipe):
    for step in recipe["steps"]:
        if step["ingredients"] != []:
            for ingredient in step["ingredients"]:
                if ingredient["category"] == "spice":
                    data = json.dumps(ingredient)
                    client.publish(f"In/Kitchen_1/Spice_Dispenser_{1}", data, 2)
                    client.loop_start()
                    sleep(20)
                elif ingredient["category"] == "liquid":
                    data = json.dumps(ingredient)
                    client.publish("In/Kitchen_1/Spice_Dispenser_X", data, 2)
                    client.loop_start()
                    sleep(20)
                else:
                    data = json.dumps(ingredient)
                    client.publish("In/Kitchen_1/Spice_Dispenser_X", data, 2)
                    client.loop_start()
                    sleep(20)
        else:
            spot_number = recipe["spot"]
            temp_data = {}
            temp_data["Id_Number"] = spot_number
            temp_data["Temperature"] = step["temperature"]
            temp_data["Speed"] = step["speed"]
            temp_data["Duration"] = step["duration"]
            data = json.dumps(temp_data)
            client.publish(f"In/Cooking_Station/{spot_number}", data, 2)
            client.loop_start()
            sleep(int(step["duration"]))

    # track process message by process name
    thread_name = current_thread().name
    print(f"Thread {thread_name} in process done.", flush=True)


def process_recipes(recipes):
    threads = [
        Thread(target=process_steps, args=(recipe,), name=recipe["spot"]) for recipe in recipes
    ]

    # start created threads
    for thread in threads:
        thread.start()

    # wait for running threads
    for thread in threads:
        thread.join()
