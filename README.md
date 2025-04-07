# Visual_Programming_Flowchart_v3.1

Base station for controling multiple robot. It's utilize the visual programming and ROS or ROS2. Make it, so usefull even for unskilled people. for using this aplication, the it should connected to pddl and solver, while it will give result as graph that related to ROS function.

## Cam API Endpoints (Backend → Frontend)

Use these APIs to **capture images from different cameras**:

| Camera View        | Endpoint                                      |
|--------------------|-----------------------------------------------|
| BEV (Bird’s Eye View)  | `http://localhost:6000/bev_diver_capture`     |
| Right Camera (Screw)   | `http://localhost:6000/screw_diver_capture`   |
| Left Camera (Gripper)  | `http://localhost:6000/gripper_diver_capture` |

Each endpoint returns a captured image frame. These are typically base64-encoded JPEGs or raw image bytes, depending on your backend setup.

---

## Prompting API (Frontend → Backend)

Use the following endpoint to send image data along with a **user prompt** to the LLM server:

```http
POST http://127.0.0.2:8000/user_prompt_to_LLM_server
