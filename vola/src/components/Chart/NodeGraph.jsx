import { ButtonProps } from "@syncfusion/ej2-react-popups";
import Graph from "react-graph-vis";
import './NodeGraph.css';
import React from "react";

const NodeGraph = () => {
    const centerX = -window.innerWidth / 2 + 400;
    const centerY = -window.innerHeight / 2;
    const graph = {
        nodes: [
            { id: 'k-0', label: "Node 0", title: "Node 0", x: centerX + 55, y: centerY + 51 },
            { id: 'k-1', label: "Node 1", title: "Node 1", x: centerX + 52, y: centerY + 79 },
            { id: 'k-2', label: "Node 2", title: "Node 2", x: centerX + 22, y: centerY + 28 },
            { id: 'k-3', label: "Node 3", title: "Node 3", x: centerX + 38, y: centerY + 95 },
            { id: 'k-4', label: "Node 4", title: "Node 4", x: centerX + 0, y: centerY + 78 },
            { id: 'k-5', label: "Node 5", title: "Node 5", x: centerX + 55, y: centerY + 51 },
            { id: 'k-6', label: "Node 6", title: "Node 6", x: centerX + 3, y: centerY + 89 },
            { id: 'k-7', label: "Node 7", title: "Node 7", x: centerX + 49, y: centerY + 29 },
            { id: 'k-8', label: "Node 8", title: "Node 8", x: centerX + 22, y: centerY + 28 },
            { id: 'k-9', label: "Node 9", title: "Node 9", x: centerX + 37, y: centerY + 100 },
            { id: 'k-10', label: "Node 10", title: "Node 10", x: centerX + 45, y: centerY + 96 },
            { id: 'k-11', label: "Node 11", title: "Node 11", x: centerX + 50, y: centerY + 13 },
            { id: 'k-12', label: "Node 12", title: "Node 12", x: centerX + 41, y: centerY + 70 },
            { id: 'k-13', label: "Node 13", title: "Node 13", x: centerX + 90, y: centerY + 20 },
            { id: 'k-14', label: "Node 14", title: "Node 14", x: centerX + 12, y: centerY + 50 }
        ],
        edges: [
            { id: 'e0', from: 'k-0', to: 'k-5' },
            { id: 'e1', from: 'k-0', to: 'k-6' },
            { id: 'e2', from: 'k-0', to: 'k-7' },
            { id: 'e3', from: 'k-0', to: 'k-8' },
            { id: 'e4', from: 'k-0', to: 'k-9' },
            { id: 'e5', from: 'k-0', to: 'k-10' },
            { id: 'e6', from: 'k-0', to: 'k-11' },
            { id: 'e7', from: 'k-0', to: 'k-12' },
            { id: 'e8', from: 'k-0', to: 'k-13' },
            { id: 'e9', from: 'k-0', to: 'k-14' },
            { id: 'e10', from: 'k-1', to: 'k-5' },
            { id: 'e11', from: 'k-1', to: 'k-6' },
            { id: 'e12', from: 'k-1', to: 'k-7' },
            { id: 'e13', from: 'k-1', to: 'k-8' },
            { id: 'e14', from: 'k-1', to: 'k-9' },
            { id: 'e15', from: 'k-1', to: 'k-10' },
            { id: 'e16', from: 'k-1', to: 'k-11' },
            { id: 'e17', from: 'k-1', to: 'k-12' },
            { id: 'e18', from: 'k-1', to: 'k-13' },
            { id: 'e19', from: 'k-1', to: 'k-14' },
            { id: 'e20', from: 'k-2', to: 'k-5' },
            { id: 'e21', from: 'k-2', to: 'k-6' },
            { id: 'e22', from: 'k-2', to: 'k-7' },
            { id: 'e23', from: 'k-2', to: 'k-8' },
            { id: 'e24', from: 'k-2', to: 'k-9' },
            { id: 'e25', from: 'k-2', to: 'k-10' },
            { id: 'e26', from: 'k-2', to: 'k-11' },
            { id: 'e27', from: 'k-2', to: 'k-12' },
            { id: 'e28', from: 'k-2', to: 'k-13' },
            { id: 'e29', from: 'k-2', to: 'k-14' },
            { id: 'e30', from: 'k-3', to: 'k-5' },
            { id: 'e31', from: 'k-3', to: 'k-6' },
            { id: 'e32', from: 'k-3', to: 'k-7' },
            { id: 'e33', from: 'k-3', to: 'k-8' },
            { id: 'e34', from: 'k-3', to: 'k-9' },
            { id: 'e35', from: 'k-3', to: 'k-10' },
            { id: 'e36', from: 'k-3', to: 'k-11' },
            { id: 'e37', from: 'k-3', to: 'k-12' },
            { id: 'e38', from: 'k-3', to: 'k-13' },
            { id: 'e39', from: 'k-3', to: 'k-14' },
            { id: 'e40', from: 'k-4', to: 'k-5' },
            { id: 'e41', from: 'k-4', to: 'k-6' },
            { id: 'e42', from: 'k-4', to: 'k-7' },
            { id: 'e43', from: 'k-4', to: 'k-8' },
            { id: 'e44', from: 'k-4', to: 'k-9' },
            { id: 'e45', from: 'k-4', to: 'k-10' },
            { id: 'e46', from: 'k-4', to: 'k-11' },
            { id: 'e47', from: 'k-4', to: 'k-12' },
            { id: 'e48', from: 'k-4', to: 'k-13' },
            { id: 'e49', from: 'k-4', to: 'k-14' }
        ]
    };


    const options = {
        autoResize: true,
        layout: {
            hierarchical: false
        },
        edges: {
            color: {
                color: "#000814",       // default color
                highlight: "#06a77d",   
                hover:"#f0c808"
            },
            width: 1,
            selectionWidth: 1
        },
        nodes: {
            color: {
                color: "#bbdefb",       // default color
                highlight: {background:"#90caf9",border:"#133c55"},   
                hover: {background:"#bbdefb",border:"#133c55"},
            },
            borderWidth: 1,
            borderWidthSelected: 2,
            font: {
                color: "#343434",

            },
        },
        physics: {
            enabled: true, // must be true to allow force-based layout
            solver: 'forceAtlas2Based',
            forceAtlas2Based: {
                gravitationalConstant: -50,
                centralGravity: 0.01,
                springLength: 150, // <--- this is the "min distance"
                springConstant: 0.08,
                avoidOverlap: 1
            },
            stabilization: {
                enabled: true,
                iterations: 200
            }
        },
        interaction: {
            dragNodes: true,
            dragView: true,
            zoomView: true,
            hover: true
        },
        height: "100%"
    };


    const events = {
        select: function (event) {
            var { nodes, edges } = event;
        }
    };



    return (
        <Graph divClassName='node-graph'
            graph={graph}
            options={options}
            events={events}
            getNetwork={network => {
                // Trigger stabilization on mount
                network.setOptions({ physics: { enabled: true } });
                network.stabilize();

                // Optionally disable physics after stabilization to lock layout
                setTimeout(() => {
                    network.setOptions({ physics: { enabled: true } });
                }, 1000);
            }}
        />
    );
}
export default NodeGraph