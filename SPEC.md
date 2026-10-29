# PySteps — Software Requirements Specification

## English

**Group 8**

Baseline: implemented application, 29 October 2026. Entry point: `main.py`. Related document: [README.md](README.md).

### 1. Purpose and product scope

PySteps gives Python beginners an actionable learning path after an incorrect answer. It links concept reading, fixed-answer assessment, explanatory feedback, targeted practice and chapter coding. PiPo interprets natural-language learning goals and uses tools to inspect progress and prepare the next learning activity.

The implemented content comprises 3 chapters, 15 concepts, 30 multiple-choice questions and 6 coding tasks with 39 cases. The target setting is individual learning or a small teaching group using a local Python service and browser. Two language interfaces support English and Chinese. This specification describes current behaviour and the criteria used to evaluate it.

**User roles.** Learners read, answer, explain, practise, code and manage backups. A local operator configures the service, model and team access code. Contributors maintain content, implementation, tests and documentation.

**System boundary.** Python owns grading, progression, ranking, review schedules, model integration, HTTP and SQLite. The browser owns interaction and restricted code execution. GLM-4.7 supplies optional diagnosis and Agent decisions. Learning spaces are identified by cookies; record transfer uses explicit JSON backup/import. Teacher administration, account-based synchronisation and arbitrary server-side learner-code execution are outside this version.

### 2. Architecture and principal use cases

```text
Browser: React interface + PiPo panel + Pyodide Worker
                         |
                    HTTP JSON API
                         |
Python server: origin/host checks, session identity, AI authorisation
       |                    |                    |
 LearningEngine        Diagnosis adapter      PiPo agent loop
       |                    |                    |
 JSON content         GLM-4.7 + validation    Model -> tool -> observation
       |                                         |
 SQLite learning state                Allowlisted learning tools
```

| Use case | Trigger and outcome |
|---|---|
| UC-01 Continue a course | Read the introduction and an available concept, complete its questions independently, and open the next available step. |
| UC-02 Learn from a mistake | Submit an answer, inspect fixed feedback, revise the reason, optionally request diagnosis and practise a related item. |
| UC-03 Ask PiPo for a next step | State a goal; PiPo inspects tools, selects content and returns an explanation plus at most one validated opening. |
| UC-04 Apply Python | Open a chapter task, edit a draft, run samples, check all cases and inspect stored submissions. |
| UC-05 Resume or transfer records | Reload a learning space, resolve a stale revision, or confirm replacement from an exported backup. |

### 3. Functional requirements

All requirements below refer to implemented behaviour. Automated evidence and interface acceptance are identified separately in §8.

#### FR-01 Language and presentation

The application shall default to English on first access and remember an explicit English/Chinese selection in browser storage. Navigation, lesson prose, feedback translations and task instructions shall follow that selection. Learner input, source code and precise expected outputs shall retain their original values.

#### FR-02 Deterministic assessment

The service shall accept a known `question_id` and an option belonging to that question. `grade()` shall compare it with the stored answer and return `correct` plus rule feedback. A correct answer produces concept `none`; a wrong option uses its mapped concept or `unknown`. Unknown questions/options shall be rejected. Fixed answers remain authoritative when AI is enabled.

#### FR-03 Course progression

`courses()` shall calculate access from introduction reading, explicit prerequisites and completion of concepts in preceding chapters. A qualifying course attempt requires the matching `course_concept`, concept reading, satisfied prerequisites, a correct answer and zero hints. For this bank, both distinct questions of the concept must have qualifying results. Free-practice and hinted successes shall not establish course completion. The implementation processes attempts in their stored order and retains concepts added to the passed set during that calculation.

#### FR-04 Reason revision

After a wrong submission, the learner shall be able to edit a reason and request further analysis of the same attempt. Updating that attempt shall preserve its identity rather than add an attempt. The interface shall reject an empty analysis reason and preserve usable rule feedback if diagnosis cannot be obtained.

#### FR-05 Targeted recommendation

`recommend()` shall exclude the current question and keep candidates in its chapter. With a specific diagnosis, ranking shall prioritise (1) unseen target-concept items, (2) due items, (3) other unseen items, then (4) remaining seen items. Due timestamps, target match, difficulty and ID provide deterministic tie-breaking in the implemented key. For `unknown`, due items lead, then unseen items, then other seen items, without forcing a concept diagnosis. The service returns existing bank questions; it does not generate questions.

#### FR-06 Review schedule

Attempts shall be sorted by their timezone-aware timestamps before scheduling. A wrong answer shall reset stage to 0 and set the due time to 10 minutes later. A hinted correct answer shall reset stage to 0 and use one day later, preserving an earlier future due time where present. A correct answer without hints shall advance a stage when there is no previous schedule or the previous due time has arrived. Intervals shall be 1, 3, 7, 14 and 30 days, capped at stage 5. Early independent repeats shall preserve the schedule.

#### FR-07 GLM-4.7 misconception diagnosis

Diagnosis shall operate on a wrong answer with a non-empty reason after configuration and team-code authorisation. The prompt shall contain instructions, question context, selected answer/reason and a JSON output contract.

| Model field | Validation contract |
|---|---|
| `concept` | The wrong option's candidate concept or `unknown`. |
| `quote` | Non-blank, at most 200 characters and a verbatim substring of the reason. |
| `answer_key` | Equal to the stored answer letter. |
| `knowledge_quote` | Verbatim substring of the standard explanation, with at least 4 non-edge-whitespace characters. |
| `explanation` | Non-blank; trimmed length 1–600 characters. |
| `hint` | Non-blank; trimmed length 1–240 characters. |

An invalid concept or learner quotation shall cause rule fallback. If these pass but answer/evidence/teaching-text checks fail, the adapter shall retain `source: "ai"` and the accepted diagnostic fields, set `personalized: false`, and use the bank explanation/hint. Valid output shall set `personalized: true`. Provider errors, timeout, oversized/incomplete output and malformed responses shall yield rule feedback. The diagnosis request reads at most 65,537 bytes and rejects responses over 65,536 bytes. Correct answers and blank reasons shall bypass model analysis.

#### FR-08 Persistence and session isolation

The service shall hash an opaque random session cookie to identify a learning space. SQLite shall store one versioned JSON state per space. `Store.save()` shall use `BEGIN IMMEDIATE`, compare the submitted revision and atomically increment it on success. A stale revision shall produce HTTP 409. Different cookies shall resolve to separate spaces.

#### FR-09 Backup and import

The interface shall export version-1 learning JSON and ask for confirmation before replacing a space. The server shall validate structure, IDs, timestamps, lengths and duplicate attempt identities, regrade quiz choices and restore rule feedback for imports. Unknown extra fields are omitted from the normalised state. Code submission pass flags are retained as submitted local learning records; the import service does not rerun code. Import validation returns normalised state, and the browser then persists the confirmed replacement through the state endpoint.

#### FR-10 Browser coding

The interface shall offer 6 chapter tasks independently of quiz completion. Run Example shall execute the first two cases; Check Answer shall execute all cases for the task. Source shall pass an AST allowlist before execution in a disposable Pyodide Worker. Forbidden constructs include imports, class definitions, arbitrary attributes, indirect calls and file access. Results shall include per-case values, output and error locations where available. Booleans shall not substitute for numbers; numeric `int`/`float` equality is allowed. Drafts and completed checks shall be stored in learning history. The UI shall stop execution by terminating the Worker.

#### FR-11 Learning analytics

The application shall show quiz counts, accuracy, concept status, coding completion and wrong-attempt details. The quiz accuracy chart and associated table shall group attempts by device-local date and select the latest 14 dates containing attempts. Hinted and repeat quiz attempts remain included. Coding completion is reported separately from quiz accuracy.

#### FR-12 PiPo learning Agent

PiPo shall accept a non-empty goal of at most 1,000 characters and up to 8 prior user/assistant messages, each at most 10,000 characters. Python shall validate the submitted learning state before running the loop. The model shall choose from the following tools, and each execution result shall be returned as a tool observation for subsequent decisions.

| Tool | Observation or permitted action |
|---|---|
| `progress` | Quiz totals, computed course states, due items, up to 5 recent mistakes with reasons truncated to 500 characters, and passed coding IDs. |
| `lesson` | Introduction or a valid concept's definition, lesson content and current course state. |
| `recommend` | Up to 3 ranked same-chapter alternatives. Defaults to the most recent wrong attempt in stored order, or the first question when none exists. Model-facing results omit answer keys and misconception maps. |
| `coding` | Task IDs, titles, topics and whether an associated passed submission exists; optional exact-topic filter. |
| `open_content` | Prepare a lesson, question or coding opening for an ID already inspected by another tool this turn. Locked lessons and a second opening are rejected. |

Tool names and argument keys shall be allowlisted; argument values shall be strings of at most 100 characters. The loop shall allow up to 5 model requests and 8 tool executions. In school JSON mode, the fifth request shall allow only a final reply; further tool plans shall be rejected. Native mode disables tools on its final request. Every model request shall consume the shared hourly allowance. JSON-mode requests shall use `max_tokens: 650` (native mode: 1400); model responses over 131,072 bytes shall be rejected. A final non-blank reply shall be at most 4,000 characters in JSON mode (10,000 in native mode) and have `finish_reason: "stop"`.

Successful responses shall contain `reply`, `trace`, `actions` and `source: "agent"`. The browser shall validate the action against available content and apply it after a completed turn. Failed turns shall return an error rather than partial actions. Tool traces shall show accepted/rejected calls. Stop shall abort browser waiting and prevent subsequent action application; it does not guarantee cancellation of an in-flight server request. Tools shall not modify grades, course reads, saved learning records or files. PiPo conversation is kept in page memory.

### 4. Non-functional requirements and operating limits

| ID | Implemented quality constraint | Verification |
|---|---|---|
| NFR-01 Local operation | The Python backend uses the standard library; built UI, icons and Pyodide are bundled. Core learning works without model access. | Start a clean distribution; block external requests and complete the core flow. |
| NFR-02 Input bounds | Body ≤10,000,000 bytes; reads ≤16; quiz attempts ≤10,000; code records ≤2,000; reasons/goals ≤1,000 characters; source ≤20,000 characters. | Boundary inputs and state validation; inspect declared limits. |
| NFR-03 Request access | Host checks; same-origin JSON POST; private paths outside static scope; HttpOnly/SameSite session cookies; response security headers. | HTTP tests plus direct Host/path checks. |
| NFR-04 Model access | Team code ≥12 characters with constant-time digest comparison; server-held provider key; shared 60 requests/hour/process. | Authorisation/rate tests; inspect outgoing model payloads. |
| NFR-05 Controlled waiting | Diagnosis: request 60 s / browser 75 s. PiPo JSON mode: up to 60 s per request, approximately 100 s turn budget / browser 115 s. Worker loading: 60 s / execution: 4 s. | Mocked timeout tests; browser stop/timeout exercise. These thresholds are not aggregate latency guarantees. |
| NFR-06 Persistence | Atomic revision checks and cookie isolation; conflicts do not silently replace newer records. | SQLite and HTTP roundtrip/conflict tests. |
| NFR-07 Maintainability | Domain, storage, HTTP, diagnosis and Agent modules have separate responsibilities; data is JSON; tests run through standard `unittest`. | Module inspection, regression suite and recorded code review. |
| NFR-08 Portability | Python 3.10+ target; CI matrix declares Ubuntu/Windows/macOS with Python 3.10/3.13 and a Node.js 22 frontend build. | Current local test result and separate remote CI records. |

The browser runtime applies syntax, output and execution controls without a hard memory quota. The application is intended for local teaching and small-group demonstrations. Numerical response-speed targets require a named machine, workload and measurement; no performance benchmark is inferred from a timeout setting.

### 5. Data contracts

Content files are `concepts.json` (15 entries), `lessons.json` (15), `questions.json` (30) and `coding_tasks.json` (6 tasks / 39 cases).

```json
{
  "version": 1,
  "reads": [],
  "attempts": [],
  "drafts": {},
  "codeAttempts": []
}
```

Quiz records contain `id`, `question_id`, `choice`, `reason`, `correct`, `diagnosis`, `created_at`, `hints_used`, `course_concept` and `feedback`. Code records contain `id`, `task_id`, `source`, `passed`, `created_at` and `details`. Timestamps shall carry a timezone. Stored `correct` values for quizzes are recomputed by state validation.

```sql
CREATE TABLE learners (
  id TEXT PRIMARY KEY,
  revision INTEGER NOT NULL,
  state TEXT NOT NULL
);
```

The state is a local learning record. It is not an account identity or an invigilated examination credential.

### 6. HTTP interface

All POST endpoints require a permitted Host/Origin, `Content-Type: application/json` and a body within the size limit. Model endpoints additionally require `X-Team-Code` when configured and applicable.

| Method and path | Input | Successful output |
|---|---|---|
| GET `/api/state` | Session cookie | `revision`, `state`, `summary` (courses and schedule). |
| POST `/api/state` | `revision`, `state` | New `revision`, computed `summary`. |
| POST `/api/import` | `state` | Validated, regraded `state`. |
| POST `/api/grade` | `question_id`, `choice` | `correct`, `feedback`. |
| POST `/api/recommend` | `question_id`, `diagnosis`, `state` | Ordered `questions`. |
| GET `/api/diagnose` | None | `configured` flag for local settings. |
| POST `/api/diagnose` | Question, choice, reason, `language` | Diagnosis or rule `feedback`. |
| POST `/api/agent` | `goal`, `history`, `language`, `state` | `reply`, tool `trace`, `actions`, `source`. |

Error statuses: 400 invalid fields; 401 team-code failure; 403 Host/Origin mismatch; 404 unknown/private path; 409 revision conflict; 413 body size; 415 content type; 503 unconfigured Agent; 502 unfinished Agent turn; 500 unexpected POST-processing failure. The configuration flag describes local settings, not provider reachability.

Example Agent request (include the team code in the header):

```json
{
  "goal": "Check my progress and open the next lesson",
  "history": [],
  "language": "en",
  "state": {"version": 1, "reads": [], "attempts": [], "drafts": {}, "codeAttempts": []}
}
```

### 7. Model and tool trust boundary

Diagnosis uses a restricted field/evidence contract. PiPo uses an allowlisted executable tool boundary. Both treat learner reasons and model text as data. The Agent system message instructs progress inspection before personalised planning, teaching through lesson content and appropriate hints; executable restrictions are enforced by Python independently of the model's prose. There are no shell, arbitrary file-write or general network tools.

The provider receives the goal, recent conversation and selected learning observations, or the question/reason data required by diagnosis. API credentials and team access codes are not included in model message bodies. A reply is learning assistance; educational claims require their own evidence.

### 8. Evaluation plan and traceability

**Current regression result:** 29 October 2026, macOS / Python 3.13.11, **43 methods passed**. Project-focused methods total 37: core 16, HTTP 6, language 2 and Agent 13. Six additional methods in `test_main.py` exercise independent examples. AI calls are simulated, and HTTP tests use temporary local services and databases. Thirty question outputs and 39 reference coding cases are exercised within those methods.

```bash
python -m unittest discover -s tests -t . -v
```

| Requirement | Automated evidence | Interface or evaluation scenario |
|---|---|---|
| FR-01 | `LanguageTests` | Switch after entering a reason/source; inspect text and retained input. |
| FR-02 | `test_all_question_answers`; HTTP grading | Correct, wrong and empty choice. |
| FR-03 | Course unlocking and hinted/free-practice tests | Read → course answers → next available lesson. |
| FR-04 | Application source contract | Edit a reason, reanalyse and verify the attempt count is unchanged. |
| FR-05 | Target/unknown recommendation; Agent recommendation test | Mixed unseen/due/seen history; verify ranked IDs and chapter. |
| FR-06 | Early-repeat scheduling test | Controlled timestamps for each interval, hints and stage cap. |
| FR-07 | `GLMDiagnosisTests`; English prompt and authorisation tests | Provider-error display and comparison with independently labelled cases. |
| FR-08 | SQLite isolation/conflict; HTTP roundtrip | Reload and make conflicting writes from two tabs. |
| FR-09 | Import regrading and invalid/oversize tests | Export → confirmed replacement; cancellation preserves state. |
| FR-10 | AST restrictions and 39 reference cases | Execute all six tasks in the actual Worker; stop/timeout/error cases. |
| FR-11 | Aggregation implementation | Known histories across local dates; compare chart and table. |
| FR-12 | 10 `PiPoTests`; Agent HTTP integration | Natural goal → tools → next content; follow-up, stop and failure. |
| NFR-02/03/04/06 | Input, HTTP, authorisation, payload and persistence assertions | Additional exact-boundary and browser checks as listed above. |

**PiPo regression responsibilities.** The thirteen Agent methods test a complete observation loop; invalid IDs/locked lessons/single-action limits; recommendation without answer fields; rate-limit prevention of network calls; excessive tool-call rejection; recovery after a rejected action; history/privacy boundaries; fifth-round tool disablement and per-request charging; timeout after a prepared action; and incomplete/oversized responses.

**Interface acceptance procedure.** Record date, code version, platform/browser, steps, actual result and evidence file for each scenario. A first-use flow should start from an empty learning space and reach a saved quiz/coding record. A returning-user flow should show a due review and a PiPo-selected activity. Model-enabled acceptance uses a tool-capable account model; compare visible tool traces with opened content.

**Live-model quality evaluation.** `scripts/evaluate_ai.py` generates a rule baseline; `--live` explicitly enables paid calls for the 12 simulated diagnosis cases. Independent reviewers should label cases and assess factual correctness and relevance before interpreting agreement. Agent scenarios should separately record appropriate tool selection, action validity, recovery and useful teaching responses. Mock regression establishes control-flow behaviour; it is not a live-model accuracy or student-learning study.

**Code review.** Review module contracts, failure paths, stored-state handling, model data exposure and tool permissions. Record reviewer, version, location, issue, resolution and recheck. Changes follow requirement → expected behaviour → test/change → regression → review → documentation. Completed review records and measured results remain distinct from assigned responsibilities.

### 9. Course alignment and presentation evidence

| Course/assessment principle | Implemented evidence |
|---|---|
| Originality and practicality, 10% | One application links an incorrect answer to explanation, further practice and a concrete PiPo-selected activity. |
| Usability, 10% | Local single-command launch, bilingual UI, contextual feedback, explicit errors and preserved records. |
| Technical depth, 55% | Python computation, functions/classes/modules, JSON data, sorting, SQLite transactions, model APIs and Agent tools. |
| Good: specification and testing | FR/NFR contracts, API/data definitions and requirement-to-verification mapping. |
| Excellent: documentation and code review | Operating README, this specification and a defined review record for findings and rechecks. |
| Generative AI engineering bonus | AI-assisted implementation, test development, specification, documentation and inspection, with actual adopted outputs verified by the group. |
| Lecture04 | Prompt elements, SRS and decomposition; human-facing README separated from detailed contracts. |
| Lecture05 | Role messages, token limits, model + harness, allowlisted tools and repeated observations. |
| Lecture06 | Pass/fail functional criteria, quantified operating constraints, unit/integration testing and matching requirements with verification. |

Two presentation formats are separate. The English/Chinese classroom decks each contain five selected technical slides with a 4:45 route, within five minutes. The English/Chinese video support decks each contain nine slides following introduction, problem, methodology, representative live demonstration and conclusion, with a 14:30 route and 8:15 of live application use. The required deliverable is the actual video within 15 minutes. Q&A preparation and the mandatory individual peer assessment are included in the recording/classroom guide.

### 10. References

Supplied sources: INT6181 *Group Project Requirements v2*, §§3–5; Lecture03 *Review of Programming II*; Lecture04 *Generative AI in Programming*, slides 12–17, 24 and 44–47; Lecture05 *Foundation of Coding Agents*, slides 17–19 and 22–28; Lecture06 *Testing and Debugging I*, slides 6, 13–16 and 22–28; *CaseStudy5 Software Requirements Specification*. Slide numbering refers to original PPTX files. Component attribution and licence locations are in README.

---

## 中文

**第 8 组**

基线：2026 年 10 月 29 日的已实现应用。入口：`main.py`。配套文档：[README.md](README.md)。

### 1. 目的与产品范围

PySteps 帮助 Python 初学者在答错后找到具体学习行动，把概念阅读、固定答案判分、解释反馈、针对性练习和章节编程连接起来。PiPo 理解自然语言学习目标，通过工具检查进度并准备下一项活动。

已实现内容为 3 章、15 个概念、30 道选择题、6 个编程任务及 39 个案例。使用场景是本地 Python 服务与浏览器支持的个人学习或小组教学，界面支持中英文。本规格描述现有行为及其评估标准。

**用户角色。** 学习者阅读、答题、解释思路、练习、编程并管理备份；本地操作者配置服务、模型和团队口令；贡献者维护内容、实现、测试与文档。

**系统边界。** Python 负责判分、课程进度、推荐、复习、模型接入、HTTP 和 SQLite；浏览器负责交互及受限代码执行；GLM-4.7 提供可选诊断与 Agent 决策。Cookie 标识学习空间，通过显式 JSON 备份迁移记录。本版本不包含教师管理、账号自动同步及服务端任意学生代码执行。

### 2. 架构与主要用例

```text
浏览器：React 界面 + PiPo 面板 + Pyodide Worker
                         |
                    HTTP JSON 接口
                         |
Python 服务：来源/主机校验、会话标识、AI 授权
       |                    |                    |
   学习规则引擎          诊断适配器           PiPo Agent 循环
       |                    |                    |
   JSON 课程数据       GLM-4.7 与字段校验     模型 -> 工具 -> 观察
       |                                         |
 SQLite 学习状态                           学习工具白名单
```

| 用例 | 触发与结果 |
|---|---|
| UC-01 继续课程 | 阅读入门和可用概念，独立完成对应问题，进入下一可用步骤。 |
| UC-02 从错题学习 | 提交答案，查看固定反馈，修订理由，可选诊断，再练习相关问题。 |
| UC-03 请 PiPo 选择下一步 | 描述目标，PiPo 检查工具、选择内容，返回说明和最多一次已验证的打开动作。 |
| UC-04 应用 Python | 打开章节任务，编辑草稿，运行示例，检查全部案例，查看历史提交。 |
| UC-05 恢复或迁移记录 | 重新加载学习空间、协调旧版本冲突，或确认用备份替换当前记录。 |

### 3. 功能需求

以下需求均对应现有实现，自动证据与界面验收分别列于第 8 节。

#### FR-01 语言与展示

首次访问默认英语，显式中英文选择保存在浏览器。导航、导学正文、反馈翻译和任务说明随语言切换；学生输入、代码及要求精确匹配的输出保留原值。

#### FR-02 固定规则判分

服务接受已知 `question_id` 和属于该题的选项。`grade()` 对照存储答案返回 `correct` 与规则反馈；答对的概念为 `none`，错项使用映射概念或 `unknown`。未知题目和无效选项被拒绝，启用 AI 后仍以固定答案判分。

#### FR-03 课程进度

`courses()` 根据入门阅读、显式前置概念及此前章节概念的完成情况计算访问资格。有效课程作答须具有匹配的 `course_concept`，已阅读概念、满足前置条件、答案正确且未用提示。当前题库中，同概念两道不同题均需满足条件；自由练习和提示作答不用于过关。实现按存储顺序处理作答，并保留本次计算中已加入通过集合的概念。

#### FR-04 理由修订

错答后可编辑理由，并对原作答请求进一步分析。更新保留作答标识，不新增作答；空理由提示补充，诊断不可得时保留可用的规则反馈。

#### FR-05 针对性推荐

`recommend()` 排除原题，并限定当前章节。明确诊断时依次优先：①目标概念未做题，②到期题，③其他未做题，④其他已做题。实现使用到期时间、目标匹配、难度和 ID 进行确定性排序。诊断为 `unknown` 时先到期题，再未做题，最后其他已做题，不强行指定概念。服务返回现有题库题目，不生成新题。

#### FR-06 复习安排

按带时区时间戳排序后计算。错答重置阶段为 0，10 分钟后到期；提示后答对重置阶段为 0，安排一天后，已有更早的未来到期时间则保留。无提示答对时，若尚无安排或已到期则推进阶段；间隔为 1、3、7、14、30 天，阶段上限为 5。提前无提示重复答对不改变原安排。

#### FR-07 GLM-4.7 概念误区诊断

配置模型并通过团队口令授权后，可对有非空理由的错答进行诊断。提示包含指令、题目上下文、所选答案/理由及 JSON 输出约定。

| 模型字段 | 校验约定 |
|---|---|
| `concept` | 错项对应候选概念，或 `unknown`。 |
| `quote` | 非空白，最多 200 字符，逐字出现在学生理由中。 |
| `answer_key` | 与题库答案字母一致。 |
| `knowledge_quote` | 标准解析的逐字子串，去除首尾空白后至少 4 字符。 |
| `explanation` | 非空白，去除首尾空白后的长度为 1–600 字符。 |
| `hint` | 非空白，去除首尾空白后的长度为 1–240 字符。 |

概念或学生引文不合格时回退规则。前两项通过而答案/依据/讲解检查未通过时，保留 `source: "ai"` 和合格诊断字段，置 `personalized: false`，讲解及提示采用题库内容；全部通过则置 `personalized: true`。服务错误、超时、超长/未完成输出及格式异常返回规则反馈。诊断最多读取 65,537 字节，超过 65,536 字节即拒绝。正确答案及空白理由不调用模型。

#### FR-08 持久化与空间隔离

服务对随机会话 Cookie 求哈希，作为学习空间标识。SQLite 为每个空间保存版本化 JSON 状态。`Store.save()` 使用 `BEGIN IMMEDIATE`，比较提交版本后原子递增保存；旧版本返回 HTTP 409。不同 Cookie 对应独立空间。

#### FR-09 备份与导入

界面导出版本 1 的学习 JSON，替换空间前请求确认。服务校验结构、ID、时间、长度及重复作答标识，重新判定选择题并在导入时恢复规则反馈；额外未知字段不进入规范状态。编程通过标记作为本地学习记录保留，导入服务不重新运行代码。导入接口返回规范状态，浏览器经确认后调用保存接口持久化替换结果。

#### FR-10 浏览器编程

提供 6 个章节任务，独立于测验完成状态。运行示例执行前两例，检查答案执行本任务全部案例。代码先通过 AST 白名单，再在可销毁的 Pyodide Worker 中执行；禁止导入、类定义、任意属性、间接调用和文件访问等。结果显示各案例值、输出和可定位的错误行；布尔值不能替代数值，数值型 `int`/`float` 可按值相等。草稿及完整检查提交写入学习历史，停止操作终止 Worker。

#### FR-11 学习统计

展示选择题数量、正确率、概念状态、编程完成情况及错题详情。正确率曲线与对应表格按设备本地日期归组，取最近 14 个有作答的日期；提示和重复作答仍计入。编程完成统计与选择题正确率分别展示。

#### FR-12 PiPo 学习 Agent

接收非空目标，最多 1,000 字符；历史最多 8 条用户/助手消息，每条最多 10,000 字符。运行前由 Python 校验学习状态。模型从以下工具中选择，每次执行结果作为工具观察返回，供后续决策。

| 工具 | 观察或允许的动作 |
|---|---|
| `progress` | 选择题总数、课程状态、到期题、最近最多 5 条错题及每条最多 500 字符的理由、已通过编程 ID。 |
| `lesson` | 入门说明或有效概念的定义、导学及课程状态。 |
| `recommend` | 最多 3 个当前章推荐项；默认使用存储顺序中最近的错题，无错题时使用第一题；发给模型的结果省略答案和误区映射。 |
| `coding` | 任务 ID、标题、主题及是否存在通过提交，可按准确主题筛选。 |
| `open_content` | 为本轮已被其他工具检查的 ID 准备课程、题目或编程打开动作；锁定课程和第二个打开动作被拒绝。 |

工具名称和参数键受白名单约束，参数值须为最多 100 字符的字符串。每轮最多 5 次模型请求、8 次工具执行，学校 JSON 模式第五次请求只允许最终回复，继续工具计划则拒绝；原生模式末轮禁用工具；每次模型请求均消耗共享小时额度。JSON 模式请求使用 `max_tokens: 650`（原生模式为 1400），响应超过 131,072 字节则拒绝。最终回复须非空白，JSON 模式最多 4,000 字符（原生模式最多 10,000 字符），且 `finish_reason: "stop"`。

成功结果包含 `reply`、`trace`、`actions` 及 `source: "agent"`。浏览器按当前可用内容再次验证动作，完成本轮后再应用；失败返回错误，不返回部分动作。工具记录显示通过或拒绝。停止取消浏览器等待并阻止后续动作应用，但不保证取消已发出的服务端请求。工具不改写分数、阅读状态、学习记录或文件，对话保存在页面内存中。

### 4. 非功能需求与运行限制

| ID | 已实现的质量约束 | 验证方式 |
|---|---|---|
| NFR-01 本地运行 | Python 后端使用标准库，网页、图标及 Pyodide 随包提供；核心学习不依赖模型。 | 完整解压启动，阻断外部请求后完成核心流程。 |
| NFR-02 输入上限 | 请求体 ≤10,000,000 字节；阅读项 ≤16；选择题记录 ≤10,000；编程记录 ≤2,000；理由/目标 ≤1,000 字符；代码 ≤20,000 字符。 | 边界输入、状态校验及限制检查。 |
| NFR-03 请求访问 | Host 校验、同源 JSON POST、静态范围外私有路径保护、HttpOnly/SameSite Cookie 与安全响应头。 | HTTP 测试及补充 Host/路径检查。 |
| NFR-04 模型访问 | 团队口令至少 12 字符，以恒定时间比较摘要；密钥保留服务端；共享每进程每小时 60 次额度。 | 授权、限流及发出模型正文检查。 |
| NFR-05 受控等待 | 诊断请求 60 秒/网页 75 秒；PiPo JSON 模式单请求最多 60 秒/轮次预算约 100 秒/网页 115 秒；Worker 加载 60 秒/执行 4 秒。 | 模拟超时与浏览器停止/超时检查；阈值不等于总响应时间保证。 |
| NFR-06 数据保存 | 原子版本检查和 Cookie 隔离，冲突不静默覆盖较新记录。 | SQLite 与 HTTP 保存/冲突测试。 |
| NFR-07 可维护性 | 规则、存储、HTTP、诊断和 Agent 分模块，内容为 JSON，使用标准 `unittest`。 | 模块检查、回归及代码审查记录。 |
| NFR-08 可移植性 | 目标 Python 3.10+；CI 配置 Ubuntu/Windows/macOS × Python 3.10/3.13，以及 Node.js 22 网页构建。 | 本次本地结果与远端 CI 记录分别验证。 |

浏览器运行时提供语法、输出与执行控制，不设置硬性内存配额。应用用于本地教学及小组演示。响应速度指标须注明机器、负载和测量方法，不把超时配置当作性能测试结果。

### 5. 数据约定

内容文件为 `concepts.json`（15 项）、`lessons.json`（15 项）、`questions.json`（30 项）和 `coding_tasks.json`（6 任务/39 案例）。

```json
{
  "version": 1,
  "reads": [],
  "attempts": [],
  "drafts": {},
  "codeAttempts": []
}
```

选择题记录含 `id`、`question_id`、`choice`、`reason`、`correct`、`diagnosis`、`created_at`、`hints_used`、`course_concept`、`feedback`；编程记录含 `id`、`task_id`、`source`、`passed`、`created_at`、`details`。时间戳必须带时区，选择题 `correct` 由状态校验重新计算。

```sql
CREATE TABLE learners (
  id TEXT PRIMARY KEY,
  revision INTEGER NOT NULL,
  state TEXT NOT NULL
);
```

状态用于本地学习记录，不作为账号身份或监考考试凭据。

### 6. HTTP 接口

全部 POST 要求允许的 Host/Origin、`Content-Type: application/json` 及限定大小的请求体。配置模型且适用时，模型接口还要求 `X-Team-Code`。

| 方法与路径 | 输入 | 成功输出 |
|---|---|---|
| GET `/api/state` | 会话 Cookie | `revision`、`state`、包含课程与复习的 `summary`。 |
| POST `/api/state` | `revision`、`state` | 新 `revision` 与计算的 `summary`。 |
| POST `/api/import` | `state` | 校验并重新判分的 `state`。 |
| POST `/api/grade` | `question_id`、`choice` | `correct`、`feedback`。 |
| POST `/api/recommend` | `question_id`、`diagnosis`、`state` | 排序后的 `questions`。 |
| GET `/api/diagnose` | 无 | 本地设置的 `configured` 标志。 |
| POST `/api/diagnose` | 题目、选项、理由、`language` | 诊断或规则 `feedback`。 |
| POST `/api/agent` | `goal`、`history`、`language`、`state` | `reply`、工具 `trace`、`actions`、`source`。 |

错误状态：400 字段无效；401 团队口令错误；403 Host/Origin 不符；404 未知/私有路径；409 版本冲突；413 请求大小；415 内容类型；503 Agent 未配置；502 Agent 本轮未完成；500 未预期的 POST 处理错误。配置标志表示本地设置，不代表服务商可达。

Agent 请求示例（团队口令放入请求头）：

```json
{
  "goal": "根据我的进度打开下一课",
  "history": [],
  "language": "zh",
  "state": {"version": 1, "reads": [], "attempts": [], "drafts": {}, "codeAttempts": []}
}
```

### 7. 模型与工具信任边界

诊断使用受限字段与依据约定，PiPo 使用工具白名单作为执行边界。两者将学生理由和模型文本视为数据。Agent 系统提示要求个性化规划前检查进度、使用导学讲解并提供适当提示；Python 独立执行操作限制，不依赖模型的文字承诺。工具不包含 shell、任意文件写入或通用网络操作。

服务商接收目标、近期对话及选定学习观察，或诊断必需的题目/理由数据；模型消息正文不包含 API 凭据和团队口令。回复用于学习辅助，教育效果主张由相应证据支持。

### 8. 评估方案与需求追踪

**本次回归结果：** 2026 年 10 月 29 日，macOS / Python 3.13.11，**43 个测试方法通过**。项目方法 37 个：核心 16、HTTP 6、语言 2、Agent 13；`test_main.py` 另有 6 个独立示例方法。AI 为模拟响应，HTTP 使用临时本机服务和数据库；部分方法遍历 30 道题输出及 39 个编程参考案例。

```bash
python -m unittest discover -s tests -t . -v
```

| 需求 | 自动证据 | 界面或效果评估场景 |
|---|---|---|
| FR-01 | `LanguageTests` | 输入理由/代码后切换语言，检查显示及输入保留。 |
| FR-02 | `test_all_question_answers`、HTTP 判分 | 正确、错误和空选择。 |
| FR-03 | 课程解锁、提示/自由练习测试 | 阅读、课程作答、进入下一课。 |
| FR-04 | 应用源码合同 | 修改理由再分析，检查次数不增加。 |
| FR-05 | 目标/未知推荐、Agent 推荐测试 | 混合未做/到期/已做历史，核对顺序与章节。 |
| FR-06 | 提前重复复习测试 | 控制时间验证各阶段、提示和封顶。 |
| FR-07 | `GLMDiagnosisTests`、英文提示及授权测试 | 服务错误显示，与独立人工标签比较。 |
| FR-08 | SQLite 隔离/冲突、HTTP 保存 | 刷新及两个页面冲突写入。 |
| FR-09 | 导入重判、无效/超长测试 | 导出后确认替换，取消则保留状态。 |
| FR-10 | AST 限制及 39 个参考案例 | 真实 Worker 执行六任务，检查停止/超时/错误。 |
| FR-11 | 汇总实现 | 跨本地日期的已知历史，核对曲线与表格。 |
| FR-12 | 10 个 `PiPoTests`、Agent HTTP 集成 | 自然语言目标、工具、打开内容、追问、停止及失败。 |
| NFR-02/03/04/06 | 输入、HTTP、授权、正文与持久化断言 | 按上表补充精确边界和浏览器检查。 |

**PiPo 回归职责。** 十三个方法分别验证完整观察循环；非法 ID/锁课/单动作；推荐省略答案；额度不足不联网；工具超限拒绝；拒绝动作后恢复；上下文与凭据边界；第五轮关闭工具及逐请求计数；准备动作后超时；未完成/超长输出。

**界面验收。** 每项记录日期、代码版本、操作系统/浏览器、步骤、实际结果和证据文件。首次流程从空空间开始，完成可保存的选择题/编程记录；回访流程展示到期复习及 PiPo 选定的活动。启用模型时使用支持工具的账户模型，对照可见工具记录和实际打开内容。

**真实模型评估。** `scripts/evaluate_ai.py` 生成规则基线，`--live` 显式开启对 12 个模拟诊断案例的付费请求。独立人员标注案例并评估事实正确性、相关性后再解释一致率。Agent 场景另记录工具选择、动作有效性、恢复能力及教学回复。模拟回归验证控制流程，不作为真实模型准确率或学生学习效果研究。

**代码审查。** 检查模块合同、失败路径、状态保存、模型数据发送和工具权限；记录审查人、版本、位置、问题、处理及复核。变更遵循“需求—预期—测试/修改—回归—审查—文档”。实际完成记录、测量结果和职责分工分别保存。

### 9. 课程对应与展示证据

| 课程/评分原则 | 已实现证据 |
|---|---|
| 原创性与实用性 10% | 同一应用把错答连接到解释、后续练习和 PiPo 选择的具体学习活动。 |
| 易用性 10% | 单命令本地启动、中英文、情境反馈、明确错误及记录保留。 |
| 技术深度 55% | Python 计算、函数/类/模块、JSON、排序、SQLite 事务、模型接口和 Agent 工具。 |
| Good：规格与测试 | 功能/非功能合同、接口/数据约定和需求验证映射。 |
| Excellent：文档与代码审查 | 运行 README、软件规格及用于记录问题和复核的审查流程。 |
| 生成式 AI 工程加分 | AI 辅助实现、测试、规格、文档和检查，小组核实实际采用的输出。 |
| Lecture04 | 提示要素、SRS、任务分解，运行说明与详细合同分别组织。 |
| Lecture05 | 角色消息、token 限制、模型与执行环境、工具白名单及连续观察。 |
| Lecture06 | 可判定功能条件、量化运行约束、单元/集成测试及需求验证匹配。 |

两类展示分别制作：中英文课堂稿各五页精选技术内容，讲解安排 4:45，控制在五分钟内；中英文视频配套稿各九页，依次包含引言、问题描述、方法论、代表性现场演示和结论，安排 14:30，其中 8:15 为真实应用操作。最终提交十五分钟内的实际视频。录制与课堂指南包含师生答问准备及每位成员必须完成的同伴互评要求。

### 10. 参考材料

所提供的 INT6181 项目要求 v2 第 3–5 节；Lecture03 编程复习；Lecture04 编程中的生成式 AI 第 12–17、24、44–47 页；Lecture05 编程 Agent 基础第 17–19、22–28 页；Lecture06 测试与调试第 6、13–16、22–28 页；CaseStudy5 软件需求规格。页码采用原始 PPTX 顺序。组件来源及许可位置见 README。

## GLM-4.7 configuration and regression scope

The named target is Z.ai GLM-4.7 via the school gateway using the OpenAI-compatible protocol. OPENAI_* configuration names are retained for compatibility. The gateway does not reliably report model identity; configured identity is not proof of actual provider routing. GLMDiagnosisTests verifies valid/unknown diagnoses, rejected fabricated evidence, standard-explanation fallback, mocked request success and timeout, App Key errors without credential disclosure, Markdown JSON compatibility and no-network fallback when a key is missing. LanguageTests verifies the outgoing glm-4.7 model ID, disabled-thinking request and preserved source evidence. PiPoTests covers native and school JSON tool loops, plain-text summaries only after real content reads, and rejection of textual tool markup. All these regression calls are simulated, not live quality or latency measurements.

## GLM-4.7 配置与回归范围

目标模型为通过学校 OpenAI 兼容网关调用的智谱 GLM-4.7，保留 OPENAI_* 配置名以兼容已有设置。学校响应未可靠报告模型身份，配置名称不等于实际路由证明。GLMDiagnosisTests 验证有效/unknown 诊断、伪造引用拒绝、标准解析回退、模拟成功与超时、App Key 错误与凭据隐藏、Markdown JSON 兼容和无密钥不联网。LanguageTests 检查请求中的 glm-4.7、关闭思考参数及原始依据保留。PiPoTests 验证原生与学校 JSON 工具循环、实际读取内容后的普通文字总结，以及伪工具标记拒绝。上述回归使用模拟响应，不代表已测得真实诊断质量或延迟。
