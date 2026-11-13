import re
from flask import Flask, request, jsonify
import requests
import threading
import time
import json
import time
import rclpy
from rclpy.node import Node
import numpy as np
import cv2
import base64
# from sensor_msgs.msg import Image
# from cv_bridge import CvBridge
from rclpy.executors import MultiThreadedExecutor
from planner_extractor import command_line, planner_extractor
# from arm2_excecutor import Arm2Controller

app = Flask(__name__)

# url_AI_server= "https://gai.hucenrotia.ngrok.dev/"
url_AI_server= "http://127.0.0.12:8000/" #local machine
url_LLM_and_GNN = url_AI_server+"LLM_GNN" #Hucenrotia_LLM_and planner_api
url_GNN = url_AI_server+"GNN_only" #Hucenrotia_planner_api
url_update_graph = "http://localhost:6000/update_graph"

url_laptop_server = "https://deea338415d1.ngrok-free.app/"
url_laptop_server_command = str(url_laptop_server)+"arm1_command"
url_laptop_server_status = str(url_laptop_server)+"arm1_status"
url_laptop_server_back = str(url_laptop_server)+"arm1_command_back"

global node, link
node, link = [], []
global robots, last_action_node_id_on_each_robot, prev_robot_active, link_id
robots, last_action_node_id_on_each_robot, prev_robot_active, link_id= None, None, "-", 0
global motion_end, GNN_terminated
motion_end, GNN_terminated= True, True
global robot_execeute, command_execeute, position_execute, robot_execeute1, command_execeute1, position_execute1, command_change
robot_execeute, command_execeute, position_execute, robot_execeute1, command_execeute1, position_execute1 = "", "", "", "", "", ""
command_change = True

# Lock = threading.Lock()
# latest_image_frame = None  

# Function for sending the data to the AI server (LLM+Planner)
def send_data_to_url(url,data):
    try:
        response = requests.post(url, json=data)
        print(f"Data sent:\n{url}\n{response.status_code}\nResponse: {response.text}")
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error sending data: {e}")
        return (f"Error sending data: {e}")

# Function for sending the data to the HMI
def send_data_to_electron(
    url,
    data,
    *,
    timeout=5.0,
    retries=3,
    backoff=1.5
):
    """
    POST 'data' to Electron/HMI.

    Accepts:
      - dict/list -> sent via requests.post(json=...)
      - Flask Response (e.g., from jsonify) -> bytes body sent with Content-Type: application/json
      - str/bytes -> sent as raw body (sets JSON content-type if it looks like JSON)

    Retries with exponential backoff on network errors or 5xx.
    Returns (status_code, text) on success; raises on final failure.
    """

    def _do_post(payload, headers=None, as_json=False):
        if as_json:
            return requests.post(url, json=payload, timeout=timeout)
        else:
            return requests.post(url, data=payload, headers=headers or {}, timeout=timeout)

    # Prepare payload & headers depending on type
    headers = None
    as_json = False
    payload = None

    # Flask Response (jsonify(...) result)
    if hasattr(data, "get_data") and callable(getattr(data, "get_data", None)):
        # Treat as Flask Response
        payload = data.get_data()  # bytes
        headers = {"Content-Type": "application/json"}
        as_json = False

    # JSON-serializable dict/list
    elif isinstance(data, (dict, list)):
        payload = data
        as_json = True

    # Raw str/bytes
    elif isinstance(data, (str, bytes)):
        if isinstance(data, str):
            payload = data.encode("utf-8")
        else:
            payload = data
        # Try to detect if it's JSON to set header
        try:
            json.loads(payload.decode("utf-8"))
            headers = {"Content-Type": "application/json"}
        except Exception:
            headers = {"Content-Type": "text/plain"}
        as_json = False

    else:
        # Last resort: try to JSON-serialize arbitrary objects
        try:
            payload = json.loads(json.dumps(data, default=str))
            as_json = True
        except Exception as e:
            raise TypeError(f"send_data_to_electron: unsupported data type {type(data)}") from e

    # Retry loop
    delay = 0.5
    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            resp = _do_post(payload, headers=headers, as_json=as_json)
            # Retry on server errors
            if 200 <= resp.status_code < 500:
                # success or client error (don’t retry client errors)
                print(f"[electron] POST {url} -> {resp.status_code}")
                return resp.status_code, resp.text
            else:
                print(f"[electron] attempt {attempt}: server {resp.status_code}, will retry...")
                last_exc = RuntimeError(f"Server returned {resp.status_code}: {resp.text[:200]}")
        except requests.exceptions.RequestException as e:
            print(f"[electron] attempt {attempt}: network error {e}, will retry...")
            last_exc = e

        if attempt < retries:
            time.sleep(delay)
            delay *= backoff

    # Exhausted retries
    raise last_exc if last_exc else RuntimeError("Unknown error posting to Electron")

@app.route('/robot_task_status', methods=['GET'])
def robot_task_status_handler():
    """
    Returns the current status of all robots.
    """
    return jsonify(robot_task_status)

@app.route('/user_prompt_to_LLM_GNN', methods=['POST'])
def user_prompt_to_LLM_GNN_handler():
    # global robot_execeute1, command_execeute1, position_execute1
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Invalid data format'}), 400
        print(f"Received message: {data['message']}")

        response = send_data_to_url(url_LLM_and_GNN,data)
        
        response_json= json.loads(response)
        data_= json.loads(response_json['data'])

        ### Extract commands
        plan_str_output=""
        for i in range(len(data_['steps'])):
            step = get_step_by_id(data_['steps'], i+1)
            if step:
                plan_str_output += step_to_str(step)
            else:
                print("Step not found.")

        # steps_str = planner_extractor.extract_command_lines(plan_str_output)
        global node, link
        node, link = planner_extractor.AI_plans_to_graph_plans(plan_str_output)
        print(node)
        data_for_frontend = {'LLM_response': data_['response'],
            'linkDataArray': link,
            'nodeDataArray': node
            }

        return jsonify({'results_from_AI':data_for_frontend,'status': 'success'}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'An error occurred LLM'}), 500

def listen_from_server():
    global robot_execeute, command_execeute, position_execute, command_change
    global motion_end, GNN_terminated
    with app.app_context():
        while True:
            if motion_end == True and GNN_terminated==False:
                data = {}
                # print('data sent[GNN]:\n', data)
                response = send_data_to_url(url_GNN,data)
                motion_end=False

                response_json= json.loads(response)
                # print(f"data_recieved: {response_json['data']}")
                
                robot="arm1"
                if response_json['data']['target_action']=="lock":
                    robot="arm2"

                robot_execeute=robot

                command_execeute=response_json['data']['target_action']
                position_execute=response_json['data']['target_terminal']
                command_change = True
                print("Robot Execute, command execute, and position")
                print(robot_execeute, command_execeute, position_execute)
                
                gnn_str_output= str(response_json['data']['target_action'])+" "+str(robot)+" "+str(response_json['data']['target_wire'])+" "+str(response_json['data']['target_terminal'])

                # print('UI data hunt [GNN str]:\n',gnn_str_output)

                global node, link, robots, last_action_node_id_on_each_robot, prev_robot_active, link_id
                node, link, robots, last_action_node_id_on_each_robot,prev_robot_active,link_id  = planner_extractor.AI_plan_to_graph_plan(node, link, gnn_str_output,robots, last_action_node_id_on_each_robot, prev_robot_active, link_id)

                data_for_frontend = {
                    'linkDataArray': link,
                    'nodeDataArray': node
                    }
                # with Lock:
                GNN_terminated = response_json['data']['terminate'] 

                post_data=jsonify({'results_from_AI':data_for_frontend,'status': 'success'})
                send_data_to_electron(url_update_graph, post_data)


def execute():
    global robot_execeute, command_execeute, motion_end, position_execute, robot_execeute1, command_execeute1, position_execute1, command_change

    print("robot execute: " + robot_execeute)
    print("command execute: " + command_execeute)

    
        # robot_execeute1 = "arm1" 
        # command_execeute1 = response_json['data']['target_action']
        # position_execute1 = response_json['data']['target_action']

    arm1_command_status=False
    while True:
        # print("Waiting for the robot and command")
        # print('Check::: ',robot_execeute, arm1_command_status)
        time.sleep(2)
        if robot_execeute == "arm1" and arm1_command_status==False and command_change:
            # data = {'action': [command_execeute1, command_execeute], 'position': [position_execute1, position_execute]}
            data = {'action': [command_execeute1, command_execeute], 'position': [position_execute1, position_execute]}
            print('Execute data:\n', data)
            reply = send_data_to_url(url_laptop_server_command,data)
            # time.sleep(10)
            print("Waiting for Arm1 tasks to complete...")
            arm1_command_status=True
            while True:
                arm1_status_response = requests.get(url_laptop_server_status)
                if arm1_status_response.status_code == 200:
                    arm1_status = arm1_status_response.json()
                    print("\narm1_status\n")
                    print(arm1_status["status"])
                    if arm1_status["status"] == "completed":
                        print("Arm1 tasks completed.")
                        arm1_command_status=False
                        command_change = False
                        break
                    elif arm1_status["status"] == "error":
                        print("Error in Arm1 tasks. Aborting Arm2 execution.")
                        return
                time.sleep(2)
            motion_end=True

        elif robot_execeute == "arm2":
            s0 = time.time()
            print(f"start_screw_time = s{0}")
            if command_execeute == "lock":
                s1 = time.time()
                print(f"time from start screw to inside conditional: {s1-s0}")
                # Arm2Controller.screwing(1, s1)
                # print("But did we arrive here?")
                # s = time.time()
                # print(f"Time from s0 to s1: {s1-s0}")
                # time.sleep(5)
                # motion_end=True
                # arm1_command_status=False
                # command_change = False
                # s = time.time()
                print(f"Time from s1 to s2: {s1-s2}")
                print(f"Total screwing time: {s2-s0}")

def get_step_by_id(steps, step_id):
    for step in steps:
        if step['id'] == step_id:
            return step
    return None

def step_to_str(step):
    step_str= "\\n("+str(step['action'])+" "+str(step['arm'])+" "+str(step['object'])+" "+str("-")+" )"
    return step_str

if __name__ == "__main__":
    rclpy.init()
    # image_listener = ImageListener()
    # executor = MultiThreadedExecutor()
    # executor.add_node(image_listener)

    # def spin_executor():
    #     executor.spin()

    # threading.Thread(target=spin_executor, daemon=True).start()
    # threading.Thread(target=execute, daemon=True).start()
    # threading.Thread(target=listen_from_server, daemon=True).start()

    app.run(host='127.0.0.2', port=8000, debug=True)
