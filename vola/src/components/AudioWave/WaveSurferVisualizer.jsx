import React, { useEffect, useState, useRef, useImperativeHandle, forwardRef } from "react";
import WaveSurfer from "wavesurfer.js";

const WaveSurferVisualizer = forwardRef(({ blob }, ref) => {
    const waveformRef = useRef(null);
    const wavesurferRef = useRef(null);
    const [playing, setPlaying] = useState(false);
    const [currentTime, setCurrentTime] = useState(0);
    const intervalRef = useRef(null);

    useImperativeHandle(ref, () => ({
        play: () => {
            if (wavesurferRef.current && !wavesurferRef.current.isPlaying()) {
                wavesurferRef.current.play();
                setPlaying(true);
                startTimer();
            }
        },
        pause: () => {
            if (wavesurferRef.current && wavesurferRef.current.isPlaying()) {
                wavesurferRef.current.pause();
                setPlaying(false);
            }
        },
        isPlaying: () => {
            return playing;
        },
        getCurrentTime: () => {
            return currentTime;
        },
    }));
    const startTimer = () => {
        stopTimer();
        intervalRef.current = setInterval(() => {
            if (wavesurferRef.current) {
                const time = wavesurferRef.current.getCurrentTime();
                setCurrentTime(time);
                //console.log(time);
            }
        }, 200);
    };

    const stopTimer = () => {
        if (intervalRef.current) {
            clearInterval(intervalRef.current);
            intervalRef.current = null;
        }
    };

    useEffect(() => {
        if (blob && waveformRef.current) {
            const url = URL.createObjectURL(blob);

            

            wavesurferRef.current = WaveSurfer.create({
                container: waveformRef.current,
                waveColor: "lightblue",
                progressColor: "#3b82f6",
                cursorColor: "#000000",
                barWidth: 1,
                barGap: 0,
                height: 50,
                responsive: true,
            });

            wavesurferRef.current.load(url);
            wavesurferRef.current.on("ready", () => {
                setCurrentTime(0);
            });
            wavesurferRef.current.on('finish', () => {
                setPlaying(false);
                setCurrentTime(0);
                stopTimer();
            });
            return () => {
                wavesurferRef.current.destroy();
                URL.revokeObjectURL(url);
            };
        } 

    }, [blob]);

    return <div ref={waveformRef} className="w-[350px] h-[50px]" />;
});

export default WaveSurferVisualizer;
