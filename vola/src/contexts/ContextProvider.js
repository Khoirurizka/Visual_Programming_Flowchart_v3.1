import React, { createContext, useContext, useState } from 'react';

const StateContext = createContext();

const initialState = {
  chat: false,
  cart: false,
  userProfile: false,
  notification: false,
};

export const ContextProvider = ({ children }) => {
  const [screenSize, setScreenSize] = useState(undefined);
  const [currentColor, setCurrentColor] = useState('#03C9D7');
  const [currentMode, setCurrentMode] = useState('Light');
  const [themeSettings, setThemeSettings] = useState(false);
  const [activeSideBar, setActiveSideBar] = useState(true);
  const [isClicked, setIsClicked] = useState(initialState);
  const [activeMenu, setActiveMenu] = useState(0);
  const [frameReceived_ScrewDriver, setframeReceived_ScrewDriver] = useState(undefined);
  const [frameReceived_Gripper, setframeReceived_Gripper] = useState(undefined);
  const [frameReceived_BEV, setframeReceived_BEV] = useState(undefined);

  const setMode = (e) => {
    setCurrentMode(e.target.value);
    localStorage.setItem('themeMode', e.target.value);
  };

  const setColor = (color) => {
    setCurrentColor(color);
    localStorage.setItem('colorMode', color);
  };

  const handleClick = (clicked) => setIsClicked({ ...initialState, [clicked]: true });

  return (
    // eslint-disable-next-line react/jsx-no-constructed-context-values
    <StateContext.Provider value={{
      currentColor, currentMode,
      activeSideBar, setActiveSideBar,
      activeMenu, screenSize,
      setScreenSize, handleClick,
      isClicked, initialState,
      setIsClicked, setActiveMenu,
      setCurrentColor, setCurrentMode,
      setMode, setColor, themeSettings,
      setThemeSettings,
      frameReceived_ScrewDriver, setframeReceived_ScrewDriver,
      frameReceived_Gripper, setframeReceived_Gripper,
      frameReceived_BEV, setframeReceived_BEV
    }}>
      {children}
    </StateContext.Provider>
  );
};

export const useStateContext = () => useContext(StateContext);