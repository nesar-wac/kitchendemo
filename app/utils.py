import json
from threading import Thread, current_thread
from time import sleep
from paho.mqtt import client as mqtt
import datetime

ing_res_msg = ""


def on_connect(client, userdata, flags, return_code):
    if return_code != 0:
        print("connection isn't established with broker.")


def on_ingredient(client, userdata, msg):
    global ing_res_msg
    ing_res_msg = msg.payload.decode("utf-8")


client = mqtt.Client("ShopAveiroOne")
client.on_connect = on_connect
client.message_callback_add("Out/Kitchen_1/Spice_Dispenser_X", on_ingredient)

client.username_pw_set(username="admin", password="Shakes2018")
client.connect("188.80.94.190", 1883)

client.subscribe("Out/Kitchen_1/Spice_Dispenser_X", 2)

client.loop_forever()


def process_steps(recipe):
    for step in recipe["steps"]:
        if step["ingredients"]:
            for ingredient in step["ingredients"]:
                global ing_res_msg
                if ingredient["category"] == "spice":
                    data = json.dumps(ingredient)
                    client.publish("In/Kitchen_1/Spice_Dispenser_X", data, 2)
                    print("before sleep", datetime.datetime.now())
                    sleep(0) if ing_res_msg == "success" else sleep(30)
                    print("after sleep", datetime.datetime.now())
                    print("waiting", ing_res_msg)
                    ing_res_msg = ""
                elif ingredient["category"] == "liquid":
                    data = json.dumps(ingredient)
                    client.publish("In/Kitchen_1/Spice_Dispenser_X", data, 2)
                    print("before sleep", datetime.datetime.now())
                    sleep(0) if ing_res_msg == "success" else sleep(30)
                    print("after sleep", datetime.datetime.now())
                    print("waiting", ing_res_msg)
                    ing_res_msg = ""
                else:
                    data = json.dumps(ingredient)
                    client.publish("In/Kitchen_1/Spice_Dispenser_X", data, 2)
                    print("before sleep", datetime.datetime.now())
                    sleep(0) if ing_res_msg == "success" else sleep(30)
                    print("after sleep", datetime.datetime.now())
                    print("waiting", ing_res_msg)
                    ing_res_msg = ""

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
