import { useState } from "react";
const API = process.env.NEXT_PUBLIC_API_URL;

export default function Chat() {
  const [q, setQ] = useState("What is GC content?");
  const [resp, setResp] = useState(null);
  const [loading, setLoading] = useState(false);

  async function ask() {
    setLoading(true); setResp(null);
    const token = localStorage.getItem("bc_token");
    if (!token) { window.location.href = "/login"; return; }
    const r = await fetch(`${API}/api/chat`, {
      method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify({ question: q }),
    });
    setResp(await r.json()); setLoading(false);
  }

  return (
    <div>
      <h1>Bio Chat (RAG)</h1>
      <div className="card">
        <textarea rows={3} value={q} onChange={e=>setQ(e.target.value)} />
        <div style={{height:10}}/>
        <button onClick={ask} disabled={loading}>{loading ? "Thinking..." : "Ask"}</button>
      </div>
      {resp && (
        <div className="card">
          <h2>Answer</h2>
          <p>{resp.answer}</p>
          <h3>Sources</h3>
          {resp.sources?.map((s, i) => (
            <pre key={i}>[{s.score.toFixed(3)}] {s.text}</pre>
          ))}
        </div>
      )}
    </div>
  );
}
