import time
import threading
import cv2
import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor

from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from geometry_msgs.msg import PoseStamped
from arm2_skills import ARM2_Skills  # Your custom class

# Assumes ARM2_Skills is available in your environment
# from arm2_skills import ARM2_Skills
class MinimalSubscriber(Node):
    def __init__(self):
        super().__init__('minimal_subscriber')
        self.tool_pose = None
        self.subscription = self.create_subscription(
            PoseStamped,
            '/tool_pose', 
        
            self.listener_callback,
            10)
        self.get_logger().info('Subscriber node started and listening on topic "topic"')

    def listener_callback(self, msg):
        # This function is called every time a new message is received on the topic
        self.tool_pose = msg  # Extract the pose
        # self.get_logger().info(f'{self.tool_pose.pose.position}')

class Arm2Controller:
    """
    Class-based controller for Arm2 with:
      - controller_arm2(): low-level motion + screw locking
      - execute_arm2(): routes high-level actions to skills
      - wait_for_arm1_and_execute_arm2(): sync with Arm1, then run Arm2
    """
    def screwing(terminal_position: int, time_keeper):
        """
        Execute the screwing approach/move sequence for a given terminal number.
        NOTE: This uses your original motion sequence (approach, descend, lift, home).
        """
        # Initialize rclpy (avoid double-init across runs)
        try:
            rclpy.init(args=None)
        except RuntimeError:
            # Already initialized
            pass

        minimal_subscriber = MinimalSubscriber()
        time_min = time.time()
        print(f"time to load minimal subscriber: {time_min-time_keeper}")
        arm2 = ARM2_Skills()
        time_arminit = time.time()
        print(f"time to init the arm: {time_arminit-time_min}")
        time_screw1 = time.time()
        print(f"time from main to inside screw function: {time_screw1-time_keeper}")
        try:
            print("IN arm2_exec")
            # Example pose (you can map 'terminal_number' -> (x,y,z,rx,ry,rz) if needed)
            x, y, z, rx, ry, rz = 282.15, -373, 46.17, -179.01, 0.3, -3.91 # x, y, z: 283.15, -370.72, 44.17,
            time_try = time.time()
            arm2.arm2_home()
            tolerance = 0.01

            # Initial approach (XY at safe Z)
            arm2.move_to(x, y, 242.23, rx, ry, rz, velocity=4.5)

            # Descend to working Z (screw head level)
            arm2.move_to(x, y, z, rx, ry, rz, velocity=1.0)

            while rclpy.ok():
                rclpy.spin_once(arm2)  # Process callback queue
                # Lock the screw 
                if arm2.tool_pose and arm2.is_pose_ready(arm2.tool_pose, [x/1000, y/1000, z/1000], tolerance):
                    arm2.get_logger().info("Tool pose reached target position. Executing lock_screw.")
                    if arm2.call_lock_screw():  # Run the screwdriver task and wait for it to complete
                        time.sleep(3)
                        arm2.move_to(x, y, z + 100, rx, ry, rz, velocity=1.0)
                        arm2.get_logger().info("Screwdriver task done. Moving to the next position.")
                        arm2.arm2_home()
                        time_motion = time.time()
                        print(f"time from inside try to second conditional: {time_motion-time_try}")
                    else:
                        arm2.get_logger().error("Screwdriver task failed. Halting further operations.")
                    break

            # arm2.arm2_home()

            # Give callbacks a moment if needed
            time.sleep(0.5)

            # Spin the subscriber (blocks). If you want non-blocking, run in a thread.
            rclpy.spin(minimal_subscriber)
            print("DONE SCREWING...")

        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"[screwing] Error: {e}")
        finally:
            # Cleanup
            try:
                minimal_subscriber.destroy_node()
            except Exception:
                pass
            try:
                arm2.destroy_node()
            except Exception:
                pass
            try:
                rclpy.shutdown()
            except Exception:
                pass
            print("DONE with 'FINALLY' section?")

   