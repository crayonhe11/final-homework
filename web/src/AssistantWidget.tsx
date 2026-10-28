import { tr } from "./i18n";
import { useEffect, useRef, useState, type FormEvent } from "react";
import { ArrowRight, MessageCircle, X } from "lucide-react";
import type { KeyboardEvent } from "react";

type Destination = "map" | "practice" | "code";
type Message = { role: "assistant" | "user"; text: string; action?: { label: string; destination: Destination } };

const shortcuts: { label: string; text: string; destination: Destination }[] = [
  { label: "从哪里开始学习？", text: "建议从「学习地图」的基础导学开始，按条件判断、循环、函数的顺序逐步学习。每关完成阅读并独立答对两道题，就能继续前进。", destination: "map" },
  { label: "我想练习答题", text: "可以去「自由练习」做题。答错时先写下自己的思路，再使用题目里的 AI 思路分析获取针对性反馈。", destination: "practice" },
  { label: "我想练习写代码", text: "去「趣味编程」选择一个任务，在编辑器里编写并运行 Python 代码。", destination: "code" },
];

export default function AssistantWidget({ onNavigate }: { onNavigate: (view: Destination) => void }) {
  const [open, setOpen] = useState(false);
  const [draft, setDraft] = useState("");
  const [messages, setMessages] = useState<Message[]>([
    { role: "assistant", text: "你好呀，我是PiPo！我可以带你找到学习地图、答题练习和编程任务。想先做什么？" },
  ]);
  const panelRef = useRef<HTMLElement>(null);

  useEffect(() => {
    if (!open) return;
    const onKeyDown = (event: globalThis.KeyboardEvent) => {
      if (event.key === "Escape") setOpen(false);
    };
    document.addEventListener("keydown", onKeyDown);
    panelRef.current?.querySelector<HTMLInputElement>("input")?.focus();
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [open]);

  const choose = (shortcut: (typeof shortcuts)[number]) => {
    setMessages((items) => [
      ...items,
      { role: "user", text: tr(shortcut.label) },
      { role: "assistant", text: shortcut.text, action: { label: "现在去看看", destination: shortcut.destination } },
    ]);
  };
  const submit = (event: FormEvent) => {
    event.preventDefault();
    const text = draft.trim();
    if (!text) return;
    const lower = text.toLowerCase();
    let shortcut = shortcuts[0];
    if (/代码|编程|写程序|python|运行|\b(code|coding|program|run)\b/.test(lower)) shortcut = shortcuts[2];
    else if (/练习|题|答题|做题|考试|\b(practice|practise|question|questions|quiz|exercise)\b/.test(lower)) shortcut = shortcuts[1];
    const response = /\b(ai|reasoning|analysis)\b|人工智能|思路|分析/.test(lower)
      ? "答错后可以在练习页填写你的解题思路，再点击「分析我的思路」。这是平台现有的 AI 反馈功能；这里的自由输入暂用于学习导航。"
      : shortcut.text;
    setMessages((items) => [
      ...items,
      { role: "user", text },
      { role: "assistant", text: response, action: { label: "打开相关页面", destination: shortcut.destination } },
    ]);
    setDraft("");
  };
  const onInputKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Escape") setOpen(false);
  };

  return (
    <div className={`assistant-widget${open ? " is-open" : ""}`}>
      {!open && <div className="assistant-hint">{tr("嗨～学习上有什么想问的？")}</div>}
      {open && (
        <section className="assistant-panel" aria-label={tr("PiPo学习助手")} ref={panelRef}>
          <header className="assistant-head">
            <img src="/ai-character.png" alt="" />
            <div><strong>{tr("PiPo学习助手")}</strong><small>{tr("陪你一起学 Python")}</small></div>
            <button type="button" className="assistant-close" aria-label={tr("关闭助手")} onClick={() => setOpen(false)}><X size={18} /></button>
          </header>
          <div className="assistant-messages" aria-live="polite">
            {messages.map((message, index) => (
              <div key={`${index}-${message.role}`} className={`assistant-message ${message.role === "user" ? "from-user" : "from-assistant"}`}>
                <p>{message.role === "assistant" ? tr(message.text) : message.text}</p>
                {message.action && <button type="button" className="assistant-action" onClick={() => { onNavigate(message.action!.destination); setOpen(false); }}>{tr(message.action.label)}<ArrowRight size={14} /></button>}
              </div>
            ))}
            {messages.length === 1 && <div className="assistant-shortcuts">{shortcuts.map((shortcut) => <button type="button" key={tr(shortcut.label)} onClick={() => choose(shortcut)}>{tr(shortcut.label)}</button>)}</div>}
          </div>
          <form className="assistant-compose" onSubmit={submit}>
            <input value={draft} onChange={(event) => setDraft(event.target.value)} onKeyDown={onInputKeyDown} aria-label={tr("告诉PiPo你想做什么")} placeholder={tr("问问怎么开始学习…")} maxLength={160} />
            <button type="submit" aria-label={tr("发送消息")} disabled={!draft.trim()}><ArrowRight size={17} /></button>
          </form>
          <div className="assistant-disclaimer">{tr("自由输入提供学习导航；题目 AI 分析请在练习页使用。")}</div>
        </section>
      )}
      <button type="button" className="assistant-launcher" aria-label={tr(open ? "关闭PiPo学习助手" : "打开PiPo学习助手")} aria-expanded={open} onClick={() => setOpen((value) => !value)}>
        <img src="/ai-character.png" alt={tr("紫色PiPo AI 助手")} />
        <span className="assistant-online" aria-hidden="true" />
        <span className="assistant-launch-icon" aria-hidden="true"><MessageCircle size={16} /></span>
      </button>
    </div>
  );
}
