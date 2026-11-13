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



class ImageSaver(Node):
    def __init__(self):
        super().__init__('image_saver')
        self.bridge = CvBridge()
        self.subscription = self.create_subscription(
            Image,
            '/techman_image',
            self.image_callback,
            10
        )

        self.tool_pose = None
        self.pose_subscriber = self.create_subscription(
            PoseStamped,
            '/tool_pose',
            self.pose_callback,
            10  # QoS profile for reliability
        )

    def image_callback(self, msg):
        prefix = 'OD'
        try:
            image_frame = self.bridge.imgmsg_to_cv2(msg)
            filename = f"captured_frame_{int(time.time())}_{prefix}.jpg"
            cv2.imwrite(filename, image_frame)
            self.get_logger().info(f"Image saved to {filename}")
        except Exception as e:
            self.get_logger().error(f"Failed to process image: {e}")

    def pose_callback(self, msg):
        """Callback to update tool_pose."""
        self.tool_pose = msg.pose  # Extract the pose
        print(tool_pose)


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

def main(args=None):
    
    rclpy.init(args=args)
    minimal_subscriber = MinimalSubscriber()
    # def print_pose():
    #     while rclpy.ok():
    #         if minimal_subscriber.tool_pose:
    #             print("Current tool pose:", minimal_subscriber.tool_pose.pose.position)
    # x, y ,z ,rx, ry, rz = 283.15, -370.72, 44.17, -179.01, 0.3, -3.91
    arm2 = ARM2_Skills()
    arm2.arm2_home()

    x, y, z, rx, ry, rz = 283.15, -370.72, 44.17, -179.01, 0.3, -3.91

    arm2.arm2_home()
    tolerance = 0.01

    # Initial approach (XY at safe Z)
    arm2.move_to(x, y, 242.23, rx, ry, rz, velocity=4.5)

    # Descend to working Z (screw head level)
    arm2.move_to(x, y, z, rx, ry, rz, velocity=1.0)

    # Lift back up a bit and go home

    while rclpy.ok():
        rclpy.spin_once(arm2)  # Process callback queue
        # Lock the screw 
        if arm2.tool_pose and arm2.is_pose_ready(arm2.tool_pose, [x/1000, y/1000, z/1000], tolerance):
            arm2.get_logger().info("Tool pose reached target position. Executing lock_screw.")
            if arm2.call_lock_screw():  # Run the screwdriver task and wait for it to complete
                time.sleep(3)
                # arm2.move_to(x, y, z+100, 178.63, 0.27, -0.53, velocity=1.0 )
                arm2.move_to(x, y, z + 100, rx, ry, rz, velocity=1.0)
                arm2.get_logger().info("Screwdriver task done. Moving to the next position.")
                arm2.arm2_home()
            else:
                arm2.get_logger().error("Screwdriver task failed. Halting further operations.")
            break
    # tolerance = 0.01
    # arm2.move_to(x, y, 242.23, rx, ry, rz, velocity=4.5) # Initial move to approach (x,y) position
    # # arm2.move_to(x, y, -10.05, 178.63, 0.27, -0.53, velocity=4.5) # Approach z position (screwhead location) 
    # arm2.move_to(x, y, z, rx, ry, rz, velocity=1.0) # Reach target position   
    # arm2.move_to(x, y, z+100, rx, ry, rz, velocity=1.0 )
    # arm2.arm2_home()
    # time.sleep(0.5)  # check every second

    # Run background thread to print tool pose
    # import threading
    # threading.Thread(target=print_pose, daemon=True).start()
    # arm2.arm2_home()

    rclpy.spin(minimal_subscriber)

    minimal_subscriber.destroy_node()
    rclpy.shutdown()


# def main(args=None):
#     rclpy.init(args=args) # Initialize ROS2 communication
#     minimal_subscriber = MinimalSubscriber() # Create an instance of the subscriber node
    
#     rclpy.spin(minimal_subscriber) # Keep the node running and processing events

#     minimal_subscriber.destroy_node() # Destroy the node when done
#     rclpy.shutdown() # Shutdown ROS2 communication


# def main():
#     """Get initial image frame of work space"""
#     rclpy.init()

#     # Start image listener node in a background thread
#     image_saver_node = ImageSaver()
#     executor = MultiThreadedExecutor()
#     executor.add_node(image_saver_node)

#     thread = threading.Thread(target=executor.spin, daemon=True)
#     thread.start()
#     rclpy.spin

#     # Run robot logic
#     # arm2 = ARM2_Skills()
#     # arm2.arm2_home()
#     # for t, task in enumerate(subtasks):
#     #     x, y, z, rx, ry, rz = coords[t]
#     #     if task == 'vision':
#     #         arm2.move_to(x, y, z, rx, ry, rz, velocity=0.5)
#     #         arm2.find()
#     #         time.sleep(1)

#     # arm2.arm2_home()
#     arm2.destroy_node()
#     # image_saver_node.destroy_node()
#     rclpy.shutdown()

    
coords_calibration=[
    [226.55, -144.01, 334.04, 158.44, -5.25, 9.98],
    [383.16, -241.98, 302.94, 173.11, 29.08, 82.94],
    [421.98, -229.93, 230.69, -176.64, 14.72, 58.64],
    [234.93, -439.42, 366.36, 162.64, -10.72, 16.28],
    [248.77, -372.06, 259.42, 179.21, -19.52, 41.73],
    [207.66, -193.33, 378.21, 176.78, 13.12, 67.43],
    [221.81, -151.81, 407.77, 176.47, 29.64, 92.19],
    [276.14, -372.26, 388.77, 162.71, 16.49, 60.98],
    [318.52, -356.87, 260.13, 173.21, -3.35, 62.77],
    [416.79, -271.16, 236.83, -175.46, 30.75, 79.03]
]

if __name__ == '__main__':
    main()
    # main(subtasks=['vision', 'vision', 'vision', 'vision', 'vision', 'vision', 'vision', 'vision', 'vision', 'vision'], coords=coords_calibration)