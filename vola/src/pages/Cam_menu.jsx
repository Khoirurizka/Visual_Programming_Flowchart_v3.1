import { ButtonProps } from "@syncfusion/ej2-react-popups";
import React, { useState } from "react";
import { ScrewDriverFrameRender, BEV_FrameRender, GripperFrameRender } from '../components';

const Cam_menu = () => {
    const [message, setMessage] = useState("");

    return (
        <div className=" w-full">
            <div style={{ width: '100%' }}>
                <div className="flex  justify-center gap-x-20 mt-10 ml-10">

                    <div className=" Left_Hand_Cam flex flex-col items-center  static space-y-6 top-[40px]" >
                        <div className="relative  bg-blue-900 h-[60px] w-[440px] m-0 p-4 shadow-lg rounded-3xl z-51">
                            <h2 className="text-lg font-semibold text-white">Left Hand Cam</h2>
                        </div>
                        <div className="relative   bg-slate-50 h-[320px] w-[440px] m-0 p-4 shadow-lg rounded-3xl z-51">
                            <div className="flex items-center justify gap-2 w-full h-full text-center">
                                <div className="ScrewDriverFrameRender"><GripperFrameRender /></div>

                            </div>
                        </div>
                        <div className="relative  bg-slate-50 h-[250px] w-[440px] m-0 p-4 shadow-lg rounded-3xl z-51">
                            <div className="flex items-center gap-2 h-full">
                                <textarea
                                    placeholder="VLM Left Hand Cam"
                                    value={message}
                                    readOnly
                                    className="flex-1 h-full rounded px-3 py-2 bg-transparent focus:outline-none resize-none"
                                />
                            </div>
                        </div>
                    </div>

                    <div className="BEV_Cam static flex flex-col items-center   space-y-6 top-[40px]" >
                        <div className="relative  bg-blue-900 h-[60px] w-[440px] m-0 p-4 shadow-lg rounded-3xl z-51">
                            <h2 className="text-lg font-semibold text-white">BEV Cam</h2>
                        </div>
                        <div className="relative   bg-slate-50 h-[320px] w-[440px] m-0 p-4 shadow-lg rounded-3xl z-51">
                            <div className="flex items-center justify gap-2 w-full h-full text-center">
                                <div className="ScrewDriverFrameRender"><BEV_FrameRender /></div>
                            </div>
                        </div>
                        <div className="relative  bg-slate-50 h-[250px] w-[440px] m-0 p-4 shadow-lg rounded-3xl z-51">
                            <div className="flex items-center gap-2 h-full">
                                <textarea
                                    placeholder="VLM BEV Cam"
                                    className="flex-1 h-full rounded px-3 py-2 bg-transparent focus:outline-none resize-none"
                                />
                            </div>
                        </div>
                    </div>


                    <div className="BEV_Cam Right_Hand_Cam flex flex-col items-center   space-y-6 top-[40px]" >
                        <div className="relative  bg-blue-900 h-[60px] w-[440px] m-0 p-4 shadow-lg rounded-3xl z-51">
                            <h2 className="text-lg font-semibold text-white">Right Hand Cam</h2>
                        </div>
                        <div className="relative bg-slate-50 h-[320px] w-[440px] m-0 p-4 shadow-lg rounded-3xl z-51">
                            <div className="flex items-center justify-center w-full h-full text-center">
                                <div className="ScrewDriverFrameRender max-h-full max-w-full p-[5px] box-border">
                                    <div className="h-full w-full">
                                        <ScrewDriverFrameRender />
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="relative  bg-slate-50 h-[250px] w-[440px] m-0 p-4 shadow-lg rounded-3xl z-51">
                            <div className="flex items-center gap-2 h-full">
                                <textarea
                                    placeholder="VLM Right Hand Cam"
                                    className="flex-1 h-full rounded px-3 py-2 bg-transparent focus:outline-none resize-none"
                                />
                            </div>
                        </div>
                    </div>

                </div>
            </div>
        </div>


    );
}
export default Cam_menu