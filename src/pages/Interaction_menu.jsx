import { ButtonProps } from "@syncfusion/ej2-react-popups";
import React from "react";
import {PLYViewer} from "../components"
const Interaction_menu = () => {
    return (
        <div className=" w-screen">
            <div className="fixed top-44 right-10 bg-slate-50 h-[360px] w-400 p-4 shadow-lg rounded-3xl z-50">
                <div className="relative -top-4 right-4  bg-blue-900 h-[60px] w-400 p-4 shadow-lg rounded-t-3xl z-51">
                    <h2 className="text-lg font-semibold text-white">Robot 1 Plan</h2>
                </div>
                <p>Plan list</p>
            </div>

            <div className="fixed bottom-44 right-10 bg-slate-50 h-[360px] w-400 p-4 shadow-lg rounded-3xl z-50">
                <div className="relative -top-4 right-4  bg-blue-900 h-[60px] w-400 p-4 shadow-lg rounded-t-3xl z-51">
                    <h2 className="text-lg font-semibold text-white">Robot 2 Plan</h2>
                </div>
                <p>Plan list</p>
            </div>
            <div style={{ width: '100vw' }}>
                <PLYViewer/>
            </div>
        </div>
 
    );
}
export default Interaction_menu