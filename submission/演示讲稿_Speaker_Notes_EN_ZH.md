# PySteps 双语展示讲稿 / Bilingual presentation script

课堂5分钟，最多5页。两种语言便于核对，现场选择一种语言讲述。

Classroom presentation: five minutes and five slides. The two languages support review. Speak in one language during delivery.

## Slide 1 / 第1页

### On-slide content / 页面内容

PySteps
Python concept diagnosis
and practice recommendation
Python 概念诊断与练习推荐
For beginners who need help understanding a wrong answer.
帮助初学者理解错因，再练习相应概念。
Conditions, loops, functions
条件判断、循环、函数与返回值
Group N / 组号待填写

### Speaker notes / 讲者备注

ENGLISH SPEAKER NOTES
0:00–0:40 (40 seconds). Introduce the learner: a Python beginner can select a wrong output without knowing which concept caused it. PySteps combines short concept lessons, answer checking and another exercise. Scope is limited to conditions, loops and functions. A wrong answer is evidence of a possible misconception, not proof of a stable learning deficit. State the real group number and introduce the team using the final member list.

中文讲稿
0:00–0:40（40秒）。介绍用户：Python初学者选错输出后，常常不知道错在哪个概念。PySteps通过简短概念导学、判分与后续练习帮助理解。范围限定为条件判断、循环、函数。一次错误只能提示可能的误区，不能证明学生稳定地不理解。填写真实组号后，按最终成员名单介绍团队。

EVIDENCE / 证据
/Users/crayon11/Downloads/EDU/Python/final-homework-3/data/concepts.json
/Users/crayon11/Downloads/EDU/Python/final-homework-3/data/questions.json
Mascot supplied by project / 形象来源：/Users/crayon11/Downloads/EDU/Python/final-homework-3/web/public/ai-character.png. Its visible watermark identifies AI generation.
/Users/crayon11/Downloads/EDU/Python/final_homework/INT6181 Group Project Requirements_v2.pdf

Submission reminders / 提交提醒
Group N and member names must be replaced by the real group details before submission. Use one spoken language for the 5-minute classroom presentation. The separate 15-minute video has not been created by this deck.
提交前填写实际组号与成员信息。课堂5分钟展示选择一种语言讲述。本PPT不代表已完成另需提交的15分钟视频。

## Slide 2 / 第2页

### On-slide content / 页面内容

Learning flow and features
学习流程与功能
02
01  Read a concept and follow the learning map
阅读概念导学，按知识地图学习
02  Answer a question and explain the reasoning
完成选择题，答错后仍可补充想法
03  Review feedback and try a targeted exercise
查看反馈，练习对应概念或到期复习题
04  Write Python in a chapter task and track progress
进入章节编程任务，查看错题与学习进度
3 chapters   15 concepts   30 questions   6 coding tasks
3章   15个概念   30道选择题   6个编程任务

### Speaker notes / 讲者备注

ENGLISH SPEAKER NOTES
0:40–1:35 (55 seconds). Explain the complete learner journey. The course map unlocks concepts through prerequisite progress. Independent correct answers to two different course questions are needed after reading. Free practice remains available and coding tasks do not require finishing the multiple-choice questions first. Show where a learner can edit the explanation after a wrong answer. Progress includes a chart and an equivalent data table. The interface supports English and Chinese. PiPo currently gives rule-based navigation, not an autonomous coding-agent service.

中文讲稿
0:40–1:35（55秒）。说明完整学习流程。知识地图按前置关系解锁，阅读后需在课程模式无提示独立答对两道不同题。自由练习随时可用，进入编程任务不要求先做完选择题。指出答错后仍可补充理由的位置。学习进度包含曲线及对应数据表。界面支持中英文。PiPo目前提供规则式学习导航，不是自主执行任务的编程智能体。

EVIDENCE / 证据
/Users/crayon11/Downloads/EDU/Python/final-homework-3/backend/domain.py (courses, summary)
/Users/crayon11/Downloads/EDU/Python/final-homework-3/web/src/App.tsx
/Users/crayon11/Downloads/EDU/Python/final-homework-3/web/src/AssistantWidget.tsx
/Users/crayon11/Downloads/EDU/Python/final-homework-3/data

Submission reminders / 提交提醒
Group N and member names must be replaced by the real group details before submission. Use one spoken language for the 5-minute classroom presentation. The separate 15-minute video has not been created by this deck.
提交前填写实际组号与成员信息。课堂5分钟展示选择一种语言讲述。本PPT不代表已完成另需提交的15分钟视频。

## Slide 3 / 第3页

### On-slide content / 页面内容

Python architecture and AI assistance
Python 架构与 AI 辅助
03
Python server / Python 服务端
Deterministic grading and SQLite records
标准答案判分，SQLite保存学习记录
Rules rank the question bank
规则对人工题库排序，排除当前原题
Browser Worker runs Python tasks
浏览器Worker运行受限制的Python任务
Kimi / Kimi 模型
Reasoning supplies extra evidence
分析文字理由，引用学生原话
Validated explanation or rule fallback
校验个性化讲解，失败时回退规则反馈
Live diagnostic quality: still pending
真实诊断质量：仍待独立人工评估
Priority: unseen target concept, due review, other unseen, remaining questions
推荐顺序：同概念未做题、到期题、其他未做题、剩余已做题

### Speaker notes / 讲者备注

ENGLISH SPEAKER NOTES
1:35–2:50 (75 seconds). Python implements grading, concept progression, scheduling, recommendation and server-side Kimi validation. JavaScript provides the browser UI, while Pyodide runs learner Python inside a Worker. The recommender filters to the current chapter and removes the current question. It prefers unseen questions matching the suspected concept, then due review, other unseen questions and remaining questions. Review intervals progress through 1, 3, 7, 14 and 30 days after qualifying independent answers. A wrong answer becomes due after 10 minutes. Kimi analyses the reason and returns the candidate concept or unknown. Evidence checks require a quote from the learner and preserve the approved answer and explanation. AI can affect the diagnosis used to rank questions but it does not generate the question bank. A successful HTTP request or billing entry does not demonstrate good diagnostic quality. Live quality evaluation remains outstanding.

中文讲稿
1:35–2:50（75秒）。Python实现判分、概念解锁、复习安排、推荐及服务端Kimi结果校验。JavaScript负责网页界面，Pyodide在Worker中运行学习者代码。推荐先限定当前章节，排除当前题，再优先同概念未做题、到期复习题、其他未做题和剩余已做题。符合条件的独立答对使复习间隔逐步达到1、3、7、14、30天，答错10分钟后到期。Kimi分析理由，返回候选概念或unknown。程序检查引用是否来自学生原话，并保留审核答案与解析。AI诊断可以影响推荐排序，但不会生成题库。HTTP成功或账单扣费都不能证明诊断质量，真实质量评估仍待完成。

EVIDENCE / 证据
/Users/crayon11/Downloads/EDU/Python/final-homework-3/main.py
/Users/crayon11/Downloads/EDU/Python/final-homework-3/backend/domain.py (schedule, recommend)
/Users/crayon11/Downloads/EDU/Python/final-homework-3/backend/ai.py (analyze, validate)
/Users/crayon11/Downloads/EDU/Python/final-homework-3/backend/storage.py
/Users/crayon11/Downloads/EDU/Python/final-homework-3/web/public/python-worker.mjs

Submission reminders / 提交提醒
Group N and member names must be replaced by the real group details before submission. Use one spoken language for the 5-minute classroom presentation. The separate 15-minute video has not been created by this deck.
提交前填写实际组号与成员信息。课堂5分钟展示选择一种语言讲述。本PPT不代表已完成另需提交的15分钟视频。

## Slide 4 / 第4页

### On-slide content / 页面内容

Engineering evidence and open checks
工程证据与待完成验证
04
Available evidence / 已有证据
21 automated tests passed
21项自动测试通过（2026-10-27）
Specification, modular code and README
功能规格、模块化代码与运行说明
39 coding cases in reference fixtures
参考解包含39个编程测试案例
Team work still needed / 团队仍需完成
Independent review with recorded findings
独立代码审查，记录问题与修复复核
Human labels and live AI comparison
人工复核标签，比较规则与真实AI结果
Windows and Linux execution evidence
Windows与Linux实际运行证据
Mock AI tests verify behavior. They do not establish diagnostic accuracy.
模拟AI测试验证程序行为，不能证明模型诊断准确率。

### Speaker notes / 讲者备注

ENGLISH SPEAKER NOTES
2:50–3:55 (65 seconds). State the current evidence precisely: all 21 unittest tests passed on 27 October 2026 without paid API calls. Tests cover grading, course flow, scheduling, persistence, HTTP behavior, AI validation and fallback, language handling, and reference coding answers. The 39 coding cases are reference fixtures, not a new cross-browser execution claim. The project includes a specification and documentation. The CI configuration contains a platform matrix, but configuration alone is not proof of successful runs. An independent teammate must review code they did not write, log findings, receive fixes and verify them. For AI evaluation, compare the rule baseline with actual model output on held-out examples with separately reviewed human labels. Keep failures and unknown cases in the report. The mock tests cannot prove better student learning.

中文讲稿
2:50–3:55（65秒）。准确说明证据：2026年10月27日，21项unittest测试全部通过，没有付费API调用。覆盖判分、课程流程、复习安排、保存、HTTP行为、AI校验与回退、语言处理及编程参考解。39个编程案例是参考解测试证据，不代表今天重新完成了跨浏览器执行验证。项目已有功能规格和文档。CI虽然配置了系统矩阵，但配置存在不等于已运行通过。独立组员应审查非本人编写的代码，记录发现，修复后再复核。AI评估需使用与调试样例分开的案例，并独立复核人工标签，比较规则与真实模型输出，保留失败与不确定案例。模拟测试不能证明真实学习效果提高。

EVIDENCE / 证据
/Users/crayon11/Downloads/EDU/Python/final-homework-3/tests
/Users/crayon11/Downloads/EDU/Python/final-homework-3/SPEC.md
/Users/crayon11/Downloads/EDU/Python/final-homework-3/README.md
/Users/crayon11/Downloads/EDU/Python/final-homework-3/.github/workflows
/Users/crayon11/Downloads/EDU/Python/final-homework-3/scripts/evaluate_ai.py
Current test execution confirmed by the project audit on 2026-10-27.
Lecture06 Testing and Debugging I.pptx: testing and debugging evidence.

Submission reminders / 提交提醒
Group N and member names must be replaced by the real group details before submission. Use one spoken language for the 5-minute classroom presentation. The separate 15-minute video has not been created by this deck.
提交前填写实际组号与成员信息。课堂5分钟展示选择一种语言讲述。本PPT不代表已完成另需提交的15分钟视频。

## Slide 5 / 第5页

### On-slide content / 页面内容

Demonstration and limitations
演示路径与能力边界
05
Demo 1  Read a concept, answer incorrectly, add a reason
演示1：阅读概念，答错后补充想法
Demo 2  Compare rule feedback and an AI analysis result
演示2：对照规则反馈与一次AI分析结果
Demo 3  Open a chapter coding task and inspect progress
演示3：进入章节编程任务，查看进度与保存记录
Current limits / 当前限制
Small question bank repeats. No account-based sync. Learning gains remain unproven.
小题库仍会重复，没有账号跨设备同步，尚未证明真实学习成绩提高。

### Speaker notes / 讲者备注

ENGLISH SPEAKER NOTES
3:55–5:00 (65 seconds). Use one rehearsed short path. Start with python3 main.py --port 8001 --open on macOS or py main.py --port 8001 --open on Windows, using the actual available port. Open the learning map, read a concept and submit a wrong answer. Add a reason after submission, then show the analysis control and feedback source. For a live API request, confirm the service configuration and team access code ahead of time and expect a charge. If a prepared mock is used, label it clearly as simulated. Do not present rule fallback as successful AI. Open one chapter coding task, run a known sample and show the progress view. Explain limitations: question repetition, manual backup for moving between devices, incomplete real-user evidence, and no proven learning gain. Finish by inviting questions about the evaluation design. This deck is limited to five slides for classroom delivery. The separate fifteen-minute video should cover the full system, source code and testing evidence without extending this five-minute classroom slot.

中文讲稿
3:55–5:00（65秒）。提前排练一条简短路径。macOS用python3 main.py --port 8001 --open，Windows用py main.py --port 8001 --open，并选择实际可用端口。进入知识地图，阅读概念，提交错误答案。提交后补充理由，展示分析入口和反馈来源。若现场调用API，提前确认服务端配置与团队口令，调用会收费；若使用预录或模拟结果，必须明确标注。不要把规则回退说成AI成功。进入一个章节编程任务，运行已准备的示例，再展示进度。说明题库会重复、换设备依赖手动备份、真实用户证据不足、学习收益未被证明。最后请老师对评估方案提出意见。课堂展示限5页、5分钟，另外15分钟的视频应完整展示功能、源码与测试，不应延长课堂时长。

EVIDENCE / 证据
/Users/crayon11/Downloads/EDU/Python/final-homework-3/main.py
/Users/crayon11/Downloads/EDU/Python/final-homework-3/web/src/App.tsx
/Users/crayon11/Downloads/EDU/Python/final-homework-3/README.md
/Users/crayon11/Downloads/EDU/Python/final_homework/INT6181 Group Project Requirements_v2.pdf

Submission reminders / 提交提醒
Group N and member names must be replaced by the real group details before submission. Use one spoken language for the 5-minute classroom presentation. The separate 15-minute video has not been created by this deck.
提交前填写实际组号与成员信息。课堂5分钟展示选择一种语言讲述。本PPT不代表已完成另需提交的15分钟视频。
