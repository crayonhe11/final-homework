import { getLanguage } from "./i18n";
import { useEffect, useRef, useState, type FormEvent } from "react";
import { ArrowRight, MessageCircle, X } from "lucide-react";
import type { LearningState } from "./types";
export type AgentAction = { kind: "lesson" | "question" | "coding"; id: string };
type Message = { role: "assistant" | "user"; text: string; trace?: { tool: string; status: string }[] };
const labels: Record<string, [string, string]> = {
  progress: ["检查学习进度与错题", "Inspect progress and mistakes"],
  lesson: ["读取概念导学", "Read concept lesson"],
  recommend: ["选择针对性练习", "Select targeted practice"],
  coding: ["检查编程任务", "Inspect coding tasks"],
  open_content: ["准备打开学习内容", "Prepare learning content"],
};
export default function AssistantWidget({ state, ready, teamCode, onTeamCode, onAction }: {
  state: LearningState; ready: boolean; teamCode: string; onTeamCode: (code: string) => void;
  onAction: (action: AgentAction) => boolean;
}) {
  const en = getLanguage() === "en";
  const say = (zh: string, english: string) => en ? english : zh;
  const [open, setOpen] = useState(false), [draft, setDraft] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [busy, setBusy] = useState(false), [error, setError] = useState("");
  const controller = useRef<AbortController | null>(null);
  const panelRef = useRef<HTMLElement>(null), endRef = useRef<HTMLDivElement>(null);
  useEffect(() => () => controller.current?.abort(), []);
  useEffect(() => { endRef.current?.scrollIntoView({ block: "nearest" }); }, [messages, busy, error]);
  useEffect(() => {
    if (!open) return;
    const key = (e: KeyboardEvent) => { if (e.key === "Escape") setOpen(false); };
    document.addEventListener("keydown", key);
    panelRef.current?.querySelector<HTMLInputElement>('input[type="text"]')?.focus();
    return () => document.removeEventListener("keydown", key);
  }, [open]);
  async function send(goal: string) {
    if (busy || !goal.trim()) return;
    if (!ready || !teamCode.trim()) { setError(say("请先配置 GLM-4.7，并填写团队 AI 口令。", "Configure GLM-4.7 and enter your team access code first.")); return; }
    setBusy(true); setError(""); setDraft("");
    const history = messages.slice(-8).map(({ role, text }) => ({ role, text }));
    setMessages(items => [...items.slice(-23), { role: "user", text: goal }]);
    const abort = new AbortController(); controller.current = abort;
    const timeout = setTimeout(() => abort.abort(), 115000);
    try {
      const response = await fetch("/api/agent", { method: "POST", signal: abort.signal,
        headers: { "Content-Type": "application/json", "X-Team-Code": teamCode },
        body: JSON.stringify({ goal, history, state, language: en ? "en" : "zh" }) });
      const result = await response.json();
      if (!response.ok) throw Error(result.error || "PiPo unavailable");
      if (abort.signal.aborted) return;
      if (typeof result.reply !== "string" || !Array.isArray(result.actions) || result.actions.length > 1 || !Array.isArray(result.trace)) throw Error("Invalid PiPo response");
      const applied = result.actions.every((action: AgentAction) => onAction(action));
      setMessages(items => [...items, { role: "assistant", text: result.reply, trace: result.trace }]);
      if (!applied) setError(say("目标内容已变化，未打开。请让 PiPo 重新检查进度。", "Content changed; ask PiPo to inspect progress again."));
    } catch (err) {
      setError(abort.signal.aborted ? say("本轮已停止，未应用后续页面操作。", "Stopped; no subsequent page action applied.") : err instanceof Error ? err.message : "PiPo unavailable");
    } finally { clearTimeout(timeout); controller.current = null; setBusy(false); }
  }
  const submit = (event: FormEvent) => { event.preventDefault(); void send(draft.trim()); };
  const shortcuts = [say("根据我的进度安排下一步，并带我开始", "Check my progress, plan my next step and open it"), say("检查我的错题，挑一道针对性练习", "Review my mistakes and open targeted practice"), say("给我选一个尚未通过的编程任务", "Choose an unfinished coding task and open it")];
  return <div className={`assistant-widget${open ? " is-open" : ""}`}>
    {!open && <div className="assistant-hint">{say("让 PiPo 帮你规划下一步", "Let PiPo plan your next step")}</div>}
    {open && <section className="assistant-panel" aria-label="PiPo Agent" ref={panelRef}>
      <header className="assistant-head"><img src="/ai-character.png" alt="" /><div><strong>PiPo Agent</strong><small>{say("观察进度 · 选择工具 · 执行任务", "Observe · Use tools · Act")}</small></div><button type="button" className="assistant-close" aria-label={say("关闭助手", "Close assistant")} onClick={() => setOpen(false)}><X size={18} /></button></header>
      <div className="assistant-messages" aria-live="polite">
        <div className="assistant-message from-assistant"><p>{say("告诉我你想学什么。我会按需要检查真实进度、读取课程、选择练习并打开具体内容，也可以解释 Python 概念。", "Tell me your learning goal. I can inspect your progress, read lessons, select practice, open specific content and explain Python concepts.")}</p></div>
        {messages.map((m, i) => <div key={i} className={`assistant-message ${m.role === "user" ? "from-user" : "from-assistant"}`}>
          {m.trace && <details className="agent-trace"><summary>{say("查看已执行的工具", "View executed tools")} ({m.trace.length})</summary><ol>{m.trace.map((t, j) => <li key={j}>{labels[t.tool]?.[en ? 1 : 0] || t.tool} · {t.status === "ok" ? say("完成", "Done") : say("已拒绝", "Rejected")}</li>)}</ol></details>}
          <p style={{ whiteSpace: "pre-wrap" }}>{m.text}</p></div>)}
        {!messages.length && <div className="assistant-shortcuts">{shortcuts.map(text => <button type="button" key={text} disabled={busy} onClick={() => void send(text)}>{text}</button>)}</div>}
        {busy && <div className="assistant-message from-assistant"><p>{say("正在读取学习情况并选择内容，学校服务较慢时可能需要约一分钟…", "Reading progress and selecting content. The school service may take about a minute…")}</p><button type="button" className="assistant-action" onClick={() => controller.current?.abort()}>{say("停止本轮", "Stop turn")}</button></div>}
        {error && <p role="alert" className="agent-error">{error}</p>}<div ref={endRef} />
      </div>
      <label className="agent-auth">{say("团队 AI 口令", "Team AI access code")}<input type="password" autoComplete="off" value={teamCode} onChange={e => onTeamCode(e.target.value)} maxLength={1000} placeholder={say("仅保留在当前页面内存", "Kept in page memory only")} /></label>
      <form className="assistant-compose" onSubmit={submit}><input type="text" value={draft} onChange={e => setDraft(e.target.value)} aria-label={say("告诉 PiPo 你的学习目标", "Tell PiPo your learning goal")} placeholder={say("例如：我总弄不清循环，帮我练习", "E.g. help me understand loops")} maxLength={1000} disabled={busy} /><button type="submit" disabled={busy || !draft.trim()} aria-label={say("发送消息", "Send message")}><ArrowRight size={17} /></button></form>
      <div className="assistant-disclaimer">{say("使用 GLM-4.7，会发送目标、近期对话及工具读取的学习摘要；每轮最多 5 次模型请求。不会代你答题或改写进度。", "Uses GLM-4.7: sends your goal, recent conversation and tool-selected learning summaries. Up to 5 model calls per turn. Does not answer quizzes for you or change progress.")}</div>
    </section>}
    <button type="button" className="assistant-launcher" aria-label={say("打开或关闭 PiPo", "Toggle PiPo")} aria-expanded={open} onClick={() => setOpen(v => !v)}><img src="/ai-character.png" alt="PiPo" /><span className="assistant-online" aria-hidden="true" /><span className="assistant-launch-icon" aria-hidden="true"><MessageCircle size={16} /></span></button>
  </div>;
}
