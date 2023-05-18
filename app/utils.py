import json
import secrets
import datetime
from time import sleep
from threading import Thread
from paho.mqtt import client as mqtt


robot_status = ""

ing_req_id = ""
ing_status = ""

spot_req_id = ""
spot_status = ""


def on_connect(client, userdata, flags, return_code):
    if return_code != 0:
        print(f"Could not connect with broker {return_code}")

    client.subscribe("Kitchen_1/Out/Liquid_Dispenser", 2)
    client.subscribe("Kitchen_1/Out/Spice_Dispenser", 2)
    client.subscribe("Kitchen_1/Out/Normal_Dispenser", 2)
    client.subscribe("Kitchen_1/Out/Cooking_Station/+", 2)


def on_liquid_msg(client, userdata, msg):
    global ing_req_id, ing_status
    data = json.loads(msg.payload.decode("utf-8"))
    ing_req_id = data["Req_Id"]
    ing_status = data["Status"]


def on_spice_msg(client, userdata, msg):
    global ing_req_id, ing_status
    data = json.loads(msg.payload.decode("utf-8"))
    ing_req_id = data["Req_Id"]
    ing_status = data["Status"]


def on_normal_msg(client, userdata, msg):
    global ing_req_id, ing_status
    data = json.loads(msg.payload.decode("utf-8"))
    ing_req_id = data["Req_Id"]
    ing_status = data["Status"]


def on_spot_message(client, userdata, msg):
    global spot_req_id, spot_status
    data = json.loads(msg.payload.decode("utf-8"))
    spot_req_id = data["Req_Id"]
    spot_status = data["Status"]


client = mqtt.Client("RecipesProcess", clean_session=False)

client.on_connect = on_connect

client.username_pw_set(username="admin", password="Shakes2018")
client.connect("188.80.94.190", 1883)

client.loop_start()

client.message_callback_add("Kitchen_1/Out/Liquid_Dispenser", on_liquid_msg)
client.message_callback_add("Kitchen_1/Out/Spice_Dispenser", on_spice_msg)
client.message_callback_add("Kitchen_1/Out/Normal_Dispenser", on_normal_msg)
client.message_callback_add(f"Kitchen_1/Out/Cooking_Station/+", on_spot_message)


def process_recipe(recipe):
    spot_number = recipe["spot"]
    for step in recipe["steps"]:
        print(step)
        if not step["ingredients"] == []:
            for ingredient in step["ingredients"]:
                global robot_status
                global ing_req_id, ing_status
                # generate random hex string
                req_id = secrets.token_hex(5)

                print("from", recipe["id"], robot_status)

                while robot_status == "busy":
                    sleep(1)

                # format publisher data
                data = json.dumps({
                    "Req_Id": req_id,
                    "Spot_Id": recipe["spot"],
                    "Volume": ingredient["volume"],
                    "Unit": ingredient["unit"],
                    "Name": ingredient["name"],
                })

                # check ingredient category and send
                # data to the dispenser based on it.
                if ingredient["category"] == "spice":
                    robot_status = "busy"
                    client.publish("Kitchen_1/In/Spice_Dispenser", data, 2)
                    # client.publish("", 2)
                    print("Spot", spot_number, "start sleep time from spice", datetime.datetime.now())
                    # wait for response until status is not success
                    while ing_req_id != req_id:
                        sleep(1)
                    # do something for return status
                    print("Spot", spot_number, "end sleep time from spice", datetime.datetime.now())
                    robot_status = "idle"
                    ing_req_id, ing_status = "", ""
                elif ingredient["category"] == "liquid":
                    robot_status = "busy"
                    client.publish("Kitchen_1/In/Liquid_Dispenser", data, 2)
                    print("Spot", spot_number, "start sleep time from liquid", datetime.datetime.now())
                    # wait for response until status is not success
                    while ing_req_id != req_id:
                        sleep(1)
                    # do something for return status
                    print("Spot", spot_number, "end sleep time from liquid", datetime.datetime.now())
                    robot_status = "idle"
                    ing_req_id, ing_status = "", ""
                else:
                    robot_status = "busy"
                    client.publish("Kitchen_1/In/Normal_Dispenser", data, 2)
                    print("Spot", spot_number, "start sleep time from general", datetime.datetime.now())
                    # wait for response until status is not success
                    while ing_req_id != req_id:
                        sleep(1)
                    # do something for return status
                    print("Spot", spot_number, "end sleep time from general", datetime.datetime.now())
                    robot_status = "idle"
                    ing_req_id, ing_status = "", ""
        else:
            global spot_req_id, spot_status
            # generate random hex string
            req_id = secrets.token_hex(5)
            target_data = json.dumps({
                "Req_Id": req_id,
                "Spot_Id": spot_number,
                "Temperature": step["temperature"],
                "Speed": step["speed"],
                "Duration": step["duration"]
            })
            topic = f"Kitchen_1/In/Cooking_Station/{spot_number}"
            client.publish(topic=topic, payload=target_data, qos=2)
            print("Spot", spot_number, "start sleep time from action.", datetime.datetime.now())
            # waiting for response until status is not success
            # and res spot id is not equal to the spot number
            while spot_req_id != req_id:
                sleep(1)
            # do something for return status
            print("Spot", spot_number, "end sleep time from action.", datetime.datetime.now())
            spot_req_id, spot_status = "", ""

    # write code for packaging


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
