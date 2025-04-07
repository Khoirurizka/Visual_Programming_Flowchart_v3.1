import React, { useEffect, useState } from 'react';
import axios from 'axios'; // Use import syntax for axios
const { ipcRenderer } = window.require("electron");

async function sendPromptToLLMServer(message, frameReceived) {
    // console.log("message: ", message)
    // console.log("frameReceived: ", frameReceived)
    try {
        const response = await axios.post("http://127.0.0.2:8000/user_prompt_to_LLM_server", {
            message: message,
            frame_screw_driver: frameReceived
        });
        if (response && response.data) {
            // Send the data to the renderer process
            console.log(response.data);
            ipcRenderer.send("update_main_graph_chat_response_from_AI", response.data.result_from_AI);
            ipcRenderer.send("update_VLM_frame_from_AI", response.data.result_from_AI.vlm_frame);
            console.log('update graph and show VLM figure  successfully');
        } else {
            console.error("Invalid response from LLM server");
        }
    } catch (error) {
        console.error("Error sending prompt to LLM server:", error);
        throw error;
    }
/*
    useEffect(() => {
        ipcRenderer.on("response_from_LLM", (event, jsonData) => {
            try {
                console.log("Received data from main process msg:", jsonData);

                console.log(jsonData.message)
                actions.handleWriteLLMResponse(jsonData.message);


            } catch (error) {
                console.error("Error parsing JSON data:", error);
            }
        });
    }, []);

    return (
        <div>
            {React.Children.map(children, (child) => {
                return React.cloneElement(child, {
                    parse: parse,
                    actions: actions,
                });
            })}
        </div>
    );*/
    return "response.data";

}

export default sendPromptToLLMServer;