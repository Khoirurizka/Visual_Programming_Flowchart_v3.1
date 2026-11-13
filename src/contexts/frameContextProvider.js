import React, { createContext, useContext, useState } from 'react';

const StateContext = createContext();

export const frameContextProvider = ({ children }) => {
  const [frameReceived_ScrewDriver, setframeReceived_ScrewDriver] = useState(undefined);
  const [frameReceived_Gripper, setframeReceived_Gripper] = useState(undefined);
  const [frameReceived_BEV, setframeReceived_BEV] = useState(undefined); 

  return (
    <StateContext.Provider value={{
      frameReceived_ScrewDriver, setframeReceived_ScrewDriver,
      frameReceived_Gripper, setframeReceived_Gripper,
      frameReceived_BEV, setframeReceived_BEV
    }}>
      {children}
    </StateContext.Provider>
  );
};

export const useStateFrameContext = () => useContext(StateContext);
