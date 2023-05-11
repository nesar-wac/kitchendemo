import json
import datetime
from time import sleep
from threading import Thread
from paho.mqtt import client as mqtt

res_spot_id = 0
res_status = ""


def on_connect(client, userdata, flags, return_code):
    if return_code != 0:
        print(f"Could not connect with broker {return_code}")
    client.subscribe("Out/Kitchen_1/Spice_Dispenser_X", 2)
    client.subscribe("Kitchen_1/Out/Cooking_Station/+", 2)


def on_ingredients_message(client, userdata, msg):
    global res_spot_id, res_status
    data = json.loads(msg.payload.decode("utf-8"))
    res_spot_id = data["Spot_Id"]
    res_status = data["Status"]


def on_cooking_message(client, userdata, msg):
    global res_spot_id, res_status
    data = json.loads(msg.payload.decode("utf-8"))
    res_spot_id = data["Spot_Id"]
    res_status = data["Status"]


client = mqtt.Client("RecipesProcess", clean_session=False)

client.on_connect = on_connect

client.username_pw_set(username="admin", password="Shakes2018")
client.connect("188.80.94.190", 1883)

client.loop_start()

client.message_callback_add("Out/Kitchen_1/Spice_Dispenser_X", on_ingredients_message)
client.message_callback_add(f"Kitchen_1/Out/Cooking_Station/+", on_cooking_message)


def process_recipe(recipe):
    spot_number = recipe["spot"]
    for step in recipe["steps"]:
        global res_spot_id, res_status
        print(step)
        if not step["ingredients"] == []:
            for ingredient in step["ingredients"]:
                data = json.dumps({
                    "Spot_Id": recipe["spot"],
                    "Volume": ingredient["volume"],
                    "Unit": ingredient["unit"],
                    "Name": ingredient["name"],
                })
                # check ingredient category and send
                # data to the dispenser based on it.
                if ingredient["category"] == "spice":
                    client.publish("In/Kitchen_1/Spice_Dispenser_X", data, 2)
                    print("Spot", spot_number, "start sleep time from spice", datetime.datetime.now())
                    # wait for response until status is not success
                    while res_spot_id != spot_number and res_status != "success":
                        sleep(1)
                    print("Spot", spot_number, "end sleep time from spice", datetime.datetime.now())
                    res_spot_id, res_status = 0, ""
                elif ingredient["category"] == "liquid":
                    client.publish("In/Kitchen_1/Spice_Dispenser_X", data, 2)
                    print("Spot", spot_number, "start sleep time from liquid", datetime.datetime.now())
                    # wait for response until status is not success
                    while res_spot_id != spot_number and res_status != "success":
                        sleep(1)
                    print("Spot", spot_number, "end sleep time from liquid", datetime.datetime.now())
                    res_spot_id, res_status = 0, ""
                else:
                    client.publish("In/Kitchen_1/Spice_Dispenser_X", data, 2)
                    print("Spot", spot_number, "start sleep time from general", datetime.datetime.now())
                    # wait for response until status is not success
                    while res_spot_id != spot_number and res_status != "success":
                        sleep(1)
                    print("Spot", spot_number, "end sleep time from general", datetime.datetime.now())
                    res_spot_id, res_status = 0, ""
        else:
            target_data = json.dumps({
                "Spot_Id": spot_number,
                "Temperature": step["temperature"],
                "Speed": step["speed"],
                "Duration": step["duration"]
            })
            topic = f"Kitchen_1/In/Cooking_Station/{spot_number}"
            client.publish(topic=topic, payload=target_data, qos=2)
            print("Spot", spot_number, "start sleep time from action.", datetime.datetime.now())
            # waiting for response until status is not success
            # and spot number is not equal to the spot number
            while res_spot_id != spot_number and res_status != "success":
                sleep(1)
            print("Spot", spot_number, "end sleep time from action.", datetime.datetime.now())
            res_spot_id, res_status = 0, ""


def run_recipes(recipes):
    threads = [
        Thread(target=process_recipe, args=(recipe,)) for recipe in recipes
    ]

    # start created threads
    for thread in threads:
        thread.start()

    # wait for running threads
    for thread in threads:
        thread.join()
