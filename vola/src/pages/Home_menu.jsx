import React, { useEffect, useState, useRef } from 'react';
import { Send, Mic, XCircle } from 'react-feather';
import { TooltipComponent } from '@syncfusion/ej2-react-popups';
import { sendPromptToLLMServer, speechInput } from '../utilities';
import { DiagramComponent } from '../components';
import { useStateContext } from '../contexts/ContextProvider';
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';
import { AudioVisualizer, LiveAudioVisualizer } from 'react-audio-visualize';
import { AudioRecorder, useAudioRecorder } from 'react-audio-voice-recorder';
import StopIcon from '@mui/icons-material/Stop';
import PauseOutlinedIcon from '@mui/icons-material/PauseOutlined';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import ReplayIcon from '@mui/icons-material/Replay';
import RadioButtonCheckedIcon from '@mui/icons-material/RadioButtonChecked';

import CancelIcon from '@mui/icons-material/Cancel';
const { ipcRenderer } = window.require("electron");

const Home_menu = () => {
  const [messageUser, setMessageUser] = useState("");
  const [voiceMode, setvoiceMode] = useState(0);
  const [isListening, setIsListening] = useState(0);
  const [playPause_Listening, setPlayPause_Listening] = useState(1);
  const [playPause_notListening, setPlayPause_notListening] = useState(1);
  const { frameReceived_ScrewDriver, setframeReceived_ScrewDriver } = useStateContext();
  const [blob, setBlob] = useState();
  const recorder = useAudioRecorder();
  const [audioPlayer, setAudioPlayer] = useState(null);

  const startListening = () => {
    setIsListening(1);
    recorder.startRecording();
  };

  const stopListening = () => {
    setIsListening(0);
    recorder.stopRecording();
  };

  useEffect(() => {
    if (recorder.recordingBlob) {
      const url = URL.createObjectURL(recorder.recordingBlob);
      setBlob(recorder.recordingBlob);
      const audio = new Audio(url);
      setAudioPlayer(audio);
    }
  }, [recorder.recordingBlob]);

  const formatTime = (totalSeconds) => {
    const hours = Math.floor(totalSeconds / 3600)
    const minutes = Math.floor((totalSeconds % 3600) / 60)
    const secs = totalSeconds % 60

    return `${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}:${String(secs).padStart(2, "0")}`
  }

  return (
    <div className=" w-screen">
      <div className="fixed top-72 right-10 bg-slate-50 h-[600px] w-96 p-4 shadow-lg rounded-3xl z-50">
        <div className="relative -top-4 right-4 bg-blue-900 h-[60px] w-96 p-4 shadow-lg rounded-t-3xl z-51">
          <h2 className="text-lg font-semibold text-white">Prompt History</h2>
        </div>
        <p>Chat</p>
      </div>

      <div className="fixed bottom-10 left-1/2 transform -translate-x-1/2 bg-slate-50 p-4 shadow-lg rounded-2xl z-50 w-[800px]" style={{ borderRadius: '30px' }}>

        {/*text mode*/}
        <div className={`flex items-center gap-2 h-full ${voiceMode === 0 ? 'block' : 'hidden'}`}>
          <textarea
            placeholder="Type a message..."
            value={messageUser}
            onChange={(e) => setMessageUser(e.target.value)}
            className="flex-1 h-full  px-3 py-2 bg-transparent focus:outline-none resize-none leading-[1.5rem]"
          />
          <TooltipComponent
            content="Send"
            position="BottomRight"
            mouseTrail={true}
            opensOn="Hover"  >
            <button onClick={() => sendPromptToLLMServer(messageUser, frameReceived_ScrewDriver)} className="px-4 py-2 rounded-full bg-transparent hover:bg-gray-100">
              <Send size={30} className="drop-shadow-md" />
            </button>
          </TooltipComponent>
          <TooltipComponent
            content="Use voice"
            position="BottomRight"
            mouseTrail={true}
            opensOn="Hover"  >
            <button onClick={() => { setvoiceMode(1); startListening(); }} className="p-2 rounded-full bg-transparent hover:bg-gray-100">
              <Mic size={30} className="drop-shadow-md" />
            </button>
          </TooltipComponent>
        </ div>
        {/*voice mode*/}
        <div className={`flex-1 items-center gap-2 h-full ${voiceMode === 1 ? 'block' : 'hidden'}`}>
          <div className={`flex items-center gap-2 h-full`}>
            {/*is Listening*/}
            <div className={`flex items-center gap-2 h-full ${isListening ? 'block' : 'hidden'}`}>
              <div className='text-[28px] text-black bg-transparent p-4 mx-0'>
                {formatTime(recorder.recordingTime || 0)}
              </div>

              <div className="flex-1 h-full px-3 py-2 bg-transparent focus:outline-none resize-none leading-[1.5rem] w-[350px] mx-5 my-0">
                {recorder.mediaRecorder && (
                  <LiveAudioVisualizer
                    mediaRecorder={recorder.mediaRecorder}
                    width={350}
                    height={50}
                  />
                )}
                {/*<AudioRecorder 
                onRecordingComplete={setBlob}
                recorderControls={recorder}
              />*/}
              </div>
              <div className={`flex items-center gap-2 h-full ${playPause_Listening ? 'block' : 'hidden'}`}>
                <TooltipComponent
                  content="Pause"
                  position="BottomRight"
                  mouseTrail={true}
                  opensOn="Hover"  >
                  <button onClick={() => { setPlayPause_Listening(0); recorder.togglePauseResume(); }} className="p-0 rounded-full bg-transparent hover:bg-gray-100">
                    <PauseOutlinedIcon className=" drop-shadow-md" />
                  </button>
                </TooltipComponent>
              </div>
              <div className={`flex items-center gap-2 h-full ${!playPause_Listening ? 'block' : 'hidden'}`}>
                <TooltipComponent
                  content="Play"
                  position="BottomRight"
                  mouseTrail={true}
                  opensOn="Hover"  >
                  <button onClick={() => { setPlayPause_Listening(1); recorder.togglePauseResume(); }} className="p-0 rounded-full bg-transparent hover:bg-gray-100">
                    <PlayArrowIcon className=" drop-shadow-md" />
                  </button>
                </TooltipComponent>
              </div>
              <TooltipComponent
                content="Stop listening"
                position="BottomRight"
                mouseTrail={true}
                opensOn="Hover"  >
                <button onClick={() => stopListening()} className="p-2 rounded-full bg-transparent hover:bg-gray-100">
                  <StopIcon className="text-red-500 drop-shadow-md" />
                </button>
              </TooltipComponent>
            </div>
            {/*is not Listening*/}
            <div className={`flex items-center gap-2 h-full ${!isListening ? 'block' : 'hidden'}`}>
              <div className='text-[28px] text-black bg-transparent p-4 mx-0'>
                {formatTime(recorder.recordingTime || 0)}
              </div>
              <div className="flex-1 h-full  px-3 py-2 bg-transparent focus:outline-none resize-none leading-[1.5rem]">
                <AudioVisualizer
                  blob={blob}
                  width={350}
                  height={50}
                  barWidth={1}
                  gap={0}
                  barColor={'lightblue'}
                />
              </div>

              <div className={`flex items-center gap-2 h-full ${!playPause_notListening ? 'block' : 'hidden'}`}>
                <TooltipComponent
                  content="Pause"
                  position="BottomRight"
                  mouseTrail={true}
                  opensOn="Hover"  >
                  <button onClick={() => {
                    setPlayPause_notListening(1); if (audioPlayer) {
                      audioPlayer.pause();
                    }
                  }} className="p-0 rounded-full bg-transparent hover:bg-gray-100">
                    <PauseOutlinedIcon className="drop-shadow-md" />
                  </button>
                </TooltipComponent>
              </div>
              <div className={`flex items-center gap-2 h-full ${playPause_notListening ? 'block' : 'hidden'}`}>
                <TooltipComponent
                  content="Play"
                  position="BottomRight"
                  mouseTrail={true}
                  opensOn="Hover"  >
                  <button onClick={() => {
                    setPlayPause_notListening(0);
                    if (audioPlayer) {
                      audioPlayer.play();
                    }
                    audioPlayer.onended = () => {
                      setPlayPause_notListening(1)
                    };
                  }} className="p-0 rounded-full bg-transparent hover:bg-gray-100">
                    <PlayArrowIcon className=" drop-shadow-md" />
                  </button>
                </TooltipComponent>
              </div>
              <TooltipComponent
                content="Listening"
                position="BottomRight"
                mouseTrail={true}
                opensOn="Hover"  >
                <button onClick={() => {startListening();setPlayPause_Listening(1);}} className="p-2 rounded-full bg-transparent hover:bg-gray-100">
                  <RadioButtonCheckedIcon className="text-blue-400 drop-shadow-md" />
                </button>
              </TooltipComponent>
            </div>
            <TooltipComponent
              content="Send"
              position="BottomRight"
              mouseTrail={true}
              opensOn="Hover"  >
              <button onClick={() => sendPromptToLLMServer(messageUser, frameReceived_ScrewDriver)} className="px-4 py-2 rounded-full bg-transparent hover:bg-gray-100">
                <Send size={30} className="drop-shadow-md" />
              </button>
            </TooltipComponent>
            <TooltipComponent
              content="Use text"
              position="BottomRight"
              mouseTrail={true}
              opensOn="Hover"  >
              <button onClick={() => { setvoiceMode(0); setIsListening(0); startListening();  if (recorder.isPaused) { recorder.togglePauseResume() } }} className="p-2 rounded-full bg-transparent hover:bg-gray-100">
                <XCircle size={30} className="drop-shadow-md" />
              </button>
            </TooltipComponent>
          </div>
        </div>
      </div>
      <div className="graph">
        <DiagramComponent />
      </div>
    </div>
  );
}
export default Home_menu