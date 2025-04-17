# Visual_Programming_Flowchart_v3.1
A software system for controlling a dual-arm robot. It features learning capabilities from both text and voice inputs to generate a visual programming graph, which is integrated with ROS2 and capable of learning new skills. The system is designed to be highly accessible, even for unskilled users. The core of its learning capability lies in its integration with a PDDL or GNN solver and a Large Language Model (LLM). These components work together to produce a graph representing action skills. These action skills are linked to ROS2 functions that generate real robot motion. Moreover, the system can acquire skills from previous actions and also generate new ones using a diffusion model.

## Cam API Endpoints (Backend → Frontend)

Use these APIs to **capture images from different cameras**:

| Camera View        | Endpoint                                      |
|--------------------|-----------------------------------------------|
| BEV (Bird’s Eye View)  | `http://localhost:6000/bev_driver_capture`     |
| Right Camera (Screw)   | `http://localhost:6000/screw_driver_capture`   |
| Left Camera (Gripper)  | `http://localhost:6000/gripper_driver_capture` |

Each endpoint returns a captured image frame. These are typically base64-encoded JPEGs or raw image bytes, depending on your backend setup.

---

## Prompting API (Frontend → Backend)

Use the following endpoint to send image data along with a **user prompt** to the LLM server:

```http
POST http://127.0.0.2:8000/user_prompt_to_LLM_server
