import { useState } from "react";
const API = process.env.NEXT_PUBLIC_API_URL;

export default function Gnn() {
  const [out, setOut] = useState(null);
  async function run() {
    const t = localStorage.getItem("bc_token");
    if (!t) return (window.location.href = "/login");
    const r = await fetch(`${API}/api/gnn/predict`, {
      method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${t}` },
      body: JSON.stringify({}),
    });
    setOut(await r.json());
  }
  return (
    <div>
      <h1>GNN Predictor (toy PPI graph)</h1>
      <div className="card">
        <p className="muted">GCN over 10-node protein graph. Classes: enzyme vs non-enzyme.</p>
        <button onClick={run}>Run Prediction</button>
        {out && <pre>{JSON.stringify(out, null, 2)}</pre>}
      </div>
    </div>
  );
}
