import { ButtonProps } from "@syncfusion/ej2-react-popups";
import React from "react";

const Knowlage_menu = () => {
    return (
        <div className=" w-screen">
            <div style={{ width: '100vw' }}>

                <div className="absolute top-72 right-80 bg-slate-50 h-[600px] w-64 p-4 shadow-lg rounded-3xl z-50">
                    <div className="relative -top-4 right-4  bg-blue-900 h-[60px] w-64 p-4 shadow-lg rounded-t-3xl z-51">
                        <h2 className="text-lg font-semibold text-white">Actions</h2>
                    </div>
                    <p>Action</p>
                </div>

                <div className="fixed top-72 right-10 bg-slate-50 h-[600px] w-64 p-4 shadow-lg rounded-3xl z-50">
                    <div className="relative -top-4 right-4  bg-blue-900 h-[60px] w-64 p-4 shadow-lg rounded-t-3xl z-51">
                        <h2 className="text-lg font-semibold text-white">Objetcs</h2>
                    </div>
                    <p>Object</p>
                </div>
                Knowlage_menu
            </div>
        </div>
    );
}
export default Knowlage_menu