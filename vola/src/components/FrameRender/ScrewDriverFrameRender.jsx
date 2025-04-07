import React, { useEffect, useState } from 'react';
import { useStateContext } from '../../contexts/ContextProvider';

const { ipcRenderer } = window.require("electron");

function ScrewDriverFrameRender() {
  const [frameReceived, setframeReceived] = useState(null);
  const { frameReceived_ScrewDriver, setframeReceived_ScrewDriver } = useStateContext();

  useEffect(() => {
    ipcRenderer.on("screw_diver_capture", (event, File_image) => {
      try {
        setframeReceived(File_image.image);
        setframeReceived_ScrewDriver(File_image.image);
      } catch (error) {
        console.error("Error parsing JSON data:", error);
      }
    });

    // Optional cleanup to avoid duplicate listeners
    return () => {
      ipcRenderer.removeAllListeners("screw_diver_capture");
    };
  }, []);

  return (
    <div
      style={{
        width: '100%',
        height: '100%',
        padding: '5px',
        boxSizing: 'border-box',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
      }}
    >
      {frameReceived ? (
        <img
          src={`data:image/jpeg;base64,${frameReceived}`}
          alt="Received"
          style={{
            maxWidth: '100%',
            maxHeight: '100%',
            objectFit: 'contain',
            borderRadius: '0.5rem',
          }}
        />
      ) : (
        <p style={{ textAlign: 'center', fontSize: '0.9rem' }}>
          The image is currently unavailable. Please wait for the right robot to capture it.
        </p>
      )}
    </div>
  );
}

export default ScrewDriverFrameRender;
