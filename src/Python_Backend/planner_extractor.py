import re
from flask import Flask, request, jsonify
import time
import json
import time
import numpy as np
import requests
import cv2
import base64
from cv_bridge import CvBridge

robots_list=["arm1","arm2"]
actions_list=["pick", "lock", "insert", "putdown","find", "pickup", "hold", "insert"]
object_item_list=["red_wire","blue_wire", "yellow_wire", "white_wire","green_wire","wave_generator", "circular_spline",
                  "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15"]
location_list=["table","terminal_0","terminal_1","terminal_2","terminal_3","terminal_4","terminal_5"
                ,"terminal_6","terminal_7","terminal_8","terminal_9","-"]

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
                    if str(ck)=="0":
                        ck="green_wire"
                    elif str(ck)=="1":
                        ck="black_wire"
                    elif str(ck)=="2":
                        ck="blue_wire"
                    elif str(ck)=="3":
                        ck="white_wire"  
                    elif str(ck)=="4":
                        ck="red_wire"    
                    self.object_item = ck
                    break
            for ll in location_list:
                if ck==ll:
                    self.location = ck
                    break

    def __str__(self):
        return f"{self.robot}->{self.action} obj:{self.object_item} on:{self.location})"

class planner_extractor():
    @staticmethod
    def color_allocator(robot):
        if robot=="arm1":
            color="white"
        elif robot=="arm2": 
            color="lightblue"
        else: 
            color=="yellow"
        return color

    ### Extract all command lines enclosed in parentheses from a text string.
    @staticmethod
    def extract_command_lines(text):
        """
        Example:
            Input:
                text = "\\n(find blue_wire)\\n(pickup arm1 blue_wire table)\\n(insert arm1 blue_wire power_supply_5)"

            Output:
                [
                    "find blue_wire",
                    "pickup arm1 blue_wire table",
                    "insert arm1 blue_wire power_supply_5"
                ]

        Note:
            - Uses regex r'\((.*?)\)' to capture content inside parentheses.
            - Returns a list of strings without the surrounding parentheses.
        """
        lines = re.findall(r'\((.*?)\)', text)
        return lines
    
    ### Extract the basic keyphrase tokens from a command string.
    @staticmethod
    def extract_basic_keyPharse(text):
        """
        Steps:
            1. Removes surrounding parentheses, if any.
            2. Splits the string into tokens (by whitespace).
            3. Passes the token list into `command_line()` for further processing.

        Example:
            Input:
                text = "(pickup arm1 blue_wire table)"
            After strip/split:
                ["pickup", "arm1", "blue_wire", "table"]
            Output (depends on `command_line` implementation):
                command_line(["pickup", "arm1", "blue_wire", "table"])
        """
        command_keypharse = text.strip('()').split()

        return command_line(command_keypharse)
    
    ### Covert single plan string into node and link to contruct a graph relationship
    @staticmethod
    def convert_plan_to_json_graph(node, link, incoming_commands, robots=None, last_action_node_id_on_each_robot=None,prev_robot_active=None, link_id=0):
        # Initialize dictionaries if not provided (first call)
        if robots is None:
            robots = {'-': {'start': -1, 'end': -1}}
        if last_action_node_id_on_each_robot is None:
            last_action_node_id_on_each_robot = {'-': -1}
        start_robot_node=""
        print(f"prev_robot_active={prev_robot_active}")

        # Helper function to check if a node exists by key
        def node_exists(node_list, key):
            return any(n["key"] == key for n in node_list)

        # Initialize robot start-end node on each robot
        for i in range(len(incoming_commands)):
            robot = str(incoming_commands[i].robot)
            has_robot = robot in robots

            if not has_robot:
                start_robot_node = "start_" + robot
                end_robot_node = "end_" + robot

                # Create start node if it doesn't exist
                if not node_exists(node, start_robot_node):
                    node_entry = {
                        "key": start_robot_node,
                        "command": "Start_" + robot,
                        "color": planner_extractor.color_allocator(robot) ,
                        "category": "StartEnd"
                    }
                    node.append(node_entry)

                # Create end node if it doesn't exist
                if not node_exists(node, end_robot_node):
                    node_entry = {
                        "key": end_robot_node,
                        "command": "End_" + robot,
                        "color": planner_extractor.color_allocator(robot) ,
                        "category": "StartEnd"
                    }
                    node.append(node_entry)

                # Update dictionary planner
                robots[robot] = {'start': start_robot_node, 'end': end_robot_node}
                last_action_node_id_on_each_robot[robot] = 0

                # Add link from start to first action node on each robot
                link_entry = {
                    "key": "start_link_" + robot,
                    "from": start_robot_node,
                    "to": "action_" + robot + "_" + str(last_action_node_id_on_each_robot[robot])
                }
                # Only append link if it doesn't already exist
                if not any(l["key"] == link_entry["key"] for l in link):
                    link.append(link_entry)

        # Add action or process or foto'switch node
        for i in range(len(incoming_commands)):
            robot = str(incoming_commands[i].robot)

            # Add switch or wait node and link
            # print(node_exists(node, start_robot_node))
            if robot != prev_robot_active and prev_robot_active != "-":
                # Add wait node for switch

                node_entry = {
                    "key": "action_" + robot + "_" + str(last_action_node_id_on_each_robot[robot]),
                    "command": "wait another",
                    "color": planner_extractor.color_allocator(robot),
                    "category": "Process"
                }
                node.append(node_entry)

                # Add switch or wait link
                link_entry = {
                    "key": "switch_link_" + str(link_id),
                    "from": "action_" + prev_robot_active + "_" + str(last_action_node_id_on_each_robot[prev_robot_active] - 1),
                    "to": "action_" + robot + "_" + str(last_action_node_id_on_each_robot[robot])
                }
                link.append(link_entry)
                last_action_node_id_on_each_robot[robot] += 1
                link_id += 1

            # Add action or process node
            node_entry = {
                "key": "action_" + robot + "_" + str(last_action_node_id_on_each_robot[robot]),
                "command": incoming_commands[i].action,
                "argument": "object: "+str(incoming_commands[i].object_item)+" "+"target: "+str(incoming_commands[i].location),
                "color": planner_extractor.color_allocator(robot),
                "category": "Process"
            }
            node.append(node_entry)
            prev_robot_active = robot
            print(f"prev_robot_active2={prev_robot_active}")

            # Add link to previous node
            if last_action_node_id_on_each_robot[robot] > 0:
                link_entry = {
                    "key": "link_" + str(link_id),
                    "from": "action_" + robot + "_" + str(last_action_node_id_on_each_robot[robot] - 1),
                    "to": "action_" + robot + "_" + str(last_action_node_id_on_each_robot[robot])
                }
                link.append(link_entry)
                link_id += 1

            last_action_node_id_on_each_robot[robot] += 1

        # Draw link to the end (termination state) on each robot
        for robot in list(last_action_node_id_on_each_robot.keys())[1:]:  # Skip '-'
            if last_action_node_id_on_each_robot[robot] > 0:  # Ensure there are actions
                link_entry = {
                    "key": "end_link_" + robot,
                    "from": "action_" + robot + "_" + str(last_action_node_id_on_each_robot[robot] - 1),
                    "to": robots[robot]["end"]
                }
                # Replace existing link if it exists, otherwise append
                existing_link_index = next((i for i, l in enumerate(link) if l["key"] == link_entry["key"]), -1)
                if existing_link_index != -1:
                    link[existing_link_index] = link_entry  # Replace existing link
                else:
                    link.append(link_entry)  # Append new link

        
        return node, link, robots, last_action_node_id_on_each_robot, prev_robot_active, link_id

    ### Covert multiple plans string into node and link to contruct a graph relationship
    @staticmethod
    def convert_plans_to_json_graph(node, link, incoming_commands):
        ################## Dictionary planner ##################
        robots={'-':{'start':-1,'end':-1}} #Initalize dictionary
        last_action_node_id_on_each_robot={'-':-1}
        ### Counter
        link_id=0
        prev_robot_active="-"

        ####### Initialize robot start-end node on each robot #####
        for i in range(len(incoming_commands)):
            robot = str(incoming_commands[i].robot)
            has_robot=False
            for rb in robots:
                if incoming_commands[i].robot == rb:
                    has_robot=True
                    break

            if not has_robot:
                ### Create start node
                
                node_entry = {
                    "key": "start_"+str(incoming_commands[i].robot),
                    "command": "Start_"+str(incoming_commands[i].robot),
                    "color": planner_extractor.color_allocator(robot) ,
                    "category": "StartEnd"
                    }
                node.append(node_entry)
                ### Create end node
                node_entry = {
                    "key":  "end_"+str(incoming_commands[i].robot),
                    "command": "End_"+str(incoming_commands[i].robot),
                    "color": planner_extractor.color_allocator(robot) ,
                    "category": "StartEnd"
                    }
                node.append(node_entry)
                ### update dictionary planner
                start_robot_node="start_"+str(incoming_commands[i].robot)
                end_robot_node="end_"+str(incoming_commands[i].robot)
                robots.update({str(incoming_commands[i].robot):{'start':start_robot_node,'end':end_robot_node}})
                last_action_node_id_on_each_robot.update({str(incoming_commands[i].robot):0})

                ### Add link from start to first action node on each robot
                link_entry = {
                    "key": "start_link_"+str(incoming_commands[i].robot), 
                    "from": start_robot_node, 
                    "to": "action_"+str(incoming_commands[i].robot)+"_"+str(last_action_node_id_on_each_robot[incoming_commands[i].robot])
                }
                link.append(link_entry)

        ################ Add action or process or switch node ###############
        for i in range(len(incoming_commands)):
            robot = str(incoming_commands[i].robot)
            ### Add switch or wait node and link
            if(i>0 and incoming_commands[i].robot!=prev_robot_active):
                ### Add wait node for switch node
                node_entry = {
                    "key": "action_"+str(incoming_commands[i].robot)+"_"+str(last_action_node_id_on_each_robot[incoming_commands[i].robot]),
                    "command": "wait another",
                    "color": planner_extractor.color_allocator(robot),
                    "category": "Process"
                }
                node.append(node_entry)

                ### Add switch or wait link
                link_entry = {
                    "key": "switch_link_"+str(link_id),
                    "from": "action_"+str(prev_robot_active)+"_"+str(last_action_node_id_on_each_robot[prev_robot_active]-1), 
                    "to": "action_"+str(incoming_commands[i].robot)+"_"+str(last_action_node_id_on_each_robot[incoming_commands[i].robot])
                }
                link.append(link_entry)
                last_action_node_id_on_each_robot[incoming_commands[i].robot]=last_action_node_id_on_each_robot[incoming_commands[i].robot]+1
                link_id=link_id+1

            ### Add action or process node
            node_entry = {
                "key": "action_"+str(incoming_commands[i].robot)+"_"+str(last_action_node_id_on_each_robot[incoming_commands[i].robot]),
                "command": incoming_commands[i].action,
                "argument": "object: "+str(incoming_commands[i].object_item), #+" "+"target: "+str(incoming_commands[i].location),
                "color": planner_extractor.color_allocator(robot),
                "category": "Process"
            }
            node.append(node_entry)
            prev_robot_active=incoming_commands[i].robot
            ### Add link on node to prev node
            if last_action_node_id_on_each_robot[prev_robot_active]>0:
                link_entry = {
                    "key": "link_"+str(link_id),
                    "from": "action_"+str(prev_robot_active)+"_"+str(last_action_node_id_on_each_robot[prev_robot_active]-1), 
                    "to": "action_"+str(incoming_commands[i].robot)+"_"+str(last_action_node_id_on_each_robot[incoming_commands[i].robot])
                }
                link.append(link_entry)
                link_id=link_id+1
            last_action_node_id_on_each_robot[incoming_commands[i].robot]=last_action_node_id_on_each_robot[incoming_commands[i].robot]+1    


        ############### Draw link to the end (termination state) on each robot ###############
        for i in range(1,len(last_action_node_id_on_each_robot)):
            link_entry = {
                "key": "end_link_"+str(list(last_action_node_id_on_each_robot.keys())[i]), 
                "from": "action_"+str(list(last_action_node_id_on_each_robot.keys())[i])+"_"+str(last_action_node_id_on_each_robot[list(last_action_node_id_on_each_robot.keys())[i]]-1), 
                "to": robots[list(last_action_node_id_on_each_robot.keys())[i]]["end"]
            }
            link.append(link_entry)

        return node,link

    # Typically used for a single-step plan (e.g., output from a GNN-based planner)
    @staticmethod
    def AI_plan_to_graph_plan(node, link, single_plan, robots=None, last_action_node_id_on_each_robot=None, prev_robot_active=None, link_id=0):
        """
        Parse single plan command lines into structured dictionaries.

        Example (multiple plans, GNN-like):
            Input (as a single string):
                "pickup arm1 blue_wire table"

            Parsed commands (each dict):
                [{"action": "pickup",  "robot_id": "arm1", "object": "blue_wire", "position": "table"}]
        """
        incoming_command=[]
        try:
            # print(f"Received output_command: {single_plan}")
            extacted_command=planner_extractor.extract_basic_keyPharse(single_plan)
            incoming_command.append(extacted_command)
                
            node, link, robots, last_action_node_id_on_each_robot, prev_robot_active, link_id=planner_extractor.convert_plan_to_json_graph(node, link, incoming_command, robots, last_action_node_id_on_each_robot, prev_robot_active, link_id)


            return node,link, robots, last_action_node_id_on_each_robot, prev_robot_active, link_id
        except Exception as e:
            print(f"Error: {e}")
            return 'Error: An error occurred'
            
    # Typically used for multi-step plans (e.g., output from a PDDL planner with checkpoints)
    @staticmethod
    def AI_plans_to_graph_plans(multiple_plans):
        """
        Parse multiple plan command lines into structured dictionaries.

        Example (multiple plans, PDDL-like):
            Input (as a single string):
                "\\n(pickup arm1 blue_wire table)\\n(insert arm1 blue_wire power_supply_5)\\n
                (putdown arm1 blue_wire power_supply_5)\\n(lock arm2 blue_wire power_supply_5)"

            Split lines:
                [
                "(pickup arm1 blue_wire table)",
                "(insert arm1 blue_wire power_supply_5)",
                "(putdown arm1 blue_wire power_supply_5)",
                "(lock arm2 blue_wire power_supply_5)",
                ]

            Parsed commands (each dict):
                [
                {"action": "pickup",  "robot_id": "arm1", "object": "blue_wire", "position": "table",        },
                {"action": "insert",  "robot_id": "arm1", "object": "blue_wire", "position": "power_supply_5"},
                {"action": "putdown", "robot_id": "arm1", "object": "blue_wire", "position": "power_supply_5"},
                {"action": "lock",    "robot_id": "arm2", "object": "blue_wire", "position": "power_supply_5"},
                ]
        """
        incoming_command=[]
        try:
            print(f"Received output_command: {multiple_plans}")

            # for multiple commands
            command_lines=planner_extractor.extract_command_lines(multiple_plans)
            for command_line in command_lines:
                extacted_command=planner_extractor.extract_basic_keyPharse(command_line)
                incoming_command.append(extacted_command)

            node, link = [], []
            node,link=planner_extractor.convert_plans_to_json_graph(node, link, incoming_command)

            return node, link
        except Exception as e:
            print(f"Error: {e}")
            return 'Error: An error occurred'