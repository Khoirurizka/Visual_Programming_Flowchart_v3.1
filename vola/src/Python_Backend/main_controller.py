"""
Draft script for low-level controller to call functions for task plan

Method :
---------
input lists of sub-tasks (correlate to functions) 
input lists of target coordinates (coordinate with list of sub-tasks, one target for each sub-task, match indicies)

Algorithm : Brute force using boolean logic (We can optimize this later)

Define exact sequence for a given subtask (e.g. insert : move_to(coords), move_to(coords), pick_up(),
                                                        move_to(coords), move_to(coords, insert(target_coords)
                                                         )
Need defined names for possible subtasks for boolean logic (correspond with PDDL actions)


Example :
--------
subtask list : [insert wire, lock screw] 

!!!!!! LIST ORDER SHOULD CORRESPOND TO TASK ORDER !!!!!!

target coordinates : [[0.405, 0.045, -0.002], [0.154, -0.309, -0.064]]
target_coordinates[0] is target coordinate for inserting the wire fork
target_coordinates[1] is the target coordinate for locking the screw

**Currently supporting manual coordinate entry**

!!!!!!!!!!!! PLEASE DOUBLE CHECK RX, RY, RZ COORDINATES PRIOR TO RUNNING WITH REAL ROBOTS !!!!!!!!!!!!!!
"""
import time
import rclpy
from rclpy.node import Node

from arm1_skills import ARM1_Skills # Gripper
from arm2_skills import ARM2_Skills # Screwdriver




def main(subtasks, coords):
    """ Brute Force boolean logic for subtask function sequences subtasks
    Args
    ----------
    subtasks : list, each element is a subtask
    coords : list, each elements is the target coordinate for a subtask

    """
    rclpy.init()
    # arm1 = ARM1_Skills()
    arm2 = ARM2_Skills()
    # arm1.arm1_home() # Set gripper to home position
    arm2.arm2_home() # Set screwdriver to home position

    for t, task in enumerate(subtasks):
        x, y, z = coords[t]
        if task == 'pickup':
            arm1.move_to(x, y , z,  173.33, 0.16, 93.13, velocity=1.0) # Move to grasping position
            arm1.pick_up() # Grasp and then lift off of buffer??

        elif task == 'putdown':
            arm1.move_to(x, y, z, rx, ry, rz, velocity=0.5) # Move to putting position
            arm1.put_down()

        elif task == 'insert':
            arm1.move_to(x, y-0.1, z, 173.33, 0.16, 93.13, velocity=1.0)
            arm1.insert(x, y, z, 166.37, 2.67, 177.51, velocity=0.5)
            arm1.arm1_home()

        elif task == 'demo':
            arm2.arm2_home()
            arm2.find()
            time.sleep(1)
            arm2.arm2_home()
            # arm1.move_to(x, y-0.1, z, 173.33, 0.16, 93.13, velocity=1.0)
            # arm1.insert(x, y, z, 166.37, 2.67, 177.51, velocity=0.5)
            # arm1.arm1_home()

        elif task == 'lock':
            tolerance = 0.0001
            arm2.move_to(x, y, 220.00, 178.63, 0.27, -0.53, velocity=1.5) # Initial move to approach (x,y) position
            arm2.move_to(x, y, -10.05, 178.63, 0.27, -0.53, velocity=1.5) # Approach z position (screwhead location) 
            arm2.move_to(x, y, z, 178.63, 0.27, -0.53, velocity=0.2) # Reach target position
            arm2.get_logger().info("Waiting for tool_pose to reach target position...")
            while rclpy.ok():
                rclpy.spin_once(arm2)  # Process callback queue
                # Lock the screw 
                if arm2.tool_pose and arm2.is_pose_ready(arm2.tool_pose, [x/1000, y/1000, z/1000], tolerance):
                    arm2.get_logger().info("Tool pose reached target position. Executing lock_screw.")
                    if arm2.call_lock_screw():  # Run the screwdriver task and wait for it to complete
                        time.sleep(3)
                        arm2.move_to(x, y, z+100, 178.63, 0.27, -0.53, velocity=1.0 )
                        arm2.get_logger().info("Screwdriver task done. Moving to the next position.")
                        arm2.arm2_home()
                    else:
                        arm2.get_logger().error("Screwdriver task failed. Halting further operations.")
                    break
    # arm1.destroy_node()
    arm2.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':

    # main(subtasks=['lock'], coords=[[299.25, -413.79, -12.05]]) # Screw on terminal 5 coordinates
    main(subtasks=['demo'], coords=[[299.25, -413.79, -12.05]]) # Screw on terminal 5 coordinates

