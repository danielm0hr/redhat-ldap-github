import React, { useRef, useEffect } from "react";
import ReactDOM from "react-dom";
import ForceGraph2D from "react-force-graph-2d";
// import "./styles.css";

var myArray = ["ba", "be", "bu"];

function App() {
  let myData = {
    nodes: [{ id: "Fix" }, { id: "Assemble" }], //props.processes.map(name => ({id: name})),
    links: [{ source: "Assemble", target: "Fix", value: 5 }] //props.processes.map((name, index, array) => ({source: name, target: array[index+1], value: 5}))
  };
  myData.nodes = myArray.map(item => ({ id: item }));
  myData.links = myArray
    .map((item, index, array) => ({
      source: item,
      target: array[index + 1],
      value: 5
    }))
    .filter((item, index, array) => index + 1 < array.length);
  const forceRef = useRef(null);
  useEffect(() => {
    forceRef.current.d3Force("charge").strength(-500);
  });
  return (
    <ForceGraph2D
      graphData={myData}
      nodeAutoColorBy="group"
      nodeLabel="id"
      nodeCanvasObject={(node, ctx, globalScale) => {
        const label = node.id;
        const fontSize = 12 / globalScale;
        ctx.font = `${fontSize}px Sans-Serif`;
        const textWidth = ctx.measureText(label).width;
        const bckgDimensions = [textWidth + 3, fontSize + 3].map(
          n => n + fontSize * 0.2
        ); // some padding
        ctx.fillStyle = "rgba(240, 245, 250, 0.8)";
        ctx.fillRect(
          node.x - bckgDimensions[0] / 2,
          node.y - bckgDimensions[1] / 2,
          ...bckgDimensions
        );
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillStyle = node.color;
        ctx.fillText(label, node.x, node.y);
      }}
      linkDirectionalParticles="value"
      linkDirectionalParticleSpeed={d => d.value * 0.001}
      linkCurvature="curvature"
      enablePointerInteraction={true}
      linkDirectionalParticleWidth={1}
      ref={forceRef}
    />
  );
}

const rootElement = document.getElementById("root");
ReactDOM.render(<App />, rootElement);
