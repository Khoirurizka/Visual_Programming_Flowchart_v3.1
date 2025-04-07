import React, { useEffect, useState } from 'react';
import { Send, Mic } from 'react-feather';
import { TooltipComponent } from '@syncfusion/ej2-react-popups';
import { sendProptToLLMServer } from '../utilities';
import * as go from 'gojs';
import { ReactDiagram } from 'gojs-react';
import { useStateContext } from '../contexts/ContextProvider';
import './Home_menu.css';  // contains .diagram-component CSS

const { ipcRenderer } = window.require("electron");

function initDiagram(layerspacing, columnSpacing) {
  const diagram = new go.Diagram({
    'undoManager.isEnabled': true,
    allowResize: true,
    layout: new go.LayeredDigraphLayout(
      {
        direction: 90,
        layerSpacing: layerspacing,
        columnSpacing: columnSpacing,
        cycleRemoveOption: go.LayeredDigraphCycleRemove.DepthFirst,
        initializeOption: go.LayeredDigraphInit.DepthFirstIn,
        layeringOption: go.LayeredDigraphLayering.OptimalLinkLength,
        aggressiveOption: go.LayeredDigraphAggressive.Less, //Crossing is less
        setsPortSpots: true,
        packOption: 1

      }
    ),
    'clickCreatingTool.archetypeNodeData': { text: 'new node', color: 'lightblue' },
    model: new go.GraphLinksModel({
      linkKeyProperty: 'key'
    })
  });

  diagram.nodeTemplateMap.add("Process",
    new go.Node("Auto")
      .bindTwoWay("location", "loc",
        (loc, node) => {
          const parsedPoint = go.Point.parse(loc);
          const xOffset = node.actualBounds.width / 2;
          const yOffset = node.actualBounds.height / 2;
          return new go.Point(parsedPoint.x - xOffset, parsedPoint.y - yOffset);
        },
        (loc, node) => {
          const parsedPoint = go.Point.parse(loc);
          const xOffset = node.actualBounds.width / 2;
          const yOffset = node.actualBounds.height / 2;
          return new go.Point(parsedPoint.x - xOffset, parsedPoint.y - yOffset);
        })
      .add(
        new go.Shape("Rectangle", {
          name: "Process",
          fill: "white",
          strokeWidth: 1,
          portId: "",
          fromLinkable: false,
          toLinkable: false,
          fromLinkableDuplicates: true,
          toLinkableDuplicates: true,
          fromSpot: go.Spot.AllSides,
          toSpot: go.Spot.NotBottomSide,
          desiredSize: new go.Size(100, 40)
        })
          .bind("fromSpot")
          .bind("fill", "color"),
        new go.Panel("Vertical", { margin: 0 })
          .add(
            new go.TextBlock({ column: 0, row: 0, columnSpan: 3, margin: 2, alignment: go.Spot.Center, editable: true })
              .bind("text", "command"),
            new go.TextBlock({ column: 0, row: 0, columnSpan: 3, margin: 2, alignment: go.Spot.Center, editable: true })
              .bind("text", "argument"),
          )
      )
  );

  diagram.nodeTemplateMap.add("Decision",
    new go.Node("Auto")
      .bindTwoWay("location", "loc",
        // Parse the location and apply an offset based on node size when loading
        (loc, node) => {
          const parsedPoint = go.Point.parse(loc);
          const xOffset = node.actualBounds.width / 2;
          const yOffset = node.actualBounds.height / 2;
          return new go.Point(parsedPoint.x - xOffset, parsedPoint.y - yOffset);
        },
        (loc, node) => {
          const parsedPoint = go.Point.parse(loc);
          const xOffset = node.actualBounds.width / 2;
          const yOffset = node.actualBounds.height / 2;
          return new go.Point(parsedPoint.x - xOffset, parsedPoint.y - yOffset);
        })
      .add(
        new go.Shape("Diamond", {
          name: "Decision",
          fill: "white",
          strokeWidth: 1,
          portId: "",
          fromLinkable: false,
          toLinkable: false,
          fromLinkableDuplicates: true,
          toLinkableDuplicates: true,
          fromSpot: go.Spot.NotTopSide,
          toSpot: go.Spot.TopCenter,
          desiredSize: new go.Size(100, 100)
        })
          .bind("fill", "color"),
        new go.TextBlock({ margin: 2, alignment: go.Spot.Center, verticalAlignment: go.Spot.Center, editable: true })
          .bindTwoWay("text", "command")
      )
  );

  diagram.nodeTemplateMap.add("StartEnd",
    new go.Node("Auto")
      .bindTwoWay("location", "loc",
        // Parse the location and apply an offset based on node size when loading
        (loc, node) => {
          const parsedPoint = go.Point.parse(loc);

          const xOffset = node.actualBounds.width / 2;
          const yOffset = node.actualBounds.height / 2;
          return new go.Point(parsedPoint.x - xOffset, parsedPoint.y - yOffset);

        },
        (loc, node) => {
          const parsedPoint = go.Point.parse(loc);
          const xOffset = node.actualBounds.width / 2;
          const yOffset = node.actualBounds.height / 2;
          return new go.Point(parsedPoint.x - xOffset, parsedPoint.y - yOffset);
        }
      )
      .add(
        new go.Shape("Ellipse", {
          name: "StartEnd",
          fill: "white",
          strokeWidth: 1,
          portId: "",
          fromLinkable: false,
          toLinkable: false,
          fromLinkableDuplicates: true,
          toLinkableDuplicates: true,
          fromSpot: go.Spot.AllSides,
          toSpot: go.Spot.AllSides,
          desiredSize: new go.Size(120, 50)
        })
          .bind("fill", "color"),
        new go.TextBlock({ margin: 2, editable: false })
          .bindTwoWay("text", "command")
      )
  );

  // Define flowchart-style link template
  diagram.linkTemplate =
    new go.Link({
      selectable: true,
      deletable: false,
      routing: go.Routing.AvoidsNodes,  // Avoid nodes to create clean flowchart lines
      curve: go.Curve.JumpOver,       // Jump over intersecting lines for readability
      corner: 10,                    // Rounded corners for smoother lines
      relinkableFrom: true,
      relinkableTo: true,  // Allow reconnecting links
      reshapable: true,              // Allow links to be reshaped
      toShortLength: 2               // Shortens the arrow point for clarity
    })
      .add(
        new go.Shape({ strokeWidth: 0.5 }),  // Line thickness
        new go.Shape({ toArrow: "Standard", }),  // Arrowhead
        new go.TextBlock({
          alignmentFocus: new go.Spot(0, 0.5, -3, 0),// segmentOffset: new go.Point(0, 20),
        }).bind("text", "text")//.bind("")   // Bind link label text
      );

  return diagram;
}

function handleModelChange(changes) {
  // Handle model changes here
}

function DiagramComponent({ layerspacing = 30, columnSpacing = 30 }) {
  let [nodeDataArray, setNodeDataArray] = useState([]);
  let [linkDataArray, setLinkDataArray] = useState([]);

  const diagramRef = React.useRef(null);

  useEffect(() => {
    // Listen for 'increment-timer' event from Electron main process
    ipcRenderer.on("update_graph", (event, jsonData) => {
      try {
        console.log("Received data from main process:", jsonData);
        //clear Node and Link
        setNodeDataArray([]);
        setLinkDataArray([]);
        // Parse and update state with the respective arrays
        setNodeDataArray(jsonData.nodeDataArray);
        setLinkDataArray(jsonData.linkDataArray);

      } catch (error) {
        console.error("Error parsing JSON data:", error);
      }
    });
  }, []);

  useEffect(() => {
    if (diagramRef.current) {
      const diagram = diagramRef.current.getDiagram();
      if (diagram) {
        diagram.startTransaction();
        diagram.layout.layerSpacing = layerspacing;
        diagram.layout.columnSpacing = columnSpacing;
        diagram.commitTransaction("Update layout spacing");
      }
    }
  }, [layerspacing, columnSpacing]);
  return (
    <div>
      <ReactDiagram
        ref={diagramRef}

        initDiagram={() => initDiagram(layerspacing, columnSpacing)}
        divClassName='graph-panel'
        nodeDataArray={nodeDataArray}

        linkDataArray={linkDataArray}
        //  [{ 'key': '-1s', 'from': -1, 'to': 0 }, { 'key': -2, 'from': 0, 'to': 1 }, { 'key': -3, 'from': 1, 'to': 2 }, { 'key': -4, 'from': 2, 'to': 3 }, { 'key': '-5s', 'from': -3, 'to': 4 }, { 'key': -5, 'from': 3, 'to': 4 }, { 'key': -6, 'from': 4, 'to': 5 }, { 'key': '-7e', 'from': 3, 'to': -2 }, { 'key': '-8e', 'from': 5, 'to': -4 }]
        /*[
        { key: -1, from: 0, to: 1 },
        { key: -2, from: -1, to: -2 },
        { key: -3, from: 2, to: 3, text: "True" },
        { key: -4, from: 2, to: 1, text: "False" },
        { key: -5, from: 3, to: 4 },
        { key: -6, from: 5, to: 6 },
        { key: -7, from: 6, to: 7 },
        { key: -8, from: 7, to: 8, text: "True" },
        { key: -9, from: 7, to: 6, text: "False" },
        { key: -10, from: 8, to: 9 }
      ]*///}
        onModelChange={handleModelChange}
      />
    </div>
  );
}


const Home_menu = () => {
  const [messageUser, setMessageUser] = useState("");
  const { frameReceived_ScrewDriver, setframeReceived_ScrewDriver } = useStateContext();

  return (
    <div className=" w-screen">
      <div className="fixed top-72 right-10 bg-slate-50 h-[600px] w-96 p-4 shadow-lg rounded-3xl z-50">
        <div className="relative -top-4 right-4 bg-blue-900 h-[60px] w-96 p-4 shadow-lg rounded-t-3xl z-51">
          <h2 className="text-lg font-semibold text-white">Prompt History</h2>
        </div>
        <p>Chat</p>
      </div>

      <div className="fixed bottom-10 left-1/2 transform -translate-x-1/2 bg-slate-50 p-4 shadow-lg rounded-2xl z-50 w-[800px]" style={{ borderRadius: '30px' }}>
        <div className="flex items-center gap-2 h-full">
          <textarea
            placeholder="Type a message..."
            value={messageUser}
            onChange={(e) => setMessageUser(e.target.value)}
            className="flex-1 h-full  px-3 py-2 bg-transparent focus:outline-none resize-none leading-[1.5rem]"
          />
          <TooltipComponent
            content="Send"
            position="BottomRight"
            mouseTrail={true}
            opensOn="Hover"  >
            <button onClick={() => sendProptToLLMServer(messageUser, frameReceived_ScrewDriver)} className="px-4 py-2 rounded-full bg-transparent hover:bg-gray-100">
              <Send size={30} className="drop-shadow-md" />
            </button>
          </TooltipComponent>
          <TooltipComponent
            content="Use Voice"
            position="BottomRight"
            mouseTrail={true}
            opensOn="Hover"  >
            <button className="p-2 rounded-full bg-transparent hover:bg-gray-100">
              <Mic size={30} className="drop-shadow-md" />
            </button>
          </TooltipComponent>

        </div>
      </div>
      <div className="graph">
        <DiagramComponent />
      </div>
    </div>
  );
}
export default Home_menu