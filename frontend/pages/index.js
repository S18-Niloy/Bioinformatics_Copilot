import Link from "next/link";
export default function Home() {
  return (
    <div>
      <h1>Bioinformatics Copilot</h1>
      <p className="muted">RAG assistant + sequence analysis + GNN — fully local, no paid APIs.</p>
      <div className="card"><h2>🤖 Chat</h2><p>Ask bioinformatics questions; answered via local RAG.</p><Link href="/chat"><button>Open Chat</button></Link></div>
      <div className="card"><h2>🧬 Sequence Analyzer</h2><p>GC content, ORFs, translation, pairwise alignment, protein similarity.</p><Link href="/sequence"><button>Open Analyzer</button></Link></div>
      <div className="card"><h2>🕸 GNN Predictor</h2><p>GCN over a toy protein-protein interaction graph.</p><Link href="/gnn"><button>Open GNN</button></Link></div>
    </div>
  );
}
