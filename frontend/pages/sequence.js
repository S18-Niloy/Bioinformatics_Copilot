import { useState } from "react";
const API = process.env.NEXT_PUBLIC_API_URL;

function authHeaders() {
  const t = typeof window !== "undefined" && localStorage.getItem("bc_token");
  return { "Content-Type": "application/json", Authorization: `Bearer ${t}` };
}

export default function Seq() {
  const [seq, setSeq] = useState("ATGGCCATTGTAATGGGCCGCTGAAAGGGTGCCCGATAGTTAG");
  const [protSeq, setProtSeq] = useState("MVLSPADKTNVKAAWGKVGAHAGEYGAEAL");
  const [seqB, setSeqB] = useState("ATGGCCATTGTGATGGGTCGGTGAAAGGGTACCCGATAGTAG");
  const [an, setAn] = useState(null);
  const [al, setAl] = useState(null);
  const [sim, setSim] = useState(null);

  async function call(path, body, setter) {
    const r = await fetch(`${API}${path}`, { method: "POST", headers: authHeaders(), body: JSON.stringify(body) });
    if (r.status === 401) return (window.location.href = "/login");
    setter(await r.json());
  }
  return (
    <div>
      <h1>Sequence Analyzer</h1>

      <div className="card">
        <h2>DNA Analysis</h2>
        <textarea rows={3} value={seq} onChange={e=>setSeq(e.target.value)} />
        <div style={{height:8}}/>
        <button onClick={()=>call("/api/sequence/analyze", {sequence: seq}, setAn)}>Analyze</button>
        {an && <pre>{JSON.stringify(an, null, 2)}</pre>}
      </div>

      <div className="card">
        <h2>Pairwise Alignment</h2>
        <textarea rows={2} value={seq} onChange={e=>setSeq(e.target.value)} />
        <div style={{height:6}}/>
        <textarea rows={2} value={seqB} onChange={e=>setSeqB(e.target.value)} />
        <div style={{height:8}}/>
        <button onClick={()=>call("/api/sequence/align", {seq_a: seq, seq_b: seqB}, setAl)}>Align</button>
        {al && <pre>{JSON.stringify(al, null, 2)}</pre>}
      </div>

      <div className="card">
        <h2>Similar Protein Search</h2>
        <textarea rows={3} value={protSeq} onChange={e=>setProtSeq(e.target.value)} />
        <div style={{height:8}}/>
        <button onClick={()=>call("/api/protein/similar", {sequence: protSeq, top_k: 5}, setSim)}>Search</button>
        {sim && <pre>{JSON.stringify(sim, null, 2)}</pre>}
      </div>
    </div>
  );
}
