# 中文版：PySteps 使用说明

PySteps 面向 Python 初学者，提供概念导学、选择题、错题理由分析与章节编程。系统是由 Python 后端支持的网页应用，统一从 `main.py` 启动。

## 1. 运行程序

环境要求：Python 3.10+、现代浏览器以及完整解压的项目。普通运行不需要 Node.js、pip 依赖或 Docker。运行服务的电脑须安装 Python；访问已部署网站的人只需浏览器。

在含 `main.py` 的目录打开终端：

|环境 |命令 |
|---|---|
|通用 | `python main.py --open` |
| macOS（python3） | `python3 main.py --open` |
|Windows 启动器 | `py main.py --open` |

打开终端显示的网址，通常为 `http://127.0.0.1:8000/`。保持终端运行，Ctrl+C 停止。端口被占用时，停止旧实例，或使用 `python main.py --port 8001 --open`；新端口不会更新旧进程。双击 `打开网页版.html` 只显示入口说明。

可选数据库位置：`python main.py --db runtime/learning.sqlite3`。

## 2. 语言与学习流程

首次访问默认英语，右上角按钮可切换中英文并记住选择。切换保留作答、个人文字与代码草稿。代码和精确输出字符串不翻译；新的 AI 请求使用当前语言，历史 AI 讲解保留原文。

1. 从学习地图阅读入门导学并选择概念。
2. 进入课程闯关，或在自由练习选择主题。
3. 提交答案，可选填写理由。
4. 答错后可补充或修改思路，并选择调用 AI 分析。
5. 继续针对性练习，或进入本章编程任务。
6. 查看学习进度并导出备份。

## 3. 已实现功能

|功能 |当前行为 |
|---|---|
|知识架构 |3 章、15 个概念和前置关系 |
|概念导学 |学习目标、解释、代码、输出与思考题 |
|课程闯关 |阅读后无提示独立答对同概念两道不同题 |
|自由练习 |30 道选择题；自由练习不解锁课程 |
|判分 |标准答案、经自动执行核验的输出和规则概念线索 |
|补充思路 |在原作答记录补充理由并重新分析，不重复计数 |
|推荐 |当前章按概念、未做记录、到期复习排序，排除当前题 |
|AI 诊断 |可选 Kimi 理由分析、原文引用、受限标签和反馈校验 |
|章节编程 |6 个故事任务、39 个测试案例，不必先完成选择题 |
|编辑器 |草稿、示例运行、全例检查、错误反馈、停止与历史 |
|学习进度 |错题、统计、概念状态、最近 14 个有作答日期的正确率曲线与表格 |
|保存 |SQLite、JSON 备份和保存冲突检测 |
|导航助手 |中英文快捷入口与关键词导航，不调用大模型 |

下一题操作位于原提交区。一次答错只是线索，不能证明存在误区；通过当前小题库也不等于全面掌握。题库的教育内容与概念标签仍待团队复核。

## 4. 推荐与复习算法

在当前章节排除原题后，依次推荐：①同疑似误区的未做题；②到期复习题，较早到期优先；③其他未做题；④尚未到期的已做题。余下排序结合适用时的目标概念、难度和题号；页面取首项。诊断为 `unknown` 时，优先到期题，再选未做题，不强行归因。

答错后 10 分钟复习；使用提示答对在一天内安排复习且不提升阶段；到期后独立答对，间隔依次为 1、3、7、14、30 天；提前重复不提升阶段。这是确定性排序与固定复习间隔，题库较小仍会重复，目前不估计个人能力来动态调整难度。

## 5. 可选 Kimi 配置

在根目录将 `config.example.json` 复制为 `config.local.json` 后编辑。真实密钥不要写入示例、前端或提交 ZIP。同名环境变量优先于文件，程序不自动读取 `.env`。修改后必须重启服务。

|字段 |含义 |
|---|---|
| `MOONSHOT_API_KEY` |API 密钥本身，不加 `Bearer ` 前缀 |
| `MOONSHOT_MODEL` |账号有权限的模型；代码默认 `kimi-k2.6`，不保证账号可用 |
| `MOONSHOT_BASE_URL` |`https://api.moonshot.cn/v1` 或 `https://api.moonshot.ai/v1`，与密钥所属服务匹配 |
| `TEAM_ACCESS_CODE` |至少 12 字符的团队口令，网页填写此项 |
| `PUBLIC_ORIGIN` |本机留空，网络访问填写准确来源地址 |

答错且理由非空时，已选择 AI 的用户可触发分析；也可提交后主动分析。答对或空理由不调用模型。修改理由会清除旧 AI 反馈，再次分析更新原记录；每次主动重试都可能收费。

模型只能选择候选误区或 `unknown`，须引用理由原文；个性化讲解还检查答案与标准解析引文。校验不等于整段讲解正确。目前 60 个错误选项都映射到各自题目的概念，诊断粒度较粗，需人工复核；Kimi 不能另选其他误区或生成新题。

后端等待最多 30 秒、界面最多 40 秒；认证、网络、输出或依据失败时回退规则。每进程每小时限 60 次，重启会重置，并非账单上限。未采用的响应也可能已产生费用。2026 年 10 月 27 日审核未进行付费调用，未验证当前密钥或真实模型质量。

## 6. 数据与代码运行边界

默认数据库为 `runtime/learning.sqlite3`，随机浏览器 Cookie 对应学习空间。保留 Cookie 与数据库才能继续原记录；没有账号自动跨设备同步。通过导出/导入转移；导入会替换当前空间、重判答案并恢复标准反馈。更换浏览器、主机名或清 Cookie 可能进入新空间；冲突时先备份再刷新。

每空间最多 10,000 次答题、2,000 次代码提交；理由最多 1,000 字符、代码 20,000 字符、请求 10 MB；没有自动归档。

代码在浏览器 Worker 内由随包 Pyodide 运行，不在服务器执行。语法白名单不允许导入、网络和文件操作；加载限 60 秒、执行限 4 秒。运行示例检查两例，检查答案运行全部案例并保存结果。没有硬性内存配额，浏览器成绩不是防篡改考试凭证。

## 7. 常见问题

|现象 |处理 |
|---|---|
|端口占用 |停止旧服务或更换端口 |
|AI 未配置 |检查密钥、至少 12 字符口令并重启 |
|Kimi 认证失败 |核对密钥、接口与环境变量，不是答案无效 |
|团队口令错误 |网页填写团队口令而非密钥 |
|界面未更新 |构建后刷新，后端或配置修改后重启 |
|证书错误 |修复系统或 Python 证书，不关闭校验 |
|编程环境失败 |保持服务运行并完整保留运行时目录 |
|保存冲突 |先导出备份，再刷新恢复 |

## 8. 测试与开发

测试目标、21 个测试方法的逐项说明、选择原因和缺口见 [SPEC.md](SPEC.md) 的中文版第 6、7 节。

```text
python -m unittest discover -s tests -t . -v
```

macOS 可用 `python3`，Windows 可用 `py`。2026 年 10 月 27 日在 macOS/Python 3.13.11 上 21 项测试通过，TypeScript 检查通过。AI 使用模拟响应，不收费。覆盖 30 道题输出、通关、推荐、复习、输入、数据库、HTTP、AI 校验与降级、双语内容及英文提示。Python 参考解核验 39 例，不等于本次重新做了浏览器运行时验收；范围见测试记录。

历史记录包含离线运行、超时、语言切换等浏览器检查，本次不把它们算作重新执行的证据。CI 配置了三系统及 Python 3.10/3.13，但未据此宣称远端执行成功。真实可用性、Windows/Linux、人工题库复核及真实诊断效果仍待验证。

### VS Code 测试发现

在 VS Code 中直接打开包含 `main.py` 的项目文件夹，通过 **Python: Select Interpreter** 选择 Python 3.10+，再刷新测试面板。`tests/__init__.py` 使测试目录可导入；从项目根目录使用 `-s tests -t . -p test_*.py` 发现测试。旧错误仍显示时执行 **Developer: Reload Window** 后刷新。不要把整个个人主目录当作本项目工作区，以免读取错误配置。

模拟理由评估：

```text
python scripts/evaluate_ai.py
python scripts/evaluate_ai.py --live
```

第一条仅生成规则基线；`--live` 可发出 12 次付费请求。模拟理由标签是初稿，并非独立金标准。须补人工标注、保留集及质量评分后才能讨论效果；当前脚本默认中文分析，不验证英文模型效果。

仅前端开发者需要 Node.js 22+ 与 npm：

```text
cd web
npm ci
npm run check
npm run build
```

修改前端源码、公共资源或导入的数据后需构建；普通运行使用随包的 `web/static`。后端/配置修改需重启。部分工作副本使用 pnpm；提交的 npm 锁文件须与依赖声明一致。

## 9. 结构、部署与提交

|路径 |用途 |
|---|---|
| `main.py` |启动入口 |
| `backend/domain.py` |判分、课程、推荐、复习 |
| `backend/storage.py` |数据库与版本冲突 |
| `backend/ai.py` |模型请求、校验与回退 |
| `backend/server.py` |接口、会话与访问限制 |
| `data/` |题库、概念、导学与任务 |
| `web/src`, `web/public`, `web/static` |源码、运行资源与网页成品 |
| `tests`, `scripts` |自动测试、评估与打包 |
| `SPEC.md`, `submission/` |规格、双语提交材料与证据 |
| `licenses/` |依赖原始许可证 |

本机运行不需 VPN，AI 需联网。局域网配置准确 `PUBLIC_ORIGIN`，再以 `--host 0.0.0.0` 启动并放行端口。公网需另备服务器、HTTPS 代理与持久存储；Docker 可选。标准库服务适用于演示/小团队，未验证高并发生产使用。




## 10. 引用与 AI 披露

Python 标准库、React/ReactDOM（MIT）、Lucide（ISC）、Pyodide（MPL-2.0）及 CPython 的相关许可见 `licenses/`；TypeScript/esbuild 用于开发。Exercism 是概念学习方向参考，不宣称复制课程或代码；如有实际复制，须逐项注明。Kimi 是可选服务，未随包分发模型。

来源：[Python](https://docs.python.org/3/library/), [React](https://github.com/facebook/react), [Lucide](https://github.com/lucide-icons/lucide), [Pyodide](https://github.com/pyodide/pyodide), [TypeScript](https://github.com/microsoft/TypeScript), [esbuild](https://github.com/evanw/esbuild), [Exercism Python](https://github.com/exercism/python), [Kimi](https://platform.moonshot.cn/).

Codex 协助实现、测试、文档、展示初稿及代码检查；团队须理解、复核并如实披露。AI 自查不能证明已完成成员独立审查；每位成员须填写真实个人贡献。

---


# English Version: PySteps User Guide

PySteps helps Python beginners learn a concept, answer questions, explain mistakes and practise coding within each chapter. It is a browser interface backed by a Python application, launched through `main.py`.

## 1. Run the application

Requirements: Python 3.10+, a modern browser and the fully extracted project. Normal use needs no Node.js, pip packages or Docker. Python must be installed on the host; visitors to an already hosted instance only need a browser.

Open a terminal in the folder containing `main.py`

| Environment| Command|
|---|---|
| Python available as `python`| `python main.py --open` |
| macOS with `python3` | `python3 main.py --open` |
| Windows Python launcher| `py main.py --open` |

Use the URL printed in the terminal, normally `http://127.0.0.1:8000/`. Keep the terminal open; use Ctrl+C to stop. If the port is occupied, stop the old instance or use `python main.py --port 8001 --open`. Starting another port does not reload the old process. Double-clicking `打开网页版.html` only shows instructions.

Optional database location: `python main.py --db runtime/learning.sqlite3`.

## 2. Language and learning flow

The first visit defaults to English. The top-right Chinese/English button changes the language and remembers the selection in this browser. Switching preserves answers, learner text and code drafts. Code and exact expected output strings remain unchanged; new AI requests use the selected language, while historical generated feedback is retained verbatim.

1. Read the introduction and select a concept on the Learning Map.
2. Enter a course lesson or choose a topic in Free Practice.
3. Submit an answer; a written reason is optional.
4. After a wrong answer, add or revise the reason and optionally request AI analysis.
5. Try targeted practice or a chapter coding challenge.
6. Review progress and export a backup.

## 3. Implemented features

| Feature| Current behaviour|
|---|---|
| Curriculum| 3 chapters, 15 concepts and prerequisites|
| Guided lessons| Objectives, explanations, code, outputs and reflection prompts|
| Course progression| Read the lesson and independently solve its two distinct questions without hints|
| Free practice| 30 multiple-choice questions; does not unlock course lessons|
| Grading| Fixed answer keys, reviewed-by-execution outputs and rule-based concept clues|
| Follow-up reasoning| Edit a wrong-answer reason and reanalyse the same attempt without increasing the attempt count|
| Recommendation| Same-chapter ranking by target concept, unseen status and due reviews; excludes current question|
| AI diagnosis| Optional Kimi analysis with quoted reasoning, constrained labels and validated feedback|
| Coding| 6 story tasks with 39 test cases, available without completing quizzes|
| Editor| Drafts, example runs, full checks, error feedback, stop and history|
| Progress| Mistake review, statistics, concept states, accuracy curve and table for the latest 14 dates with attempts|
| Persistence| SQLite, JSON backups and conflict detection|
| PiPo| Chinese/English shortcuts and keyword navigation; it does not call a language model|

The next-question action stays in the original submit area. An incorrect answer is a clue, not proof of a misconception. Passing the small course question bank is not proof of complete mastery. Educational content and concept labels still require team review.

## 4. Recommendation and review algorithm

Within the current chapter, excluding the current question, priority is: (1) unseen questions matching the suspected concept; (2) due reviews, earliest due first; (3) other unseen questions; (4) previously seen questions not yet due. Remaining ties use target match where applicable, difficulty and question ID. The interface takes the first result. When the diagnosis is `unknown`, due reviews come before unseen questions without forcing a target misconception.

Wrong answers schedule a review in 10 minutes. Correct answers with hints schedule one within a day without advancing a stage. Independent correct answers at/after the due time advance through 1, 3, 7, 14 and 30 days. Early repetition does not advance a stage. This is deterministic ranking with a fixed review schedule, not a trained recommendation model. A small bank still leads to repetitions; difficulty is not estimated from an individual learner model.

## 5. Optional Kimi configuration

Copy `config.example.json` to `config.local.json` in the root, then edit the local file. Never put a real key into the example, frontend or submitted ZIP. Same-named environment variables override file values. `.env` is not loaded automatically. Restart the server after changing settings.

| Field| Meaning|
|---|---|
| `MOONSHOT_API_KEY` | Actual API key, without the `Bearer ` prefix|
| `MOONSHOT_MODEL` | A model available to your account; the code fallback is `kimi-k2.6`, not a guarantee of availability|
| `MOONSHOT_BASE_URL` | `https://api.moonshot.cn/v1` or `https://api.moonshot.ai/v1`, matching the key|
| `TEAM_ACCESS_CODE` | Team access password of at least 12 characters; this is what learners enter|
| `PUBLIC_ORIGIN` | Empty locally; the exact browser origin for network access|

A wrong answer plus a non-empty reason can trigger AI if opted in, or learners can request it after submitting. Correct answers and blank reasons do not trigger a model call. Editing a reason clears old AI feedback, then reanalysis updates the original attempt. Each deliberate reanalysis may incur fees.

The model can choose only the candidate misconception or `unknown`. It must quote the reason; personalised feedback also checks the answer key and a verbatim excerpt of the standard explanation. These checks do not prove the whole explanation is correct. All 60 current wrong-option mappings point to their question's own concept, so the diagnostic taxonomy is coarse and needs human review. Kimi cannot choose an unrelated alternative concept or generate new practice questions.

The backend waits up to 30 seconds and the interface up to 40 seconds. Authentication, connection, output or evidence failures use rule feedback. Each process limits requests to 60 per hour; restart resets the count, so it is not a billing cap. A failed/unused response may still have incurred provider charges. No live paid call was made in the 27 October 2026 audit; current credentials and model quality were not verified by that audit.

## 6. Storage and coding limits

The default database is `runtime/learning.sqlite3`. A random browser cookie identifies a learning space. Keep both cookie and database to resume it. There is no account-based automatic cross-device sync. Transfer records using export/import; import replaces the current space, regrades answers and restores standard feedback. Changing browser/host or clearing cookies may create a new space. A save conflict requires a backup and refresh, not repeated overwriting.

Each space allows up to 10,000 quiz attempts and 2,000 code attempts. Reasons are limited to 1,000 characters, code to 20,000 and requests to 10 MB. No automatic archive exists.

Python practice runs in a browser Worker using a bundled Pyodide runtime. It does not execute learner code on the server. The syntax allowlist excludes imports, network and filesystem operations. Loading times out after 60 seconds; execution stops after 4 seconds. Example runs use two cases; full checks use all cases and save a result. There is no hard memory quota, and browser results are learning records rather than tamper-proof exam credentials.

## 7. Troubleshooting

| Symptom| Action|
|---|---|
| Address already in use| Stop the old process or use `--port 8001`|
| AI not configured| Check server key and 12+ character team code, then restart|
| 401 from Kimi| Check key, endpoint and environment overrides; the learner answer is not invalid|
| Team code rejected| Enter the team code, not the API key|
| Old interface| Refresh after rebuilding; restart after backend/config changes|
| Certificate error| Repair system/Python trust certificates; do not disable verification|
| Coding runtime unavailable| Keep the server running and retain `web/static/pyodide`|
| Save conflict| Export a backup, refresh and recover carefully|

## 8. Tests and development

See sections 6 and 7 of the English version in [SPEC.md](SPEC.md) for all 21 test methods, their targets, rationale and remaining gaps.

```text
python -m unittest discover -s tests -t . -v
```

Use `python3` on macOS or `py` on Windows if needed. The audit on 27 October 2026 passed 21 tests on macOS/Python 3.13.11 and passed TypeScript checking. Tests use simulated AI responses and do not incur API charges. They cover all 30 question outputs, course progression, ranking, review scheduling, input validation, SQLite, HTTP, AI validation/fallback, bilingual content and English prompting. Python reference solutions validate 39 coding cases; this is distinct from a fresh browser-runtime test. See `submission/test_results_2026-10-27.txt` for the recorded scope.

Earlier project records describe browser checks, including offline operation, timeout handling and language switching. Those are historical records, not freshly rerun evidence in this audit. The CI matrix configures Windows/macOS/Linux and Python 3.10/3.13, but no successful remote CI run is claimed. Human usability, Windows/Linux execution, independent content review and live diagnostic quality remain pending.

### VS Code test discovery

Open the project folder containing `main.py` directly in VS Code, select Python 3.10+ using **Python: Select Interpreter**, then refresh the Testing panel. The test package contains `tests/__init__.py`; discovery uses `-s tests -t . -p test_*.py` from the project root. If the old discovery error persists, use **Developer: Reload Window** and refresh tests. Opening your entire home folder instead of this project can cause the wrong workspace configuration to be used.

For the synthetic AI evaluation

```text
python scripts/evaluate_ai.py
python scripts/evaluate_ai.py --live
```

The first command writes a rule baseline without a model call. `--live` can issue 12 paid requests. Labels are draft labels for simulated reasons, not independently validated ground truth. Human labelling, a held-out set and quality scoring are required before making effectiveness claims. The current script defaults to Chinese analysis; it does not establish English-model performance.

Only frontend developers need Node.js 22+ and npm

```text
cd web
npm ci
npm run check
npm run build
```

Rebuild after editing `web/src`, `web/public` or imported data. Runtime use relies on committed/bundled `web/static`; backend/config changes require a restart. Some project copies use pnpm, but the distributed npm lockfile must stay consistent with `package.json`.

## 9. Structure, hosting and submission

| Path| Purpose|
|---|---|
| `main.py` | Python entry point|
| `backend/domain.py` | Grading, course rules, ranking and review|
| `backend/storage.py` | SQLite and revision conflicts|
| `backend/ai.py` | Kimi request, evidence validation and fallback|
| `backend/server.py` | HTTP, sessions and access controls|
| `data/` | Questions, concepts, lessons and tasks|
| `web/src`, `web/public`, `web/static` | Source, runtime assets and built application|
| `tests`, `scripts` | Automated tests, evaluation and packaging|
| `SPEC.md`, `submission/` | Requirements, bilingual submission material and evidence|
| `licenses/` | Original dependency licence texts|

Local operation needs no VPN; optional AI needs network access. For LAN use configure the exact `PUBLIC_ORIGIN`, then run `python main.py --host 0.0.0.0` and allow the port through the firewall. Public hosting needs a reachable server, HTTPS reverse proxy and persistent storage. A Dockerfile is optional. This standard-library server is for demonstrations/small teams, not validated high-concurrency production.



## 10. Attribution and AI disclosure

Python standard library, React/ReactDOM (MIT), Lucide (ISC), bundled Pyodide (MPL-2.0) and CPython licences are retained in `licenses/`. TypeScript and esbuild support development. Exercism inspired the concept-led learning direction; no copying of its curriculum/code is asserted. Record any actual copied material precisely. Kimi is an optional service, not a distributed model.

Source links: [Python](https://docs.python.org/3/library/), [React](https://github.com/facebook/react), [Lucide](https://github.com/lucide-icons/lucide), [Pyodide](https://github.com/pyodide/pyodide), [TypeScript](https://github.com/microsoft/TypeScript), [esbuild](https://github.com/evanw/esbuild), [Exercism Python](https://github.com/exercism/python), [Kimi](https://platform.moonshot.cn/).

Codex assisted implementation, tests, documentation, presentation drafting and code inspection. The team must understand, verify and disclose this assistance. AI self-review is not evidence of completed human peer review. Actual individual authorship and contributions must be recorded by each member.
