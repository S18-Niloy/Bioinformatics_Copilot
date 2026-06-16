import Link from "next/link";
import { useEffect, useState } from "react";

export default function Nav() {
  const [user, setUser] = useState(null);
  useEffect(() => {
    if (typeof window !== "undefined") setUser(localStorage.getItem("bc_user"));
  }, []);
  function logout() {
    localStorage.removeItem("bc_token");
    localStorage.removeItem("bc_user");
    window.location.href = "/login";
  }
  return (
    <nav>
      <Link href="/">🧬 Bio Copilot</Link>
      <Link href="/chat">Chat</Link>
      <Link href="/sequence">Sequence</Link>
      <Link href="/gnn">GNN</Link>
      <div style={{ marginLeft: "auto" }}>
        {user ? <><span className="muted">{user}</span> &nbsp;<a onClick={logout} style={{cursor:"pointer"}}>Logout</a></>
              : <Link href="/login">Login</Link>}
      </div>
    </nav>
  );
}
