import { useState } from "react";
const API = process.env.NEXT_PUBLIC_API_URL;

function GraphView({ nodes, edges }) {
  const size = 600;
  const center = size / 2;
  const radius = Math.max(120, Math.min(220, (nodes.length * 30)));
  const nodePositions = nodes.map((node, index) => {
    const angle = (index / nodes.length) * Math.PI * 2;
    return {
      x: center + radius * Math.cos(angle),
      y: center + radius * Math.sin(angle),
    };
  });

  return (
    <svg viewBox={`0 0 ${size} ${size}`} width={size} height={size} style={{ border: "1px solid #ccc", background: "#fafafa" }}>
      {edges.map(([source, target], idx) => {
        if (source >= nodes.length || target >= nodes.length) return null;
        const a = nodePositions[source];
        const b = nodePositions[target];
        return <line key={`edge-${idx}`} x1={a.x} y1={a.y} x2={b.x} y2={b.y} stroke="#999" strokeWidth="2" />;
      })}
      {nodes.map((node, idx) => {
        const pos = nodePositions[idx];
        const color = node.pred === 1 ? "#d1495b" : "#33658a";
        return (
          <g key={node.id}>
            <circle cx={pos.x} cy={pos.y} r={28} fill={color} stroke="#333" strokeWidth="1" />
            <text x={pos.x} y={pos.y - 6} textAnchor="middle" dominantBaseline="middle" fill="#fff" fontSize="11" fontWeight="700">
              {node.name}
            </text>
            <text x={pos.x} y={pos.y + 12} textAnchor="middle" dominantBaseline="middle" fill="#fff" fontSize="10">
              {node.label}
            </text>
          </g>
        );
      })}
    </svg>
  );
}

export default function Gnn() {
  const [nodeCount, setNodeCount] = useState(5);
  const [proteinText, setProteinText] = useState("HBA,HBB,ALB,EGFR,BRCA1");
  const [graph, setGraph] = useState(null);
  const [error, setError] = useState("");

  async function generateGraph() {
    const token = localStorage.getItem("bc_token");
    if (!token) return (window.location.href = "/login");

    const names = proteinText
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean);

    const response = await fetch(`${API}/api/gnn/graph`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ node_count: Number(nodeCount), protein_names: names }),
    });

    if (!response.ok) {
      setError("Unable to generate graph. Please check your entry and try again.");
      setGraph(null);
      return;
    }

    setError("");
    setGraph(await response.json());
  }

  return (
    <div>
      <h1>GNN Protein Graph Generator</h1>
      <div className="card">
        <p className="muted">Enter the number of nodes and comma-separated protein names to build an interactive graph.</p>
        <label>
          Number of nodes:
          <input
            type="number"
            min="1"
            max="12"
            value={nodeCount}
            onChange={(e) => setNodeCount(e.target.value)}
            style={{ marginLeft: "0.5rem", width: "4rem" }}
          />
        </label>
        <label style={{ display: "block", marginTop: "1rem" }}>
          Protein names (comma-separated):
          <textarea
            value={proteinText}
            onChange={(e) => setProteinText(e.target.value)}
            rows={3}
            style={{ width: "100%", marginTop: "0.5rem" }}
          />
        </label>
        <button onClick={generateGraph} style={{ marginTop: "1rem" }}>
          Generate Graph
        </button>
        {error && <p style={{ color: "red" }}>{error}</p>}
      </div>

      {graph && (
        <div className="card" style={{ marginTop: "1rem" }}>
          <h2>Generated Graph</h2>
          <GraphView nodes={graph.nodes} edges={graph.edges} />
          <div style={{ marginTop: "1rem" }}>
            <h3>Node summary</h3>
            <pre>{JSON.stringify(graph.nodes, null, 2)}</pre>
          </div>
        </div>
      )}
    </div>
  );
}
