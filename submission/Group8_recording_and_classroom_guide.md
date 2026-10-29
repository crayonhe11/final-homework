# Group 8 — Presentation delivery guide

## English

### Two separate assessed outputs

| Output | Material | Target duration | Delivery |
|---|---|---:|---|
| Group video | 9-slide video support deck + live application | 14:30, with 0:30 reserve below 15:00 | Record the presenters and representative live application use; submit the actual video. |
| Classroom technical showcase | 5 selected technical slides | 4:45, with 0:15 reserve below 5:00 | Explain the implementation techniques and answer instructor/classmate questions. |

The video deck is a recording aid. A PPTX file does not replace the required video submission. Use one language version for a timed presentation; do not read both languages in the same slot.

### Video structure and timing

| Time | Segment | What the audience sees |
|---|---|---|
| 0:00–0:45 | Introduction | Group 8, application purpose and target learners. |
| 0:45–1:45 | Problem | A beginner confuses strict comparison and equality, needs the next activity and retained records. |
| 1:45–3:15 | Methodology | Concept reading, fixed grading, reasoning, ranking, Agent tools, coding and shared state. |
| 3:15–5:30 | Live demonstration: feedback | Submit boundary_1 incorrectly, inspect feedback, revise a reason and analyse the same attempt. |
| 5:30–8:00 | Live demonstration: PiPo | Give a natural goal, expand real tools and verify the actual opened question. |
| 8:00–10:30 | Live demonstration: coding | Run starter code, use the prepared function, execute samples and all seven task cases, show errors/history. |
| 10:30–11:30 | Live demonstration: saved use | Inspect records, refresh and export a backup. |
| 11:30–13:30 | Engineering evidence | Python modules, SRS/test mapping, current result and review criteria. |
| 13:30–14:30 | Conclusion | Practical use, ease of use and the demonstrated contribution. |

The four application segments total **8:15**. Keep the screen recording on the real application during those segments. Show the pointer actions, input, outputs and resulting state rather than replacing them with slide screenshots.

### Representative live scenario

Use one continuous learner story: a comparison mistake leads to related practice, then to a coding task that uses the same boundary.

1. Launch from the project directory with `python main.py --open`. Use a dedicated demonstration browser space and the chosen language.
2. In Free practice, select `boundary_1`: `x = 5; print(x > 5)`. Choose **B: True**, enter “I thought greater than includes equality”, and submit. Show that the fixed answer is **A: False**.
3. Show the standard explanation/hints. With a working configured GLM-4.7 model, request reasoning analysis and point to the actual quoted reason.
4. Revise the reason and reanalyse. Check the same attempt identity/count in the displayed history.
5. Ask PiPo: “Review my latest comparison mistake and open related practice.” Expand the actual trace. Explain the calls that occurred and check that the opened question is a valid related item, not the original question. Ask a brief concept follow-up.
6. Open Coding challenges → Spaceport Entry Pass. Run the starter `pass` function to show an interpretable failure. Insert the prepared source below, run two examples and then all **seven** cases for this task. Show the 19/20 boundary and the saved submission. Demonstrate one syntax error and restore the source.
7. Open mistake/progress history, refresh and verify persistence. Export a JSON backup. Explain explicit backup transfer and the confirmed-replacement import behaviour without importing into a real learner's space.

Prepared demonstration function:

```python
def gate_status(energy, has_badge):
    if energy < 20:
        return "充能"
    elif has_badge:
        return "放行"
    return "等待"
```

The strings are exact task outputs and remain unchanged in the English interface.

### Recording preparation

- Check that the selected model is available and supports function tool calls, the team code is accepted, and a complete PiPo turn works before recording. Keep the provider key and private config out of the capture.
- Prepare the code and source windows. Use the same application space throughout the learner story.
- Record at a readable resolution with audible speech; rehearse the complete capture and watch the exported file. Check duration, legible UI, the real outputs and the final conclusion.
- Reserve the 30 seconds for transitions/model latency. If a real model turn fails, record the actual state and correct the setup for the final take. A mock test is labelled test evidence, not substituted as a live model demonstration.

### Classroom technical selection

| Slide | Time | Key technical point |
|---|---|---|
| 1 | 0:00–0:35 | Python module architecture and browser/server responsibilities. |
| 2 | 0:35–1:35 | Dictionaries, sets, ranking tuples and testable learning rules. |
| 3 | 1:35–2:40 | Model/tool/observation loop, validated actions and bounded execution. |
| 4 | 2:40–3:40 | SQLite transactions/revisions and AST/Worker execution boundaries. |
| 5 | 3:40–4:45 | SRS-to-test evidence, 38-method inventory, AI engineering use and review records. |

There is no extra cover or Q&A slide: the total is **five**, including the first slide. The classroom deck is a selected technical account, not the nine-slide video deck. Keep answer preparation outside the slide count.

### Questions to prepare

| Question | Concise answer supported by the implementation |
|---|---|
| Why is this a Python project? | Python owns grading, course rules, ranking, review, SQLite, HTTP and model/tool execution. React supplies interaction; Pyodide runs learner Python in the browser. |
| How is PiPo an Agent rather than keyword routing? | The model chooses a tool, receives its real Python observation and chooses again. The loop and action validation are implemented in agent.py. |
| Can the model change scores? | Fixed question keys determine quiz grading. PiPo tools inspect learning information and prepare a validated opening; they have no grade-writing tool. |
| What do the tests establish? | The current suite has 38 passing methods: 32 project methods, including 10 Agent methods, plus 6 independent examples. Simulated model tests establish program control flow, not live diagnostic accuracy. |
| Why is code run in a Worker? | Learner code runs in a disposable browser runtime with AST restrictions and a timeout; it is not executed on the Python web server. |
| How are conflicting saves handled? | SQLite uses a transaction and compares revisions. A stale save receives 409 rather than silently replacing the newer state. |
| What makes it useful and easy to use? | The demonstrated learner can inspect a mistake, reach a concrete practice/coding activity, resume records, switch language and launch locally with one command. |
| How was AI used in engineering? | AI assisted implementation, tests, SRS, documentation and code inspection. Show a specific adopted output and its verification; use actual records for human code review. |

### Submission and participation

- Submit the **actual video, no longer than 15 minutes**, in the Moodle group video entry.
- Submit the selected classroom PowerPoint as `group8_presentation.pptx`; it contains at most five slides.
- Rehearse the classroom route within five minutes and prepare answers for the instructor and classmates.
- **Every member must complete the required peer assessment.** Record each member's completion through the course process; one person's group submission does not replace individual participation.

---

## 中文

### 两项分别评估的展示

| 交付 | 材料 | 目标时长 | 形式 |
|---|---|---:|---|
| 小组视频 | 9 页视频配套稿与真实应用操作 | 14:30，距 15:00 留 30 秒 | 录制讲解和代表性现场操作，提交实际视频。 |
| 课堂技术展示 | 5 页精选技术幻灯片 | 4:45，距 5:00 留 15 秒 | 解释实现技术，回答教师和同学提问。 |

视频 PPT 是录制辅助，不能代替必须提交的视频。每次计时展示选择一种语言，不在同一时段重复朗读中英文。

### 视频结构与计时

| 时段 | 环节 | 观众应看到的内容 |
|---|---|---|
| 0:00–0:45 | 引言 | 第 8 组、应用目的与目标用户。 |
| 0:45–1:45 | 问题描述 | 初学者混淆严格大于与等于，需要下一步和保留记录。 |
| 1:45–3:15 | 方法论 | 概念、固定判分、理由、推荐、Agent 工具、编程和共用状态。 |
| 3:15–5:30 | 现场演示：反馈 | 错答 boundary_1，检查反馈，修订理由并分析同一次作答。 |
| 5:30–8:00 | 现场演示：PiPo | 输入自然语言目标，展开真实工具，核对实际打开题目。 |
| 8:00–10:30 | 现场演示：编程 | 运行外壳、使用准备代码、检查示例和全部七例、展示错误与历史。 |
| 10:30–11:30 | 现场演示：持续使用 | 查看记录，刷新恢复，导出备份。 |
| 11:30–13:30 | 工程证据 | Python 模块、规格测试映射、本次结果及审查标准。 |
| 13:30–14:30 | 结论 | 实用性、易用性与已经展示的贡献。 |

四段真实应用操作合计 **8 分 15 秒**。这些时段录制实际界面、鼠标操作、输入、输出和最终状态，不用静态截图替代操作。

### 代表性现场场景

贯穿同一学习故事：比较边界答错，进入相关练习，再在使用同一边界的编程任务中应用。

1. 在项目目录运行 `python main.py --open`，使用专门的演示浏览器空间，并选择展示语言。
2. 自由练习选择 `boundary_1`：`x = 5; print(x > 5)`。选 **B：True**，写“我以为大于包含等于”并提交，展示固定答案为 **A：False**。
3. 展示标准解析与提示。使用已能正常工作的 GLM-4.7 请求分析，指出真实引用的学生理由。
4. 修订理由后重新分析，在历史中核对作答标识/次数没有增加。
5. 请 PiPo “检查我最近的比较运算错题，打开相关练习”。展开真实工具记录，按实际调用讲解，检查新题有效且相关，不是原题，再做简短概念追问。
6. 打开趣味编程—星港通行证。先运行只有 `pass` 的外壳展示可理解的失败，再粘贴本指南提供的函数，运行前两例及本任务全部 **七例**，突出 19/20 边界和保存的提交。演示一次语法错误后恢复代码。
7. 查看错题与进度，刷新核对保留，导出 JSON。说明备份迁移与确认替换导入，不向真实学习空间导入演示数据。

准备的演示函数：

```python
def gate_status(energy, has_badge):
    if energy < 20:
        return "充能"
    elif has_badge:
        return "放行"
    return "等待"
```

字符串是任务要求的精确输出，英文界面也保留原文。

### 录制前准备

- 确认所选模型可用并支持工具调用，团队口令有效，完整 PiPo 一轮正常；录屏不显示模型密钥和私有配置。
- 准备代码及源码窗口，全程使用同一演示学习空间。
- 以可读分辨率和清晰声音录制；完整排练并观看导出视频，检查时长、界面可读性、真实输出及结论。
- 30 秒用于转场与模型延迟。真实调用失败时显示真实状态，最终录制前修正配置。模拟测试作为已标明的测试证据，不替代现场模型演示。

### 课堂精选技术内容

| 页 | 时段 | 技术重点 |
|---|---|---|
| 1 | 0:00–0:35 | Python 模块架构及浏览器/服务端职责。 |
| 2 | 0:35–1:35 | 字典、集合、排序元组及可测试学习规则。 |
| 3 | 1:35–2:40 | 模型—工具—观察循环、动作校验及执行次数。 |
| 4 | 2:40–3:40 | SQLite 事务/版本与 AST/Worker 执行边界。 |
| 5 | 3:40–4:45 | 规格测试映射、38 项清单、AI 工程应用与审查记录。 |

不额外加封面或答问页，含第一页共 **五页**。课堂展示使用精选技术稿，不使用九页视频稿。答问准备放在讲稿中，不增加幻灯片。

### 答问准备

| 问题 | 与实现一致的简洁回答 |
|---|---|
| 为什么算 Python 项目？ | Python 负责判分、课程、推荐、复习、SQLite、HTTP、模型与工具执行；React 负责界面，Pyodide 在浏览器运行学生 Python。 |
| PiPo 为什么是 Agent？ | 模型选择工具、读取 Python 返回的真实观察后继续决策，agent.py 实现循环和动作校验，不是关键词跳转。 |
| 模型能改分吗？ | 选择题固定答案判分，PiPo 读取学习信息并准备有效打开动作，没有写成绩工具。 |
| 测试证明什么？ | 当前 38 项通过，其中 32 项项目测试、含 10 项 Agent，另有 6 项独立示例。模拟响应验证控制流程，不证明真实模型诊断准确率。 |
| 为什么在 Worker 运行代码？ | 学生代码在可销毁的浏览器运行时中执行，受 AST 与超时控制，不在 Python 网页服务端运行。 |
| 保存冲突怎么处理？ | SQLite 事务比较版本，旧版本返回 409，不静默覆盖新状态。 |
| 实用、易用体现在哪里？ | 已演示错因理解、具体练习/编程、保存恢复、语言切换和单命令本地启动。 |
| 如何使用 AI 改进工程？ | AI 辅助实现、测试、规格、文档和检查，用一个实际采用并验证的输出举例，人工审查用真实完成记录支撑。 |

### 提交与参与

- Moodle 小组视频入口提交**不超过 15 分钟的实际视频**。
- 课堂 PowerPoint 正式命名为 `group8_presentation.pptx`，最多五页。
- 五分钟内排练课堂技术路线，准备回答教师和同学提问。
- **每位组员必须参与同伴互评。** 按课程流程分别确认完成，一名组员的小组提交不能替代个人互评参与。
