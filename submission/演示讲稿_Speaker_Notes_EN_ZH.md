# Group 8 — Video presentation · 14:30

## 1. PySteps: Python learning with PiPo

**0:00–0:45**

Introduce Group 8 and the learner problem. Say: “PySteps connects a wrong answer with an explanation, a related exercise and a coding activity. PiPo can inspect our learning records and select a next step.” State that the video includes live use of the application.

## 2. The learner problem

**0:45–1:45**

Use one learner throughout the demonstration: a beginner confuses > with >=, practises a comparison, then applies it in gate_status. Explain practical settings: an individual studying independently, a tutor working with a small group, and classroom practice. Each needs concrete feedback, a next task and saved records. These are use scenarios, not reported study outcomes.

## 3. Method: one continuous learning workflow

**1:45–3:15**

Explain the method before switching to live use. Python compares answers to the question bank; course completion requires reading and two independent unhinted answers. Recommendation stays in the current chapter and excludes the question just answered. Optional GLM-4.7 diagnosis analyses reasons; PiPo uses a separate repeated model/tool/observation loop. SQLite connects the activities through a learning state. Explain simple usability: a local launch command, a visible language switch, saved drafts and meaningful errors.

## 4. Live demonstration: mistake feedback

**3:15–5:30**

SWITCH TO THE RUNNING APPLICATION for this full segment; do not remain on this slide. Open Free practice and select boundary_1 (the first conditionals question). Enter “I thought greater than includes equality”, choose B: True, submit and show the fixed incorrect result. Point to the standard explanation and available hints. With the prechecked configured model, request analysis and show the quoted reason; explain that it does not change the answer key. Revise the reason to “I now distinguish > from >=; equality makes this expression false”, reanalyse and show that the attempt count has not increased. Briefly show the language switch and clear labels. Narrate the expected result only after it is visible.

## 5. Live demonstration: PiPo chooses practice

**5:30–8:00**

STAY IN THE APPLICATION. Open PiPo, enter the team access code without showing the provider key, and send the displayed goal. Wait for the real completed response. Expand the visible tool trace and explain the actual calls rather than reading a predetermined sequence. Confirm that the opened question is a valid inspected item in the relevant chapter and not boundary_1. Ask a short follow-up: “Explain why equality matters here without giving me the answer.” Point out tool decisions and the distinction between model-selected tools and Python-executed actions. If the account model cannot complete the turn, show the actual error and explain the observed state; arrange a functioning account before the final recording. Do not substitute simulated test output for this live segment.

## 6. Live demonstration: Python coding

**8:00–10:30**

STAY IN THE APPLICATION. Open Coding challenges → Spaceport Entry Pass. Explain the rule: energy below 20 returns the required recharge string; otherwise a badge permits entry. First run the starter pass body to show useful failing case results, then paste the prepared reference function from the recording guide. Run examples (first two cases), then Check answer (all seven cases for this task). Highlight the 19/20 boundary, all visible passing results and the saved submission. Briefly introduce a syntax error and show its location, then restore the correct source. Explain that the Worker executes browser Python, while the backend stores progress.

## 7. Live demonstration: returning to saved learning

**10:30–11:30**

STAY IN THE APPLICATION. Open Review mistakes and identify the comparison attempt and revised reason. Open Learning progress and show the coding completion/attempt counts. Refresh and confirm records remain in the same browser space. Export a JSON backup and explain that import is a confirmed replacement. These actions establish practical continuity for self-study and tutor-led sessions. Do not clear cookies or import a backup into a real learner space during the recording.

## 8. Engineering method and verification

**11:30–13:30**

Return to the slides. Show domain.py, agent.py and storage.py briefly using prepared windows. Explain functions/classes/collections (Lecture03), prompt contracts and SRS (Lecture04), model plus harness (Lecture05), and requirement/test matching (Lecture06). Show the current saved regression result dated 29 October 2026: 38 passed, including 10 PiPo methods. Explain that model responses in the automated tests are simulated; the live application segment is a separate demonstration. Show one requirement in SPEC and the named test. Describe the review record fields—reviewer, code location, finding, resolution and recheck—and show actual completed records if available. Identify CI as a configured multi-platform pipeline, not an invented successful run. State that AI assisted implementation, tests and documentation.

## 9. Conclusion: feedback connected to a next step

**13:30–14:30**

Summarise only what the audience has just seen: incorrect answer and explanation, revised reason, PiPo-selected practice, task cases and persistent records. State the practical contribution without asserting measured learning gains. Thank the audience. Finish by 14:30, leaving 30 seconds before the 15-minute cap for transitions or variable model latency.


# Group 8 — Classroom technical presentation · 4:45

## 1. Python architecture for learning decisions

**0:00–0:35**

Introduce the purpose in one sentence, then focus on architecture. Python owns learning decisions and persistence; React handles interaction; Pyodide runs student code in a browser Worker. Name the module boundaries. Lecture03: functions, classes and modularity.

## 2. Learning rules as testable Python functions

**0:35–1:35**

Use boundary_1 to illustrate deterministic grading: 5 > 5 is False. Explain how dictionaries store questions, sets express prerequisites and passed concepts, and a tuple key ranks candidates. A wrong answer schedules ten minutes; independent due-time success advances stage. Connect each rule to a named LearningTests test. This is technical explanation, not a long product tour.

## 3. PiPo model/tool/observation loop

**1:35–2:40**

Explain one concrete goal: “Review my mistake and open related practice.” The model receives tools, selects one, sees Python’s observation and chooses its next step. Highlight that this differs from keyword routing. Python rejects unknown tools, uninspected IDs and locked lessons. State the per-turn limits: up to five model requests, eight tool executions and one opening. Refer to the multi-round and rejected-action-recovery tests. A brief prepared tool trace may be shown within this timing, but do not spend the slot waiting for a network request.

## 4. Reliable records and controlled code execution

**2:40–3:40**

Explain the two-tab stale-revision example and why atomic writes avoid silent replacement. Distinguish backend learning Python from browser learner Python. A Worker can be terminated without executing student source in the web server. Explain diagnosis evidence checks and shared 60/hour allowance. Match the claims to SQLite/HTTP/AST/AI tests. These are implemented engineering choices, not claims of production security certification.

## 5. Requirements, tests and review evidence

**3:40–4:45**

Show the source of the test count and one SPEC-to-test mapping. Explain that automated model tests are simulated and live teaching quality is a separate evaluation. State how AI assisted implementation, tests and documentation. Describe code review evidence using reviewer, code location, finding, resolution and recheck; show actual records if completed. Conclude that the technical contribution is an inspectable Python learning engine plus a bounded tool-using Agent. Finish at 4:45, preserving 15 seconds within the five-minute slot for transitions. Answer instructor/classmate questions afterwards as directed.


---

# 第 8 组 — 视频汇报 · 14:30

## 1. PySteps：Python 学习与 PiPo

**0:00–0:45**

介绍第 8 组与学习者问题。开场：“PySteps 把错答连接到解释、相关练习和编程活动。PiPo 能读取学习记录并选择下一步。”说明本视频会现场操作应用。

## 2. 学习者面对的问题

**0:45–1:45**

贯穿同一名学习者：把 > 与 >= 混淆，完成比较运算练习，再应用到 gate_status。说明现实场景：个人自学、教师带小组、课堂练习。三者都需要具体解释、下一项任务与保存记录。这是应用场景，不是虚构用户实验结果。

## 3. 方法论：连续的学习流程

**1:45–3:15**

先解释方法，再切到实际操作。Python 对照题库判分；课程通过需要阅读和两道无提示独立正确作答。推荐保持同章并排除刚做的原题。GLM-4.7 诊断用于理由分析，PiPo 则使用独立的多轮模型—工具—观察循环。SQLite 用同一状态连接各项活动。指出易用设计：本地单命令启动、清晰语言切换、草稿保存和明确错误。

## 4. 现场演示：理解一次错答

**3:15–5:30**

本段切换到正在运行的应用，不停留在幻灯片。打开自由练习并选择 boundary_1（条件判断第一题）。写“我以为大于包含等于”，选择 B：True 后提交，展示固定错误判分、标准解析与提示。使用录制前已检查的真实模型请求分析，展示引用的学生理由，说明模型不更改答案。改成“我现在能区分 > 和 >=，相等时这条表达式为假”，重新分析，检查作答次数不增加。简短展示语言切换与明确标签。看到实际结果后再说明结果。

## 5. 现场演示：PiPo 选择练习

**5:30–8:00**

继续在应用内操作。打开 PiPo，输入团队口令，避免露出模型密钥，发送本页目标。等待真实完成响应，展开工具记录，按实际调用说明，不背诵预设工具顺序。检查打开的是已检查、相关章节的有效题目，且不是 boundary_1。追问“先不告诉我答案，解释这里为什么要检查等于”。说明模型选择工具、Python 执行动作的分工。若账户模型无法完成，应显示实际错误，并在最终录制前准备可正常工作的账户；不把模拟测试当作现场模型输出。

## 6. 现场演示：用 Python 应用概念

**8:00–10:30**

继续在应用内。进入趣味编程—星港通行证。讲解低于 20 需充能，否则检查通行证。先运行只有 pass 的函数，展示清楚的失败案例，再粘贴录制指南里的参考函数。运行示例检查前两例，再检查答案运行全部七例，突出 19/20 边界、通过结果及提交保存。短暂制造语法错误，展示错误行后恢复正确代码。说明浏览器 Worker 执行 Python，后端保存记录。

## 7. 现场演示：恢复保存的学习

**10:30–11:30**

继续在应用内。进入错题回顾，找到比较运算作答和修订理由；在学习进度展示编程完成与答题次数。刷新，确认同一浏览器空间记录仍在。导出 JSON，说明导入前需确认替换。用这些操作说明自学和教师带组的连续使用价值。录制时不清除真实用户 Cookie，也不向真实学习空间导入备份。

## 8. 工程方法与验证证据

**11:30–13:30**

回到幻灯片，短暂展示预先打开的 domain.py、agent.py、storage.py。对应 Lecture03 的函数、类与容器，Lecture04 的提示合同与 SRS，Lecture05 的模型与执行环境，Lecture06 的需求验证匹配。展示 2026 年 10 月 29 日回归记录：38 项通过，其中 10 项 PiPo。说明自动测试使用模拟模型，与刚才真实应用演示是不同证据。展示 SPEC 中一条需求及其测试名称。介绍审查人、位置、问题、处理、复核字段，有真实完成记录时展示。CI 说明为已配置的多平台流程，不虚构绿色运行。说明 AI 辅助实现、测试和文档。

## 9. 结论：把反馈连接到下一步

**13:30–14:30**

只总结观众已经看到的链条：错答解释、理由修订、PiPo 推荐、编程案例与保存记录。说明应用价值，不声称已测得成绩提升。感谢观众，14:30 前结束，距 15 分钟上限留 30 秒用于转场或模型等待。


# 第 8 组 — 课堂技术展示 · 4:45

## 1. 支持学习决策的 Python 架构

**0:00–0:35**

用一句话介绍用途，立即进入架构。Python 负责学习决策与保存；React 负责交互；Pyodide 在浏览器 Worker 运行学生代码。说明模块边界，对应 Lecture03 的函数、类与模块化。

## 2. 把学习规则写成可测试的 Python 函数

**0:35–1:35**

以 boundary_1 说明固定判分：5 > 5 为 False。字典保存题目，集合表达前置和通过状态，排序元组决定推荐。错答十分钟后复习，到期独立成功推进阶段。对应 LearningTests 的具体测试。此处讲技术，不展开长时间产品导览。

## 3. PiPo 的模型—工具—观察循环

**1:35–2:40**

使用具体目标“检查我的错题并打开相关练习”。模型拿到工具、选择工具、读取 Python 观察，再决定下一步，区别于关键词导航。Python 拒绝未知工具、未检查 ID 和锁课。说明每轮最多五次模型请求、八次工具、一次打开。对应多轮和拒绝后恢复测试。可短暂展示预先准备的真实工具记录，但不占用本段等待网络。

## 4. 可靠保存与受控代码执行

**2:40–3:40**

以两个页面旧版本保存说明原子写入如何避免静默覆盖。区分后端学习规则和浏览器学生代码，终止 Worker 不需把学生代码放到网页服务器执行。说明诊断引用检查及共享每小时六十次额度，对应 SQLite、HTTP、AST 和 AI 测试。这些是实现机制，不作生产安全认证主张。

## 5. 需求、测试与审查证据

**3:40–4:45**

展示测试计数来源及一条 SPEC 到测试的映射。说明自动模型测试使用模拟响应，真实教学质量另评估。交代 AI 辅助实现、测试与文档。代码审查用审查人、位置、问题、处理与复核作为证据，有实际完成记录时展示。结尾强调可检查的 Python 学习引擎和受限工具 Agent。4:45 结束，五分钟内留十五秒转场；按课堂安排回答师生问题。
