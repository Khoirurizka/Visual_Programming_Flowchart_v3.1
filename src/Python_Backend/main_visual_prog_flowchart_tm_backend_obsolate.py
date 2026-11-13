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

from arm1_skills import ARM1_Skills # Gripper
from arm2_skills import ARM2_Skills # Screwdriver
import threading
import requests
import cv2
import base64
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from rclpy.executors import MultiThreadedExecutor

app = Flask(__name__)

#url_LLM_and_GNN = "http://127.0.0.1:9000/AI_reciever_prompt_image" #Dummy LLM VLM API
url_LLM_and_GNN = "https://gai.hucenrotia.ngrok.dev/LLM_GNN" #Hucenrotia_LLM_server
url_laptop_server = "https://6c03-140-113-149-84.ngrok-free.app/arm1_command"
url_laptop_server_status = "https://6c03-140-113-149-84.ngrok-free.app/arm1_status"
url_laptop_server_back = "https://6c03-140-113-149-84.ngrok-free.app/arm1_command_back"


LLM_message="" #"hello I am LLM tester"
output_command_str ="" # "\n(find red_wire)\n(pickup arm1 red_wire table)\n(insert arm1 red_wire power_supply_5)\n(putdown arm1 red_wire power_supply_5)\n(lock arm2 red_wire power_supply_5)"

robots_list=["arm1","arm2"]
actions_list=["pickup","lock", "insert", "putdown","find"]
object_item_list=["red_wire","blue_wire", "yellow_wire", "white_wire","green_wire"]
location_list=["table","power_supply_5"]

extracted_command=[]


latest_image_frame = None  


class ImageListener(Node):
    def __init__(self):
        super().__init__('image_listener')
        self.image_frame = None
        self.bridge = CvBridge()
        self.subscription = self.create_subscription(
            Image,
            '/techman_image',
            self.image_callback,
            10
        )

    def image_callback(self, msg):
        global latest_image_frame
        self.image_frame = self.bridge.imgmsg_to_cv2(msg)
        latest_image_frame = self.image_frame

        # Save to a JPG file
        filename = "captured_frame_now.jpg"
        cv2.imwrite(filename, self.image_frame)
        print(f"Image saved to {filename}")


class command_line:
    def __init__(self, command_keypharse):
        self.action="-"
        self.robot="-"
        self.object_item="-"
        self.location="-"

        for ck in command_keypharse:
            for al in actions_list:
                if ck==al:
                    self.action = ck
                    break
            for rl in robots_list:
                if ck==rl:
                    self.robot = ck
                    break

            for oi in object_item_list:
                if ck==oi:
                    self.object_item = ck
                    break
            for ll in location_list:
                if ck==ll:
                    self.location = ck
                    break

    def __str__(self):
        return f"{self.robot}->{self.action} obj:{self.object_item} on:{self.location})"

def extract_command_lines(text):
    lines = re.findall(r'\((.*?)\)', text)

    return lines

def extract_basic_keyPharse(text):
    command_keypharse = text.strip('()').split()

    return command_line(command_keypharse)

def convert_single_pair_plan_to_jsonGraph(extracted_command):
    node = []
    link = []
    robot={'-':{'start':0,'end':0}} #to prevent null value
    last_key_id_on_each_robot={'-':-1}
    has_robot=True

    ### Initialize robot start-end node
    for i in range(len(extracted_command)):
        has_robot=True
        for rb in robot:
            if extracted_command[i].robot == rb:
                has_robot=False

        if has_robot:
            start_robot_node=-(2*len(robot)-1)
            end_robot_node=-(2*len(robot))
            node_entry = {
            "key": start_robot_node,
            "command": "Start_"+str(extracted_command[i].robot),
            "color": "lightblue",
            "category": "StartEnd"
            }
            node.append(node_entry)
            node_entry = {
            "key": end_robot_node,
            "command": "End_"+str(extracted_command[i].robot),
            "color": "lightblue",
            "category": "StartEnd"
            }
            node.append(node_entry)
            robot.update({str(extracted_command[i].robot):{'start':start_robot_node,'end':end_robot_node}})
            last_key_id_on_each_robot.update({str(extracted_command[i].robot):-1})
    give_key_id=0
    prev_robot_active="-"
    # print(last_key_id_on_each_robot)
   
    for i in range(len(extracted_command)):
        # Draw node
        if (i==0):
            prev_robot_active=list(robot.keys())[1]
        elif(i>0 and extracted_command[i].robot!=prev_robot_active):
            ### add wait node for switch robot
            node_entry = {
            "key": give_key_id,
            "command": "wait another",
            "color": "white",
            "category": "Process"
            }
            node.append(node_entry)
            # add link from start robot node to node
            if last_key_id_on_each_robot[extracted_command[i].robot]<0:
                last_key_id_on_each_robot[extracted_command[i].robot]=robot[extracted_command[i].robot]["start"]

                link_entry = {
                    "key": str(-give_key_id-1)+"s", 
                    "from": last_key_id_on_each_robot[extracted_command[i].robot], 
                    "to": give_key_id
                }
                
                last_key_id_on_each_robot[extracted_command[i].robot]=give_key_id
                link.append(link_entry)

            # add link from previous process node to node
            link_entry = {
                    "key": -give_key_id-1, 
                    "from": last_key_id_on_each_robot[extracted_command[i-1].robot], 
                    "to": give_key_id
                }
                
            last_key_id_on_each_robot[extracted_command[i].robot]=give_key_id
            link.append(link_entry)
            give_key_id=give_key_id+1

            prev_robot_active=extracted_command[i].robot

        ### add main node
        node_entry = {
            "key": give_key_id,
            "command": extracted_command[i].action,
            "color": "white",
            "category": "Process"
        }
        node.append(node_entry)
        

        ### Draw link main process
        # draw link on initial
        if (i==0):
            link_entry = {
                "key": str(-give_key_id-1)+"s", 
                "from": robot[list(robot.keys())[1]]["start"], 
                "to": give_key_id
            }
            last_key_id_on_each_robot[extracted_command[1].robot]=give_key_id
            link.append(link_entry)
        # draw link on each step
        else:
            link_entry = {
                "key": -give_key_id-1, 
                "from": last_key_id_on_each_robot[extracted_command[i].robot], 
                "to": give_key_id
            }
            last_key_id_on_each_robot[extracted_command[i].robot]=give_key_id
            link.append(link_entry)

        give_key_id=give_key_id+1
        ### Draw terminator link, node each robot to the end
    for i in range(1,len(last_key_id_on_each_robot)):
        link_entry = {
            "key": str(-give_key_id-1)+"e", 
            "from": last_key_id_on_each_robot[list(last_key_id_on_each_robot.keys())[i]], 
            "to": robot[list(last_key_id_on_each_robot.keys())[i]]["end"]
        }
        link.append(link_entry)

        give_key_id=give_key_id+1


    return node,link

# Function to send data automatically
def send_data_to_url(url,data):
    try:
        response = requests.post(url, json=data)
        print(f"Data sent: {response.status_code}, Response: {response.text}")
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error sending data: {e}")
        return (f"Error sending data: {e}")

##---CONTROLLER ARM 2---##
def controller_arm2(subtasks, coords):
    # arm1 = ARM1_Skills()
    arm2 = ARM2_Skills()
    
    for t, task in enumerate(subtasks):
        x, y, z, rx, ry, rz = coords[t]
        # if task == 'pickup':
        #     arm1.move_to(x, y , z,  173.33, 0.16, 93.13, velocity=1.0) # Move to grasping position
        #     arm1.pick_up() # Grasp and then lift off of buffer??

        # elif task == 'putdown':
        #     arm1.move_to(x, y, z, rx, ry, rz, velocity=0.5) # Move to putting position
        #     arm1.put_down()

        # elif task == 'insert':
        #     arm1.move_to(x, y-0.1, z, 173.33, 0.16, 93.13, velocity=1.0)
        #     arm1.insert(x, y, z, 166.37, 2.67, 177.51, velocity=0.5)
        #     arm1.arm1_home()

        # if task == 'find':
        #     arm2.get_logger().info("Executing 'find' task.")
        #     if arm2.find():
        #         arm2.get_logger().info("Image successfully processed in 'find' task.")
        #     else:
        #         arm2.get_logger().error("Failed to process image in 'find' task.")
        #     scalled_frame = cv2.resize(arm2.image_frame, (480, 320))
        #     # Encode the frame into bytes (JPEG format)
        #     _, img_encoded = cv2.imencode('.jpg', scalled_frame)

        #     # Convert to bytes for sending
        #     base64_image = base64.b64encode(img_encoded)
        #     response = requests.post(url_update_screw_driver_capture, json={"image": base64_image})
        #     print(f"Server response: {response.text}")

        if task == 'lock':
            tolerance = 0.01
            arm2.move_to(x, y, 242.23, rx, ry, rz, velocity=4.5) # Initial move to approach (x,y) position
            # arm2.move_to(x, y, -10.05, 178.63, 0.27, -0.53, velocity=4.5) # Approach z position (screwhead location) 
            arm2.move_to(x, y, z, rx, ry, rz, velocity=1.0) # Reach target position   

            arm2.get_logger().info("Waiting for tool_pose to reach target position...")
            while rclpy.ok():
                rclpy.spin_once(arm2)  # Process callback queue
                # Lock the screw 
                if arm2.tool_pose and arm2.is_pose_ready(arm2.tool_pose, [x/1000, y/1000, z/1000], tolerance):
                    print("here")
                    arm2.get_logger().info("Tool pose reached target position. Executing lock_screw.")
                    if arm2.call_lock_screw():  # Run the screwdriver task and wait for it to complete
                        time.sleep(3)
                        arm2.move_to(x, y, z+100, rx, ry, rz, velocity=1.0 )
                        arm2.get_logger().info("Screwdriver task done. Moving to the next position.")
                        arm2.arm2_home()
                    else:
                        arm2.get_logger().error("Screwdriver task failed. Halting further operations.")
                    break
    # arm1.destroy_node()
    arm2.destroy_node()

def AI_plan_data_to_graph_plan(data_json):
    extracted_command=[]
    node = []
    link=[]
    output_command_str=""
    try:


        output_command_str = data['output_command']
        
        print(f"Received output_command: {output_command_str}")
        parsed_tasks = []
        command_lines = output_command_str.strip().splitlines()

        parsed_commands = []

        for command in command_lines:
            command = command.strip()  # Remove leading/trailing spaces
            if not command:
                continue  # Skip empty lines

            print(f"Processing command: {command}")

            match = re.match(r"\((\w+)(?:\s+(\w+))?(?:\s+(\w+))?(?:\s+(\w+))?\)", command)
            if match:
                action = match.group(1)
                robot_id = match.group(2)
                obj = match.group(3)
                position = match.group(4)

                # Special case: "find" action
                if action == "find":
                    robot_id = "arm2"
                    obj = match.group(2)  # Object is the word after "find"
                    position = "table"  # Position is always "table"

                # Extract terminal number if position contains 'power_supply_X'
                terminal = None
                if position and "power_supply" in position:
                    terminal_match = re.search(r"power_supply_(\d+)", position)
                    if terminal_match:
                        terminal = terminal_match.group(1)

                parsed_commands.append({
                    "action": action,
                    "robot_id": robot_id,
                    "object": obj,
                    "position": position,
                    "terminal": terminal
                })
            else:
                print(f"No match found for: {command}")

        # Output the parsed commands
        print("Parsed commands:", parsed_commands)


        for command in output_command_str:
            # extract action, robot_id, object, position
            match = re.match(r"\((\w+)(?:\s+(\w+))?\s+(\w+)(?:\s+(\w+))?\)", command)
            if match:
                action = match.group(1)
                robot_id = match.group(2)
                obj = match.group(3)
                position = match.group(4)
                
                # extract terminal number if position contains 'power_supply_X'
                terminal = None
                if position and "power_supply" in position:
                    terminal_match = re.search(r"power_supply_(\d+)", position)
                    if terminal_match:
                        terminal = terminal_match.group(1)
                
                parsed_tasks.append({
                    "action": action,
                    "robot_id": robot_id,
                    "object": obj,
                    "position": position,
                    "terminal": terminal
                })

        print(parsed_tasks)
        # for multiple commands
        # command_lines=extract_command_lines(output_command_str)
        # for command_line in command_lines:
        #     extacted_command=extract_basic_keyPharse(command_line)
        #     extracted_command.append(extacted_command)
        
        if data['vlm_frame'] is not None:
            img_bytes = base64.b64decode(data['vlm_frame'])

            # Convert bytes to 1D uint8 array
            nparr = np.frombuffer(img_bytes, np.uint8)

            # Decode image (cv2.IMREAD_COLOR can be changed if needed)
            img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            scalled_frame = cv2.resize(img_np, (480, 320))
            # Encode the frame into bytes (JPEG format)
            _, img_encoded = cv2.imencode('.jpg', scalled_frame)

            # Convert to bytes for sending
            base64_image = base64.b64encode(img_encoded).decode('utf-8')  # <-- decode here

            data['vlm_frame'] = base64_image
        else:
            print("Warning: image_frame is None!")
            data['vlm_frame'] = ""

        node,link=convert_single_pair_plan_to_jsonGraph(extracted_command)
        post_data = {'LLM_response': data['LLM_response'],
                     'vlm_frame':data['vlm_frame'],
                     'linkDataArray': link,
                     'nodeDataArray': node
                     }

        action_1 = []  
        position_1 = []

        action_2 = []
        position_2 = []

        for command in parsed_commands:
            action = command["action"]
            robot_id = command["robot_id"]
            obj = command["object"]
            position = command["position"]

            if robot_id == "arm1":
                print("Processing arm1:", action, position)
                action_1.append(action)
                position_1.append(position)

            if robot_id == "arm2":
                print("Processing arm2:", action, position)
                action_2.append(action)
                position_2.append(position)
        
        data = {'action': action_1, 'position': position_1}
        data2 = {'action': action_2, 'position': position_2}
        print("Data to send:", data)
        print("Run ARM2:", data2)

        
        send_data_to_url(url_laptop_server, data)
       
        threading.Thread(
            target=wait_for_arm1_and_execute_arm2,
            args=(data2["action"], data2["position"]),
            daemon=True
        ).start()

        return post_data
    except Exception as e:
        print(f"Error: {e}")
        return 'Error: An error occurred'

def wait_for_arm1_and_execute_arm2(action_2, position_2):
    """
    Wait for Arm1 tasks to complete and then execute Arm2 tasks.
    """
    try:
        print("Waiting for Arm1 tasks to complete...")
        while True:
            arm1_status_response = requests.get(url_laptop_server_status)
            if arm1_status_response.status_code == 200:
                arm1_status = arm1_status_response.json()
                if arm1_status["status"] == "completed":
                    print("Arm1 tasks completed.")
                    break
                elif arm1_status["status"] == "error":
                    print("Error in Arm1 tasks. Aborting Arm2 execution.")
                    return
            time.sleep(2)

        # Execute Arm2 tasks
        print("Executing Arm2 tasks...")

        result = execute_arm2({"action": action_2, "position": position_2})

        if result:
            print("Arm2 tasks completed.")
            data = {'action': ['home'], 'position': ['table']}
        else:
            print("Arm2 tasks failed.")
            data = {'action': ['fail'], 'position': ['table']}

        time.sleep(5)
        send_data_to_url(url_laptop_server_back, data)


    except Exception as e:
        print(f"Error while waiting for Arm1 or executing Arm2 tasks: {e}")


@app.route('/robot_task_status', methods=['GET'])
def robot_task_status_endpoint():
    """
    Returns the current status of all robots.
    """
    return jsonify(robot_task_status)

def execute_arm2(data):
    """
    Executes Arm2 tasks based on the received data.
    """
    success = True
    try:
        actions = data["action"]
        positions = data["position"]
        print("Check flow")

        for action, position in zip(actions, positions):
            if action == "lock":
                print("ARM2 move")
                controller_arm2(subtasks=["lock"], coords=[[283.15, -370.72, 242.23], [-179.01, 0.3, 44.17]])
            else:
                print(f"Unsupported task for Arm2: {action}")

    except Exception as e:
        print(f"Error while executing Arm2 tasks: {e}")
        success = False
    return success


@app.route('/')
def home():
    return jsonify({"status": "Flask app running", "message": "Automatic data sending to Electron enabled"})

@app.route('/user_prompt_to_LLM_GNN', methods=['POST'])
def user_prompt_to_LLM_handler():
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Invalid data format'}), 400
        
        message = data['message']
        print(f"Received message: {message}")

        # frame = latest_image_frame
        # if frame is not None:
        #     _, buffer = cv2.imencode('.jpg', frame)
        #     base64_image = base64.b64encode(buffer).decode('utf-8')
        #     data['frame_screw_driver'] = base64_image
        # else:
        #     print("Warning: image_frame is None!")
        #     data['frame_screw_driver'] = ""

        response =  send_data_to_url(url_LLM_and_GNN,data)
        
        response_json= json.loads(response)
        print(f"data_recieved: {response_json['data']}")
        # 'output_command': "\n(find blue_wire)\n(pickup arm1 blue_wire table)\n(insert arm1 blue_wire power_supply_5)\n(putdown arm1 blue_wire power_supply_5)\n(lock arm2 blue_wire power_supply_5)",

        results_from_AI= AI_plan_data_to_graph_plan(response_json['data'])
        print(results_from_AI)
        data_for_frontend = {'LLM_response': response_json['data']['LLM_response'],
            # 'vlm_frame':data['vlm_frame'],
            # 'linkDataArray': link,
            # 'nodeDataArray': node
            }
        print(f"results_from_AI: {data_for_frontend}")
        # return jsonify({'results_from_AI':results_from_AI,'status': 'success'}), 200
        return jsonify({'results_from_AI':data_for_frontend,'status': 'success'}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'An error occurred LLM'}), 500


if __name__ == "__main__":
    rclpy.init()
    image_listener = ImageListener()
    executor = MultiThreadedExecutor()
    executor.add_node(image_listener)

    def spin_executor():
        executor.spin()

    threading.Thread(target=spin_executor, daemon=True).start()

    app.run(host='127.0.0.2', port=8000, debug=True)
