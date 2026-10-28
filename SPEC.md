# PySteps — Software Requirements Specification / 软件需求规格说明书

版本 / Version: 1.1 · 日期 / Date: 2026-10-28 · 适用代码 / Baseline: `final-homework-3`

本文以现有实现为基线整理需求，不追溯声称在编码前完成。需求中的“应”表示验收标准；“已实现”“自动验证”“待人工验收”分别记录，不互相替代。文档采用课程所讲的 SRS、功能/非功能分类与需求—测试对应原则，不声称获得 ISO/IEC/IEEE 29148 认证，也不把课件示例全部当作项目必需功能。

This specification documents the existing implementation; it is not evidence of a pre-implementation SRS. “Shall” denotes an acceptance condition, not a completed test. Implementation, automated verification and pending manual acceptance are distinct. The document applies the course's SRS and traceability principles without claiming certification or treating every lecture example as mandatory functionality.

## 1. 目的、用户与范围 / Purpose, users and scope

目标是帮助 Python 初学者根据概念导学和作答反馈继续练习。主要用户为学习者；维护者负责内容、配置和版本；组员负责测试及审查。程序不是正式考试评分系统，不根据一次答错确定学生能力，也不宣称已证实提升学习成绩。

The system supports Python beginners with lessons, feedback and follow-up practice. Learners use the application; maintainers manage content and configuration; team members verify it. It is not a formal assessment system or evidence of improved learning outcomes.

当前范围：3 章（条件判断、循环、函数与返回值）、15 个概念、30 道选择题、6 个编程任务。包含双语界面、可选 Kimi、SQLite 和备份。排除教师后台、任意学科、图片识题、账号同步、自主代理及服务器执行任意学生代码。

Scope: 3 chapters, 15 concepts, 30 questions, 6 coding tasks, bilingual UI, optional Kimi, SQLite and backups. Teacher dashboards, arbitrary subjects, image recognition, account sync, autonomous agents and arbitrary learner-code execution on the server are excluded.

术语 / Terms: FR = 功能需求 / functional requirement; NFR = 非功能需求 / non-functional requirement; AC = 验收案例 / acceptance case; `unknown` = 证据不足 / insufficient evidence; revision = 保存版本 / optimistic save version. “规则反馈”来自题库和确定性逻辑；“AI 反馈”是通过有限校验的补充输出。

## 2. 运行环境与系统边界 / Operating context and boundaries

Python 3.10+ 标准库后端，通过 `main.py` 启动，默认 `127.0.0.1:8010`；React 构建产物随包提供。Node.js 22 与 npm 仅用于前端开发。浏览器加载本地 Pyodide 后运行受限代码；模型分析需网络和有效配置。

The Python 3.10+ standard-library server starts via `main.py`, defaulting to `127.0.0.1:8010`. React assets and Pyodide are bundled. Node.js 22/npm are frontend development tools. Model analysis requires connectivity and valid credentials.

| 边界 / Boundary | 责任 / Responsibility |
|---|---|
| 浏览器 → Python HTTP | JSON 输入、原始来源检查、服务端判题与存储 / JSON input, origin checks, grading and persistence |
| Python → Kimi | 可选单次请求、受限证据与输出校验 / Optional single request, bounded evidence and output validation |
| 浏览器 → Worker | 学生代码及案例；禁止服务器执行 / Learner source and cases; no server execution |
| 浏览器 Cookie → SQLite | 匿名学习空间与 revision；非账号认证 / Opaque learning space and revision, not an account |

PiPo 的预设对话与关键词导航不使用模型。AI 诊断不运行工具，不形成代理循环。学习理由、代码与备份属于输入数据，不能被当作程序指令或可信成绩。

PiPo is rule-based navigation. Diagnosis has no tool execution or agent loop. Reasons, source and backups are untrusted data, not instructions or trusted grades.

## 3. 功能需求 / Functional requirements

优先级 / Priority: P1 = 基础交付 / core delivery; P2 = 可选 AI / optional AI. 各项均描述代码中的现有行为，验证范围见第 8 节。


### FR-01 · 学习内容与语言 / Content and language · P1

**要求：** 首次访问应默认英语，允许中英切换；显示现有三章内容。代码、精确输出与学生原文应保留，新的模型请求携带当前语言。

**Requirement:** First visits shall default to English and allow EN/ZH switching. Code, exact outputs and learner text shall remain unchanged; new model requests shall carry the selected language.

**实现与验证索引 / Implementation and verification:** `AC-01; LanguageTests; web/src/i18n.ts`。测试名称表示相关证据，不代表整条需求已全部覆盖。 / A named test is relevant evidence, not full coverage.


### FR-02 · 选择题判分 / Quiz grading · P1

**要求：** 输入必须是已知题号与有效选项。应按题库固定答案返回 correct 和规则反馈；非法题号/选项应报错，不能由模型改分。

**Requirement:** A known question and valid choice shall be graded against the fixed key and return correctness and rule feedback. Unknown IDs/options shall be rejected; the model shall not change grades.

**实现与验证索引 / Implementation and verification:** `AC-02; test_all_question_answers; test_grading_and_ai_rule_fallback`。测试名称表示相关证据，不代表整条需求已全部覆盖。 / A named test is relevant evidence, not full coverage.


### FR-03 · 课程过关 / Progression · P1

**要求：** 完成入门阅读和前置概念后开放课程。当前概念已读，且课程模式下两道不同题均最新无提示答对时通过；自由练习和提示答对不能代替独立通关。处理按状态中记录顺序进行。

**Requirement:** A course shall open after introduction/prerequisites. In the current bank, the read concept passes when both distinct questions have correct, hint-free course attempts. Free practice and hinted answers shall not pass it. Stored attempt order is used.

**实现与验证索引 / Implementation and verification:** `AC-03; test_entire_course_unlocks_in_order; test_hint_and_free_practice_do_not_pass_course`。测试名称表示相关证据，不代表整条需求已全部覆盖。 / A named test is relevant evidence, not full coverage.


### FR-04 · 补充理由 / Revised reasoning · P1

**要求：** 错答后应允许修改理由；清除旧 AI 反馈，重新分析更新同一记录，不增加作答次数；理由最多1000字符。

**Requirement:** After a mistake, editing the reason shall invalidate old AI feedback and update the same attempt without increasing the count; reasons are limited to 1,000 characters.

**实现与验证索引 / Implementation and verification:** `AC-04; App.tsx; validate_state`。测试名称表示相关证据，不代表整条需求已全部覆盖。 / A named test is relevant evidence, not full coverage.


### FR-05 · 练习推荐 / Recommendation · P1

**要求：** 应限定同章并排除当前题。非 unknown 时排序为：目标概念未做题、到期题、其他未做题、其他已做题；到期更早优先。unknown 时不强行指定概念，先到期、再未做、再已做；用难度和题号等规则稳定排序。

**Requirement:** Recommendations shall remain in the chapter and exclude the current question. With a known target: unseen target items, due items, other unseen items, then remaining seen items. Due items use earlier due time. Unknown avoids a target, ranking due/unseen/seen, with deterministic difficulty/ID tie-breaking.

**实现与验证索引 / Implementation and verification:** `AC-05; test_recommendation_target_and_unknown; LearningEngine.recommend`。测试名称表示相关证据，不代表整条需求已全部覆盖。 / A named test is relevant evidence, not full coverage.


### FR-06 · 复习计划 / Review scheduling · P1

**要求：** 按时间排序处理作答；错误重置到阶段0、10分钟后复习。提示答对回到阶段0、至多一天后复习；到期独立答对按1/3/7/14/30天推进且封顶，提前重复独立答对不推进。

**Requirement:** Chronological attempts shall schedule an error at stage 0 after ten minutes. Hinted success resets to stage 0 with a review within one day. Due independent success advances through 1/3/7/14/30 days, capped at stage 5; early independent repeats do not advance.

**实现与验证索引 / Implementation and verification:** `AC-06; test_schedule_early_repeat_not_advance`。测试名称表示相关证据，不代表整条需求已全部覆盖。 / A named test is relevant evidence, not full coverage.


### FR-07 · AI 理由分析 / AI analysis · P2

**要求：** 仅错答、非空理由、配置可用且口令正确时请求模型。候选为当前错项映射概念或 unknown；要求逐字引用理由。标签/引文失败整体退回规则；答案或解析依据失败则仅讲解/提示恢复题库内容。固定答案不变。

**Requirement:** Only wrong answers with non-empty reasons, valid configuration and team authorisation shall request the model. Labels are the wrong-choice candidate or unknown with a verbatim reason quote. Invalid label/quote causes full rule fallback; invalid answer/knowledge evidence replaces prose with bank content. Keys remain fixed.

**实现与验证索引 / Implementation and verification:** `AC-07; AITests; test_team_authorization_and_rate_limit`。测试名称表示相关证据，不代表整条需求已全部覆盖。 / A named test is relevant evidence, not full coverage.


### FR-08 · 学习记录与保存 / Persistence · P1

**要求：** 以随机 Cookie 对应学习空间，保存读取、答题、草稿与编程记录。写入应携带 revision；旧版本返回409，不能静默覆盖；读取应返回本空间数据。

**Requirement:** A random cookie shall identify the space holding reads, attempts, drafts and coding records. Saves require a revision; stale writes shall return 409 without silent overwrite. Reads return only that space.

**实现与验证索引 / Implementation and verification:** `AC-08; test_sqlite_persistence_isolation_and_conflict; test_state_roundtrip_cookie_and_conflict`。测试名称表示相关证据，不代表整条需求已全部覆盖。 / A named test is relevant evidence, not full coverage.


### FR-09 · 备份迁移 / Backup · P1

**要求：** 应支持版本1 JSON导出及确认后替换导入。导入时校验结构、ID、长度和时间，重新判分并移除不可信AI反馈；不合并账号或设备。

**Requirement:** Version-1 JSON export and confirmed replacement import shall be available. Imports validate shape, IDs, lengths and timestamps, recompute grades and discard untrusted AI feedback. There is no account/device merge.

**实现与验证索引 / Implementation and verification:** `AC-09; test_import_regrades_and_removes_untrusted_feedback; test_import_rejects_invalid_and_oversize`。测试名称表示相关证据，不代表整条需求已全部覆盖。 / A named test is relevant evidence, not full coverage.


### FR-10 · 编程练习 / Coding · P1

**要求：** 应支持草稿、前两例运行、全例检查、停止与历史。仅在浏览器Worker运行受限Python；结果按类型和值比较。运行时加载/执行超时应终止Worker，不生成通过记录。

**Requirement:** Coding shall support drafts, first-two-case runs, full checks, stop and history. Restricted Python runs only in a browser Worker with type/value comparisons. Loading/execution timeout shall terminate it without a passing record.

**实现与验证索引 / Implementation and verification:** `AC-10; test_restricted_syntax; App.tsx; python-worker.mjs`。测试名称表示相关证据，不代表整条需求已全部覆盖。 / A named test is relevant evidence, not full coverage.


### FR-11 · 学习汇总 / Progress · P1

**要求：** 应显示课程状态、作答统计与错题；图表按设备时区汇总最近14个有作答日期。重复和提示作答仍计入历史，不能解释为独立掌握率。

**Requirement:** The UI shall show course state, attempt statistics and mistakes, aggregating the latest 14 dates with attempts in device timezone. Repeated/hinted attempts remain in history and are not independent mastery measures.

**实现与验证索引 / Implementation and verification:** `AC-11; App.tsx; summary`。测试名称表示相关证据，不代表整条需求已全部覆盖。 / A named test is relevant evidence, not full coverage.


### FR-12 · 小精灵导航 / PiPo · P1

**要求：** 快捷入口或关键词应引导至地图、练习或编程。空输入不提交，输入最多160字符；输入AI问题时说明到练习页使用分析。此功能不发送模型请求。

**Requirement:** Shortcuts/keywords shall navigate to map, practice or coding. Empty input is not submitted; input is capped at 160 characters. AI questions point to exercise analysis. No model request is sent.

**实现与验证索引 / Implementation and verification:** `AC-12; AssistantWidget.tsx`。测试名称表示相关证据，不代表整条需求已全部覆盖。 / A named test is relevant evidence, not full coverage.


## 4. 非功能需求 / Non-functional requirements

下列可量化阈值有两类：实现内已有的限制，以及待团队实测的验收目标。二者分别标明。没有用“快速、安全、易用”等形容词代替验收条件。

Implemented limits and proposed measurement targets are distinguished below. Proposed targets are project acceptance choices, not instructor-prescribed numbers or established results.

| ID | 要求 / Requirement | 验证方法与状态 / Verification and status |
|---|---|---|
| NFR-01 可靠性 / Reliability | 无模型配置时，核心判题、规则反馈、推荐、保存仍可用；模型失败不更改固定分数。 / Core learning remains usable without AI; failure does not alter keys. | AITests、HTTP fallback 已自动验证部分路径；完整界面 AC-07 待验收。 / Partly automated; UI acceptance pending. |
| NFR-02 响应 / Responsiveness | 本机固定题库下，连续20次规则判题接口调用每次应在1秒内返回。 / On the reference local setup, each of 20 rule-grading calls should finish within 1 s. | **新增验收目标、未测量**；记录设备、版本、负载、每次耗时，不含AI。 / Proposed, unmeasured; record setup and timings, excluding AI. |
| NFR-03 等待界限 / Bounded waits | 模型timeout参数30s、UI等待40s；Worker加载60s、执行4s；数据库连接timeout参数10s。 / API parameter 30 s, UI 40 s, Worker loading 60 s/execution 4 s, DB timeout parameter 10 s. | 配置及部分模拟验证；浏览器终止行为待 AC-10。参数不是整体时延保证。 / Inspected/partly mocked, browser pending; not overall latency guarantees. |
| NFR-04 数据访问 / Data access | 仅公开静态目录可访问；非法Host/Origin应拒绝；不同Cookie空间隔离，旧revision不能覆盖。 / Restrict public files, reject invalid host/origin, isolate spaces and prevent stale overwrite. | HTTPTests验证部分；非法Host、HEAD及更多路径仍需补例。 / Partial HTTP coverage; more cases pending. |
| NFR-05 资源与费用 / Resources | 输入按第5节限额；模型每进程60次/小时、max_tokens=1200、响应最多65536字节；没有硬内存或费用上限。 / Enforce §5; 60 calls/hour/process, 1,200 token allowance, 65,536 response bytes; no hard memory/spend cap. | 61次拒绝和部分长度已测；窗口重置及其余边界待补。 / Rate limit and some lengths tested; reset/remaining boundaries pending. |
| NFR-06 易用性 / Usability | 一名未参与核心开发的组员应能仅按README启动，完成答题→反馈→推荐→备份，无开发者代操作。 / A non-core-developer should complete startup and the learning/backup flow using README without takeover. | 项目验收目标；记录求助点、错误和修改，尚未执行。 / Proposed acceptance; record difficulties; pending. |
| NFR-07 可移植性 / Portability | 目标为Windows/macOS/Linux、Python3.10/3.13及现代浏览器。 / Target Windows/macOS/Linux, Python 3.10/3.13 and modern browsers. | CI配置不是运行证据；本次仅macOS/Python3.12自动测试通过，目标组合待确认。 / Only macOS/Python3.12 rerun; target matrix unconfirmed. |
| NFR-08 可维护性 / Maintainability | 领域规则、存储、HTTP、AI分层；修改映射需求与测试；提交前另一成员审查并记录问题闭环。 / Separate domain/storage/HTTP/AI; trace changes to tests and obtain independent review. | 代码结构已检查，成员审查完成情况未据此确认。 / Structure inspected; human review not established. |
| NFR-09 离线资源 / Offline assets | 后端运行且禁止外部网络时，本地导学、规则练习和编程资源应可用，AI明确不可用。 / With server running and external traffic blocked, bundled learning/coding resources remain usable; AI is unavailable. | 资源随包提供；本次未重新进行离线浏览器验收。 / Bundled assets inspected; browser acceptance not rerun. |

## 5. 数据与接口约束 / Data and interface constraints

状态格式 / State: `version=1`, `reads`, `attempts`, `drafts`, `codeAttempts`。服务端重算选择题正确性。SQLite 使用 `learners(id, revision, state)`，ID 是随机 Cookie 的 SHA-256 摘要；这不是实名认证，也不是数据库加密。

Quiz correctness is recomputed server-side. SQLite stores `learners(id, revision, state)` with the digest of an opaque cookie. Hashing the identifier is neither account authentication nor database encryption.

| 字段或对象 / Field | 约束 / Constraint |
|---|---|
| reads | 列表最多16项，ID为入门或已知概念；去重 / At most 16 entries, known concept/introduction IDs; deduplicated |
| attempts / codeAttempts | 最多10,000 / 2,000条；各自ID唯一、非空、最多80字符 / Separate unique nonempty IDs, at most 80 characters |
| reason / source / details | 最多1,000 / 20,000 / 4,000字符 / Character limits |
| created_at | 可解析、带时区的ISO时间 / Parseable timezone-aware ISO timestamp |
| hints_used | 整数，0至该题提示数量 / Integer within the question hint range |
| revision | 非负整数，保存时匹配当前版本 / Nonnegative integer matching stored version |
| HTTP body | JSON对象，1至10,000,000字节；禁止NaN等非有限值 / JSON object with finite values |

### 5.1 HTTP 接口 / API contract

POST需同源、正确Content-Type和合法Host。`/api/import`只验证并返回清洗后状态，客户端随后保存；不能把该接口单独当作已写数据库。

POST requests require matching origin, JSON content type and a valid host. `/api/import` validates and returns sanitised state; the client then saves it. Import validation alone does not persist data.

| Method/path | 输入 / Input | 输出或错误 / Output or error |
|---|---|---|
| GET `/api/state` | Cookie | revision, state, summary；必要时新Cookie / new cookie when needed |
| POST `/api/state` | revision, state | new revision, summary；旧版本409 / stale version 409 |
| POST `/api/import` | state | validated state；非法400 / invalid 400 |
| POST `/api/grade` | question_id, choice | correct, feedback |
| POST `/api/recommend` | question_id, diagnosis, state | ordered questions |
| GET `/api/diagnose` | 无 / none | configured flag，不证明服务可达 / not provider availability |
| POST `/api/diagnose` | question_id, choice, reason, language；X-Team-Code | feedback；错误口令401；失败/限流可返回规则 / invalid code 401; fallback where applicable |

其他错误 / Other errors: 不匹配Host/Origin 403；未知接口404；Content-Type错误415；空/超大请求413；字段错误400；POST处理中未预期异常500。后者不代表所有GET或启动错误都已统一处理。

Other statuses: 403 host/origin, 404 route, 415 content type, 413 size, 400 fields, 500 unexpected POST processing error. This does not claim universal GET/startup exception handling.

### 5.2 AI 提示与输出 / Prompt and output contract

按Lecture04的四个提示要素记录：指令是谨慎诊断且不执行学生指令；上下文是题目、标准解析和候选概念；输入是所选答案和理由；输出是JSON。Lecture05的角色消息和token限制用于单次请求，没有工具循环。

The prompt has an instruction, bounded context, input data and a JSON output indicator. It uses role messages and a token allowance, not an autonomous tool loop.

输出字段 / Output fields: `concept`, `quote` (1–200字符、理由逐字子串 / verbatim reason substring), `answer_key`, `knowledge_quote` (标准解析子串、去空白至少4字符 / explanation substring, >=4 trimmed characters), `explanation` (1–600), `hint` (1–240)。实现检查是结构和依据约束，不能证明语义正确、消除所有提示注入或代替人工审查。

当前每个错项的候选都指向题目自身概念，模型只能选择该候选或unknown；不能宣称进行了开放式、多误区诊断。Lecture05建议的指数退避和缓存未实现；本项目选择单次调用与规则回退，避免自动重试费用。它是已说明的取舍，不是声称满足所有课件建议。

Each current wrong-option candidate is the question's own concept. The model chooses it or unknown, not unrestricted alternative misconceptions. Exponential backoff and explicit caching suggested in Lecture05 are not implemented; single-call fallback avoids automatic retry charges. This is a disclosed trade-off.

## 6. 模块设计与函数契约 / Modules and function contracts

本节是支持规格的实现说明，不将内部类名当作用户需求。Lecture03的函数、容器、排序、类和文件处理在以下职责中使用。

This section explains implementation, not additional user requirements. Functions, containers, sorting, classes and file operations support the following boundaries.

| 模块/接口 / Module or function | 前置条件与结果 / Preconditions and result |
|---|---|
| `LearningEngine.grade(qid, choice)` | 已知ID与有效选项；返回固定判分，否则ValueError / known ID/choice → grade; invalid → ValueError |
| `LearningEngine.courses(state)` | 已校验状态；按前置集合与记录计算passed/locked/read/solved / validated state → course flags |
| `LearningEngine.recommend(qid, diagnosis, state, now)` | 合法诊断ID/unknown/none；排序返回当前章其他题 / valid label → same-chapter ranked alternatives |
| `LearningEngine.schedule(attempts)` | 有效带时区时间及判分；返回due毫秒与stage / valid attempts → due milliseconds and stage |
| `LearningEngine.validate_state(raw, importing)` | 不信任输入；返回规范状态或ValueError / untrusted data → sanitised state or ValueError |
| `Store.get/save` | 参数化SQL；revision控制原子写入，冲突抛ConflictError / parameterised SQL, versioned transaction |
| `analyze/validate_output` | 模型适配与字段校验；保留规则回退 / model boundary with fallback |
| `Handler` | 传输、来源、会话与错误映射；业务规则交给engine / transport/session checks delegate domain rules |
| `App.tsx` / Worker | UI状态和受限浏览器运行；非服务端执行 / UI state and browser-only execution |

## 7. 人工验收案例 / Manual acceptance cases

以下均为**待执行步骤，不是通过记录**。执行者记录日期、版本、操作系统/浏览器、实际结果、问题编号及复核人。自动测试只覆盖部分条件，不能代替这些界面检查。

These are pending procedures, not pass records. Record date, version, platform/browser, actual result, issue ID and reviewer.

| AC | 操作与预期 / Action and expected outcome |
|---|---|
| AC-01 | 首次访问切语言，填写理由/代码后再切换；初始英语，输入保留，代码不被翻译 / Switch after entering text/source; default EN and preserve input. |
| AC-02 | 同题正确、错误、空选项各一次；正确判分，空选项提示 / Exercise correct/wrong/empty selection; clear outcomes. |
| AC-03 | 未读、读后提示答对、自由练习答对、课程独立答对；仅满足完整条件解锁 / Compare progression conditions. |
| AC-04 | 错答后修改理由并重分析；原记录更新、次数不增加 / Reanalyse without adding attempts. |
| AC-05 | 准备目标未做/到期/其他未做/已做混合历史；对照排序，排除原题 / Check full ranking using mixed history. |
| AC-06 | 固定时钟测试提前、刚好到期、阶段封顶与提示答对；逐项核对间隔 / Use controlled timestamps for all boundaries. |
| AC-07 | 无配置、空理由、错误口令、模拟超时/异常输出；固定分数不变，显示原因且规则可用 / Check fallbacks; mock failures rather than paid calls. |
| AC-08 | 保存刷新后记录保留；两个页面提交旧revision出现冲突且不覆盖 / Persistence and two-tab conflict. |
| AC-09 | 导出、改成伪造成绩、导入确认；重新判分且替换；取消不改变状态 / Import regrading, replacement and cancellation. |
| AC-10 | 浏览器运行6任务参考案例、非法语法、停止、超时与环境加载失败；不得伪造通过 / Real Worker checks across 39 fixtures and failures. |
| AC-11 | 用空历史、重复/提示作答及跨日期样例核对表格和图表 / Verify aggregation against known histories. |
| AC-12 | PiPo快捷按钮及中英关键词；跳转正确，无模型网络请求 / Verify navigation and absence of model calls. |

## 8. 需求—测试可追踪性 / Requirement-to-test traceability

2026-10-28重新运行 `python -m unittest discover -s tests -t . -v`：macOS/Python3.12，21个测试方法通过。初次受限环境无法绑定本机端口；允许本机HTTP后完整重跑通过。使用临时数据库和模拟模型，无付费调用。

On 2026-10-28, all 21 methods passed on macOS/Python3.12. The initial restricted run could not bind a local socket; the authorised local-HTTP rerun passed. Temporary databases and mocked models were used, with no paid calls.

| 需求 / Requirement | 现有证据 / Existing evidence | 剩余范围 / Remaining scope |
|---|---|---|
| FR-01 | 2 LanguageTests | UI切换和译文质量 / UI switching and translation quality |
| FR-02 | all_question_answers; HTTP grading | 更多非法输入 / more invalid inputs |
| FR-03 | entire_course_unlocks; hint_and_free_practice | 界面及异常记录顺序 / UI and unusual ordering |
| FR-04 | 源码检查 / source inspection | AC-04 |
| FR-05 | recommendation_target_and_unknown | 混合历史完整排序 / mixed-history ordering |
| FR-06 | schedule_early_repeat_not_advance | 全阶段、提示与精确边界 / all stages and boundaries |
| FR-07 | 5 AITests; language prompt; authorisation/rate limit | 真实质量、其他服务错误 / live quality and other failures |
| FR-08 | SQLite + HTTP roundtrip/conflict | 浏览器提示与数据库失败 / UI and database failures |
| FR-09 | import regrading; invalid/oversize | 替换确认与其余边界 / confirmation and remaining bounds |
| FR-10 | restricted_syntax; 39 Python reference cases | 实际浏览器Worker / actual browser execution |
| FR-11 / FR-12 | 源码检查 / source inspection | AC-11 / AC-12 |
| NFR-01/04/05 | 规则回退、HTTP、限流等部分断言 / partial assertions | 更多边界和失败路径 / additional paths |
| NFR-02/03/06/07/08/09 | 阈值、结构、CI配置检查 / inspected config/structure | 测量、人工、跨平台和独立审查 / measurements, human/platform review |

测试方法明细如下；列出目标不等于验证目标的所有分支。未测量行覆盖率或分支覆盖率，不能用“21通过”声称100%覆盖。课件介绍doctest，本项目采用标准库unittest；课程文档没有要求必须改成doctest。

The inventory below lists assertions, not exhaustive branch coverage. No line/branch coverage was measured. Lecture06 introduces doctest; using unittest is an implementation choice, not a claim that doctest was used.

| Test method | Direct or indirect target | Actual assertions | Why it was selected |
|---|---|---|---|
| `test_all_question_answers` | `LearningEngine.grade(); question data` | Execute all 30 snippets against expected output; check grading for each option and presence of wrong-option mappings. | Wrong answer keys undermine all feedback; this does not validate educational labels. |
| `test_entire_course_unlocks_in_order` | `LearningEngine.courses(); requirements() [indirect]` | Start locked, read and complete lessons in order, and verify all 15 concepts pass. | Check that the normal learning path can be completed. |
| `test_hint_and_free_practice_do_not_pass_course` | `LearningEngine.courses()` | Hinted or free-practice successes do not pass the boundary lesson. | Avoid treating assisted or off-course attempts as independent mastery. |
| `test_schedule_early_repeat_not_advance` | `LearningEngine.schedule()` | An early repeat preserves the schedule; due success reaches stage 2; an error is due in 600000 ms. | Check review timing boundaries and error scheduling. |
| `test_recommendation_target_and_unknown` | `LearningEngine.recommend()` | With empty history, first item matches concept; exclude current item; remain in chapter; unknown returns nine candidates. | Check basic selection constraints; mixed-history ranking is not established. |
| `test_import_regrades_and_removes_untrusted_feedback` | `LearningEngine.validate_state(importing=True); grade()` | Import falsified correctness and AI feedback; recompute the wrong result and restore rule feedback. | Do not trust grades or generated explanations supplied by a backup. |
| `test_import_rejects_invalid_and_oversize` | `LearningEngine.validate_state()` | Reject an unknown concept/task, empty attempt, unsupported version and a 20001-character draft. | Prevent malformed stored data; not an exhaustive boundary test. |
| `test_sqlite_persistence_isolation_and_conflict` | `Store.save(); Store.get(); connect() [indirect]` | Read data through a new Store instance, isolate users and reject stale revisions with ConflictError. | Prevent lost data, cross-user leakage and stale overwrites. |
| `test_valid_and_unknown_diagnoses` | `validate_output()` | Valid output is personalised; unknown is allowed. | Allow supported feedback and abstention. |
| `test_bad_quote_and_label_rejected` | `validate_output()` | Reject invented quotes and unknown concept labels. | Constrain fabricated evidence and labels. |
| `test_wrong_answer_or_anchor_uses_reviewed_explanation` | `validate_output()` | A wrong answer key or unsupported knowledge quote causes standard-explanation fallback. | Keep answer keys fixed and retain standard explanations on invalid evidence. |
| `test_mock_success_and_timeout_fallback` | `analyze(); validate_output() [indirect]` | Accept mocked valid output, assert a 30-second timeout and fall back on simulated TimeoutError. | Exercise success and timeout paths without a paid call. |
| `test_no_key_does_not_call_network` | `analyze()` | Without a key, return rules; fail the test if the network stub is called. | Ensure missing configuration never triggers a model request. |
| `test_restricted_syntax` | `validate_source(); gate_status(); ticket_price(); collect_coins(); countdown(); checkout(); route_parcel() [reference solutions]` | Allow a basic function; compare type/value for 39 cases across six solutions; reject imports/open/eval/attribute access/getattr/classes. | Check reference solutions and selected restrictions, not the entire browser sandbox. |
| `test_static_and_private_files` | `create_server(); Handler.do_GET() [via HTTP]` | Root contains the app node; source, private config, traversal and directory listing return 404. | Prevent private-file exposure through static serving. |
| `test_state_roundtrip_cookie_and_conflict` | `Handler.do_GET()/do_POST()/identity(); Store [via HTTP]` | HttpOnly cookie, save/read consistency, stale-version 409 and empty state for a different cookie jar. | Verify real integration of API, session identity and persistence. |
| `test_bad_origin_and_input` | `Handler.do_POST(); LearningEngine.question()/grade() [indirect]` | A cross-origin POST returns 403; an unknown question returns 400. | Check two invalid requests, not every Host or malformed-JSON case. |
| `test_grading_and_ai_rule_fallback` | `Handler.do_POST(); LearningEngine.grade(); AI route [via HTTP]` | The grading endpoint recognises the correct answer; unconfigured diagnosis returns rule feedback. | Verify the endpoints used by the frontend reach the domain logic. |
| `test_team_authorization_and_rate_limit` | `Application.ai_enabled(); authorize_ai(); allow_call()` | Configured availability, correct/incorrect passwords, first 60 calls allowed and the 61st rejected. | Protect access and request volume; hourly reset is not tested. |
| `test_all_learning_prose_has_english_translation` | `data/*.json; web/src/en.json [data check]` | Check translation entries for selected learning prose, excluding code/options/tests and other skipped fields. | Detect missing entries, not translation quality or UI switching. |
| `test_english_prompt_preserves_original_evidence` | `analyze(language="en")` | Mocked request asks for English while preserving the reason and standard explanation; English output is accepted. | Avoid altering evidence during language selection; live English quality is not established. |


## 9. 变更、审查与验收责任 / Change, review and acceptance

组长维护基线和整合；计算机B维护测试；计算机C牵头独立审查与运行验证；教育成员审查内容；设计成员检查交互和PiPo；管理成员维护需求、验收与提交清单。此处是职责安排，不证明工作已经完成。

The leader integrates; computing B maintains tests; computing C leads independent review and execution checks; education reviews content; design checks interaction; management maintains requirements and acceptance records. Assigned responsibility is not completion evidence.

修改流程 / Change process: 标注FR/NFR → 明确预期 → 尽可能先补复现测试 → 修改 → 回归 → 另一成员审查 → 更新README/SPEC及验收记录。 / Identify requirement, define behaviour, preferably reproduce with a test, change, regress, independently review and update documents.

审查记录至少包含 / Minimum review fields: 日期/date、审查人/reviewer、代码版本/version、位置/location、问题/finding、处理/resolution、复核/recheck。不编造签名或补写不存在的测试先行历史。

当前待完成 / Outstanding: 浏览器验收、目标平台运行证据、独立内容与代码审查、NFR响应测量。可选真实AI评估须区分规则基线、模拟样例标签和独立人工判断；API可调用不等于诊断有效。项目无需为满足课件而增加所有代理、模型或企业系统功能。

Pending evidence includes browser/platform checks, human review and response measurements. Optional live evaluation must distinguish rule baselines, synthetic labels and independent judgments. API availability is not diagnostic validity.

## 10. 课程依据与评分对应 / Course basis and assessment mapping

页码采用原始PPTX的幻灯片顺序。Lecture04 PDF为相同48页版本；Lecture05译文PDF为27页，不能直接套用30页PPTX页码。以下是所提供材料中的原则，不是对外部标准完整条文的复述。

Slide numbers refer to the original PPTX order. Lecture04 has a matching 48-page PDF; the 27-page Lecture05 translation does not share the 30-slide numbering. References describe supplied course principles, not a complete external standard.

| 依据 / Source | 原则 / Principle | 本文落实 / Application |
|---|---|---|
| Lecture03, functions/data structures/classes/files | 参数、返回、容器、排序、模块职责 / parameters, returns, collections, sorting, responsibilities | §5–6 契约与分层 / contracts and modules |
| Lecture04, slides 12–17 | 提示四要素；SRS；引用29148及不完整示例 / prompt elements, SRS, cited standard/example | §1–5、提示合同；不声称认证 / scope and contracts, no certification claim |
| Lecture04, slides 24, 44 | 分解、规格、审查、测试反馈、同步文档 / decomposition, specification, review, feedback | §6、8–9；不伪造TDD历史 / traceable change process |
| Lecture04, slides 45–47 | README面向人，AGENTS用于代理附加指令 / human README vs agent instructions | README保留运行、项目和贡献说明；详细契约归SPEC / separate purposes |
| Lecture05, slides 17–19, 22–28 | 消息、JSON、额度及调用建议；模型与代理循环的区别 / messages, JSON, bounds, agents | §2、5.2；明确未实现重试/缓存 / explicit limitations |
| Lecture06, slides 6, 8, 10 | V模型需求与验证匹配 / requirement–verification matching | §7–8 AC与测试映射 / acceptance and traceability |
| Lecture06, slides 13–16, 22–28 | 功能/非功能、可量化质量、单元测试与边界 / FR/NFR, measurable quality, unit/boundary tests | §3–4、8；目标与结果分开 / separate targets and evidence |
| Project Requirements v2, §3.1–3.3 | 实用10%、易用10%、技术55%；Excellent含文档与代码审查 / usefulness, usability, technical depth | 范围、NFR、测试、README、独立审查记录 / scope, tests, docs, review |
| Project Requirements v2, §4–5 | main.py、README、代码及测试ZIP、引用 / entry point, instructions, packaging, attribution | README运行/提交/来源 / run, package, attribute |

本次重写提供规格和文档证据，并不替代真实独立代码审查，也不保证最终Excellent成绩。展示20%、个人报告5%、互评及Moodle提交要求由小组另行完成。

This rewrite supplies specification/documentation evidence, not independent human review or a guaranteed grade. Presentation (20%), individual report (5%), peer assessment and Moodle obligations remain separate.

参考材料 / Supplied references:

1. INT6181 Group Project Requirements_v2.pdf, pp.1–3.
2. Lecture03 Review of Programming II.pptx.
3. Lecture04 Generative AI in Programming.pptx / matching PDF.
4. Lecture05 Foundation of Coding Agents.pptx; translated PDF used as a secondary reading aid.
5. Lecture06 Testing and Debugging I.pptx.

软件依赖和外部资源的来源见README及licenses。对课件引用的ISO标准只采用课件已介绍的概念，没有声称核查完整标准。文档由AI协助整理并对照代码；最终团队验收应依据真实记录。

Dependency attribution is in README/licenses. The full ISO standard was not audited. AI assisted this code-grounded documentation; final team acceptance requires actual records.
