from collections import namedtuple
import re

def convert_plans_to_jsonGraph(node,link, incoming_commands):
    ################## Dictionary planner ##################
    robots={'-':{'start':-1,'end':-1}} #Initalize dictionary
    last_action_node_id_on_each_robot={'-':-1}
    ### Counter
    link_id=0
    action_function_id=0
    prev_robot_active="-"

    ####### Initialize robot start-end node on each robot #####
    for i in range(len(incoming_commands)):
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
                "color": "lightblue",
                "category": "StartEnd"
                }
            node.append(node_entry)
            ### Create end node
            node_entry = {
                "key":  "end_"+str(incoming_commands[i].robot),
                "command": "End_"+str(incoming_commands[i].robot),
                "color": "lightblue",
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
        ### Add switch or wait node and link
        if(i>0 and incoming_commands[i].robot!=prev_robot_active):
            ### Add wait node for switch node
            node_entry = {
                "key": "action_"+str(incoming_commands[i].robot)+"_"+str(last_action_node_id_on_each_robot[incoming_commands[i].robot]),
                "command": "wait another",
                "color": "white",
                "category": "Process"
            }
            node.append(node_entry)

            ### Add switch or wait link
            link_entry = {
                "key": "switch_link"+str(link_id),
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
            "color": "white",
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

        action_function_id=action_function_id+1
    return node,link

# Parse input commands
def parse_commands(input_string):
    Command = namedtuple('Command', ['robot', 'action'])
    commands = []
    lines = input_string.strip().split('\n')
    
    for line in lines:
        # Remove parentheses and split by spaces
        line = line.strip()[1:-1]  # Remove ( and )
        parts = line.split()
        if parts[0] == 'find':
            # No robot specified, assume arm1
            robot = 'arm1'
            action = ' '.join(parts)
        else:
            # Robot is the second word, action is the rest
            robot = parts[1]
            action = ' '.join(parts[0:1] + parts[2:])
        commands.append(Command(robot=robot, action=action))
    
    return commands

# Test code
if __name__ == "__main__":
    input_string = """(find blue_wire)
    (pickup arm1 blue_wire table)
    (insert arm1 blue_wire power_supply_5)
    (putdown arm1 blue_wire power_supply_5)
    (lock arm2 blue_wire power_supply_5)
    """
    
    # Parse commands
    incoming_commands = parse_commands(input_string)
    
    # Generate graph
    node = []
    link = []
    node, link = convert_plans_to_jsonGraph(node, link, incoming_commands)
    
    # Print results
    print("Nodes:")
    for n in node:
        print(n)
    print("\nLinks:")
    for l in link:
        print(l)