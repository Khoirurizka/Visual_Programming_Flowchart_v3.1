import cv2
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

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