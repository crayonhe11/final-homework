import {tr,getLanguage,setLanguage} from "./i18n";
import { useEffect, useRef, useState } from "react";
import {
  ArrowRight,
  BookOpen,
  Check,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  Code2,
  Download,
  Flag,
  Flame,
  GitBranch,
  Lightbulb,
  Lock,
  Map,
  Play,
  RotateCcw,
  Sparkles,
  Target,
  TrendingUp,
  Upload,
  X,
  Terminal,
  Compass,
  NotebookPen,
} from "lucide-react";
import questionsJSON from "../../data/questions.json";
import conceptsJSON from "../../data/concepts.json";
import lessons from "../../data/lessons.json";
import tasks from "../../data/coding_tasks.json";
import AssistantWidget from "./AssistantWidget";
import {
  CHAPTERS,
  emptyState,
  api,
  uid,
  type Summary,
  type LearningState,
  type Question,
  type Concept,
  type Feedback,
  type Attempt,
} from "./types";
const questions = questionsJSON as Question[],
  concepts = conceptsJSON as Record<string, Concept>;
const ordered = Object.keys(concepts).sort(
  (a, b) => concepts[a].order - concepts[b].order,
);
type View = "map" | "lesson" | "practice" | "code" | "review" | "progress";
type Task = (typeof tasks)[number];
const icons = [GitBranch, RotateCcw, Code2];
const descriptions = [
  "让程序学会做选择",
  "让重复的事情自动发生",
  "把想法装进可复用的函数",
];
function Code({ children }: { children: string }) {
  return (
    <pre className="code-block">
      <code>{children}</code>
    </pre>
  );
}
function Pill({ children }: { children: React.ReactNode }) {
  return <span className="pill">{tr(children)}</span>;
}
function dateLabel(date: string) {
  return new Date(date).toLocaleString(getLanguage() === "en" ? "en-GB" : "zh-CN", {
    month: "numeric",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}
export default function App() {
 const [language, updateLanguage] = useState(getLanguage);
 useEffect(() => {document.documentElement.lang = language === "en" ? "en" : "zh-CN";document.title = language === "en" ? "PySteps · Learn Python" : "PySteps · Python 学习之旅";},[language]);
  const [state, setState] = useState<LearningState>(emptyState),
    [loaded, setLoaded] = useState(false),
    [view, setView] = useState<View>("map"),
    [chapter, setChapter] = useState(0),
    [lesson, setLesson] = useState("__intro__"),
    [quiz, setQuiz] = useState({
      id: questions[0].id,
      course: null as string | null,
      key: 0,
    }),
    [task, setTask] = useState(tasks[0].id),
    [notice, setNotice] = useState(""),
    [ai, setAI] = useState(false),
    [aiReady, setAIReady] = useState(false),
    [restoreOpen, setRestoreOpen] = useState(false),
    [saving, setSaving] = useState(false),
    [saveFailed, setSaveFailed] = useState(false),
    [teamCode, setTeamCode] = useState(""),
    [serverView, setServerView] = useState<Summary | null>(null);
  const revision = useRef(0),
    pending = useRef<LearningState | null>(null),
    inFlight = useRef(false),
    latestState = useRef(state);
  latestState.current = state;
  const importRef = useRef<HTMLInputElement>(null),
    pendingImport = useRef<LearningState | null>(null);
  useEffect(() => {
    api("state")
      .then((data) => {
        revision.current = data.revision;
        setState(data.state);
        setServerView(data.summary);
        setLoaded(true);
      })
      .catch((err) => setNotice("无法读取Python服务：" + err.message));
    api("diagnose")
      .then((data) => setAIReady(data.configured === true))
      .catch(() => {});
  }, []);
  useEffect(() => {
    if (!loaded) return;
    pending.current = state;
    async function flush() {
      if (inFlight.current) return;
      inFlight.current = true;
      setSaving(true);
      setSaveFailed(false);
      try {
        while (pending.current) {
          const snapshot = pending.current;
          pending.current = null;
          const result = await api("state", {
            revision: revision.current,
            state: snapshot,
          });
          revision.current = result.revision;
          if (snapshot === latestState.current) setServerView(result.summary);
        }
      } catch (err) {
        pending.current = null;
        setSaveFailed(true);
        setNotice(
          "进度未保存：" +
            (err instanceof Error ? err.message : "请导出备份后重试"),
        );
      } finally {
        inFlight.current = false;
        setSaving(false);
      }
    }
    void flush();
  }, [state, loaded]);
  useEffect(() => {
    const handler = (e: BeforeUnloadEvent) => {
      if (inFlight.current || pending.current || saveFailed) {
        e.preventDefault();
        e.returnValue = "";
      }
    };
    window.addEventListener("beforeunload", handler);
    return () => window.removeEventListener("beforeunload", handler);
  }, [saveFailed]);
  const states =
      serverView?.courses ??
      Object.fromEntries(
        ordered.map((k) => [
          k,
          {
            passed: false,
            locked: true,
            read: false,
            solved: 0,
            latest: {} as Record<string, boolean>,
          },
        ]),
      ),
    passed = ordered.filter((k) => states[k].passed).length;
  const recommendQuestion = async (
    q: Question,
    diagnosis: string,
    course: string | null = null,
  ) => {
    try {
      const result = await api("recommend", {
        question_id: q.id,
        diagnosis,
        state: latestState.current,
      });
      const next = result.questions[0];
      if (next)
        openQuiz(next, course && next.concept === course ? course : null);
    } catch (err) {
      setNotice(err instanceof Error ? err.message : "推荐失败");
    }
  };
  const active = ordered.find((k) => !states[k].locked && !states[k].passed);
  const go = (v: View) => {
    setView(v);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };
  const openLesson = (cid: string) => {
    setLesson(cid);
    if (concepts[cid]) setChapter(CHAPTERS.indexOf(concepts[cid].topic));
    go("lesson");
  };
  const openQuiz = (q: Question, course: string | null = null) => {
    setQuiz((prev) => ({ id: q.id, course, key: prev.key + 1 }));
    setChapter(CHAPTERS.indexOf(q.topic));
    go("practice");
  };
  const startCourse = (cid: string) => {
    const group = questions.filter((q) => q.concept === cid);
    const q =
      group.find(
        (q) =>
          !states[cid].latest[q.id] &&
          (view !== "practice" || quiz.course !== cid || q.id !== quiz.id),
      ) ??
      group.find((q) => !states[cid].latest[q.id]) ??
      group[0];
    openQuiz(q, cid);
  };
  const openTask = (id: string) => {
    setTask(id);
    setChapter(CHAPTERS.indexOf(tasks.find((t) => t.id === id)!.topic));
    go("code");
  };
  const markRead = (cid: string) =>
    setState((s) => ({ ...s, reads: [...new Set([...s.reads, cid])] }));
  const exportData = () => {
    const url = URL.createObjectURL(
      new Blob([JSON.stringify(state, null, 2)], { type: "application/json" }),
    );
    const a = document.createElement("a");
    a.href = url;
    a.download = `pysteps-backup-${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  };
  const nextQuestion = () => {
    if (quiz.course) {
      if (states[quiz.course].passed) {
        const next = ordered.find(
          (k) => !states[k].locked && !states[k].passed,
        );
        if (next) openLesson(next);
        else go("map");
      } else startCourse(quiz.course);
    } else {
      const q = questions.find((q) => q.id === quiz.id)!;
      void recommendQuestion(q, q.concept);
    }
  };
  const nav: [View, string, typeof Map][] = [
    ["map", "学习地图", Map],
    ["practice", "自由练习", NotebookPen],
    ["code", "趣味编程", Code2],
    ["review", "错题回顾", BookOpen],
    ["progress", "学习进度", TrendingUp],
  ];
  const correct = state.attempts.filter((r) => r.correct).length;
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a
          className="brand"
          href="#"
          onClick={(e) => {
            e.preventDefault();
            go("map");
          }}
        >
          <span className="brand-icon">
            <Code2 size={25} />
          </span>
          <span>
            PySteps<small>{tr("一步一步，写出可能")}</small>
          </span>
        </a>
        <span className="nav-caption">{tr("我的学习空间")}</span>
        <nav aria-label={tr("主要导航")}>
          {tr(nav.map(([id, label, Icon]) => (
            <button
              key={id}
              className={
                (view === id && !(id === "practice" && quiz.course)) ||
                (id === "map" &&
                  (view === "lesson" ||
                    (view === "practice" && Boolean(quiz.course))))
                  ? "nav-item active"
                  : "nav-item"
              }
              onClick={() => {
                if (id === "practice")
                  openQuiz(
                    questions.find((q) => q.topic === CHAPTERS[chapter])!,
                  );
                else if (id === "code")
                  openTask(
                    tasks.find((t) => t.topic === CHAPTERS[chapter])!.id,
                  );
                else go(id);
              }}
            >
              <Icon size={20} />
              {tr(label)}
              {tr(id === "map" && <span className="nav-dot" />)}
            </button>
          )))}
        </nav>
        <div className="sidebar-note">
          <span className="sparkle-badge">
            <Sparkles size={18} />
          </span>
          <b>{tr("每一步，都算数。")}</b>
          <p>{tr("理解一个小概念，")}<br />{tr("就是离独立编程更近一步。")}</p>
          <div className="progress-track">
            <i style={{ width: `${(passed / 15) * 100}%` }} />
          </div>
          <small>{tr("已通过")}{tr(passed)}{tr("/ 15 个概念")}</small>
        </div>
        <div className="local-status">
          <i />{tr("个人学习空间")}<small>
            {tr(saveFailed
              ? "保存失败，请导出备份"
              : saving
                ? "正在保存到SQLite…"
                : "Python · SQLite 已保存")}
          </small>
        </div>
      </aside>
      <div className="workspace">
        <header className="topbar">
          <div className="breadcrumb">{tr("Python 入门")}<ChevronRight size={14} />{tr(" ")}
            <strong>
              {tr(view === "lesson"
                ? "章节导学"
                : view === "practice" && quiz.course
                  ? "课程闯关"
                  : nav.find((n) => n[0] === view)?.[1])}
            </strong>
          </div>
          <div className="topbar-right">
<button className="language-switch" type="button" aria-label="Switch language / 切换语言" onClick={() => {const next = language === "zh" ? "en" : "zh";setLanguage(next);updateLanguage(next);}}>{language === "zh" ? "English" : "中文"}</button>
            <span>
              <Flame size={16} />{tr(" ")}
              {
                tr(new Set(state.attempts.map((r) => r.created_at.slice(0, 10)))
                  .size)
              }{tr(" ")}{tr("个练习日")}</span>
            <span className="avatar">{tr("我")}</span>
          </div>
        </header>
        <main>
          {tr(notice && (
            <div className="notice" role="status">
              {tr(notice)}
              {tr(saveFailed && (
                <button onClick={() => setState((s) => ({ ...s }))}>{tr("重试保存")}</button>
              ))}
              <button aria-label={tr("关闭提醒")} onClick={() => setNotice("")}>
                <X size={16} />
              </button>
            </div>
          ))}
          {tr(!loaded ? (
            <div className="empty">{tr("正在读取你的学习进度…")}</div>
          ) : (
            <>
              {tr(view === "map" && (
                <>
                  <div className="page-heading">
                    <div>
                      <div className="eyebrow">YOUR PYTHON JOURNEY</div>
                      <h1>{tr("从理解，到写出自己的代码")}<span className="heading-dot">.</span>
                      </h1>
                      <p>{tr("先认识概念，再动手验证。用一个个小挑战，拼出完整的 Python 知识地图。")}</p>
                    </div>
                    <Pill>{tr("入门路线 · 3 个章节")}</Pill>
                  </div>
                  <section className="journey-hero">
                    <div>
                      <span className="hero-tag">
                        <Compass size={15} />{tr("你的下一步")}</span>
                      <h2>
                        {tr(!state.reads.includes("__intro__")
                          ? "第一次见面，Python。"
                          : active
                            ? concepts[active].label
                            : "你已走完这条入门路线！")}
                      </h2>
                      <p>
                        {tr(!state.reads.includes("__intro__")
                          ? "从变量、输出和缩进开始。花几分钟建立基础，再开启第一章。"
                          : active
                            ? lessons[active as keyof typeof lessons].objective
                            : "回顾薄弱概念，或者到编程工坊，把知识变成真正运行的代码。")}
                      </p>
                      <button
                        className="button light"
                        onClick={() =>
                          passed === 15
                            ? go("code")
                            : openLesson(
                                state.reads.includes("__intro__")
                                  ? (active ?? "boundary")
                                  : "__intro__",
                              )
                        }
                      >
                        {tr(!state.reads.includes("__intro__")
                          ? "开始入门导学"
                          : passed === 15
                            ? "进入编程工坊"
                            : "继续学习")}
                        <ArrowRight size={17} />
                      </button>
                    </div>
                    <div className="hero-art" aria-hidden="true">
                      <div className="art-orbit orbit-one" />
                      <div className="art-orbit orbit-two" />
                      <div className="mini-code">
                        <span className="window-dots">● ● ●</span>
                        <code>
                          <em>while</em> learning:
                          <br />
                          &nbsp; explore()
                          <br />
                          &nbsp; try_again()
                          <br />
                          &nbsp; <span>grow += 1</span>
                        </code>
                      </div>
                      <span className="art-chip chip-a">
                        <Check size={16} />{tr("理解 +1")}</span>
                      <span className="art-chip chip-b">
                        <Code2 size={20} />
                      </span>
                    </div>
                  </section>
                  <div className="stats-strip">
                    <div>
                      <span className="stat-icon violet">
                        <Flag />
                      </span>
                      <div>
                        <b>
                          {tr(passed)}
                          <small> / 15</small>
                        </b>
                        <span>{tr("已通过概念")}</span>
                      </div>
                    </div>
                    <div>
                      <span className="stat-icon peach">
                        <Target />
                      </span>
                      <div>
                        <b>{tr(state.attempts.length)}</b>
                        <span>{tr("累计作答")}</span>
                      </div>
                    </div>
                    <div>
                      <span className="stat-icon mint">
                        <Code2 />
                      </span>
                      <div>
                        <b>
                          {
                            tr(new Set(
                              state.codeAttempts
                                .filter((r) => r.passed)
                                .map((r) => r.task_id),
                            ).size)
                          }
                          <small> / 6</small>
                        </b>
                        <span>{tr("完成编程任务")}</span>
                      </div>
                    </div>
                  </div>
                  <div className="section-heading">
                    <div>
                      <h2>{tr("你的知识地图")}</h2>
                      <p>{tr("每个概念：读导学 → 独立答对两道题 → 解锁下一步")}</p>
                    </div>
                    <button
                      className="text-button"
                      onClick={() => openLesson("__intro__")}
                    >{tr("重看基础导学")}<ArrowRight size={15} />
                    </button>
                  </div>
                  <div
                    className="chapter-tabs"
                    role="tablist"
                    aria-label={tr("知识章节")}
                  >
                    {tr(CHAPTERS.map((c, i) => (
                      <button
                        role="tab"
                        aria-selected={chapter === i}
                        className={chapter === i ? "selected" : ""}
                        key={c}
                        onClick={() => setChapter(i)}
                      >
                        <span>0{tr(i + 1)}</span>
                        {tr(c)}
                        <small>
                          {
                            tr(ordered.filter(
                              (k) =>
                                concepts[k].topic === c && states[k].passed,
                            ).length)
                          }
                          /5
                        </small>
                      </button>
                    )))}
                  </div>
                  <section className="chapter-panel">
                    <div className="chapter-title">
                      <div className="chapter-icon">
                        {tr((() => {
                          const Icon = icons[chapter];
                          return <Icon size={24} />;
                        })())}
                      </div>
                      <div>
                        <h2>{tr(CHAPTERS[chapter])}</h2>
                        <p>{tr(descriptions[chapter])}</p>
                      </div>
                      <Pill>{tr("5 个概念 · 2 个编程任务")}</Pill>
                    </div>
                    <div className="concept-list">
                      {tr(ordered
                        .filter((k) => concepts[k].topic === CHAPTERS[chapter])
                        .map((cid, i) => {
                          const s = states[cid];
                          return (
                            <button
                              className={`concept-row ${s.passed ? "done" : s.locked ? "locked" : "available"}`}
                              key={cid}
                              onClick={() => openLesson(cid)}
                            >
                              <span className="concept-index">
                                {tr(s.passed ? (
                                  <Check size={18} />
                                ) : s.locked ? (
                                  <Lock size={16} />
                                ) : (
                                  String(i + 1).padStart(2, "0")
                                ))}
                              </span>
                              <span className="concept-copy">
                                <b>{tr(concepts[cid].label)}</b>
                                <small>
                                  {
                                    tr(lessons[cid as keyof typeof lessons]
                                      .objective)
                                  }
                                </small>
                              </span>
                              <span className="concept-state">
                                {tr(s.passed
                                  ? "已通过"
                                  : s.locked
                                    ? "可预习 · 待解锁"
                                    : s.read
                                      ? `练习 ${s.solved}/2`
                                      : "开始学习")}
                              </span>
                              <ChevronRight size={17} />
                            </button>
                          );
                        }))}
                    </div>
                    <div className="chapter-code">
                      <div>
                        <span className="eyebrow">BUILD SOMETHING FUN</span>
                        <h3>{tr("把这一章，变成一个小作品")}</h3>
                        <p>{tr("不必等到通关。随时用代码解决一个有趣的问题。")}</p>
                      </div>
                      <div>
                        {tr(tasks
                          .filter((t) => t.topic === CHAPTERS[chapter])
                          .map((t) => (
                            <button key={t.id} onClick={() => openTask(t.id)}>
                              <Code2 size={16} />
                              {tr(t.title)}
                              <ArrowRight size={15} />
                            </button>
                          )))}
                      </div>
                    </div>
                  </section>
                  <p className="footnote">{tr("锁定的概念仍可预习；自由练习和趣味编程随时开放。通关反映本题表现，不等于已经完全掌握。")}</p>
                </>
              ))}
              {tr(view === "lesson" && (
                <>
                  <button className="back-button" onClick={() => go("map")}>
                    <ChevronLeft size={16} />{tr("回到知识地图")}</button>
                  <div className="page-heading">
                    <div>
                      <div className="eyebrow">LEARN BEFORE YOU TRY</div>
                      <h1>
                        {tr(lesson === "__intro__"
                          ? "出发前，认识 Python"
                          : concepts[lesson].label)}
                      </h1>
                      <p>
                        {tr(lesson === "__intro__"
                          ? "不用急着答题。先弄懂代码是怎样表达想法的。"
                          : lessons[lesson as keyof typeof lessons].objective)}
                      </p>
                    </div>
                    <Pill>
                      {tr(lesson === "__intro__"
                        ? "基础导学"
                        : concepts[lesson].topic)}
                    </Pill>
                  </div>
                  <div className="lesson-layout">
                    <section className="panel lesson-content">
                      {tr(lesson === "__intro__" ? (
                        <>
                          <h2>{tr("01 · 变量，为一个值起名字")}</h2>
                          <p>{tr("变量像贴了标签的盒子。用 = 保存值，用 print() 把值显示出来。字符串用引号，数字不用。")}</p>
                          <Code>
                            {
                              'name = "Python"\nsteps = 1\nprint(name)\nprint(steps)'
                            }
                          </Code>
                          <h2>{tr("02 · 常用的几种值")}</h2>
                          <p>{tr("整数如 3，小数如 1.5，字符串如 \"你好\"，布尔值是 True 或 False。列表用方括号装多个值，例如 [1, 2, 3]。% 用来求余数，例如 5 % 2 的结果是 1。")}</p>
                          <h2>{tr("03 · 缩进，让代码分成小组")}</h2>
                          <p>{tr("Python 用缩进表示“这些语句属于同一块”。在条件、循环和函数后面写冒号，再把里面的代码缩进四个空格。")}</p>
                          <Code>
                            {
                              'temperature = 28\nif temperature > 25:\n    print("带上水杯")\nprint("出门吧")'
                            }
                          </Code>
                          <div className="callout">
                            <Lightbulb size={19} />
                            <p>{tr("读代码时，按执行顺序跟踪变量的值。不要只看最后一行，也不用靠猜。")}</p>
                          </div>
                        </>
                      ) : (
                        <>
                          <h2>{tr("先理解这个概念")}</h2>
                          {tr(lessons[
                            lesson as keyof typeof lessons
                          ].explanations.map((p, i) => (
                            <p key={i}>{tr(p)}</p>
                          )))}
                          <h2>{tr("跟着代码走一遍")}</h2>
                          <Code>
                            {
                              lessons[lesson as keyof typeof lessons]
                                .example_code
                            }
                          </Code>
                          <span className="field-label">{tr("输出")}</span>
                          <pre className="output-block">
                            {
                              lessons[lesson as keyof typeof lessons]
                                .example_output
                            }
                          </pre>
                          <p>
                            {
                              tr(lessons[lesson as keyof typeof lessons]
                                .walkthrough)
                            }
                          </p>
                          <div className="callout">
                            <Lightbulb size={19} />
                            <div>
                              <b>{tr("停下来想一想")}</b>
                              <p>
                                {
                                  tr(lessons[lesson as keyof typeof lessons]
                                    .reflection)
                                }
                              </p>
                            </div>
                          </div>
                        </>
                      ))}
                      <div className="lesson-actions">
                        <button
                          className="button primary"
                          onClick={() => {
                            markRead(lesson);
                            if (lesson === "__intro__") openLesson("boundary");
                            else if (!states[lesson].locked) {
                              startCourse(lesson);
                            } else
                              setNotice(
                                "已记录预习。完成前置概念后即可进入本关。",
                              );
                          }}
                        >
                          {tr(lesson === "__intro__"
                            ? "我理解了，开启第一章"
                            : states[lesson].locked
                              ? "标记已预习"
                              : "我理解了，开始验证")}
                          <ArrowRight size={17} />
                        </button>
                        {tr(lesson !== "__intro__" && (
                          <button
                            className="button secondary"
                            onClick={() =>
                              openQuiz(
                                questions.find((q) => q.concept === lesson)!,
                              )
                            }
                          >{tr("自由练习")}</button>
                        ))}
                      </div>
                    </section>
                    <aside className="panel lesson-side">
                      <span className="eyebrow">{tr("学习小贴士")}</span>
                      <h3>{tr("理解比速度重要")}</h3>
                      <p>{tr("读懂例子后，试着先预测输出，再检查自己的想法。")}</p>
                      <ol>
                        <li>{tr("阅读概念和例子")}</li>
                        <li>{tr("用自己的话解释")}</li>
                        <li>{tr("独立答对两道不同的题")}</li>
                      </ol>
                      {tr(lesson !== "__intro__" && (
                        <>
                          <hr />
                          <b>
                            {tr(states[lesson].locked
                              ? "本关尚未解锁"
                              : states[lesson].passed
                                ? "本关已通过"
                                : `独立验证 ${states[lesson].solved}/2`)}
                          </b>
                          <p>
                            {tr(states[lesson].locked
                              ? "需要完成基础导学、上一章节及本概念的前置知识。你仍然可以预习或自由练习。"
                              : "使用提示的正确答案会记录进度，但不计入独立通关。")}
                          </p>
                        </>
                      ))}
                      <button
                        className="text-button"
                        onClick={() =>
                          openTask(
                            tasks.find((t) => t.topic === CHAPTERS[chapter])!
                              .id,
                          )
                        }
                      >{tr("本章趣味编程")}<ArrowRight size={15} />
                      </button>
                    </aside>
                  </div>
                </>
              ))}
              {tr(view === "practice" && (
                <Quiz
                  key={quiz.key}
                  question={questions.find((q) => q.id === quiz.id)!}
                  course={quiz.course}
                  passed={Boolean(quiz.course && states[quiz.course].passed)}
                  saving={saving || saveFailed}
                  teamCode={teamCode}
                  setTeamCode={setTeamCode}
                  ai={ai}
                  aiReady={aiReady}
                  setAI={setAI}
                  onSave={(row) =>
                    setState((s) => ({ ...s, attempts: [...s.attempts, row] }))
                  }
                  onUpdate={(id, feedback, reason) =>
                    setState((s) => ({
                      ...s,
                      attempts: s.attempts.map((a) =>
                        a.id === id
                          ? {
                              ...a,
                              reason,
                              feedback,
                              diagnosis: feedback.concept,
                            }
                          : a,
                      ),
                    }))
                  }
                  onNext={nextQuestion}
                  onLesson={() =>
                    openLesson(questions.find((q) => q.id === quiz.id)!.concept)
                  }
                  onTopic={(topic) =>
                    openQuiz(questions.find((q) => q.topic === topic)!)
                  }
                  onCode={() =>
                    openTask(
                      tasks.find(
                        (t) =>
                          t.topic ===
                          questions.find((q) => q.id === quiz.id)!.topic,
                      )!.id,
                    )
                  }
                  onRecommend={(f) => {
                    const q = questions.find((q) => q.id === quiz.id)!;
                    void recommendQuestion(q, f.concept, quiz.course);
                  }}
                />
              ))}
              {tr(view === "code" && (
                <>
                  <div className="page-heading">
                    <div>
                      <div className="eyebrow">CODE · RUN · DISCOVER</div>
                      <h1>{tr("让知识，真正跑起来")}<span className="heading-dot">.</span>
                      </h1>
                      <p>{tr("每章两个小任务。写代码、运行测试，在真实的 Python 中验证你的想法。")}</p>
                    </div>
                    <Pill>{tr("浏览器内运行 · 无需安装")}</Pill>
                  </div>
                  <div
                    className="chapter-tabs"
                    role="tablist"
                    aria-label={tr("编程章节")}
                  >
                    {tr(CHAPTERS.map((c, i) => (
                      <button
                        role="tab"
                        aria-selected={chapter === i}
                        className={chapter === i ? "selected" : ""}
                        key={c}
                        onClick={() => {
                          setChapter(i);
                          setTask(tasks.find((t) => t.topic === c)!.id);
                        }}
                      >
                        <span>0{tr(i + 1)}</span>
                        {tr(c)}
                      </button>
                    )))}
                  </div>
                  <div className="task-picker">
                    {tr(tasks
                      .filter((t) => t.topic === CHAPTERS[chapter])
                      .map((t) => (
                        <button
                          className={task === t.id ? "selected" : ""}
                          key={t.id}
                          onClick={() => setTask(t.id)}
                        >
                          <span className="task-symbol">
                            {tr(tasks.indexOf(t) % 2 ? "✦" : "⌘")}
                          </span>
                          <span>
                            <b>{tr(t.title)}</b>
                            <small>
                              {tr(t.concepts
                                .map((k) => concepts[k].label)
                                .slice(0, 2)
                                .join(" / "))}
                            </small>
                          </span>
                          {tr(state.codeAttempts.some(
                            (a) => a.task_id === t.id && a.passed,
                          ) ? (
                            <CheckCircle2 size={20} />
                          ) : (
                            <ChevronRight size={20} />
                          ))}
                        </button>
                      )))}
                  </div>
                  <CodeLab
                    key={task}
                    task={tasks.find((t) => t.id === task)!}
                    source={
                      state.drafts[task] ??
                      tasks.find((t) => t.id === task)!.starter
                    }
                    onDraft={(source) =>
                      setState((s) => ({
                        ...s,
                        drafts: { ...s.drafts, [task]: source },
                      }))
                    }
                    onResult={(source, passed, details) =>
                      setState((s) => ({
                        ...s,
                        codeAttempts: [
                          ...s.codeAttempts,
                          {
                            id: uid(),
                            task_id: task,
                            source,
                            passed,
                            details,
                            created_at: new Date().toISOString(),
                          },
                        ],
                      }))
                    }
                  />
                </>
              ))}
              {tr(view === "review" && (
                <>
                  <div className="page-heading">
                    <div>
                      <div className="eyebrow">REFLECT & RETRY</div>
                      <h1>{tr("错题，是下一步的线索")}</h1>
                      <p>{tr("一次错误不定义你的能力。看看当时的思路，再给自己一次验证的机会。")}</p>
                    </div>
                    <Pill>
                      {tr(state.attempts.filter((a) => !a.correct).length)}{tr(" ")}{tr("次错误作答")}</Pill>
                  </div>
                  {tr(state.attempts.filter((a) => !a.correct).length === 0 ? (
                    <div className="panel empty">
                      <BookOpen size={36} />
                      <h2>{tr("这里还没有错题")}</h2>
                      <p>{tr("完成练习后，错误作答及其反馈会保存在这里。")}</p>
                      <button
                        className="button primary"
                        onClick={() => openQuiz(questions[0])}
                      >{tr("开始一次练习")}<ArrowRight size={16} />
                      </button>
                    </div>
                  ) : (
                    <div className="review-list">
                      {tr([...state.attempts]
                        .reverse()
                        .filter((a) => !a.correct)
                        .map((a) => {
                          const q = questions.find(
                            (q) => q.id === a.question_id,
                          )!;
                          const due = serverView?.schedule[q.id];
                          return (
                            <article className="panel review-card" key={a.id}>
                              <div className="review-head">
                                <Pill>{tr(q.topic)}</Pill>
                                <small>{tr(dateLabel(a.created_at))}</small>
                              </div>
                              <h3>{tr(concepts[q.concept].label)}</h3>
                              <Code>{q.code}</Code>
                              <p>{tr("你的选择：")}{tr(a.choice)}{tr("正确选项：")}{tr(q.answer)}
                              </p>
                              {tr(a.reason && (
                                <blockquote>{tr("当时的思路：")}{a.reason}</blockquote>
                              ))}
                              <p>{a.feedback.source === "ai" && a.feedback.personalized ? a.feedback.explanation : tr(a.feedback.explanation)}</p>
                              <div className="review-bottom">
                                <span>
                                  {tr(due && due.due <= Date.now()
                                    ? "已到复习时间"
                                    : due
                                      ? `建议复习：${dateLabel(new Date(due.due).toISOString())}`
                                      : "可随时重练")}
                                </span>
                                <button
                                  className="button secondary"
                                  onClick={() => openQuiz(q)}
                                >{tr("再试一次")}<RotateCcw size={16} />
                                </button>
                              </div>
                            </article>
                          );
                        }))}
                    </div>
                  ))}
                </>
              ))}
              {tr(view === "progress" && (
                <>
                  <div className="page-heading">
                    <div>
                      <div className="eyebrow">SMALL STEPS, REAL PROGRESS</div>
                      <h1>{tr("看见自己的每一点进步")}</h1>
                      <p>{tr("统计反映练习表现，不能单独证明概念掌握或学习成绩提升。")}</p>
                    </div>
                    <button className="button secondary" onClick={exportData}>
                      <Download size={16} />{tr("导出学习记录")}</button>
                  </div>
                  <div className="stats-strip">
                    <div>
                      <span className="stat-icon violet">
                        <Target />
                      </span>
                      <div>
                        <b>{tr(state.attempts.length)}</b>
                        <span>{tr("总作答次数")}</span>
                      </div>
                    </div>
                    <div>
                      <span className="stat-icon mint">
                        <CheckCircle2 />
                      </span>
                      <div>
                        <b>
                          {tr(state.attempts.length
                            ? Math.round(
                                (correct / state.attempts.length) * 100,
                              ) + "%"
                            : "—")}
                        </b>
                        <span>{tr("累计正确率")}</span>
                      </div>
                    </div>
                    <div>
                      <span className="stat-icon peach">
                        <Flag />
                      </span>
                      <div>
                        <b>{tr(passed)}/15</b>
                        <span>{tr("已通过概念")}</span>
                      </div>
                    </div>
                  </div>
                  <ProgressChart attempts={state.attempts} />
                  <section className="panel">
                    <div className="section-heading">
                      <h2>{tr("知识点表现")}</h2>
                      <Pill>{tr("含提示与重复作答")}</Pill>
                    </div>
                    <div className="table-scroll">
                      <table>
                        <thead>
                          <tr>
                            <th>{tr("概念")}</th>
                            <th>{tr("作答次数")}</th>
                            <th>{tr("正确率")}</th>
                            <th>{tr("课程状态")}</th>
                          </tr>
                        </thead>
                        <tbody>
                          {tr(ordered.map((cid) => {
                            const rows = state.attempts.filter(
                              (a) =>
                                questions.find((q) => q.id === a.question_id)
                                  ?.concept === cid,
                            );
                            return (
                              <tr key={cid}>
                                <td>
                                  <button
                                    className="text-button"
                                    onClick={() => openLesson(cid)}
                                  >
                                    {tr(concepts[cid].label)}
                                  </button>
                                </td>
                                <td>{tr(rows.length)}</td>
                                <td>
                                  {tr(rows.length
                                    ? Math.round(
                                        (rows.filter((a) => a.correct).length /
                                          rows.length) *
                                          100,
                                      ) + "%"
                                    : "—")}
                                </td>
                                <td>
                                  {tr(states[cid].passed
                                    ? "已通过"
                                    : states[cid].locked
                                      ? "待解锁"
                                      : "学习中")}
                                </td>
                              </tr>
                            );
                          }))}
                        </tbody>
                      </table>
                    </div>
                  </section>
                  <section className="panel backup-panel">
                    <div>
                      <h3>{tr("把进度带到另一台电脑")}</h3>
                      <p>{tr("学习")}{tr(saveFailed
                          ? "保存失败，请导出备份"
                          : saving
                            ? "正在保存到SQLite…"
                            : "Python · SQLite 已保存")}{tr("，不会自动跨设备同步。导出后，可在另一台设备导入。")}</p>
                    </div>
                    <button
                      className="button secondary"
                      onClick={() => importRef.current?.click()}
                    >
                      <Upload size={16} />{tr("导入备份")}</button>
                    <input
                      type="file"
                      accept="application/json,.json"
                      hidden
                      ref={importRef}
                      onChange={async (e) => {
                        const f = e.target.files?.[0];
                        e.target.value = "";
                        if (!f) return;
                        try {
                          if (f.size > 10000000)
                            throw Error("文件不能超过 10 MB");
                          pendingImport.current = (
                            await api("import", {
                              state: JSON.parse(await f.text()),
                            })
                          ).state;
                          setRestoreOpen(true);
                        } catch (err) {
                          setNotice(
                            err instanceof Error ? err.message : "导入失败",
                          );
                        }
                      }}
                    />
                  </section>
                  {tr(state.codeAttempts.length > 0 && (
                    <section className="panel">
                      <h2>{tr("最近的编程尝试")}</h2>
                      {tr([...state.codeAttempts]
                        .reverse()
                        .slice(0, 10)
                        .map((a) => (
                          <details className="attempt-detail" key={a.id}>
                            <summary>
                              {tr(tasks.find((t) => t.id === a.task_id)?.title)} ·{tr(" ")}
                              {tr(a.passed ? "已通过" : "继续尝试")} ·{tr(" ")}
                              {tr(dateLabel(a.created_at))}
                            </summary>
                            <Code>{a.source}</Code>
                            <p>{tr(a.details)}</p>
                            <button
                              className="text-button"
                              onClick={() => {
                                setState((s) => ({
                                  ...s,
                                  drafts: {
                                    ...s.drafts,
                                    [a.task_id]: a.source,
                                  },
                                }));
                                openTask(a.task_id);
                              }}
                            >{tr("载入这次代码")}<ArrowRight size={15} />
                            </button>
                          </details>
                        )))}
                    </section>
                  ))}
                </>
              ))}
            </>
          ))}
          <footer>
            PySteps <span>{tr("用理解连接知识，用练习验证想法。")}</span>
            <small>{tr("为 Python 初学者设计")}</small>
          </footer>
        </main>
      </div>
      <AssistantWidget state={state} ready={aiReady && loaded} teamCode={teamCode} onTeamCode={setTeamCode} onAction={(action) => {
        if (action.kind === "lesson" && (action.id === "__intro__" || (concepts[action.id] && !states[action.id].locked))) { openLesson(action.id); return true; }
        if (action.kind === "question") { const q = questions.find(q => q.id === action.id); if (q) { openQuiz(q); return true; } }
        if (action.kind === "coding" && tasks.some(t => t.id === action.id)) { openTask(action.id); return true; }
        return false;
      }} />
      {tr(restoreOpen && (
        <div className="modal-backdrop">
          <div
            className="panel modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="import-title"
          >
            <h2 id="import-title">{tr("导入并替换当前进度？")}</h2>
            <p>{tr("备份含")}{tr(pendingImport.current?.attempts.length)}{tr(" ")}{tr("次作答。当前会话的服务器记录将被替换，建议先导出一份备份。")}</p>
            <div className="button-row">
              <button
                className="button secondary"
                onClick={() => setRestoreOpen(false)}
              >{tr("取消")}</button>
              <button className="button secondary" onClick={exportData}>{tr("先导出")}</button>
              <button
                className="button primary"
                onClick={() => {
                  if (pendingImport.current) setState(pendingImport.current);
                  setRestoreOpen(false);
                  setNotice(
                    "备份已导入。AI 原始反馈已还原为可验证的标准解析。",
                  );
                }}
              >{tr("确认导入")}</button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
function Quiz({
  question: q,
  course,
  passed,
  saving,
  teamCode,
  setTeamCode,
  ai,
  aiReady,
  setAI,
  onSave,
  onUpdate,
  onNext,
  onLesson,
  onTopic,
  onCode,
  onRecommend,
}: {
  question: Question;
  course: string | null;
  passed: boolean;
  saving: boolean;
  teamCode: string;
  setTeamCode: (s: string) => void;
  ai: boolean;
  aiReady: boolean;
  setAI: (b: boolean) => void;
  onSave: (a: Attempt) => void;
  onUpdate: (id: string, f: Feedback, reason: string) => void;
  onNext: () => void;
  onLesson: () => void;
  onTopic: (t: string) => void;
  onCode: () => void;
  onRecommend: (f: Feedback) => void;
}) {
  const [choice, setChoice] = useState(""),
    [reason, setReason] = useState(""),
    [hints, setHints] = useState(0),
    [feedback, setFeedback] = useState<Feedback | null>(null),
    [busy, setBusy] = useState(false),
    [error, setError] = useState(""),
    [isCorrect, setIsCorrect] = useState(false);
  const attemptId = useRef<string | null>(null);
  const ruleFeedback = useRef<Feedback | null>(null);
  const abort = useRef<AbortController | null>(null),
    alive = useRef(true);
  useEffect(() => {
    alive.current = true;
    return () => {
      alive.current = false;
      abort.current?.abort();
    };
  }, []);
  const submit = async () => {
    if (feedback || busy) return;
    if (!choice) {
      setError("请先选择一个答案。");
      return;
    }
    setError("");
    setBusy(true);
    let graded;
    try {
      graded = await api("grade", { question_id: q.id, choice });
    } catch (err) {
      setError(err instanceof Error ? err.message : "判分失败");
      setBusy(false);
      return;
    }
    if (!alive.current) return;
    const f: Feedback = graded.feedback,
      id = uid();
    attemptId.current = id;
    ruleFeedback.current = f;
    setIsCorrect(graded.correct);
    setFeedback(f);
    setBusy(false);
    onSave({
      id,
      question_id: q.id,
      choice,
      reason,
      correct: graded.correct,
      diagnosis: f.concept,
      created_at: new Date().toISOString(),
      hints_used: hints,
      course_concept: course,
      feedback: f,
    });
    if (!ai || !aiReady || graded.correct || !reason.trim()) return;
    await analyzeReason(id, f, reason);
  };
  const analyzeReason = async (id: string, f: Feedback, reason: string) => {
    if (!reason.trim()) {
      setError("先补充你的想法，再请 AI 分析。");
      return;
    }
    if (!teamCode.trim()) {
      setError("请填写团队 AI 口令，再分析思路。");
      return;
    }
    setError("");
    setAI(true);
    setBusy(true);
    const controller = new AbortController();
    abort.current = controller;
    const timer = setTimeout(() => controller.abort(), 75000);
    try {
      const r = await fetch("/api/diagnose", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Team-Code": teamCode,
        },
        signal: controller.signal,
        body: JSON.stringify({ question_id: q.id, choice, reason, language: getLanguage() }),
      });
      const data = (await r.json()) as Feedback & { error?: string };
      if (!r.ok) throw Error(data.error || "AI 服务暂时不可用");
      if (
        !["ai", "rule"].includes(data.source) ||
        typeof data.explanation !== "string"
      )
        throw Error("AI 返回内容无效");
      if (alive.current) {
        setFeedback(data);
        onUpdate(id, data, reason);
      }
    } catch (err) {
      if (alive.current) {
        const fallback = {
          ...f,
          message:
            err instanceof Error && err.name !== "AbortError"
              ? err.message + " 已使用规则反馈。"
              : "AI 分析超时，已使用规则反馈。",
        };
        setFeedback(fallback);
        onUpdate(id, fallback, reason);
      }
    } finally {
      clearTimeout(timer);
      if (alive.current) setBusy(false);
    }
  };
  const correct = isCorrect;
  return (
    <>
      <div className="page-heading">
        <div>
          <div className="eyebrow">ONE CONCEPT AT A TIME</div>
          <h1>{tr("练习工作区")}</h1>
          <p>
            {tr(course
              ? "课程闯关 · 独立答对本概念两道不同的题，即可通关。"
              : "自由练习 · 随时验证想法，不计入课程解锁。")}
          </p>
        </div>
        <select
          aria-label={tr("选择练习主题")}
          value={q.topic}
          onChange={(e) => onTopic(e.target.value)}
        >
          {tr(CHAPTERS.map((t) => (
            <option key={t} value={t}>{tr(t)}</option>
          )))}
        </select>
      </div>
      <div className="quiz-meta">
        <Pill>{tr(concepts[q.concept].label)}</Pill>
        <span>{tr("难度")}{tr(q.difficulty)} / 3</span>
        <button className="text-button" onClick={onLesson}>{tr("本题导学")}<BookOpen size={15} />
        </button>
      </div>
      <div className="quiz-layout">
        <section className="panel quiz-form">
          <h3>
            <span className="step-label">01</span>{tr("阅读代码")}</h3>
          <p>{tr(q.prompt)}</p>
          <Code>{q.code}</Code>
          <fieldset disabled={Boolean(feedback)}>
            <legend>
              <span className="step-label">02</span>{tr("选择完整输出")}</legend>
            {tr(Object.entries(q.options).map(([key, value]) => (
              <label
                className={`option ${choice === key ? "chosen" : ""} ${feedback && key === q.answer ? "right-option" : ""}`}
                key={key}
              >
                <input
                  type="radio"
                  name="answer"
                  value={key}
                  checked={choice === key}
                  onChange={() => {
                    setChoice(key);
                    setError("");
                  }}
                />
                <span className="option-key">{tr(key)}</span>
                <pre>{value}</pre>
                {tr(feedback && key === q.answer && <CheckCircle2 size={18} />)}
              </label>
            )))}
          </fieldset>
          <label className="reason-label" htmlFor="reason">
            <span className="step-label">03</span>
            {tr(feedback && !correct ? "补充或修改你的思路" : "说说你的思路")}{tr(" ")}
            <small>{tr("选填 · 答错后也可补充")}</small>
          </label>
          <textarea
            id="reason"
            className="reason-input"
            placeholder={tr("例如：我觉得结束值也会被包含，所以…")}
            value={reason}
            maxLength={1000}
            disabled={busy || (Boolean(feedback) && correct)}
            onChange={(e) => {
              const value = e.target.value;
              setReason(value);
              setError("");
              if (attemptId.current && ruleFeedback.current) {
                // A changed reason invalidates any previous AI explanation and diagnosis.
                setFeedback(ruleFeedback.current);
                onUpdate(attemptId.current, ruleFeedback.current, value);
              }
            }}
          />
          <label className="ai-toggle">
            <input
              type="checkbox"
              checked={ai}
              disabled={!aiReady || busy || (Boolean(feedback) && correct)}
              onChange={(e) => setAI(e.target.checked)}
            />
            <Sparkles size={15} />{tr("用 GLM-4.7 分析我的理由")}{tr(" ")}
            <small>
              {tr(aiReady ? "答错且填写思路时才调用 AI" : "等待服务端配置")}
            </small>
          </label>
          {tr(aiReady && (ai || (Boolean(feedback) && !correct)) && (
            <label className="ai-code-label">{tr("团队 AI 口令")}<input
                type="password"
                value={teamCode}
                onChange={(e) => setTeamCode(e.target.value)}
                maxLength={200}
                autoComplete="off"
                placeholder={tr("由部署者提供，仅用于AI分析")}
              />
            </label>
          ))}
          {tr(feedback && !correct && (
            <div className="reason-followup" aria-live="polite">
              <p>
                {tr(!reason.trim()
                  ? "本次先显示规则反馈。你可以补充刚才的想法，再让 GLM-4.7 分析。"
                  : feedback.source === "ai"
                    ? "已根据这段思路完成 AI 分析。修改想法后可以重新分析。"
                    : "思路已记录。点击下方按钮，让 GLM-4.7 根据你的想法补充分析。")}
              </p>
              <button
                className="button secondary"
                disabled={!aiReady || busy || saving || !reason.trim()}
                onClick={() => {
                  if (attemptId.current && ruleFeedback.current)
                    void analyzeReason(
                      attemptId.current,
                      ruleFeedback.current,
                      reason,
                    );
                }}
              >
                <Sparkles size={16} />
                {tr(busy
                  ? "正在分析思路…"
                  : feedback.source === "ai"
                    ? "重新分析我的思路"
                    : "分析我的思路")}
              </button>
              <small>
                {tr(aiReady
                  ? "仅更新这次作答的理由与反馈，不增加答题次数。"
                  : "AI 尚未配置，补充的思路仍会保存。")}
              </small>
            </div>
          ))}
          {tr(hints > 0 && (
            <div className="hint-box">
              <Lightbulb size={17} />
              <p>{tr(q.hints.slice(0, hints).join("\n"))}</p>
            </div>
          ))}
          {tr(error && (
            <p className="error" role="alert">
              {tr(error)}
            </p>
          ))}
          <div className="answer-actions">
            <button
              className="button secondary"
              disabled={Boolean(feedback) || hints >= q.hints.length}
              onClick={() => setHints((h) => h + 1)}
            >
              <Lightbulb size={16} />{tr("提示")}{tr(hints)}/{tr(q.hints.length)}
            </button>
            <button
              className="button primary"
              disabled={busy || saving}
              onClick={feedback ? onNext : submit}
            >
              {tr(busy
                ? "正在处理…"
                : saving
                  ? "正在保存…"
                  : feedback
                    ? passed
                      ? "继续下一课"
                      : correct
                        ? "下一题"
                        : "继续练习"
                    : "提交答案")}
              <ArrowRight size={17} />
            </button>
          </div>
        </section>
        <aside className="panel feedback-panel" aria-live="polite">
          <span className="eyebrow">FEEDBACK & NEXT STEP</span>
          <h2>{tr("让每次尝试都有收获")}</h2>
          {tr(!feedback ? (
            <div className="feedback-empty">
              <span className="feedback-icon">
                <Lightbulb size={30} />
              </span>
              <h3>{tr("先试着说出你的想法")}</h3>
              <p>{tr("提交后，你会看到答案解析、")}<br />{tr("可能的概念线索和下一步建议。")}</p>
            </div>
          ) : (
            <>
              <div
                className={`feedback-result ${correct ? "success" : "try-again"}`}
              >
                {tr(correct ? <CheckCircle2 size={24} /> : <Lightbulb size={24} />)}
                <div>
                  <b>{tr(correct ? "本次答对了！" : "发现了一个值得探索的地方")}</b>
                  <small>
                    {tr(correct
                      ? "用不同题目，继续验证你的理解。"
                      : "答错只是线索，不代表你一定不懂。")}
                  </small>
                </div>
              </div>
              {tr(busy && (
                <p className="ai-working">
                  <Sparkles size={16} />{tr("GLM-4.7 正在阅读你的思路…")}</p>
              ))}
              <Pill>
                {tr(feedback.source === "ai" ? "AI 辅助诊断" : "规则反馈")}
              </Pill>
              <p>{tr(feedback.message)}</p>
              {tr(!correct && (
                <div className="diagnosis">
                  <small>{tr("可能的概念线索")}</small>
                  <b>
                    {tr(feedback.concept === "unknown"
                      ? "理由不足，暂不判断误区"
                      : (concepts[feedback.concept]?.label ?? "需要更多证据"))}
                  </b>
                </div>
              ))}
              {tr(feedback.quote && (
                <blockquote>{tr("你提到：“")}{feedback.quote}”</blockquote>
              ))}
              <h3>{tr(feedback.personalized ? "针对你的思路" : "答案解析")}</h3>
              <p>{feedback.source === "ai" && feedback.personalized ? feedback.explanation : tr(feedback.explanation)}</p>
              <details className="standard-answer">
                <summary>{tr("查看标准答案与解析")}</summary>
                <p>{tr("正确选项：")}{tr(q.answer)}</p>
                <p>{tr(q.explanation)}</p>
              </details>
              {tr(!correct && (
                <div className="hint-box">
                  <Lightbulb size={17} />
                  <p>{feedback.source === "ai" && feedback.personalized ? feedback.hint : tr(feedback.hint)}</p>
                </div>
              ))}
              {tr(passed && (
                <div className="course-pass">
                  <Flag size={18} />{tr("本关已通过！可以继续下一课。")}</div>
              ))}
              {tr(!correct && (
                <button
                  disabled={busy || saving}
                  className="button secondary full-width"
                  onClick={() => onRecommend(feedback)}
                >
                  {tr(feedback.concept === "unknown"
                    ? "再用一道基础题验证"
                    : "练一道针对性题目")}
                  <ArrowRight size={16} />
                </button>
              ))}
            </>
          ))}
          <div className="feedback-bottom">
            <span>{tr("想换一种方式试试？")}</span>
            <button className="text-button" onClick={onCode}>{tr("本章趣味编程")}<ArrowRight size={16} />
            </button>
          </div>
        </aside>
      </div>
    </>
  );
}
type RunResult = {
  passed: boolean;
  error?: string;
  line?: number;
  stdout?: string;
  rows?: {
    args: unknown[];
    expected: unknown;
    actual: unknown;
    passed: boolean;
  }[];
};
function CodeLab({
  task,
  source,
  onDraft,
  onResult,
}: {
  task: Task;
  source: string;
  onDraft: (s: string) => void;
  onResult: (source: string, passed: boolean, details: string) => void;
}) {
  const [result, setResult] = useState<RunResult | null>(null),
    [status, setStatus] = useState(""),
    [running, setRunning] = useState(false),
    [hints, setHints] = useState(0),
    [mode, setMode] = useState("all"),
    [reset, setReset] = useState(false);
  const worker = useRef<Worker | null>(null),
    timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const stop = () => {
    worker.current?.terminate();
    worker.current = null;
    if (timer.current) clearTimeout(timer.current);
  };
  useEffect(
    () => () => {
      worker.current?.terminate();
      if (timer.current) clearTimeout(timer.current);
    },
    [],
  );
  const run = (all: boolean) => {
    stop();
    setResult(null);
    setRunning(true);
    setMode(all ? "all" : "sample");
    setStatus("正在加载本站提供的 Python 环境…");
    const snapshot = source;
    const w = new Worker("/python-worker.mjs", { type: "module" });
    worker.current = w;
    const finish = (r: RunResult) => {
      stop();
      setResult(r);
      setRunning(false);
      setStatus("");
      if (all)
        onResult(
          snapshot,
          r.passed,
          r.error ??
            `${r.rows?.filter((t) => t.passed).length ?? 0}/${task.tests.length} 项测试通过`,
        );
    };
    timer.current = setTimeout(
      () =>
        finish({
          passed: false,
          error: "Python 环境加载超时，请确认本机服务仍在运行后重试。",
        }),
      60000,
    );
    w.onerror = () =>
      finish({
        passed: false,
        error: "Python 环境未能加载，请确认项目完整解压并刷新页面。",
      });
    w.onmessage = ({ data }) => {
      if (data.type === "ready") {
        if (timer.current) clearTimeout(timer.current);
        setStatus("正在运行测试…");
        timer.current = setTimeout(
          () =>
            finish({
              passed: false,
              error: "运行超过 4 秒，已停止。请检查循环的结束条件。",
            }),
          4000,
        );
        w.postMessage({
          source: snapshot,
          function: task.function,
          tests: all ? task.tests : task.tests.slice(0, 2),
        });
      } else if (data.type === "init-error")
        finish({ passed: false, error: data.error });
      else if (data.type === "result") finish(data.result);
    };
  };
  return (
    <div className="coding-layout">
      <section className="panel task-brief">
        <span className="eyebrow">{tr("你的任务")}</span>
        <h2>{tr(task.title)}</h2>
        <p>{tr(task.story)}</p>
        <h3>{tr("完成目标")}</h3>
        <p>{tr(task.objective)}</p>
        <div className="callout">
          <Flag size={17} />
          <p>{tr("请保留函数名")}<code>{task.function}</code>{tr("，用 return 返回结果。")}</p>
        </div>
        <h3>{tr("输入 / 输出示例")}</h3>
        {tr(task.tests.slice(0, 2).map((t, i) => (
          <div className="example" key={i}>
            <code>
              {task.function}({t.args.map((a) => JSON.stringify(a)).join(", ")})
            </code>
            <span>→ {JSON.stringify(t.expected)}</span>
          </div>
        )))}
        <button
          className="text-button"
          onClick={() => setHints(Math.min(task.hints.length, hints + 1))}
          disabled={hints === task.hints.length}
        >
          <Lightbulb size={16} />{tr("需要一点提示？")}{tr(hints)}/{tr(task.hints.length)}
        </button>
        {tr(task.hints.slice(0, hints).map((h) => (
          <p className="hint-box" key={h}>
            {tr(h)}
          </p>
        )))}
        <p className="footnote">{tr("支持基础 Python 语法，不支持导入模块、网络或文件操作。运行环境由本站提供；本机运行无需外网。")}</p>
      </section>
      <section className="editor-panel">
        <div className="editor-header">
          <span>
            <span className="python-dot" /> {tr(task.function)}.py
          </span>
          <button
            aria-label={tr("恢复初始代码")}
            title={tr("恢复初始代码")}
            onClick={() => setReset(true)}
            disabled={running}
          >
            <RotateCcw size={16} />
          </button>
        </div>
        <div className="editor-body">
          <div className="line-numbers" aria-hidden="true">
            {tr(source.split("\n").map((_, i) => (
              <span key={i}>{tr(i + 1)}</span>
            )))}
          </div>
          <textarea
            aria-label={tr("Python 代码编辑器")}
            spellCheck={false}
            autoCapitalize="off"
            autoCorrect="off"
            value={source}
            maxLength={20000}
            disabled={running}
            onChange={(e) => onDraft(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Tab") {
                e.preventDefault();
                const el = e.currentTarget,
                  start = el.selectionStart,
                  end = el.selectionEnd;
                onDraft(source.slice(0, start) + "    " + source.slice(end));
                requestAnimationFrame(() => {
                  el.selectionStart = el.selectionEnd = start + 4;
                });
              }
              if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
                e.preventDefault();
                if (!running) run(true);
              }
            }}
          />
        </div>
        <div className="editor-toolbar">
          <small>{tr("Python · 自动保存草稿")}</small>
          <div>
            {tr(running ? (
              <button
                className="button secondary"
                onClick={() => {
                  stop();
                  setRunning(false);
                  setStatus("运行已停止");
                }}
              >{tr("停止运行")}</button>
            ) : (
              <>
                <button className="button secondary" onClick={() => run(false)}>
                  <Play size={15} />{tr("运行示例")}</button>
                <button className="button primary" onClick={() => run(true)}>{tr("检查答案")}<ArrowRight size={16} />
                </button>
              </>
            ))}
          </div>
        </div>
        <div className="test-results" aria-live="polite">
          <h3>
            <Terminal size={17} />{tr("运行结果")}{tr(result && (
              <Pill>{tr(mode === "sample" ? "示例测试" : "全部测试")}</Pill>
            ))}
          </h3>
          {tr(status && <p>{tr(status)}</p>)}
          {tr(!result && !running && !status && (
            <p className="muted">{tr("代码准备好后，点击“检查答案”。通过测试后会记录到学习进度。")}</p>
          ))}
          {tr(result && (
            <>
              <p className={result.passed ? "success-text" : "error"}>
                {tr(result.error
                  ? `${result.line ? `第 ${result.line} 行 · ` : ""}${result.error}`
                  : result.passed
                    ? mode === "sample"
                      ? "示例通过，接下来检查全部测试。"
                      : "全部测试通过，你完成了这个任务！"
                    : "还有测试未通过，比较实际结果和期望结果。")}
              </p>
              {tr(result.rows?.map((row, i) => (
                <div
                  className={`test-row ${row.passed ? "test-pass" : ""}`}
                  key={i}
                >
                  {tr(row.passed ? <CheckCircle2 size={16} /> : <X size={16} />)}
                  <span>{tr("测试")}{tr(i + 1)}</span>
                  <code>{tr("输入")}{JSON.stringify(row.args)}</code>
                  <code>{tr("期望")}{JSON.stringify(row.expected)}</code>
                  <code>{tr("实际")}{JSON.stringify(row.actual)}</code>
                </div>
              )))}
              {tr(result.stdout && (
                <>
                  <small>{tr("打印输出")}</small>
                  <pre className="output-block">{result.stdout}</pre>
                </>
              ))}
            </>
          ))}
        </div>
      </section>
      {tr(reset && (
        <div className="modal-backdrop">
          <div className="panel modal" role="dialog" aria-modal="true">
            <h2>{tr("恢复初始代码？")}</h2>
            <p>{tr("当前草稿会被替换，已提交的代码记录会保留。")}</p>
            <div className="button-row">
              <button
                className="button secondary"
                onClick={() => setReset(false)}
              >{tr("取消")}</button>
              <button
                className="button primary"
                onClick={() => {
                  onDraft(task.starter);
                  setResult(null);
                  setReset(false);
                }}
              >{tr("恢复初始代码")}</button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
function ProgressChart({ attempts }: { attempts: Attempt[] }) {
  const days: Record<string, { total: number; correct: number }> = {};
  for (const a of attempts) {
    const date = new Date(a.created_at);
    const key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
    days[key] ??= { total: 0, correct: 0 };
    days[key].total++;
    if (a.correct) days[key].correct++;
  }
  const data = Object.entries(days)
    .sort(([a], [b]) => a.localeCompare(b))
    .slice(-14);
  const width = 800,
    height = 230,
    pad = 35;
  const points = data.map(([date, d], i) => ({
    date,
    ...d,
    x:
      pad +
      (width - pad * 2) * (data.length === 1 ? 0.5 : i / (data.length - 1)),
    y: height - pad - (height - pad * 2) * (d.correct / d.total),
  }));
  return (
    <section className="panel chart-panel">
      <div className="section-heading">
        <div>
          <h2>{tr("练习正确率曲线")}</h2>
          <p>{tr("最近 14 个有作答的日期 · 按当前设备时区统计")}</p>
        </div>
        <span className="chart-legend">
          <i />{tr("每日正确率")}</span>
      </div>
      {tr(!points.length ? (
        <div className="chart-empty">
          <TrendingUp size={30} />
          <h3>{tr("你的第一条曲线，从一次练习开始")}</h3>
          <p>{tr("作答后，这里会显示每天的正确率与练习量。")}</p>
        </div>
      ) : (
        <>
          <svg
            className="progress-chart"
            viewBox={`0 0 ${width} ${height}`}
            role="img"
            aria-label={tr("每日练习正确率折线图，详细数据见下表")}
          >
            {tr([0, 25, 50, 75, 100].map((n) => (
              <g key={n}>
                <line
                  x1={pad}
                  x2={width - pad}
                  y1={height - pad - ((height - pad * 2) * n) / 100}
                  y2={height - pad - ((height - pad * 2) * n) / 100}
                  stroke="#eceaf2"
                  strokeDasharray="4 4"
                />
                <text
                  x="0"
                  y={height - pad - ((height - pad * 2) * n) / 100 + 4}
                  fontSize="10"
                  fill="#88849a"
                >
                  {tr(n)}%
                </text>
              </g>
            )))}
            <polyline
              points={points.map((p) => `${p.x},${p.y}`).join(" ")}
              fill="none"
              stroke="#7654db"
              strokeWidth="3"
              strokeLinejoin="round"
            />
            {tr(points.map((p, i) => (
              <g key={p.date}>
                <circle
                  cx={p.x}
                  cy={p.y}
                  r="5"
                  fill="#7654db"
                  stroke="white"
                  strokeWidth="2"
                >
                  <title>
                    {tr(p.date)}：{tr(Math.round((p.correct / p.total) * 100))}%，
                    {tr(p.total)}{tr("次")}</title>
                </circle>
                {tr((i === 0 || i === points.length - 1 || points.length < 8) && (
                  <text
                    x={p.x}
                    y={height - 8}
                    textAnchor="middle"
                    fontSize="11"
                    fill="#88849a"
                  >
                    {tr(p.date.slice(5))}
                  </text>
                ))}
              </g>
            )))}
          </svg>
          <details className="chart-details">
            <summary>{tr("查看曲线数据")}</summary>
            <table>
              <thead>
                <tr>
                  <th>{tr("日期")}</th>
                  <th>{tr("作答次数")}</th>
                  <th>{tr("答对次数")}</th>
                  <th>{tr("正确率")}</th>
                </tr>
              </thead>
              <tbody>
                {tr(points.map((p) => (
                  <tr key={p.date}>
                    <td>{tr(p.date)}</td>
                    <td>{tr(p.total)}</td>
                    <td>{tr(p.correct)}</td>
                    <td>{tr(Math.round((p.correct / p.total) * 100))}%</td>
                  </tr>
                )))}
              </tbody>
            </table>
          </details>
        </>
      ))}
    </section>
  );
}
