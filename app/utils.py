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


def convert_str_list(message):
    response_list = []
    # split the message based on comma
    split_on_comma = message.split(",")
    for item in split_on_comma:
        # split the item based on colon
        split_on_colon = item.split(":")
        for value in split_on_colon:
            # remove whitespace from text
            rmv_space = value.strip()
            # add item to the response_list
            response_list.append(rmv_space)
    return response_list


def convert_list_to_dict(data):
    response_dict = {}
    for i in range(0, len(data), 2):
        response_dict[data[i]] = data[i + 1]
    return response_dict


def on_connect(client, userdata, flags, return_code):
    if return_code != 0:
        print(f"Could not connect with broker {return_code}")

    client.subscribe("Out/Robot", 2)
    client.subscribe("Out/Spice", 2)
    client.subscribe("Out/Add_Ons", 2)
    client.subscribe("Out/Solid_Dispensers", 2)
    client.subscribe("Out/Cooking_Station/+", 2)


def on_liquid_msg(client, userdata, msg):
    global ing_res_id, ing_res_status
    # data = json.loads(msg.payload.decode("utf-8"))
    message = msg.payload.decode("utf-8")
    res_list = convert_str_list(message)
    format_data = convert_list_to_dict(res_list)
    ing_res_id = format_data["Req_Id"]
    ing_res_status = format_data["Status"]


def on_spice_msg(client, userdata, msg):
    global ing_res_id, ing_res_status
    message = msg.payload.decode("utf-8")
    res_list = convert_str_list(message)
    format_data = convert_list_to_dict(res_list)
    ing_res_id = format_data["Req_Id"]
    ing_res_status = format_data["Status"]


def on_normal_msg(client, userdata, msg):
    global ing_res_id, ing_res_status
    message = msg.payload.decode("utf-8")
    res_list = convert_str_list(message)
    format_data = convert_list_to_dict(res_list)
    ing_res_id = format_data["Req_Id"]
    ing_res_status = format_data["Status"]


def on_spot_message(client, userdata, msg):
    global spot_res_id, spot_res_status
    message = msg.payload.decode("utf-8")
    res_list = convert_str_list(message)
    format_data = convert_list_to_dict(res_list)
    spot_res_id = format_data["Req_Id"]
    spot_res_status = format_data["Status"]


def on_robot_message(client, userdata, msg):
    global robot_res_id, robot_res_status
    message = msg.payload.decode("utf-8")
    res_list = convert_str_list(message)
    format_data = convert_list_to_dict(res_list)
    robot_res_id = format_data["Req_Id"]
    robot_res_status = format_data["Status"]


client = mqtt.Client(client_id, clean_session=False)

client.on_connect = on_connect

client.username_pw_set(username="admin", password="Shakes2018")
client.connect("188.80.94.190", 1883)

client.loop_start()

client.message_callback_add("Out/Robot", on_robot_message)
client.message_callback_add("Out/Spice", on_spice_msg)
client.message_callback_add("Out/Add_Ons", on_liquid_msg)
client.message_callback_add("Out/Solid_Dispensers", on_normal_msg)
client.message_callback_add("Out/Cooking_Station/+", on_spot_message)


def process_recipe(recipe):
    # extract spot id from recipe
    spot_number = recipe["spot"]
    # iterate steps one by one
    for step in recipe["steps"]:
        print(step)
        # check, does a step contain ingredient
        if not step["ingredients"] == []:
            global robot_status
            global ing_res_id, ing_res_status
            global robot_res_id, robot_res_status

            # iterate ingredients one by one
            for ingredient in step["ingredients"]:
                # wait for robot availability
                while robot_status == "busy":
                    sleep(1)

                # change robot state
                robot_status = "busy"

                # get random hex string for req id
                ing_req_id = secrets.token_hex(5)
                # get dispenser id from ingredient
                dispenser = ingredient["dispenser"]
                ingredient_msg = json.dumps({
                    "Req_Id": ing_req_id,
                    "Dispenser": dispenser,
                    "Grams": ingredient["volume"],
                })

                # first pickup the solid ingredient cup
                # get random hex string for request id
                robot_req_id = secrets.token_hex(5)
                pickup_cup_msg = json.dumps({
                    "Req_Id": robot_req_id,
                    "Id_Number": ingredient["pickup_cup"]["program_id"],
                    "AxisX": ingredient["pickup_cup"]["axis_x"],
                    "SpeedX": ingredient["pickup_cup"]["speed_x"],
                    "AxisY": ingredient["pickup_cup"]["axis_y"],
                    "SpeedY": ingredient["pickup_cup"]["speed_y"],
                    "ControlParam": ingredient["pickup_cup"]["control_param"],
                })

                # send data to the robot to pick up a solid cup
                client.publish("In/Robot", pickup_cup_msg, 2)
                print(spot_number, "start cup pickup", datetime.datetime.now())

                # waiting for the mqtt response until
                # robot_req_id is equal to robot_res_id
                while robot_res_id != robot_req_id:
                    sleep(1)
                print(spot_number, "end cup pickup", datetime.datetime.now())

                # if success, reset robot's id and status
                if robot_res_status == "success":
                    robot_res_id = ""
                    robot_res_status = ""

                # second drive picked up cup to dispenser
                # get random hex string for request id
                robot_req_id = secrets.token_hex(5)
                drive_to_dispenser_msg = json.dumps({
                    "Req_Id": robot_req_id,
                    "Id_Number": ingredient["drive_to_disp"]["program_id"],
                    "AxisX": ingredient["drive_to_disp"]["axis_x"],
                    "SpeedX": ingredient["drive_to_disp"]["speed_x"],
                    "AxisY": ingredient["drive_to_disp"]["axis_y"],
                    "SpeedY": ingredient["drive_to_disp"]["speed_y"],
                    "ControlParam": ingredient["drive_to_disp"]["control_param"],
                })

                # send data to the robot to drive the cup to dispenser
                client.publish("In/Robot", drive_to_dispenser_msg, 2)
                print(spot_number, "start drive cup", datetime.datetime.now())

                # waiting for the mqtt response until
                # robot_req_id is equal to robot_res_id
                while robot_res_id != robot_req_id:
                    sleep(1)
                print(spot_number, "end drive cup", datetime.datetime.now())

                # if success, reset robot's id and status
                if robot_res_status == "success":
                    robot_res_id = ""
                    robot_res_status = ""

                # third dispense ingredient to the picked up cap
                # send data to the robot to dispense ingredient to the cup
                if ingredient["cup"] == "spice":
                    client.publish("In/Spice", ingredient_msg, 2)
                elif ingredient["cup"] == "liquid":
                    client.publish("In/Add_Ons", ingredient_msg, 2)
                else:
                    client.publish("In/Solid_Dispensers", ingredient_msg, 2)

                print(spot_number, "start dispense ingredient", datetime.datetime.now())

                # waiting for the mqtt response until
                # req_id is not equal to ing_res_id
                while ing_res_id != ing_req_id:
                    sleep(1)
                print(spot_number, "end dispense ingredient", datetime.datetime.now())

                # if success, reset ing_res id and status
                if ing_res_status == "success":
                    ing_res_id = ""
                    ing_res_status = ""

                # fourth drive to home from dispenser
                # get random hex string for request id
                robot_req_id = secrets.token_hex(5)
                drive_to_home_msg = json.dumps({
                    "Req_Id": robot_req_id,
                    "Id_Number": ingredient["drive_to_home"]["program_id"],
                    "AxisX": ingredient["drive_to_home"]["axis_x"],
                    "SpeedX": ingredient["drive_to_home"]["speed_x"],
                    "AxisY": ingredient["drive_to_home"]["axis_y"],
                    "SpeedY": ingredient["drive_to_home"]["speed_y"],
                    "ControlParam": ingredient["drive_to_home"]["control_param"],
                })

                # send data to the robot to drive the cup to home
                client.publish("In/Robot", drive_to_home_msg, 2)
                print(spot_number, "start back to home", datetime.datetime.now())

                # waiting for the mqtt response until
                # robot_req_id is equal to robot_res_id
                while robot_res_id != robot_req_id:
                    sleep(1)
                print(spot_number, "end back to home", datetime.datetime.now())

                # if success, reset robot's id and status
                if robot_res_status == "success":
                    robot_res_id = ""
                    robot_res_status = ""

                # fifth drive cup and pour on spot's pot
                # get random hex string for request id
                robot_req_id = secrets.token_hex(5)
                pour_ing_msg = json.dumps({
                    "Req_Id": robot_req_id,
                    "Id_Number": ingredient["drive_to_spot"]["program_id"],
                    "AxisX": ingredient["drive_to_spot"]["axis_x"],
                    "SpeedX": ingredient["drive_to_spot"]["speed_x"],
                    "AxisY": ingredient["drive_to_spot"]["axis_y"],
                    "SpeedY": ingredient["drive_to_spot"]["speed_y"],
                    "ControlParam": ingredient["drive_to_spot"]["control_param"],
                })

                # send data to the robot to pour ingredient
                client.publish("In/Robot", pour_ing_msg, 2)
                print(spot_number, "start pouring ingredient", datetime.datetime.now())

                # waiting for the mqtt response until
                # robot_req_id is equal to robot_res_id
                while robot_res_id != robot_req_id:
                    sleep(1)
                print(spot_number, "end pouring ingredient", datetime.datetime.now())

                # if success, reset robot's id and status
                if robot_res_status == "success":
                    robot_res_id = ""
                    robot_res_status = ""

                # sixth drop out the cup in init place
                # get random hex string for request id
                robot_req_id = secrets.token_hex(5)
                dropout_cup_msg = json.dumps({
                    "Req_Id": robot_req_id,
                    "Id_Number": ingredient["dropout_cup"]["program_id"],
                    "AxisX": ingredient["dropout_cup"]["axis_x"],
                    "SpeedX": ingredient["dropout_cup"]["speed_x"],
                    "AxisY": ingredient["dropout_cup"]["axis_y"],
                    "SpeedY": ingredient["dropout_cup"]["speed_y"],
                    "ControlParam": ingredient["dropout_cup"]["control_param"],
                })

                # send data to the robot to drop out the cup
                client.publish("In/Robot", dropout_cup_msg, 2)
                print(spot_number, "start dropping cup", datetime.datetime.now())

                # waiting for the mqtt response until
                # robot_req_id is equal to robot_res_id
                while robot_res_id != robot_req_id:
                    sleep(1)
                print(spot_number, "end dropping cup", datetime.datetime.now())

                # if success, reset robot's id and status
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
            topic = f"In/Cooking_Station/{spot_number}"
            client.publish(topic=topic, payload=target_data, qos=2)
            print(spot_number, "start from action.", datetime.datetime.now())
            # waiting for the mqtt response until
            # req_id is not equal to spot_req_id
            while spot_res_id != spot_req_id:
                sleep(1)
            print(spot_number, "end from action.", datetime.datetime.now())
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
