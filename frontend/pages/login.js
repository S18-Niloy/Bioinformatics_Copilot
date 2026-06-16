import { useState } from "react";
const API = process.env.NEXT_PUBLIC_API_URL;

export default function Login() {
  const [username, setU] = useState(""); const [password, setP] = useState("");
  const [mode, setMode] = useState("login"); const [err, setErr] = useState("");
  async function submit(e) {
    e.preventDefault(); setErr("");
    try {
      const r = await fetch(`${API}/api/users/${mode}`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      if (!r.ok) throw new Error((await r.json()).detail || "Failed");
      const d = await r.json();
      localStorage.setItem("bc_token", d.access_token);
      localStorage.setItem("bc_user", username);
      window.location.href = "/";
    } catch (e) { setErr(e.message); }
  }
  return (
    <div className="card" style={{maxWidth:420, margin:"40px auto"}}>
      <h1>{mode === "login" ? "Login" : "Register"}</h1>
      <form onSubmit={submit}>
        <input placeholder="username" value={username} onChange={e=>setU(e.target.value)} required />
        <div style={{height:10}}/>
        <input type="password" placeholder="password" value={password} onChange={e=>setP(e.target.value)} required />
        <div style={{height:14}}/>
        <button type="submit">{mode === "login" ? "Login" : "Register"}</button>
      </form>
      {err && <p style={{color:"#ff7676"}}>{err}</p>}
      <p className="muted" style={{marginTop:14, cursor:"pointer"}} onClick={()=>setMode(mode==="login"?"register":"login")}>
        {mode === "login" ? "Need an account? Register" : "Have an account? Login"}
      </p>
    </div>
  );
}
