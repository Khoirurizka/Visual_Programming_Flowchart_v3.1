import { ButtonProps } from "@syncfusion/ej2-react-popups";
import React from "react";
import { Link, NavLink } from "react-router-dom";
import FeatherIcon from 'feather-icons-react';
import { TooltipComponent } from '@syncfusion/ej2-react-popups';

const Sidebar = () => {
    const activeMenu = true;
    return (
        <div className=" md:overflow-hidden overflow-auto
        md:hover:overflow-auto pb-10" style={{ height: 'calc(100vh)' }}>
            {activeMenu && (<> <div className="flex justify-between items-center" >
                <div className="flex items-center justify-center h-14 w-full bg-gray-400 shadow-md">
                    <div className=' w-full flex items-center  justify-center '>
                        <p className="font-semibold text-lg underline">Projects</p>
                    </div >
                </div>

            </div>
                <div className="flex items-center justify-center h-12 w-64 bg-gray-200 m-5" style={{ borderRadius: '15px' }}>
                    <div className="w-full flex items-center justify-center">
                        <span className="font-normal text-base">Power Supply Assembly</span>
                    </div>
                </div>
            </>)}
        </div>
    );
}
export default Sidebar