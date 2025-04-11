import React, { useEffect, useState } from 'react';
import axios from 'axios'; 
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition'

const { ipcRenderer } = window.require("electron");

function speechInput() {
    const {
        transcript,
        listening,
        resetTranscript,
        browserSupportsSpeechRecognition
      } = useSpeechRecognition();
    
      if (!browserSupportsSpeechRecognition) {
        console.log("Browser doesn't support speech recognition");
      }
    /*
      return (
        <div>
          <p>Microphone: {listening ? 'on' : 'off'}</p>
          <button onClick={SpeechRecognition.startListening}>Start</button>
          <button onClick={SpeechRecognition.stopListening}>Stop</button>
          <button onClick={resetTranscript}>Reset</button>
          <p>{transcript}</p>
        </div>
      );
      */
    try {
        SpeechRecognition.startListening;
        console.log(transcript);
       /* if (response && response.data) {
            // Send the data to the renderer process
            console.log(response.data);
            ipcRenderer.send("SpeechTranscript", response.data.result_from_AI);
            ipcRenderer.send("update_VLM_frame_from_AI", response.data.result_from_AI.vlm_frame);
            console.log('update graph and show VLM figure  successfully');
        } else {
            console.error("Invalid response from LLM server");
        }*/
    } catch (error) {
        console.error("Error transcription:", error);
        throw error;
    }
}

export default speechInput;