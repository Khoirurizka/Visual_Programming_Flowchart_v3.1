import time
import rclpy
from rclpy.node import Node

from arm2_skills import ARM2_Skills # Screwdriver


def main(subtasks, coords):
    """ Get initial image frame of work space
    """
    rclpy.init()
    arm2 = ARM2_Skills()
    arm2.arm2_home() # Set screwdriver to home position

    for t, task in enumerate(subtasks):
        x, y, z = coords[t]
        if task == 'demo':
            arm2.arm2_home()
            arm2.find()
            time.sleep(1)
            arm2.arm2_home()

    arm2.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':

    main(subtasks=['demo'], coords=[[299.25, -413.79, -12.05]])

