import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { FiSettings } from 'react-icons/fi';
import { TooltipComponent } from '@syncfusion/ej2-react-popups';
import { Navbar, Sidebar } from '../components';
import './MainPage.css';
import { useStateContext } from '../contexts/ContextProvider';
import { Home_menu, Knowlage_menu, Cam_menu, Interaction_menu } from '../pages';


const MainPage = () => {
  const { activeSideBar, setActiveSideBar, activeMenu, setActiveMenu } = useStateContext();

  return (
    <div>
      <BrowserRouter>
        <div className="flex fixed dark:bg-main-dark-bg" style={{ width: '100vw' }}>


          <div className={`dark:bg-main-bg bg-main-bg min-h-screen w-full`}>
            <header className="h-28 w-full bg-gradient-to-r from-blue-950 to-blue-800 flex items-center">
              <div className='navbar mt-2  '>
                <Navbar />
              </div>
            </header>
            <header className="h-7 w-full bg-white flex items-center drop-shadow-xl">
              <div className='navbar mt-0  font-normal text-sm'>
                Developed by Hucenrotia Human-Centered Robotics and Automation Lab
              </div>

            </header>
            <div className="flex">
              {activeSideBar ? (
                <div className='w-72 fixed  dark:bg-secondary-dark-bg bg-gray-100 drop-shadow-md'>
                  <Sidebar />
                </div>
              ) : (
                <div className='w-0 dark:bg-secondary-dark-bg'>
                  <Sidebar />
                </div>
              )}

              <div className={`dark:bg-main-bg bg-main-bg  ${activeSideBar ? 'ml-72 w-[100%-316px]' : ' ml-0 w-full'}`} >
                <div>
                  <div style={{ display: activeMenu === 0 ? 'block' : 'none' }}>
                    <Home_menu />
                  </div>
                  <div style={{ display: activeMenu === 1 ? 'block' : 'none' }}>
                    <Knowlage_menu />
                  </div>
                  <div style={{ display: activeMenu === 2 ? 'block' : 'none' }}>
                    <Cam_menu />
                  </div>
                  <div style={{ display: activeMenu === 3 ? 'block' : 'none' }}>
                    <Interaction_menu />
                  </div>
                </div>

              </div>
            </div>
          </div>
        </div>
      </BrowserRouter>
    </div>
  );
};

export default MainPage;
