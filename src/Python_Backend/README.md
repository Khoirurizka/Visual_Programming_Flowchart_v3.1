To run the robot, press the power button on its pendant (O), wait till the monitor and robot is ready. The project name is "sp_listenllll". 


Terminal 1
source ~/gai_ws/install/setup.bash
ros2 run tm_driver tm_driver robot_ip:=192.168.13.2

Terminal 2
source ~/gai_ws/install/setup.bash
ros2 run tm_get_status image_talker

Terminal 3
source ~/gai_ws/install/setup.bash
ros2 run custom_package sub_img

Terminal 4
source ~/gai_ws/install/setup.bash
ros2 service call /send_script tm_msgs/srv/SendScript "{id: 'L', script: 'ScriptExit()'}"

/home/gai-hucenrotia/gai_ws/src/scripts/Visual_Programming_Flowchart_v3.1/vola/src/Python_Backend/arm2_collect_vision_data.py

/home/gai-hucenrotia/gai_ws/src/scripts/Visual_Programming_Flowchart_v3.1.3/vola/src/Python_Backend/arm2_move_robot.py

### Tool pose coordinates for calibrating force sensor
Tool pose: geometry_msgs.msg.Point(x=0.31373693847656253, y=-0.1308803253173828, z=0.2411018981933594)
