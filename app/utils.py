import json
import secrets
import datetime
from time import sleep
from threading import Thread
from paho.mqtt import client as mqtt

# declare global variables
robot_status = ""

robot_res_id = ""
robot_res_status = ""

ing_res_id = ""
ing_res_status = ""

spot_res_id = ""
spot_res_status = ""

# generate hex number for client id
client_id = secrets.token_hex(10)


def on_connect(client, userdata, flags, return_code):
    if return_code != 0:
        print(f"Could not connect with broker {return_code}")

    client.subscribe("Kitchen_1/Out/Robot", 2)
    client.subscribe("Kitchen_1/Out/Liquid_Dispenser/+", 2)
    client.subscribe("Kitchen_1/Out/Spice_Dispenser/+", 2)
    client.subscribe("Kitchen_1/Out/Normal_Dispenser/+", 2)
    client.subscribe("Kitchen_1/Out/Cooking_Station/+", 2)


def on_liquid_msg(client, userdata, msg):
    global ing_res_id, ing_res_status
    data = json.loads(msg.payload.decode("utf-8"))
    ing_res_id = data["Req_Id"]
    ing_res_status = data["Status"]


def on_spice_msg(client, userdata, msg):
    global ing_res_id, ing_res_status
    data = json.loads(msg.payload.decode("utf-8"))
    ing_res_id = data["Req_Id"]
    ing_res_status = data["Status"]


def on_normal_msg(client, userdata, msg):
    global ing_res_id, ing_res_status
    data = json.loads(msg.payload.decode("utf-8"))
    ing_res_id = data["Req_Id"]
    ing_res_status = data["Status"]


def on_spot_message(client, userdata, msg):
    global spot_res_id, spot_res_status
    data = json.loads(msg.payload.decode("utf-8"))
    spot_res_id = data["Req_Id"]
    spot_res_status = data["Status"]


def on_robot_message(client, userdata, msg):
    global robot_res_id, robot_res_status
    data = json.loads(msg.payload.decode("utf-8"))
    robot_res_id = data["Req_Id"]
    robot_res_status = data["Status"]


client = mqtt.Client(client_id, clean_session=False)

client.on_connect = on_connect

client.username_pw_set(username="admin", password="Shakes2018")
client.connect("188.80.94.190", 1883)

client.loop_start()

client.message_callback_add("Kitchen_1/Out/Robot", on_robot_message)
client.message_callback_add("Kitchen_1/Out/Liquid_Dispenser/+", on_liquid_msg)
client.message_callback_add("Kitchen_1/Out/Spice_Dispenser/+", on_spice_msg)
client.message_callback_add("Kitchen_1/Out/Normal_Dispenser/+", on_normal_msg)
client.message_callback_add("Kitchen_1/Out/Cooking_Station/+", on_spot_message)


def process_recipe(recipe):
    # extract spot id from recipe
    spot_number = recipe["spot"]
    # iterate steps one by one
    for step in recipe["steps"]:
        print(step)
        # check, does a step contain ingredient
        if not step["ingredients"] == []:
            # iterate ingredients one by one
            for ingredient in step["ingredients"]:
                global robot_status
                global ing_res_id, ing_res_status
                global robot_res_id, robot_res_status

                # wait for robot availability
                while robot_status == "busy":
                    sleep(1)

                # extract dispenser id from ingredient
                dispenser = ingredient["dispenser"]

                # generate random hex for ing_req
                ing_req_id = secrets.token_hex(5)

                # restructure ing data
                ing_dict = json.dumps({
                    "Req_Id": ing_req_id,
                    "Dispenser": dispenser,
                    "Time": ingredient["volume"],
                })

                # check ingredient category and send
                # data to the dispenser based on it.
                if ingredient["category"] == "spice":
                    robot_status = "busy"

                    # generate random hex string value
                    robot_req_id = secrets.token_hex(5)
                    forw_step_dict = json.dumps({
                        "Req_Id": robot_req_id,
                        "AxisX": 0,
                        "SpeedX": 0,
                        "AxisY": 0,
                        "SpeedY": 0,
                        "ControlParam": 2
                    })
                    client.publish("Kitchen_1/In/Robot", forw_step_dict, 2)
                    print("Spot", spot_number, "start sleep time from robot forward step", datetime.datetime.now())
                    # waiting for the mqtt response until
                    # robot_req_id is not equal to robot_res_id
                    while robot_res_id != robot_req_id:
                        sleep(1)
                    print("Spot", spot_number, "end sleep time from robot forward step", datetime.datetime.now())
                    if robot_res_status == "success":
                        robot_res_id = ""
                        robot_res_status = ""

                    topic = f"Kitchen_1/In/Spice_Dispenser/{dispenser}"
                    client.publish(topic=topic, payload=ing_dict, qos=2)
                    print("Spot", spot_number, "start sleep time from spice", datetime.datetime.now())
                    # waiting for the mqtt response until
                    # ing_req_id is not equal to ing_res_id
                    while ing_res_id != ing_req_id:
                        sleep(1)
                    print("Spot", spot_number, "end sleep time from spice", datetime.datetime.now())
                    # if ing_res_status is equal to success
                    # reset ing id, status and robot status
                    if ing_res_status == "success":
                        ing_res_id = ""
                        ing_res_status = ""

                    # generate random hex robot req id
                    robot_req_id = secrets.token_hex(5)
                    back_step_dict = json.dumps({
                        "Req_Id": robot_req_id,
                        "AxisX": 0,
                        "SpeedX": 0,
                        "AxisY": 0,
                        "SpeedY": 0,
                        "ControlParam": 2
                    })
                    client.publish("Kitchen_1/In/Robot", back_step_dict, 2)
                    print("Spot", spot_number, "start sleep time from robot backward step", datetime.datetime.now())
                    # waiting for the mqtt response until
                    # robot_req_id is equal to robot_res_id
                    while robot_res_id != robot_req_id:
                        sleep(1)
                    print("Spot", spot_number, "end sleep time from robot backward step", datetime.datetime.now())
                    if robot_res_status == "success":
                        robot_res_id = ""
                        robot_res_status = ""

                    robot_status = "idle"
                elif ingredient["category"] == "liquid":
                    robot_status = "busy"

                    # generate random hex string value
                    robot_req_id = secrets.token_hex(5)
                    forw_step_dict = json.dumps({
                        "Req_Id": robot_req_id,
                        "AxisX": 0,
                        "SpeedX": 0,
                        "AxisY": 0,
                        "SpeedY": 0,
                        "ControlParam": 2
                    })
                    client.publish("Kitchen_1/In/Robot", forw_step_dict, 2)
                    print("Spot", spot_number, "start sleep time from robot forward step", datetime.datetime.now())
                    # waiting for the mqtt response until
                    # robot_req_id is equal to robot_res_id
                    while robot_res_id != robot_req_id:
                        sleep(1)
                    print("Spot", spot_number, "end sleep time from robot forward step", datetime.datetime.now())
                    if robot_res_status == "success":
                        robot_res_id = ""
                        robot_res_status = ""

                    topic = f"Kitchen_1/In/Liquid_Dispenser/{dispenser}"
                    client.publish(topic=topic, payload=ing_dict, qos=2)
                    print("Spot", spot_number, "start sleep time from liquid", datetime.datetime.now())
                    # waiting for the mqtt response until
                    # req_id is not equal to ing_res_id
                    while ing_res_id != ing_req_id:
                        sleep(1)
                    print("Spot", spot_number, "end sleep time from liquid", datetime.datetime.now())
                    # if ing_res_status is equal to success
                    # reset ing id, status and robot status
                    if ing_res_status == "success":
                        ing_res_id = ""
                        ing_res_status = ""

                    # generate random hex robot req id
                    robot_req_id = secrets.token_hex(5)
                    back_step_dict = json.dumps({
                        "Req_Id": robot_req_id,
                        "AxisX": 0,
                        "SpeedX": 0,
                        "AxisY": 0,
                        "SpeedY": 0,
                        "ControlParam": 2
                    })
                    client.publish("Kitchen_1/In/Robot", back_step_dict, 2)
                    print("Spot", spot_number, "start sleep time from robot backward step", datetime.datetime.now())
                    # waiting for the mqtt response until
                    # robot_req_id is equal to robot_res_id
                    while robot_res_id != robot_req_id:
                        sleep(1)
                    print("Spot", spot_number, "end sleep time from robot backward step", datetime.datetime.now())
                    if robot_res_status == "success":
                        robot_res_id = ""
                        robot_res_status = ""

                    robot_status = "idle"
                else:
                    robot_status = "busy"

                    # generate random hex for robot req id
                    robot_req_id = secrets.token_hex(5)
                    forw_step_dict = json.dumps({
                        "Req_Id": robot_req_id,
                        "AxisX": 0,
                        "SpeedX": 0,
                        "AxisY": 0,
                        "SpeedY": 0,
                        "ControlParam": 2
                    })
                    client.publish("Kitchen_1/In/Robot", forw_step_dict, 2)
                    print("Spot", spot_number, "start sleep time from robot forward step", datetime.datetime.now())
                    # waiting for the mqtt response until
                    # robot_req_id is equal to robot_res_id
                    while robot_res_id != robot_req_id:
                        sleep(1)
                    print("Spot", spot_number, "end sleep time from robot forward step", datetime.datetime.now())
                    if robot_res_status == "success":
                        robot_res_id = ""
                        robot_res_status = ""

                    topic = f"Kitchen_1/In/Normal_Dispenser/{dispenser}"
                    client.publish(topic=topic, payload=ing_dict, qos=2)
                    print("Spot", spot_number, "start sleep time from general", datetime.datetime.now())
                    # waiting for the mqtt response until
                    # ing_req_id is equal to ing_res_id
                    while ing_res_id != ing_req_id:
                        sleep(1)
                    print("Spot", spot_number, "end sleep time from general", datetime.datetime.now())
                    # if ing_res_status is equal to success
                    # reset ing id, status and robot status
                    if ing_res_status == "success":
                        ing_res_id = ""
                        ing_res_status = ""

                    # generate random hex robot req id
                    robot_req_id = secrets.token_hex(5)
                    back_step_dict = json.dumps({
                        "Req_Id": robot_req_id,
                        "AxisX": 0,
                        "SpeedX": 0,
                        "AxisY": 0,
                        "SpeedY": 0,
                        "ControlParam": 2
                    })
                    client.publish("Kitchen_1/In/Robot", back_step_dict, 2)
                    print("Spot", spot_number, "start sleep time from robot backward step", datetime.datetime.now())
                    # waiting for the mqtt response until
                    # robot_req_id is equal to robot_res_id
                    while robot_res_id != robot_req_id:
                        sleep(1)
                    print("Spot", spot_number, "end sleep time from robot backward step", datetime.datetime.now())
                    if robot_res_status == "success":
                        robot_res_id = ""
                        robot_res_status = ""

                    robot_status = "idle"
        else:
            global spot_res_id, spot_res_status
            # generate random hex for spot req id
            spot_req_id = secrets.token_hex(5)
            # restructure spot data
            target_data = json.dumps({
                "Req_Id": spot_req_id,
                "Temperature": step["temperature"],
                "Speed": step["speed"],
                "Duration": step["duration"]
            })
            topic = f"Kitchen_1/In/Cooking_Station/{spot_number}"
            client.publish(topic=topic, payload=target_data, qos=2)
            print("Spot", spot_number, "start sleep time from action.", datetime.datetime.now())
            # waiting for the mqtt response until
            # req_id is not equal to spot_req_id
            while spot_res_id != spot_req_id:
                sleep(1)
            print("Spot", spot_number, "end sleep time from action.", datetime.datetime.now())
            # if  response  status  is success
            # reset the spot res id and status
            if spot_res_status == "success":
                spot_res_id = ""
                spot_res_status = ""

    # write code for handling package


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
