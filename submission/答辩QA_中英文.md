> PiPo 功能更新：下文关于“预设关键词导航 / 非 Agent”的描述是旧版状态，已被受限模型工具循环替代。当前实现、演示路径与验证边界以 [PiPo Agent](PiPo_Agent.md) 为准。 / PiPo's old navigation-only descriptions below are superseded by the bounded tool-loop implementation documented in PiPo_Agent.md.

# 中文版：PySteps 答辩 Q&A

依据当前final-homework-3与已核对的课程要求整理，更新日期2026-10-28。以下是可能问题，不是老师的确定题目。建议回答为可练习草稿；将“我们/我”替换为真实贡献，未完成事项不得改成已完成。优先练习第4、6、9、11、13、14、19题。

## 1. 你们解决了什么问题？

分类：项目定位

建议回答：Python 初学者答错后，往往只能看到标准答案，不知道应回到哪个概念继续练习。PySteps 把概念导学、答题、理由反馈、针对性练习和章节编程放进同一个流程，帮助学习者找到下一步。我们聚焦条件判断、循环、函数与返回值三个主题。

追问准备与边界：说“帮助定位下一步”，不要说已经证明提升真实学习成绩。

## 2. 和普通题库、Exercism 有什么不同？有什么原创性？

分类：项目定位

建议回答：我们的重点是答错后的学习过程：学生可以补充理由，再看概念线索并进入同章练习或编程。知识地图组织学习顺序，编程任务嵌入章节。Exercism 是设计参考，我们没有证据声称首创这些机制；原创性应体现在本项目的具体整合、题目设计和团队实际改进，并如实引用第三方资源。

追问准备与边界：不要说所有组件自研，也不要未经比较声称优于 Exercism。

## 3. 为什么只做三个主题、30道题？题库是不是太小？

分类：项目定位

建议回答：这是为课程项目控制范围，先把学习、诊断、推荐、保存和编程流程做完整。当前15个概念各两道题，确实限制了推荐多样性，也可能让学生记住答案。它适合作为原型验证，不足以证明全面掌握。下一步应优先补人工审核过的同概念变式题，而不是直接放入未经验证的AI生成题。

追问准备与边界：承认规模限制，解释取舍；不把所有重复都说成有意的间隔复习。

## 4. 这是网页，为什么算Python项目？main.py做了什么？

分类：Python与架构

建议回答：main.py解析启动参数并启动Python服务。实际业务在Python后端：判分、课程解锁、推荐、复习、状态校验、SQLite和GLM-4.7结果处理。React负责网页交互；浏览器里的Pyodide运行受限制的练习代码。Python并非仅用来打开一个网页。

追问准备与边界：现场打开main.py及backend/domain.py说明调用关系；课程是否接受该GUI形式以老师确认的口径为准。

## 5. 你们用到了哪些课堂编程知识？为什么要拆模块？

分类：Python与架构

建议回答：题库用列表，按ID查找用字典，前置关系和完成状态用集合；推荐用sorted和排序键；业务、存储与接口使用函数、类和模块。LearningEngine管规则，Store管保存，server管HTTP，ai管模型接入。分开后规则可以不启动网页直接测试，修改界面也不需要改判分逻辑。

追问准备与边界：准备解释一个自己真正理解的函数，不要只背技术名词。

## 6. 推荐练习使用什么算法？为什么没有机器学习？

分类：推荐与诊断

建议回答：当前采用确定性规则排序：先限定同章并排除当前题，再优先同概念未做题、到期复习题、其他未做题，最后已做未到期题；还结合到期时间、概念、难度和题号处理排序。unknown时不强行针对某个误区，优先到期题。题库和用户数据较少，规则更容易解释、测试和复现，目前没有训练推荐模型。

追问准备与边界：代码位置：LearningEngine.recommend()。注意普通继续练习与反馈中的针对性推荐传入的概念来源有所不同。

## 7. 答错就能确定学生不懂某个概念吗？

分类：推荐与诊断

建议回答：不能。错误可能来自手误、猜测或不同的理解问题，因此我们只显示可能的概念线索。当前映射较粗：错误选项都指向各自题目的概念。GLM-4.7根据理由支持这个候选或返回unknown，不能从整个知识体系任意另选误区。后续题目能提供更多表现证据，但系统尚未形成统计意义上的诊断证明。

追问准备与边界：可以举“选输出5，可能是不懂比较返回布尔值，不一定是不懂边界”的反例。

## 8. 复习时间如何决定？是否使用成熟的记忆算法？

分类：推荐与诊断

建议回答：当前是简化的固定间隔规则：答错后十分钟；使用提示答对不提升阶段，并在一天内安排复习；到期后独立答对按1、3、7、14、30天推进。提前重复不推进。这是易于解释和测试的设计选择，没有在本项目中验证这些间隔最优，也没有实现个体化记忆参数。

追问准备与边界：不要称为完整实现SM-2或其他未实现算法；代码为schedule()。

## 9. AI到底有什么用？不用AI也能运行吗？

分类：AI作用

建议回答：可以不用AI。标准判分、固定解析、推荐、保存和编程都可运行。GLM-4.7的额外作用是分析学生文字理由，引用原话，判断是否支持候选误区，并组织个性化解释。信息不足可以返回unknown。这种能力是否比规则更好，需要同一批独立标注案例的实际比较，目前不能直接宣布更准确。

追问准备与边界：展示“AI辅助诊断”和“规则反馈”的区别，避免把固定文案当成模型输出。

## 10. 你们如何防止AI胡说或改变答案？

分类：AI作用

建议回答：答案始终由题库和Python逻辑确定。模型只能返回候选概念或unknown，理由引文须来自学生原话，个性化讲解还核对答案标识及标准解析引文。校验失败就拒绝相应结果或回退标准反馈。但引文正确并不能保证整段解释正确，所以还需要人工质量评估，不能声称消除了幻觉。

追问准备与边界：代码：validate_output()与analyze()。提示学生文本不可信只是防护一部分，不是安全证明。

## 11. 你们的AI效果验证了吗？准备如何验证？

分类：AI作用

建议回答：目前自动测试使用模拟响应，验证接入和回退，不验证真实诊断准确率。已有12条模拟理由，但标签尚未独立复核。计划先独立标注并保留未用于调提示词的数据，再比较规则和AI的一致率、unknown识别、事实正确性与针对性，同时单列有效模型输出和回退。不能从这些模拟案例推导真实成绩提升。

追问准备与边界：若尚未运行，就说未运行；不要临场给出虚构百分比。

## 12. PiPo是不是AI Agent？你们怎么使用了生成式AI？

分类：AI作用

建议回答：PiPo目前是预设文案和关键词导航，没有自主规划或工具调用循环。GLM-4.7是受限的单次诊断服务。开发过程中Codex协助实现、测试、文档和检查，这与应用运行时使用GLM-4.7是两件事。我们应展示真实采用、修改或拒绝AI建议的记录，并由成员解释最终代码。

追问准备与边界：不要把同一AI的自查说成已经完成团队成员独立审查。

## 13. 21项测试究竟测了什么？为什么选择这些？

分类：测试与质量

建议回答：它们优先覆盖会影响正确性或造成损失的路径：判分、通关、推荐、复习、导入、数据库隔离与冲突、AI结果校验与回退、部分执行限制、HTTP和双语数据。21是测试方法数，内部还循环核对30题输出和39个参考解案例。SPEC第6节逐项说明目标、断言和原因。

追问准备与边界：可以现场运行：python3 -m unittest discover -s tests -t . -v。测试使用模拟AI，不收费。

## 14. 测试全通过是否证明项目没有问题？还缺什么？

分类：测试与质量

建议回答：不能。现有测试是基础回归保障，未测量覆盖率。推荐还缺混合历史的完整排序，复习缺全部阶段，AI缺更多错误分支；浏览器补理由、语言切换、Worker超时、图表和导入流程也要单独验收。真实AI质量、人工题库审查和可用性不能由单元测试代替。

追问准备与边界：说出一个具体未覆盖分支，比泛称“测试很全面”更可信。

## 15. 你们遇到过什么真实问题？如何定位和修复？

分类：测试与质量

建议回答：一个有记录的问题是VS Code报测试目录不可导入。修复过程中先用从项目根目录发现测试的命令复现，发现tests缺少__init__.py。补包标记并固定工作目录后，又暴露参考答案模块的导入路径问题；改为tests.reference_solutions后，两种测试发现方式均通过21项。这个例子说明能在一种命令下运行，不保证编辑器使用的导入方式也正确。

追问准备与边界：这是项目中由AI协助完成的修复；若成员没有亲自操作，不应把上述“我”当作个人贡献。可改说“项目记录中”。

## 16. CI/CD做到了哪一步？

分类：测试与质量

建议回答：仓库有GitHub Actions配置：推送或PR触发Windows、macOS、Linux与Python3.10/3.13的测试矩阵，以及网页检查构建。但目前尚未取得真实远端成功记录；打包与网页构建仍是独立任务，没有连接本次构建产物、上传产物或部署服务器。所以准确说法是配置了CI，远端执行和CD未完成。

追问准备与边界：本机21项通过不等于GitHub六种环境通过；Dockerfile也不等于部署完成。

## 17. 学习记录怎么保存？能跨设备吗？

分类：数据与安全

建议回答：数据在SQLite中，随机浏览器Cookie对应学习空间。版本号防止旧标签页覆盖新记录。相同浏览器与Cookie保留时可继续学习；当前没有账号自动同步。跨设备通过导出JSON再导入，导入替换当前空间并重新判分。不能把备份转移说成自动同步。

追问准备与边界：清Cookie、更换浏览器或主机名可能进入新空间；先提醒用户备份。

## 18. 学生代码会危害服务器吗？密钥如何保护？

分类：数据与安全

建议回答：学生代码在浏览器Worker运行，不在服务器执行；有语法限制和执行超时，但没有硬内存配额，不能称为绝对安全沙箱。API密钥在服务端配置或环境变量，打包排除私有配置；网页使用团队口令。来源检查、长度限制和每小时60次请求限制降低风险，但限流不是账户账单上限。

追问准备与边界：不要在展示中打开真实配置；不要为证明AI可用而反复请求收费接口。

## 19. 你本人做了什么？是否读懂AI写的代码？审查完成了吗？

分类：个人贡献与审查

建议回答：这一题必须按真实情况填写：我负责[具体模块/内容]，做了[具体决定或修改]，证据是[文件/提交/测试/审查记录]；AI协助了[部分]，我用[方法]验证。若独立成员审查未完成，就明确说明已有AI检查，但成员审查记录仍待完成，不能把模板当结果。

追问准备与边界：每人准备一段能解释输入、输出、分支和异常的代码；不替其他成员编造贡献。

## 20. 如果再给你们两周，最先改什么？

分类：改进与总结

建议回答：先补影响可靠性的证据和内容：人工复核误区标签、增加同概念变式题；补推荐/复习/模型异常测试与完整浏览器流程；做小规模独立标注的AI比较；获得跨平台CI结果。是否增加账号同步或更多功能，要看真实用户需求，而不是先扩充复杂度。

追问准备与边界：将改进和当前具体缺口对应，避免承诺泛化到所有学科或自动生成全部题库。

## 现场代码演示准备

准备打开：`main.py`、`backend/domain.py`的`recommend()/schedule()`、`backend/ai.py`的`validate_output()/analyze()`、`backend/storage.py`的`save()`、`tests/test_core.py`。先用一句话说函数目的，再说明输入、关键分支、输出，最后指出对应测试与一个未覆盖情况。不要整页逐行朗读。

## 不知道答案时如何回应

“这部分目前没有验证，我不能给出准确结论。现有实现是……；要确认这个问题，我们需要补……测试/数据。”

建议每题先回答20–40秒，有追问再展开。不要现场猜测AI准确率、性能、覆盖率或其他成员贡献。

---

# English Version: PySteps Q&A Preparation

Prepared for the current final-homework-3 and the reviewed course requirements, dated 28 October 2026. These are likely questions, not confirmed instructor questions. Answers are rehearsal drafts: use genuine contributions and keep incomplete work labelled incomplete. Prioritise questions 4, 6, 9, 11, 13, 14 and 19.

## 1. What problem does your project solve?

Category: Project purpose

Suggested answer: Python beginners often see the correct answer without knowing which concept to practise next. PySteps connects short lessons, questions, feedback on reasoning, targeted practice and chapter coding. We focus on conditionals, loops, and functions and return values.

Follow-up preparation and boundaries: Describe the intended support, not a proven improvement in learning outcomes.

## 2. How does it differ from a normal question bank or Exercism?

Category: Project purpose

Suggested answer: Our emphasis is the learning process after a mistake: learners can add reasoning, examine concept clues and continue with related practice or chapter coding. A learning map organises progression. Exercism is a design reference. We do not claim to have invented these mechanisms; our contribution is the specific integration, content and verified team improvements, with proper attribution.

Follow-up preparation and boundaries: Do not claim every component is original or that the project outperforms Exercism without evidence.

## 3. Why only three topics and 30 questions? Is the bank too small?

Category: Project purpose

Suggested answer: The scope makes the full learning, diagnosis, recommendation, persistence and coding workflow manageable. Fifteen concepts have two questions each, which limits variety and permits memorisation. This is a prototype, not proof of mastery. The next step is more human-reviewed variations, not unverified AI-generated items.

Follow-up preparation and boundaries: Acknowledge the trade-off; not every repetition is intentional spaced review.

## 4. Why is this a Python project if it has a web interface? What does main.py do?

Category: Python and architecture

Suggested answer: main.py parses launch arguments and starts the Python server. Python implements grading, progression, recommendations, scheduling, state validation, SQLite persistence and GLM-4.7 result handling. React provides interaction, while browser Pyodide executes restricted practice code. Python does more than open a webpage.

Follow-up preparation and boundaries: Show main.py and backend/domain.py; acceptance of the browser GUI is ultimately the instructor’s decision.

## 5. Which taught techniques do you use, and why separate modules?

Category: Python and architecture

Suggested answer: We use lists for question collections, dictionaries for ID lookup, sets for prerequisites, and sorted with a custom key for ranking. Functions, classes and modules separate responsibilities: LearningEngine handles rules, Store persistence, server HTTP and ai model integration. Rules can be tested without opening the interface.

Follow-up preparation and boundaries: Be ready to explain one function you genuinely understand, not just list techniques.

## 6. What recommendation algorithm do you use, and why not machine learning?

Category: Recommendation and diagnosis

Suggested answer: We use deterministic ranking. Candidates stay in the chapter and exclude the current question. Priority is unseen target-concept items, due reviews, other unseen items, then seen items not yet due, with due time, concept, difficulty and ID tie-breaking. Unknown diagnoses avoid forced targeting. With a small bank and limited learner data, rules are explainable and testable; no recommender is trained.

Follow-up preparation and boundaries: See LearningEngine.recommend(). Ordinary continuation and feedback-based recommendation may supply different concept sources.

## 7. Does a wrong answer prove a misconception?

Category: Recommendation and diagnosis

Suggested answer: No. A mistake may be a slip, guess or a different misunderstanding. We present possible concept clues. Current mappings are coarse: wrong options point to the question’s concept. GLM-4.7 can support that candidate or return unknown, not freely choose another concept. Follow-up performance provides more evidence, but not a statistically validated diagnosis.

Follow-up preparation and boundaries: For example, selecting output 5 may reflect confusion about Boolean results rather than comparison boundaries.

## 8. How are review intervals chosen? Is this a validated memory algorithm?

Category: Recommendation and diagnosis

Suggested answer: We use a simplified fixed schedule: ten minutes after an error; hinted success does not advance the stage and schedules a review within a day; independent success when due progresses through 1, 3, 7, 14 and 30 days. Early repetition does not advance it. These intervals are a design choice, not validated as optimal or fitted to individual memory.

Follow-up preparation and boundaries: Do not label it a full implementation of SM-2 or another unimplemented algorithm; show schedule().

## 9. What does AI contribute, and can the application work without it?

Category: AI contribution

Suggested answer: The application works without AI: grading, standard explanations, ranking, persistence and coding remain available. GLM-4.7 adds analysis of written reasoning, verbatim evidence, support for or abstention from a candidate diagnosis, and personalised explanation. Whether it improves on rules requires a comparison on independently labelled cases; we do not yet claim higher accuracy.

Follow-up preparation and boundaries: Distinguish AI-assisted feedback from fixed rule feedback in the demonstration.

## 10. How do you handle hallucinations or attempts to change the answer?

Category: AI contribution

Suggested answer: Answer keys remain fixed by the bank and Python logic. Labels are restricted to the candidate or unknown; quotations must occur in the learner’s reason, and personalised feedback checks the answer key and an excerpt of the standard explanation. Invalid results are rejected or replaced with standard feedback. Correct quotations do not guarantee factual correctness, so human evaluation remains necessary.

Follow-up preparation and boundaries: Show validate_output() and analyze(). Treating learner text as untrusted is one safeguard, not a proof of safety.

## 11. Have you evaluated AI quality? How would you evaluate it?

Category: AI contribution

Suggested answer: Current automated tests mock responses and verify integration/fallback, not live accuracy. Twelve synthetic reasons exist, but their labels need independent review. We would label cases independently, reserve untouched evaluation data, then compare rules and AI for label agreement, unknown detection, factual correctness and relevance, separating valid outputs from fallback. This would not by itself prove learning gains.

Follow-up preparation and boundaries: If it has not been run, say so. Do not invent a percentage.

## 12. Is PiPo an AI agent? How did you use generative AI?

Category: AI contribution

Suggested answer: PiPo currently uses preset responses and keyword navigation, without autonomous planning or a tool loop. GLM-4.7 provides bounded diagnostic requests. Codex assistance during implementation, testing, documentation and inspection is separate from runtime GLM-4.7 use. We should show actual examples of accepted, modified or rejected suggestions and explain the final code ourselves.

Follow-up preparation and boundaries: Do not describe AI self-inspection as completed independent human team review.

## 13. What do the 21 tests cover, and why were they selected?

Category: Testing and quality

Suggested answer: The suite prioritises correctness and failure risks: grading, progression, ranking, scheduling, import, database isolation/conflicts, AI validation/fallback, selected execution restrictions, HTTP and bilingual data. Twenty-one is the method count; loops also check 30 question outputs and 39 reference-solution cases. SPEC section 6 maps targets, assertions and reasons.

Follow-up preparation and boundaries: Run python3 -m unittest discover -s tests -t . -v. Model responses are mocked, with no API charge.

## 14. Does passing all tests prove the application is correct? What is missing?

Category: Testing and quality

Suggested answer: No. These are baseline regression checks, with no measured coverage percentage. Gaps include full mixed-history ranking, every review stage and more AI error paths. Browser reasoning edits, language switching, Worker timeouts, charts and import need separate acceptance. Unit tests cannot replace live AI evaluation, content review or usability studies.

Follow-up preparation and boundaries: A specific uncovered branch is more credible than claiming comprehensive coverage.

## 15. What real defect did you encounter, and how was it fixed?

Category: Testing and quality

Suggested answer: One recorded defect was VS Code failing to import the tests directory. Root-based discovery reproduced it: tests lacked __init__.py. Adding the package marker and fixing the working directory exposed a reference-solution import issue. Using tests.reference_solutions made both discovery modes pass all 21 tests. Success with one command does not ensure the editor’s import mode also works.

Follow-up preparation and boundaries: This was AI-assisted project work. If you did not perform it personally, say “the project record shows” rather than claim it as your own contribution.

## 16. What stage has your CI/CD reached?

Category: Testing and quality

Suggested answer: GitHub Actions is configured for push/PR-triggered tests across Windows, macOS and Linux with Python 3.10/3.13, plus frontend checking/building. Successful remote execution is not yet evidenced. Packaging and frontend building remain independent; current-build handoff, artifact upload and server deployment are absent. CI is configured, while remote verification and CD are incomplete.

Follow-up preparation and boundaries: Local test success is not six-platform-matrix success; a Dockerfile is not a completed deployment.

## 17. How are records stored? Can users switch devices?

Category: Data and safety

Suggested answer: SQLite stores each learning space identified by a random browser cookie. Revisions reject stale writes. Keeping the browser cookie enables continuation, but there is no account-based automatic sync. Users can export/import JSON between devices; import replaces the current space and regrades answers. Backup transfer is not automatic synchronisation.

Follow-up preparation and boundaries: Clearing cookies or changing browser/host can create another space; explain backup requirements.

## 18. Could learner code harm the server, and how are keys protected?

Category: Data and safety

Suggested answer: Learner code runs in a browser Worker rather than on the server. Syntax restrictions and timeouts apply, but there is no hard memory quota or absolute sandbox guarantee. API keys stay in server configuration/environment variables and are excluded from packaging; the browser uses a team code. Origin/length checks and a 60-request hourly limit reduce risks, but rate limiting is not a billing cap.

Follow-up preparation and boundaries: Do not show real credentials or repeatedly call a paid endpoint merely to prove connectivity.

## 19. What did you personally contribute? Do you understand the AI-written code? Is review complete?

Category: Individual contribution and review

Suggested answer: Use your actual work: I was responsible for [module/content], made [decision/change], supported by [file/commit/test/review evidence]. AI assisted with [part], which I verified using [method]. If human review is incomplete, say that AI inspection exists but member review records remain pending. A template is not a result.

Follow-up preparation and boundaries: Each member should explain inputs, outputs, branches and errors in a relevant code segment. Do not invent contributions.

## 20. What would you prioritise with two more weeks?

Category: Improvements and conclusion

Suggested answer: First improve reliability and evidence: review concept labels, add same-concept variations, strengthen ranking/scheduling/AI-error and browser tests, conduct an independently labelled AI comparison, and obtain cross-platform CI results. New accounts or features should follow observed user needs rather than complexity for its own sake.

Follow-up preparation and boundaries: Tie improvements to specific gaps rather than promising all subjects or automatic question generation.

## Code walkthrough preparation

Prepare main.py, recommend()/schedule() in backend/domain.py, validate_output()/analyze() in backend/ai.py, save() in backend/storage.py and tests/test_core.py. State the purpose, inputs, main branches and outputs, then show a test and an uncovered case. Avoid reading an entire file line by line.

## Responding when uncertain

“We have not verified that aspect, so I cannot give a reliable conclusion. The current implementation does …; to establish it, we would need … tests or data.”

Start with a 20–40-second answer and expand on follow-up. Do not guess accuracy, performance, coverage or other members’ contributions.
