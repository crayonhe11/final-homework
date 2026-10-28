# 中文版：功能规格与测试说明

## 1. 目标与范围

为 Python 初学者提供有序导学、谨慎的误区线索及章节编程。Python 3.10+ 标准库服务器提供网页界面和本地资源，范围为 3 章、15 概念、30 题、6 编程任务。

范围外：教师后台、任意学科、图片识题、账号同步、服务器执行任意学生代码、自主 AI Agent。这些是范围决定，不是课程评分表明确要求的缺项。

## 2. 输入、处理、输出与验收

| ID |行为 |验收证据 |
|---|---|---|
| F01 |题号和有效选项 → 标准判分、解析与概念线索 | `test_all_question_answers`, `test_grading_and_ai_rule_fallback` |
| F02 |阅读、课程记录、前置条件 → 锁定/开放/通过；提示与自由练习不计独立通关 | `test_entire_course_unlocks_in_order`, `test_hint_and_free_practice_do_not_pass_course` |
| F03 |当前题、诊断、历史 → 同章排序排除原题；目标未做优先；unknown 不强行归因 | `test_recommendation_target_and_unknown` |
| F04 |时间、正误、提示 → 错后十分钟，独立到期答对按1/3/7/14/30天推进，提前重复不推进 | `test_schedule_early_repeat_not_advance` |
| F05 |版本 1 备份 → 校验题号、长度、日期、课程字段；重判和恢复解析 | `test_import_regrades_and_removes_untrusted_feedback`, `test_import_rejects_invalid_and_oversize` |
| F06 |随机 Cookie、状态、版本 → 隔离保存及过期写入 409 | `test_sqlite_persistence_isolation_and_conflict`, `test_state_roundtrip_cookie_and_conflict` |
| F07 |错选、非空理由、授权 AI 请求 → 受限诊断反馈或规则回退 | `AITests`, `test_team_authorization_and_rate_limit` ；浏览器行为另验 |
| F08 |限长、允许语法与函数名的代码 → Worker 案例结果；布尔值与数字严格区分 | `CodeSyntaxTests` ；浏览器行为另验 |
| F09 |历史 → 设备时区最近 14 个作答日期统计、表格与曲线 | 手动浏览器验收，非本次自动测试证据 |
| F10 |提交 → 原位下一步；修改理由更新同一记录 | 手动浏览器验收，非本次自动测试证据 |
| F11 |首访英语；切换记忆并保留答案草稿；新 AI 带语言 | `test_all_learning_prose_has_english_translation`, `test_english_prompt_preserves_original_evidence` ；浏览器行为另验 |
| F12 |PiPo 快捷入口或关键词 → 页面跳转，不调用模型 | `AssistantWidget.tsx` ；浏览器行为另验 |
| N01 |本机断外部请求 → 基础学习/编程可用 | 手动浏览器验收，非本次自动测试证据 ；浏览器行为另验 |
| N02 |异源写入、非法 Host、私有路径 → 拒绝且不暴露文件 | `test_bad_origin_and_input`, `test_static_and_private_files` |

## 3. 数据与约束

SQLite 表为 `learners(id, revision, state)`；ID 是随机 Cookie 的 SHA-256 摘要，不收集姓名学号。状态含读课、作答、草稿及编程记录。选择题由服务器重判；AI 与浏览器编程结果是学习记录，不是防篡改考试凭证。

每空间限 10,000 次选择题、2,000 次代码提交；请求 10 MB，理由 1,000 字符，代码 20,000。没有自动归档。导入确认后替换当前空间，忽略未知字段，拒绝未知题/任务，不合并不同设备。

## 4. 异常行为

- 缺网页成品或端口冲突：显示启动错误，不伪报成功。
- 保存失败或冲突：显示备份/重试提示，不假定已保存而跳题。
- AI 未配置、未授权、超时或无效：说明原因并回退规则。
- 加载超过 60 秒或执行超过 4 秒：终止 Worker，不记录通过。
- 数据库异常：通用错误，不记录密钥或学生理由。

## 5. 验证状态与局限

2026-10-27，macOS 上 21 项 Python 测试与 TypeScript 检查通过。39 个 Python 参考案例不等于本次重新跑了 39 个浏览器案例。跨平台 CI 有配置，未核实执行结果；最终浏览器/Windows/Linux 验收仍需记录。

现有错误选项全部映射到本题概念；Kimi 只能选候选或 unknown，不能任意推断其他概念。引文匹配不保证讲解正确。人工内容复核、独立标签 AI 评估与学习效果研究未完成。

浏览器沙箱没有硬性内存配额；统计含重复/提示作答；通关仅表示当前题库表现，不等于全面掌握；AI 检查和自动测试不等于独立团队审查完成。

## 6. 现有21项测试：函数、内容和选择原因

21指21个test_方法，不是21个函数，也不是只有21组输入。其中有30道题和39个编程案例的subTest循环。按测试类计数：LearningTests 8、AITests 5、CodeSyntaxTests 1、HTTPTests 5、LanguageTests 2。辅助函数可能被间接执行，但这不证明它的每个分支都被断言。

| 测试方法 | 直接或间接测试对象 | 实际断言 | 为什么选择 |
|---|---|---|---|
| `test_all_question_answers` | `LearningEngine.grade(); question data` | 执行全部30题代码并比较标准输出；检查各选项判分和错误选项映射存在。 | 防止答案错误污染所有反馈；不证明误区标签合理。 |
| `test_entire_course_unlocks_in_order` | `LearningEngine.courses(); requirements() [indirect]` | 从全锁定开始，依次阅读、完成课程，检查15概念最终通过。 | 验证正常学习路径能完整走通。 |
| `test_hint_and_free_practice_do_not_pass_course` | `LearningEngine.courses()` | 提示后答对及自由练习答对，均不使boundary课程通过。 | 防止把非独立作答误计为课程掌握。 |
| `test_schedule_early_repeat_not_advance` | `LearningEngine.schedule()` | 提前一小时重复不改变计划；到期答对升至阶段2；错答安排600000毫秒后。 | 验证复习时间边界与错后重练。 |
| `test_recommendation_target_and_unknown` | `LearningEngine.recommend()` | 空历史下首项同概念；排除当前题；全部同章；unknown返回9个候选。 | 验证最基本选题约束；尚未证明混合历史的全部排序规则。 |
| `test_import_regrades_and_removes_untrusted_feedback` | `LearningEngine.validate_state(importing=True); grade()` | 导入伪造正确标记与AI反馈后，重算为错误并恢复规则反馈。 | 不能信任备份里自报的成绩和模型讲解。 |
| `test_import_rejects_invalid_and_oversize` | `LearningEngine.validate_state()` | 拒绝未知概念、空作答对象、未知任务、错误版本及20001字符草稿。 | 防止坏数据进入存储；未穷举所有字段边界。 |
| `test_sqlite_persistence_isolation_and_conflict` | `Store.save(); Store.get(); connect() [indirect]` | 保存后新Store实例能读回；用户隔离；旧revision写入抛ConflictError。 | 防止记录丢失、串用户和覆盖。 |
| `test_valid_and_unknown_diagnoses` | `validate_output()` | 合法结构可采用个性化反馈；unknown合法。 | 既接受有依据结果，也允许暂不判断。 |
| `test_bad_quote_and_label_rejected` | `validate_output()` | 拒绝学生未说过的引文及不存在的概念。 | 限制模型编造证据与标签。 |
| `test_wrong_answer_or_anchor_uses_reviewed_explanation` | `validate_output()` | 错误答案标识或不在标准解析中的依据导致固定解析回退。 | 模型不能改答案，证据无效时保留可靠解析。 |
| `test_mock_success_and_timeout_fallback` | `analyze(); validate_output() [indirect]` | 模拟合法响应采用AI；确认30秒超时参数；模拟TimeoutError后回退规则。 | 验证服务可用和超时两条路径，不产生费用。 |
| `test_no_key_does_not_call_network` | `analyze()` | 无密钥时返回规则；若调用模拟网络则立即失败。 | 保证未配置时不发起模型请求。 |
| `test_restricted_syntax` | `validate_source(); gate_status(); ticket_price(); collect_coins(); countdown(); checkout(); route_parcel() [reference solutions]` | 允许基础函数；6参考解的39案例比较类型和值；拒绝import/open/eval/属性访问/getattr/class。 | 检查题目参考解和部分执行限制；不等于浏览器沙箱完整验证。 |
| `test_static_and_private_files` | `create_server(); Handler.do_GET() [via HTTP]` | 首页有root节点；main.py、私有配置、穿越路径、目录列表返回404。 | 避免通过网页读取私有文件。 |
| `test_state_roundtrip_cookie_and_conflict` | `Handler.do_GET()/do_POST()/identity(); Store [via HTTP]` | Cookie为HttpOnly；接口保存读回一致；旧版本409；另一Cookie为空状态。 | 验证接口、会话与存储连接后的真实行为。 |
| `test_bad_origin_and_input` | `Handler.do_POST(); LearningEngine.question()/grade() [indirect]` | 异源POST返回403；未知题号返回400。 | 检查两种非法请求；没有覆盖所有Host或JSON错误。 |
| `test_grading_and_ai_rule_fallback` | `Handler.do_POST(); LearningEngine.grade(); AI route [via HTTP]` | 正确答案接口返回correct；无AI配置时诊断接口返回规则反馈。 | 验证网页所调用接口与业务层连通。 |
| `test_team_authorization_and_rate_limit` | `Application.ai_enabled(); authorize_ai(); allow_call()` | 配置可用；正确/错误口令；前60次允许，第61次拒绝。 | 保护模型使用入口与额度；未测一小时后重置。 |
| `test_all_learning_prose_has_english_translation` | `data/*.json; web/src/en.json [data check]` | 检查指定学习文本在英文字典中有条目；代码、选项、测试等跳过。 | 发现漏译；不评价译文质量或界面切换。 |
| `test_english_prompt_preserves_original_evidence` | `analyze(language="en")` | 模拟请求含英文指令；学生理由和中文标准解析不变；英文响应可采用。 | 避免切换语言改写引用证据；不验证真实模型英语质量。 |

## 7. 这些测试足够了吗？

结论：足以作为核心逻辑的基础回归测试，不足以声称整个系统已充分验证或保证Excellent评分。选择这些测试的依据是：规则是否正确、数据是否丢失、AI失败能否继续用、私有数据是否暴露。没有测出错误不代表不存在错误，也未测量行/分支覆盖率。

### 7.1 优先补充的自动测试

1. 推荐：构造同概念未做、不同概念到期、同概念已做未到期等混合历史，断言整个顺序；测试unknown时到期优先、相同难度/到期的稳定排序、题库做完后的选择。
2. 复习：完整1/3/7/14/30天及阶段封顶；提示答对规则；错后重置；刚好到期前后；乱序历史。
3. AI：401/403/429、网络与TLS错误、非法JSON、截断输出、响应过长、字段类型/长度边界；答对/空理由不应请求模型。全部可用模拟完成，不必付费。
4. 数据/API：重复作答ID、时间戳、最大次数/长度边界、非法Host、畸形请求、数据库失败与限流窗口重置。

### 7.2 需要浏览器和真实人员的验证

- 完整流程：提交→补充理由→重新分析→推荐→保存→刷新；次数不增加，切语言不丢答案/草稿。
- Worker：实际Pyodide运行全部案例，运行/停止/超时、布尔值与数字比较、运行环境加载失败。
- 图表与导入：统计计算、时区、空记录、备份替换确认、冲突提示。
- 独立人工题库审查与真实AI质量评估；Windows/Linux成功日志；初学者可用性试用。

这些是具体缺口，不在本次文档调整中标成已补。历史浏览器测试记录与当前可重跑的自动测试必须分开。

## 8. README与SPEC分别负责什么

README面向使用者/接手成员：如何运行、功能和学习流程、模型配置、保存边界、常见错误、测试开发、部署打包、资源披露。

SPEC面向实现者/审查者：系统做什么、输入处理输出、验收条件、数据约束、失败行为、验证状态、本节逐项测试映射和缺口。某需求写在SPEC里或列出一个测试名，不等于该需求的全部行为已经测试。

---

# English Version: Specification and Test Rationale

## 1. Purpose and scope

Provide Python beginners with ordered lessons, cautious misconception clues and chapter coding practice. The Python 3.10+ standard-library server supplies a browser GUI and local assets. Scope: 3 chapters, 15 concepts, 30 questions and 6 coding tasks.

Excluded: teacher dashboard, arbitrary subjects, image recognition, account-based sync, general server-side execution of learner code and an autonomous AI agent. These are scope decisions, not claimed project-rubric requirements.

## 2. Inputs, processing, outputs and acceptance

| ID | Behaviour| Evidence|
|---|---|---|
| F01 | Question ID + valid option → fixed-key grading, explanation and concept clue| `test_all_question_answers`, `test_grading_and_ai_rule_fallback` |
| F02 | Reading + course attempts + prerequisites → locked/open/passed; hinted/free-practice answers do not independently pass| `test_entire_course_unlocks_in_order`, `test_hint_and_free_practice_do_not_pass_course` |
| F03 | Current question + diagnosis + history → same-chapter ranking, excluding current question; target unseen first; unknown avoids forced target| `test_recommendation_target_and_unknown` |
| F04 | Time + correctness + hints → ten-minute retry after error, stages 1/3/7/14/30 days after due independent success; early repeats do not advance| `test_schedule_early_repeat_not_advance` |
| F05 | Version-1 JSON backup → validate IDs/lengths/timestamps/course fields, regrade and restore standard explanations| `test_import_regrades_and_removes_untrusted_feedback`, `test_import_rejects_invalid_and_oversize` |
| F06 | Random cookie + state + revision → isolated SQLite space and 409 conflict on stale writes| `test_sqlite_persistence_isolation_and_conflict`, `test_state_roundtrip_cookie_and_conflict` |
| F07 | Wrong choice + non-empty reason + authorised AI request → constrained diagnosis and feedback, or rule fallback| `AITests`, `test_team_authorization_and_rate_limit` ; browser behaviour needs separate acceptance |
| F08 | ≤20,000-character source with allowed syntax/function → Worker case results; strict Boolean/numeric equality| `CodeSyntaxTests` ; browser behaviour needs separate acceptance |
| F09 | Attempt history → stats/table/accuracy for latest 14 dates with attempts in device timezone| Manual browser acceptance; not established by this automated run |
| F10 | Submitted question → next action in original submit area; edited reasoning updates same attempt| Manual browser acceptance; not established by this automated run |
| F11 | First visit → English; switch → EN/ZH preference with answers/drafts preserved; new AI requests carry language| `test_all_learning_prose_has_english_translation`, `test_english_prompt_preserves_original_evidence` ; browser behaviour needs separate acceptance |
| F12 | PiPo shortcut/keyword → learning-map/practice/coding navigation, no model call| `AssistantWidget.tsx` ; browser behaviour needs separate acceptance |
| N01 | Local service with external requests blocked → main learning/coding resources available| Manual browser acceptance; not established by this automated run ; browser behaviour needs separate acceptance |
| N02 | Cross-origin POST, invalid Host or private path → reject without exposing files| `test_bad_origin_and_input`, `test_static_and_private_files` |

## 3. Data and constraints

SQLite table: `learners(id, revision, state)`. The ID is a SHA-256 digest of a random cookie; names/student IDs are not collected. State contains reads, attempts, drafts and codeAttempts. Quiz grades are recalculated server-side. AI/browser coding results remain personal learning notes, not tamper-proof examination credentials.

Limits per space: 10,000 quiz attempts, 2,000 code attempts; request 10 MB; reason 1,000 characters; code 20,000. No automatic archiving. Import replaces the current space after confirmation, ignores unknown fields, rejects unknown questions/tasks, and does not merge devices.

## 4. Failure behaviour

- Missing built assets or port conflicts: visible startup error; no false success.
- Save failure/conflict: visible backup/retry guidance; do not proceed as if saved.
- AI unavailable/unauthorised/timed-out/invalid: visible cause and rule fallback.
- Runtime load exceeds 60 seconds or execution exceeds 4 seconds: terminate Worker, no passing record.
- Database error: generic error, without logging secrets or learner reasons.

## 5. Verification status and limitations

On 27 October 2026, 21 Python tests and TypeScript checking passed on macOS. The 39 reference cases run in Python do not establish a fresh 39-case browser run. Cross-platform CI is configured, not verified as executed. Final browser/Windows/Linux acceptance remains to be recorded.

All current wrong-option mappings point to the question’s own concept. Kimi may choose that candidate or unknown, not infer an unrestricted alternative. Evidence matching does not prove explanation truth. Human content review, independently labelled AI evaluation and learner-outcome studies are not complete.

The browser sandbox has no hard memory quota. Historical progress includes repeated/hinted answers. Course passing means performance on the current bank, not universal mastery. AI inspection and automated tests are not evidence of completed independent team review.

## 6. Existing 21 tests: targets, assertions and rationale

21 means 21 test_ methods, not 21 functions or input cases. Several methods loop over 30 questions or 39 coding cases with subTest. Counts: LearningTests 8, AITests 5, CodeSyntaxTests 1, HTTPTests 5, LanguageTests 2. Indirect execution of a helper does not prove assertions cover every branch.

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

## 7. Are these tests sufficient?

They provide a baseline regression suite for core logic, but do not establish complete system validation or guarantee an Excellent grade. Selection prioritises correct rules, data preservation, AI failure handling and private-file protection. No detected failure does not mean no defects, and line/branch coverage has not been measured.

### 7.1 Priority automated additions

1. Recommendation: mixed histories with unseen targets, due non-targets and seen not-yet-due targets; assert the full ordering, unknown-mode due priority, deterministic ties and exhausted-bank behaviour.
2. Scheduling: all 1/3/7/14/30-day stages and the cap, hinted success, error reset, exact due-time boundaries and out-of-order history.
3. AI: HTTP401/403/429, network/TLS errors, malformed JSON, truncated or oversized responses, field type/length boundaries, and no calls for correct answers or blank reasons. These can all use mocks without fees.
4. State/API: duplicate attempt IDs, timestamps, count/length limits, invalid Host, malformed requests, database failures and rate-window reset.

### 7.2 Browser and human validation

- Full flow: submit, revise reason, reanalyse, recommend, save and reload; no extra attempt and no lost answer/draft on language switch.
- Worker: actual Pyodide cases, run/stop/timeouts, Boolean versus numeric comparison and runtime loading failure.
- Charts/import: aggregation, timezones, empty history, replacement confirmation and conflict feedback.
- Independent content review and live AI-quality evaluation, Windows/Linux logs and beginner usability observations.

These are documented gaps, not additions completed by this documentation change. Historical browser records and currently repeatable automated tests must remain distinct.

## 8. Different purposes of README and SPEC

README serves users and maintainers: running, features and workflow, model configuration, storage limits, troubleshooting, tests/development, hosting/packaging and attribution.

SPEC serves implementers and reviewers: intended behaviour, input/process/output, acceptance, constraints, failure handling, verification status, detailed test mapping and gaps. Listing a requirement or a nearby test does not establish coverage of every part of the requirement.

