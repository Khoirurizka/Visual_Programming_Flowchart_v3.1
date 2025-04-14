import React, { useEffect, useState, useRef } from 'react';
import { Send, Mic, XCircle } from 'react-feather';
import { TooltipComponent } from '@syncfusion/ej2-react-popups';
import { sendPromptToLLMServer, speechInput, blobToWav } from '../utilities';
import { DiagramComponent, WaveSurferVisualizer } from '../components';
import { useStateContext } from '../contexts/ContextProvider';
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';
import { AudioVisualizer, LiveAudioVisualizer } from 'react-audio-visualize';
import { WaveformVisualizer } from 'react-audio-visualizer-pro';
import { AudioRecorder, useAudioRecorder } from 'react-audio-voice-recorder';
import StopIcon from '@mui/icons-material/Stop';
import PauseOutlinedIcon from '@mui/icons-material/PauseOutlined';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import ReplayIcon from '@mui/icons-material/Replay';
import RadioButtonCheckedIcon from '@mui/icons-material/RadioButtonChecked';
import * as speech_sdk from "microsoft-cognitiveservices-speech-sdk";
import CancelIcon from '@mui/icons-material/Cancel';

const { ipcRenderer } = window.require("electron");

const Home_menu = () => {
  const [messageUser, setMessageUser] = useState("");
  const [messageUserVoice, setMessageUserVoice] = useState("");
  const [detectedLanguage, setDetectedLanguage] = useState("");

  const [voiceMode, setvoiceMode] = useState(0);
  const [isListening, setIsListening] = useState(0);
  const [playPause_Listening, setPlayPause_Listening] = useState(1);
  const [playPause_notListening, setPlayPause_notListening] = useState(1);
  const { frameReceived_ScrewDriver, setframeReceived_ScrewDriver } = useStateContext();
  const [blob, setBlob] = useState();
  const recorder = useAudioRecorder();
  const [audioPlayer, setAudioPlayer] = useState(null);
  const [blobDuration, setBlobDuration] = useState(0);
  const [audioUrl, setAudioUrl] = useState(0);
  const [audCurrentTime, setAudCurrentTime] = useState(0);


  //Animation Play
  const visualizerRef = useRef(null);

  const handlePlay = () => {
    if (visualizerRef.current) {
      visualizerRef.current.play();
    }
  };

  const handlePause = () => {
    if (visualizerRef.current) {
      visualizerRef.current.pause();
    }
  };


  useEffect(() => {
    const interval = setInterval(() => {
      if (visualizerRef.current) {
        const playing = visualizerRef.current.isPlaying();
        setPlayPause_notListening(playing ? 0 : 1);
        const curTime = visualizerRef.current.getCurrentTime();
        setAudCurrentTime(curTime);
      }
    }, 200); // every 200ms

    return () => clearInterval(interval);
  }, []);

  const startListening = () => {
    setIsListening(1);
    recorder.startRecording();
  };

  const stopListening = () => {
    setIsListening(0);
    recorder.stopRecording();
  };


  const formatTime = (totalSeconds) => {
    const hours = Math.floor(totalSeconds / 3600)
    const minutes = Math.floor((totalSeconds % 3600) / 60)
    const secs = totalSeconds % 60

    return `${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}:${String(secs).padStart(2, "0")}`
  }

  const transcribeAudioBlob = async (audioBlob) => {
    try {
      const wavBlob = await blobToWav(audioBlob);
      const wavFile = new File([wavBlob], 'temp.wav', { type: 'audio/wav' });

      const audioConfig = speech_sdk.AudioConfig.fromWavFileInput(wavFile);
      const speechConfig = speech_sdk.SpeechConfig.fromSubscription("81032fb3c28f43d79b682e5f7f09d525", "eastasia");

      const autoDetectSourceLanguageConfig = speech_sdk.AutoDetectSourceLanguageConfig.fromLanguages(["en-US", "de-DE", "zh-TW", "id-ID"]);
      const recognizer = speech_sdk.SpeechRecognizer.FromConfig(speechConfig, autoDetectSourceLanguageConfig, audioConfig);

      recognizer.recognizeOnceAsync((result) => {
        const languageDetectionResult = speech_sdk.AutoDetectSourceLanguageResult.fromResult(result);
        const language = languageDetectionResult.language;
        console.log(language);
        setDetectedLanguage(language);
        if (result.reason === speech_sdk.ResultReason.RecognizedSpeech) {
          setMessageUserVoice(result.text.replace(/\n/g, '').trim());
        } else {
          console.error("Recognition failed:", result.errorDetails || result);
        }
        recognizer.close();
      });

    } catch (err) {
      console.error("Error during transcription:", err);
    }
  };


  useEffect(() => {
    if (recorder.recordingBlob) {
      const url = URL.createObjectURL(recorder.recordingBlob);
      setAudioUrl(url);
      setBlob(recorder.recordingBlob);
      const audio = new Audio(url);
      setAudioPlayer(audio);
    }
  }, [recorder.recordingBlob]);
  useEffect(() => {

    if (blob instanceof Blob) {
      try {
        transcribeAudioBlob(blob);
        handlePlay();

      } catch (err) {
        console.error("Error during WAV conversion or transcription:", err);
      }
    }

  }, [blob]);

  useEffect(() => {
    const fetchDuration = async () => {
      if (blob) {
        const arrayBuffer = await blob.arrayBuffer();
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
        setBlobDuration(Math.floor(audioBuffer.duration)); // convert float to int
      } else {
        setBlobDuration(0);
      }
    };

    fetchDuration();
  }, [blob]);

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
            <button onClick={() => { sendPromptToLLMServer(messageUser, frameReceived_ScrewDriver);; setMessageUser("") }} className="px-4 py-2 rounded-full bg-transparent hover:bg-gray-100">
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
          <div className="flex items-center justify-center h-full w-full">
            <textarea
              placeholder="Press record, and I will process your commands..."
              value={messageUserVoice}
              readOnly
              className="transcript w-full h-full px-3 py-2 bg-transparent focus:outline-none resize-none leading-[1.5rem] text-center overflow-auto"
            />
          </div>
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
                <button onClick={() => {
                  stopListening(); setPlayPause_notListening(0);

                }} className="p-2 rounded-full bg-transparent hover:bg-gray-100">
                  <StopIcon className="text-red-500 drop-shadow-md" />
                </button>
              </TooltipComponent>
            </div>
            {/*is not Listening*/}
            <div className={`flex items-center gap-2 h-full ${!isListening ? 'block' : 'hidden'}`}>
              {/*is Playing */}
              <div className={`text-[28px] text-black bg-transparent p-4 mx-0 ${!playPause_notListening ? 'block' : 'hidden'}`}>
                {formatTime(Math.floor(audCurrentTime))}
              </div>
              {/*on silent */}
              <div className={`text-[28px] text-black bg-transparent p-4 mx-0 ${playPause_notListening ? 'block' : 'hidden'}`}>
                {formatTime(blobDuration)}
              </div>
              <div className={`flex-1 h-full items-center gap-2 px-3 py-2 bg-transparent focus:outline-none resize-none leading-[1.5rem]`}>
                {blob && <WaveSurferVisualizer ref={visualizerRef} blob={blob} />}
              </div>

              <div className={`flex items-center gap-2 h-full ${!playPause_notListening ? 'block' : 'hidden'}`}>
                <TooltipComponent
                  content="Pause"
                  position="BottomRight"
                  mouseTrail={true}
                  opensOn="Hover"  >
                  <button onClick={() => {
                    setPlayPause_notListening(1); handlePause();
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
                    handlePlay();
                    ;
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
                <button onClick={() => { handlePause(); startListening(); setPlayPause_Listening(1); }} className="p-2 rounded-full bg-transparent hover:bg-gray-100">
                  <RadioButtonCheckedIcon className="text-blue-400 drop-shadow-md" />
                </button>
              </TooltipComponent>
            </div>
            <TooltipComponent
              content="Send"
              position="BottomRight"
              mouseTrail={true}
              opensOn="Hover"  >
              <button onClick={() => { sendPromptToLLMServer(messageUserVoice, frameReceived_ScrewDriver); setMessageUserVoice("") }} className="px-4 py-2 rounded-full bg-transparent hover:bg-gray-100">
                <Send size={30} className="drop-shadow-md" />
              </button>
            </TooltipComponent>
            <TooltipComponent
              content="Use text"
              position="BottomRight"
              mouseTrail={true}
              opensOn="Hover"  >
              <button onClick={() => { handlePause(); setvoiceMode(0); setIsListening(0); startListening(); if (recorder.isPaused) { recorder.togglePauseResume() } }} className="p-2 rounded-full bg-transparent hover:bg-gray-100">
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