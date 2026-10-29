# PySteps

Python learning with explanatory feedback and the PiPo learning agent

## English

**Group 8**

### 1. Project overview

PySteps helps Python beginners decide what to do after a mistake. It connects concept reading, answer feedback, targeted practice and chapter coding in one learning application. PiPo adds a conversational route through the same content: it can inspect the learner's progress, read lessons, select practice and open a specific activity through a bounded model–tool loop.

The curriculum covers **3 chapters, 15 concepts, 30 multiple-choice questions and 6 coding tasks with 39 test cases**. Topics are conditionals, loops, and functions and return values. The application supports self-study, classroom practice and small-group demonstrations.

Python implements the learning rules, model integration, HTTP service and SQLite persistence. React provides the interface, while Pyodide executes learner code in a browser Worker. The distribution includes the built interface and browser runtime, so the core learning flow runs locally without a package installation or external CDN.

### 2. Start the application

Requirements: **Python 3.10 or later**, a modern browser and the fully extracted project.

Run from the directory containing `main.py`:

```bash
python main.py --open
```

Use `python3 main.py --open` on macOS if needed, or `py main.py --open` with the Windows Python launcher. Open **http://127.0.0.1:8010/**, or follow the URL printed in the terminal. Keep the terminal running; press `Ctrl+C` to stop.

```bash
python main.py --port 8011 --open
python main.py --db runtime/learning.sqlite3
```

Normal use requires no third-party Python packages, Node.js or Docker. The service serves `web/static/`; opening its HTML directly does not start the application.

### 3. Current features

| Feature | Current behaviour |
|---|---|
| Learning map and lessons | Introduction and ordered concept lessons with objectives, explanations, worked code and reflection prompts. |
| Course quizzes | Prerequisites determine access. Reading and independent correct answers to both concept questions establish completion in the current bank. Hinted answers and free practice do not establish course completion. |
| Free practice | Practise any of the 30 questions, with fixed answer keys, explanations, progressive hints and wrong-option concept clues. |
| Reason revision | Add or edit a reason after submitting a wrong answer, then request analysis of the same attempt. |
| Targeted practice | Rank existing same-chapter questions, excluding the current question: unseen target concept, due review, other unseen items, then other seen items. |
| Review scheduling | Wrong answers become due in 10 minutes; independent successes at the due time progress through 1, 3, 7, 14 and 30 days. |
| GLM-4.7 diagnosis | Optional analysis quotes the learner's reason and checks the model's answer/evidence fields against the question bank before displaying personalised teaching text. |
| PiPo learning agent | Interpret a learning goal, inspect progress and content through tools, adapt to observations and open one validated activity. Tool activity is visible in the reply. |
| Chapter coding | Six tasks with saved drafts, sample execution, full case checking, error locations, execution timeout and submission history. Tasks can be opened before completing quizzes. |
| Progress and mistakes | Inspect course states, attempts, coding completion and wrong-answer history. The accuracy plot covers the latest 14 dates with quiz attempts, using the device's timezone. |
| Persistence and backup | SQLite learning spaces, revision conflict detection and JSON export/import. Imports replace the current space after confirmation and regrade quiz answers. |
| Language | English on first visit, with a remembered English/Chinese switch. |

### 4. PiPo in use

Open PiPo, enter the team AI access code and give it a goal such as:

- “Check my progress, plan my next step and open it.”
- “Review my mistakes and choose targeted practice.”
- “Choose a coding task I have not passed.”
- “Explain the difference between `and` and `or`.”

PiPo uses five tools: `progress`, `lesson`, `recommend`, `coding` and `open_content`. The model chooses tools; Python executes them and returns observations to the model. A turn permits **up to 5 model requests, 8 tool executions and 1 content opening**. Content must be inspected before it can be opened, and locked lessons are rejected. A follow-up turn receives the current learning state.

PiPo can read learning information and prepare navigation to specific content. Grading, course completion and saved records remain under the existing learning rules and learner actions. The Stop control cancels browser waiting and pending page actions; a model request already issued by the server may continue.

### 5. Optional model configuration

Copy `config.example.json` to `config.local.json` in the project root, configure the values and restart. Matching environment variables take precedence. The program does not automatically load `.env`.

| Setting | Use |
|---|---|
| `OPENAI_API_KEY` | School gateway API key for GLM-4.7, without a `Bearer ` prefix. |
| `OPENAI_MODEL` | Account-available model ID. The code uses `glm-4.7` when this field is empty. PiPo requires function tool-call support. |
| `OPENAI_BASE_URL` | `https://maas.eduhk.hk/api/v1` (school gateway). |
| `TEAM_ACCESS_CODE` | At least 12 characters. Enter this access code in the browser; keep the provider key on the server. |
| `PUBLIC_ORIGIN` | Leave empty for local use; set the exact origin for LAN access. |

Diagnosis is requested for an incorrect answer with a non-empty reason. It sends the question, standard explanation, answer information, learner reason and candidate concept to GLM-4.7. PiPo sends the learning goal, up to eight recent conversation messages and tool-selected observations. Progress observations include up to five recent wrong-answer reasons, each truncated to 500 characters. PiPo tools do not send code drafts or credentials to the model. Conversation history stays in page memory.

Diagnosis and PiPo share **60 model requests per hour per server process**. Each PiPo model round counts separately; restarting resets the counter. Provider usage may incur charges. Diagnosis uses a 60-second request timeout and a 75-second browser wait threshold; PiPo JSON mode uses up to 60 seconds per model request and a 115-second browser wait threshold. These are operational limits, not a total latency guarantee.

Without model configuration, lessons, rule feedback, recommendations, coding and backups remain available. Diagnosis uses rule feedback on provider failure. PiPo displays an explicit failure if its turn cannot complete. Model response validation constrains fields and evidence; it does not establish diagnostic accuracy or learning improvement.

### 6. Python design and course concepts

| Responsibility | Implementation | Course connection |
|---|---|---|
| Learning decisions | `LearningEngine` functions, dictionaries, sets and ordered ranking | Functions, classes, collections and modularity in Lecture03. |
| Reliable records | SQLite transactions and revision checks | File/data handling, exceptions and separation of responsibilities. |
| Model interaction | Structured messages, bounded inputs and JSON validation | Instruction, context, input and output format in Lecture04. |
| Autonomous learning support | Model calls, allowlisted tools and observations in `backend/agent.py` | Model + harness and the agent loop in Lecture05. |
| Verifiable behaviour | Requirements, automated tests and interface acceptance cases | Functional/non-functional requirements and matching verification in Lecture06. |

### 7. Tests and quality evidence

Run the complete suite:

```bash
python -m unittest discover -s tests -t . -v
```

**Verified on 29 October 2026: 38 test methods passed on macOS with Python 3.12.** Of these, 32 exercise project behaviour; 6 in `test_main.py` exercise self-contained examples. AI responses are simulated and HTTP tests use temporary local services/databases, so this command makes no paid model calls.

| Test file | Methods | Main evidence |
|---|---:|---|
| `test_core.py` | 14 | All 30 question outputs, course progression, review scheduling, recommendation, backup validation, SQLite, diagnosis and 39 reference coding cases. |
| `test_http.py` | 6 | Actual local endpoints, private-file access, cookies, revision conflicts, invalid requests, AI access and Agent responses. |
| `test_language.py` | 2 | Translation entries and English diagnosis prompts preserving source evidence. |
| `test_agent.py` | 10 | Multi-round tools, error recovery, valid actions, context/privacy boundaries, call budgets and invalid output handling. |
| `test_main.py` | 6 | Independent configuration/scoring examples. |

GitHub Actions defines Python checks on Ubuntu, Windows and macOS with Python 3.10/3.13, plus frontend checking/building. Current local results above are separate from remote run outcomes. Browser acceptance and live-model evaluation have their own procedures in [SPEC.md](SPEC.md).

For code review, record the reviewer, version, code location, finding, resolution and recheck. AI can assist review; completed human-review records provide the independent review evidence used in the course assessment.

### 8. Development and project structure

```text
main.py                 Python entry point
backend/domain.py       Grading, courses, ranking, review, state validation
backend/agent.py        PiPo model–tool loop and tool execution
backend/ai.py           GLM-4.7 diagnosis, validation and TLS
backend/server.py       HTTP endpoints, access checks, session identity
backend/storage.py      SQLite transactions and revision control
data/                   Concepts, lessons, questions and coding tasks
web/src/                React/TypeScript source
web/public/             Worker, validator, images and local Pyodide
web/static/             Built browser distribution
tests/                  Automated tests and reference solutions
scripts/                Packaging and AI evaluation
submission/             English/Chinese presentations and supporting material
licenses/               Upstream licence texts
SPEC.md                 Functional contracts and evaluation plan
```

Frontend contributors use Node.js and npm; CI selects Node.js 22:

```bash
cd web
npm ci
npm run check
npm run build
```

Rebuild after changing frontend source, public assets or imported content. Restart after changing backend code or configuration.

### 9. Records, deployment and troubleshooting

The default database is `runtime/learning.sqlite3`. A random browser cookie identifies a learning space. Use JSON export/import to move records across browsers or devices. On a version conflict, export current records before refreshing.

The current limits are 10,000 quiz attempts, 2,000 coding records, 1,000-character reasons/goals, 20,000-character code and 10,000,000-byte HTTP bodies. Browser code loading has a 60-second threshold and execution a 4-second threshold. The AST validator restricts imports, file access and indirect operations. The runtime does not impose a hard memory quota.

For LAN demonstrations, set `PUBLIC_ORIGIN` to the exact LAN origin and run `python main.py --host 0.0.0.0 --port 8010`. The terminal prints a loopback URL; other devices should use the server's LAN address. The intended deployment is local learning and small-group use.

| Symptom | Action |
|---|---|
| Port in use | Stop the existing service or select a different port. |
| Old interface | Rebuild the frontend, then refresh. |
| PiPo unavailable | Check model configuration, tool-call support, team code, network and request allowance; restart after config changes. |
| Runtime fails to load | Preserve the full `web/static/pyodide/` directory. |
| Save conflict | Export a backup, then refresh and reconcile records. |
| TLS certificate error | Repair Python/system certificate configuration and retain certificate verification. |

### 10. Submission, AI disclosure and sources

```bash
python scripts/package_submission.py --group 8
```

The Group 8 archive is `dist/group8_project.zip`; it includes backend/frontend source, data, tests and built assets, and excludes local credentials, learner databases, dependency caches and Git history. Classroom slides are `submission/group8_presentation.pptx` (English) and `submission/group8_presentation_zh.pptx` (Chinese): five technical slides, targeting 4:45 within five minutes. Video support decks are `submission/group8_video_en.pptx` and `submission/group8_video_zh.pptx`: nine slides, targeting 14:30 with 8:15 of live application demonstration. Submit the actual recording within 15 minutes; a slide deck is not the video. The recording/classroom guide contains operating steps, Q&A preparation and the mandatory peer-assessment checklist. Submit the 15-minute video, individual PDF reports of at least 600 words and peer assessments through the course's Moodle entries.

Generative AI assisted implementation, test development, specification writing, documentation and code inspection. GLM-4.7 also powers the optional diagnosis and PiPo features at runtime. The group owns design decisions, verifies accepted outputs and records actual individual contributions. AI-assisted development artefacts support the course's bonus criterion for engineering use of generative AI.

Sources: supplied INT6181 Project Requirements v2; Lecture03 *Review of Programming II*; Lecture04 *Generative AI in Programming*; Lecture05 *Foundation of Coding Agents*; Lecture06 *Testing and Debugging I*. Third-party components: [Python](https://www.python.org/), [React](https://github.com/facebook/react), [Lucide](https://github.com/lucide-icons/lucide), [Pyodide](https://github.com/pyodide/pyodide), [TypeScript](https://github.com/microsoft/TypeScript) and [esbuild](https://github.com/evanw/esbuild). Licence texts are retained in `licenses/`. Reports should cite the particular external resources actually used by each contributor.

---

## 中文

**第 8 组**

### 1. 项目概述

PySteps 帮助 Python 初学者解决“答错以后，下一步该学什么”的问题。系统把概念阅读、错因反馈、针对性练习与章节编程连接成完整的学习流程。PiPo 提供自然语言入口：读取学习进度、查阅导学、选择练习，再通过受限的模型—工具循环打开具体学习活动。

现有课程包含 **3 章、15 个概念、30 道选择题、6 个编程任务及 39 个任务测试案例**，覆盖条件判断、循环、函数与返回值，适用于自主学习、课堂练习与小组演示。

Python 负责学习规则、模型接入、HTTP 服务及 SQLite 持久化；React 提供交互界面，Pyodide 在浏览器 Worker 中运行学生代码。随包提供网页构建产物和浏览器 Python 运行时，核心学习流程可在本地使用，无需安装第三方 Python 包或访问外部 CDN。

### 2. 启动应用

准备 **Python 3.10 或以上版本**、现代浏览器，并完整解压项目。在包含 `main.py` 的目录运行：

```bash
python main.py --open
```

macOS 可使用 `python3 main.py --open`，Windows 可使用 `py main.py --open`。默认地址为 **http://127.0.0.1:8010/**，以终端实际输出为准。保持终端运行，按 `Ctrl+C` 停止。

```bash
python main.py --port 8011 --open
python main.py --db runtime/learning.sqlite3
```

正常使用无需 Node.js、Docker 或第三方 Python 依赖。服务从 `web/static/` 提供网页，直接双击静态 HTML 不会启动应用。

### 3. 已实现功能

| 功能 | 当前行为 |
|---|---|
| 学习地图与导学 | 提供入门导学及按顺序组织的概念课程，包含目标、讲解、代码示例与思考问题。 |
| 课程测验 | 按前置条件开放课程；当前题库中，阅读后无提示独立答对该概念的两道题即可过关。提示作答和自由练习不计入课程完成。 |
| 自由练习 | 随时练习 30 道题，提供固定答案、标准解析、逐级提示及错误选项对应的概念线索。 |
| 理由修订 | 错答后可补充或修改理由，再分析原有作答，不增加作答次数。 |
| 针对性推荐 | 在当前章节排除原题，按“目标概念未做题、到期复习、其他未做题、其他已做题”排序。 |
| 复习安排 | 错答后 10 分钟到期；到期后无提示答对，按 1、3、7、14、30 天逐级安排。 |
| GLM-4.7 思路诊断 | 可选模型分析引用学生原话，按题库检查答案及依据字段，再展示个性化讲解。 |
| PiPo 学习 Agent | 理解学习目标，自主调用进度和内容工具，根据观察继续决策，并打开一个已验证的活动；回复可展开工具记录。 |
| 章节编程 | 六项任务提供草稿保存、示例运行、完整测试、错误行提示、执行超时及提交历史，可在完成测验前进入。 |
| 进度与错题 | 查看课程状态、答题统计、编程完成情况及错题历史；曲线按设备时区展示最近 14 个有选择题作答的日期。 |
| 保存与备份 | SQLite 独立学习空间、版本冲突检测、JSON 导出与导入；确认导入后替换当前空间并重新判分。 |
| 语言切换 | 首次访问默认英语，可切换中英文并记忆选择。 |

### 4. 使用 PiPo

打开 PiPo，输入团队 AI 口令，然后描述目标，例如：

- “根据我的进度安排下一步，并带我开始。”
- “检查我的错题，挑一道针对性练习。”
- “选择一个我还没有通过的编程任务。”
- “解释一下 `and` 和 `or` 的区别。”

PiPo 有五个工具：`progress`、`lesson`、`recommend`、`coding`、`open_content`。模型选择工具，Python 执行工具并把观察结果返回模型。每轮最多 **5 次模型请求、8 次工具执行、1 次内容打开**。打开前必须先检查相应内容，锁定课程会被拒绝；后续对话使用当前学习状态。

PiPo 可读取学习信息并准备打开具体内容；判分、课程完成和学习记录仍由既有规则与学生操作控制。点击“停止本轮”会取消浏览器等待和待应用的页面操作；服务端已经发出的模型请求可能继续。

### 5. 可选模型配置

在项目根目录复制 `config.example.json` 为 `config.local.json`，填写后重启。匹配的环境变量优先于文件，程序不自动加载 `.env`。

| 配置项 | 用途 |
|---|---|
| `OPENAI_API_KEY` | 学校网关用于 GLM-4.7 的服务端密钥，不添加 `Bearer ` 前缀。 |
| `OPENAI_MODEL` | 账户可用模型 ID；为空时使用代码默认值 `glm-4.7`。PiPo 需要模型支持函数工具调用。 |
| `OPENAI_BASE_URL` | 学校网关：`https://maas.eduhk.hk/api/v1`。 |
| `TEAM_ACCESS_CODE` | 至少 12 个字符；网页填写团队口令，模型密钥留在服务端。 |
| `PUBLIC_ORIGIN` | 本机运行留空；局域网访问时填写准确来源地址。 |

错答且理由非空时可请求思路诊断，向 GLM-4.7 发送题目、标准解析、答案信息、学生理由与候选概念。PiPo 发送学习目标、最近最多八条对话及工具读取的信息；进度工具包含最近最多五条错题理由，每条截取 500 字符。PiPo 工具不向模型发送代码草稿或凭据；对话记录保留在页面内存中。

诊断与 PiPo 共享**每个服务进程每小时 60 次模型请求**，PiPo 每轮模型调用分别计数，重启会重置计数。模型调用可能产生费用。诊断的请求超时参数为 60 秒、浏览器等待阈值为 75 秒；PiPo JSON 模式每次模型请求最多为 60 秒、浏览器等待阈值为 115 秒。这些是运行限制，不是总响应时间保证。

未配置模型时仍可使用导学、规则反馈、推荐、编程与备份。诊断遇到服务故障保留规则反馈；PiPo 未完成本轮时明确显示失败。模型输出校验约束字段与引用依据，诊断准确性和学习效果需通过相应评估确定。

### 6. Python 设计与课程知识

| 职责 | 实现方式 | 课程对应 |
|---|---|---|
| 学习决策 | `LearningEngine`、函数、字典、集合与排序 | Lecture03 的函数、类、容器及模块化。 |
| 学习记录 | SQLite 事务与版本检查 | 数据处理、异常处理和职责分离。 |
| 模型交互 | 结构化消息、受限输入与 JSON 校验 | Lecture04 的指令、上下文、输入与输出格式。 |
| 自主学习支持 | `backend/agent.py` 的模型调用、工具白名单和观察结果 | Lecture05 的模型加执行环境及 Agent 循环。 |
| 行为验证 | 需求、自动测试及界面验收案例 | Lecture06 的功能/非功能需求与验证对应。 |

### 7. 测试与质量证据

在项目根目录运行完整测试：

```bash
python -m unittest discover -s tests -t . -v
```

**2026 年 10 月 29 日，macOS / Python 3.12 环境下 38 个测试方法全部通过。** 其中 32 个验证项目行为，`test_main.py` 中另有 6 个自包含示例测试。模型响应使用模拟数据，HTTP 测试使用临时本机服务和数据库，不调用付费模型。

| 测试文件 | 方法数 | 主要证据 |
|---|---:|---|
| `test_core.py` | 14 | 30 道题输出、课程路径、复习、推荐、备份校验、SQLite、诊断及 39 个编程参考案例。 |
| `test_http.py` | 6 | 真实本机接口、私有文件访问、Cookie、版本冲突、无效请求、AI 授权及 Agent 响应。 |
| `test_language.py` | 2 | 翻译条目完整性与保留原始依据的英文诊断提示。 |
| `test_agent.py` | 10 | 多轮工具、拒绝后恢复、动作校验、上下文与凭据边界、次数限制及异常输出。 |
| `test_main.py` | 6 | 独立配置读取与成绩计算示例。 |

GitHub Actions 配置 Ubuntu、Windows、macOS 与 Python 3.10/3.13 矩阵，以及网页检查和构建。上述本地结果与远端运行结果分别记录；浏览器验收及真实模型评估流程见 [SPEC.md](SPEC.md)。

代码审查记录包含审查人、版本、代码位置、问题、处理与复核。AI 可辅助审查，真实完成的人工审查记录用于呈现课程要求的独立审查证据。

### 8. 开发与目录

```text
main.py                 Python 启动入口
backend/domain.py       判分、课程、推荐、复习与状态校验
backend/agent.py        PiPo 模型工具循环与工具执行
backend/ai.py           GLM-4.7 诊断、输出校验与 TLS
backend/server.py       HTTP 接口、访问校验与会话标识
backend/storage.py      SQLite 事务与版本控制
data/                   概念、导学、题目与编程任务
web/src/                React/TypeScript 源码
web/public/             Worker、校验器、图片与本地 Pyodide
web/static/             网页构建产物
tests/                  自动测试与参考解
scripts/                打包与 AI 评估脚本
submission/             中英文演示文稿及辅助材料
licenses/               第三方许可
SPEC.md                 功能合同与评估方案
```

修改前端时使用 Node.js 和 npm，CI 采用 Node.js 22：

```bash
cd web
npm ci
npm run check
npm run build
```

修改前端源码、公开资源或前端导入的数据后重新构建；修改后端或配置后重启服务。

### 9. 数据、部署与排错

默认数据库为 `runtime/learning.sqlite3`，随机浏览器 Cookie 对应一个学习空间。通过 JSON 导出/导入迁移到其他浏览器或设备。遇到版本冲突，先导出当前记录再刷新。

当前限制为每空间 10,000 条选择题记录、2,000 条编程记录，理由/目标最多 1,000 字符，代码最多 20,000 字符，HTTP 请求体最多 10,000,000 字节。浏览器运行时加载阈值为 60 秒、代码执行阈值为 4 秒。AST 校验器限制导入、文件访问及间接操作；运行时不提供硬性内存配额。

局域网演示时，将 `PUBLIC_ORIGIN` 设为准确的局域网来源，运行 `python main.py --host 0.0.0.0 --port 8010`。终端仍打印回环地址，其他设备使用服务器局域网地址访问。应用面向本地学习与小组使用。

| 情况 | 处理方式 |
|---|---|
| 端口已占用 | 停止旧服务或指定其他端口。 |
| 页面仍是旧版 | 重新构建前端并刷新。 |
| PiPo 不可用 | 检查模型配置、工具调用支持、团队口令、网络及请求额度；改配置后重启。 |
| 编程环境加载失败 | 保留完整的 `web/static/pyodide/`。 |
| 保存冲突 | 导出备份，再刷新协调记录。 |
| TLS 证书错误 | 修复 Python/系统证书配置，保留证书验证。 |

### 10. 提交、AI 声明与来源

```bash
python scripts/package_submission.py --group 8
```

第 8 组提交包为 `dist/group8_project.zip`。提交包包含前后端源码、数据、测试及构建资源，排除本地凭据、学习数据库、依赖缓存和 Git 历史。课堂稿为 `submission/group8_presentation.pptx`（英文）及 `submission/group8_presentation_zh.pptx`（中文），均为五页技术精选，目标讲解 4:45，控制在五分钟内。视频配套稿为 `submission/group8_video_en.pptx` 与 `submission/group8_video_zh.pptx`，均九页，目标 14:30，其中安排 8:15 真实应用操作。实际录制视频控制在十五分钟内，PPT 不替代视频。录制与课堂指南包含操作步骤、答问准备及全员同伴互评清单。15 分钟视频、每人至少 600 词的个人 PDF 报告及同伴评价按 Moodle 对应入口提交。

项目使用生成式 AI 辅助实现、测试开发、规格编写、文档及代码检查；GLM-4.7 在运行时支持可选诊断与 PiPo。小组负责设计决策、核对采用的输出，并记录真实个人贡献。开发过程中的 AI 使用材料用于呈现课程规定的工程应用加分项。

依据：所提供的 INT6181 项目要求 v2、Lecture03 编程复习、Lecture04 编程中的生成式 AI、Lecture05 编程 Agent 基础、Lecture06 测试与调试。第三方组件包括 [Python](https://www.python.org/)、[React](https://github.com/facebook/react)、[Lucide](https://github.com/lucide-icons/lucide)、[Pyodide](https://github.com/pyodide/pyodide)、[TypeScript](https://github.com/microsoft/TypeScript) 与 [esbuild](https://github.com/evanw/esbuild)，许可文本保存在 `licenses/`。个人报告应注明本人实际采用的外部资源。

## GLM-4.7 学校平台配置说明

在 config.local.json 的 OPENAI_API_KEY 中自行填写学校密钥，保留 TEAM_ACCESS_CODE 后重启 main.py。旧供应商密钥已从本地配置移除；环境变量优先于文件，请检查是否已有 OPENAI_API_KEY 覆盖文件值。不要将配置文件提交到仓库。

建议模型为 glm-4.7，适合短篇诊断、JSON 输出及 PiPo 工具调用；学校列表已列出此模型；网关是否接受同名 API ID 及完整参数仍待实测。若平台使用不同 ID，请按学校列表修改 OPENAI_MODEL。地址为 https://maas.eduhk.hk/api/v1，程序追加 /chat/completions。公开路由返回认证错误，不能据此认定完整 OpenAI 参数兼容；填入密钥后仍需验证诊断与工具调用。此次迁移未调用付费模型。

## GLM-4.7 configuration

Enter your school key in OPENAI_API_KEY in config.local.json, keep TEAM_ACCESS_CODE and restart main.py. The previous provider key was removed from local configuration. Environment variables override file settings. Never commit the local configuration.

The recommended model is glm-4.7 for short diagnoses, JSON output and PiPo function calls. The school lists this model; gateway model-ID mapping and parameter support still require live verification. Set OPENAI_MODEL to the ID available in your school account. The base URL is https://maas.eduhk.hk/api/v1; the client appends /chat/completions. An authentication response from the public route does not prove full parameter compatibility. Live diagnosis and tool calls still need verification after you enter the key. No paid model request was made during migration.

模型成本 / Model cost: 用户提供的学校价格为 glm-4.7 输入 0.1、输出 0.5 积分/1K tokens。School-listed rates: 0.1 input and 0.5 output credits per 1K tokens. Requests disable GLM thinking to reduce reasoning overhead; gateway support remains unverified. 学校提供 OpenAI 兼容接口，实际模型为智谱 GLM，并非 OpenAI GPT。The gateway is OpenAI-compatible; the selected model is Z.ai GLM, not OpenAI GPT.

学校认证错误 / School authentication error: 如果服务返回 “use the app key rather than the account key”，当前接口要求应用的 App Key，不能使用账户页面生成的 Account Key。请在学校平台的应用/API 发布配置中查找应用密钥；若无权限，请向学校管理员索取兼容 Chat Completions、支持指定模型及 tools 参数的正确访问方式。Do not substitute an Account Key when this endpoint requires an App Key. Ask the school administrator for the supported account-level model endpoint if application keys are unavailable. A successful App Key authentication still requires verification that model selection, JSON output and tool calls are supported; some application endpoints use a preconfigured workflow instead.

学校响应兼容 / School response compatibility: 诊断允许纯 JSON 或单个 Markdown JSON 代码块，解包后仍执行原有答案、概念标签及逐字引用校验。Diagnosis accepts plain JSON or one fenced JSON block; answer, concept and evidence validation still apply. The school response may leave model and usage metadata empty or placeholder-valued; do not treat those fields as verified model identity or billing evidence. 学校返回的模型及用量字段可能为空或占位值，不能据此确认实际模型或计费。

## 学校网关的等待与工具兼容

诊断限制为简短讲解，输出上限 700 tokens；后端单次等待 60 秒，网页等待 75 秒。没有自动重试。增加等待只减少过早超时，不能保证学校服务提速或不会超时。学校可能忽略 thinking 参数，实际推理开销由学校应用配置决定。

AI_AGENT_MODE=json 为学校网关的默认本地配置：PiPo 先读取真实进度，再让模型返回 JSON 工具计划；程序逐项校验并执行，再传回结果。使用单个 JSON 对象而非原生 tool_calls，避免网关将工具标记输出给学生。每轮最多 5 次模型调用、8 个计划工具及 1 次页面打开，另有 1 次本地进度读取；总时间预算约 100 秒，单次最多等待 60 秒，网页等待 115 秒。失败不应用页面操作；正在进行的网络读取不保证能即时中止。原生工具模式仍可供经验证支持 tools 的网关使用（AI_AGENT_MODE=native）。

## School gateway latency and tools

Diagnosis uses concise output capped at 700 tokens, a 60-second backend socket timeout and a 75-second browser wait, without automatic retries. Longer waits reduce premature timeouts but cannot guarantee faster service. The gateway may ignore thinking controls; the school application's configuration determines actual reasoning overhead.

AI_AGENT_MODE=json reads real progress locally, requests a JSON tool plan, validates and executes allowed tools, and returns observations to the model. It does not rely on native tool_calls support. A turn allows five model calls, eight planned tools and one content opening, plus an initial local progress read. The turn budget is approximately 100 seconds, each model wait at most 60 seconds, and the browser waits 115 seconds. Failed turns do not apply page actions; in-flight reads may not stop immediately. Verified gateways can use AI_AGENT_MODE=native.

模型命名说明 / Model naming: 界面与文档统一使用 GLM-4.7（智谱），学校平台是访问网关。OPENAI_API_KEY、OPENAI_MODEL、OPENAI_BASE_URL 是兼容接口的配置字段，并不表示使用 GPT。界面名称表示配置的目标模型；学校响应未给出可信模型 ID，实际路由仍需以学校应用设置为准。The displayed name GLM-4.7 identifies the configured Z.ai model, accessed through the school gateway. OPENAI_* keys describe the compatible API configuration, not a GPT model. Since gateway model metadata is empty, the actual routing must be confirmed in the school application settings.
