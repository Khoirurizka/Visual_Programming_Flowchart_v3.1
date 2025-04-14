import { ButtonProps } from "@syncfusion/ej2-react-popups";
import React from "react";
import { TooltipComponent } from '@syncfusion/ej2-react-popups';
import { logo, home_menu, kowlagebase_menu, cam_menu, interaction_menu } from '../assets'
import "./Navbar.css";
import { useStateContext } from '../contexts/ContextProvider';
import { useNavigate } from 'react-router-dom';

const Navbar = () => {
    const { activeSideBar, setActiveSideBar,activeMenu, setActiveMenu } = useStateContext();

    //const navigate = useNavigate();
    return (

        <div className="navbar">
            <div className="h-fit">
                <TooltipComponent
                    content="Show/Hide Menu"
                    position="BottomRight"
                    mouseTrail={true}
                    opensOn="Hover"
                >
                    <button type='button' onClick={() => activeSideBar ? setActiveSideBar(false) : setActiveSideBar(true)} className='text-3xl  hover:drop-shadow-xl '>
                        <img src={logo} alt="" className="w-auto h-20 ml-0" draggable={false} />
                    </button>
                </TooltipComponent>
            </div>
            <div className="flex justify-center items-center ml-10">
                <TooltipComponent
                    content="Home"
                    position="BottomRight"
                    mouseTrail={true}
                    opensOn="Hover"                >
                    <button type='button' onClick={() => setActiveMenu(0)} className='text-3xl p-3 hover:drop-shadow-xl hover:bg-light-gray text-white'
                        style={{ background: 'transparent', borderRadius: '50%' }}
                    >
                        <img src={home_menu} alt="" className="w-auto h-12" draggable={false} />
                    </button>
                </TooltipComponent>
                <TooltipComponent
                    content="Knowledge"
                    position="BottomRight"
                    mouseTrail={true}
                    opensOn="Hover"                >
                    <button type='button' onClick={() => setActiveMenu(1)} className='text-3xl p-3 hover:drop-shadow-xl hover:bg-light-gray text-white'
                        style={{ background: 'transparent', borderRadius: '50%' }}
                    >
                        <img src={kowlagebase_menu} alt="" className="w-auto h-12" draggable={false} />
                    </button>
                </TooltipComponent>
                <TooltipComponent
                    content="Camera"
                    position="BottomRight"
                    mouseTrail={true}
                    opensOn="Hover"                >
                    <button type='button' onClick={() => setActiveMenu(2)} className='text-3xl p-3 hover:drop-shadow-xl hover:bg-light-gray text-white'
                        style={{ background: 'transparent', borderRadius: '50%' }}
                    >
                        <img src={cam_menu} alt="" className="w-auto h-12" draggable={false} />
                    </button>
                </TooltipComponent>
                <TooltipComponent
                    content="Robot Skills"
                    position="BottomRight"
                    mouseTrail={true}
                    opensOn="Hover"                >
                    <button type='button' onClick={() => setActiveMenu(3)} className='text-3xl p-3 hover:drop-shadow-xl hover:bg-light-gray text-white'
                        style={{ background: 'transparent', borderRadius: '50%' }}
                    >
                        <img src={interaction_menu} alt="" className="w-auto h-12" draggable={false} />
                    </button>
                </TooltipComponent>
            </div>
        </div>

    );
}
export default Navbar