import React, { useEffect, useState } from 'react';
import * as go from 'gojs';
import { ReactDiagram } from 'gojs-react';
import './DiagramComponent.css';  // contains .diagram-component CSS

const { ipcRenderer } = window.require("electron");

function initDiagram(layerspacing, columnSpacing) {
  const diagram = new go.Diagram({
    'undoManager.isEnabled': true,
    allowResize: true,
    grid: go.GraphObject.make(go.Panel, "Grid",
      { gridCellSize: new go.Size(100, 100) },
      go.GraphObject.make(go.Shape, "LineH", { stroke: "lightgray", strokeWidth: 0.5 }),
      go.GraphObject.make(go.Shape, "LineV", { stroke: "lightgray", strokeWidth: 0.5 })
    ),
    "grid.visible": true,
    "draggingTool.isGridSnapEnabled": true,
    "resizingTool.isGridSnapEnabled": true,
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
        divClassName='graph-panel'
        ref={diagramRef}
        initDiagram={() => initDiagram(layerspacing, columnSpacing)}
        nodeDataArray={nodeDataArray}
        linkDataArray={linkDataArray}

        onModelChange={handleModelChange}
      />
    </div>
  );
}
export default DiagramComponent;