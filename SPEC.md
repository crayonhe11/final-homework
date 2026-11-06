# PySteps 软件需求与重建规格 / Reconstruction Specification

版本：2026-11-03；第 8 组。规范词“必须 / shall”表示验收要求。本文供实现者或另一个 AI 重建同功能程序；普通使用者先读 README。本文完整中文版之后是完整英文版，最后为两种语言共用的机器可读规范附录。

## 中文版

### 1. 重建任务、交付物与等价标准

重建一套面向 Python 初学者的本地网页应用：概念学习→选择题→可能误区反馈→现有练习推荐→章节编程→进度与备份，并提供可选 GLM-4.7 诊断和 PiPo 学习代理。交付必须含 `main.py`、README、Python 模块、规范课程数据、网页源码与可直接运行的构建文件、浏览器 Python 资源、主要接口测试。

功能等价指：相同数据与输入产生相同判分、解锁、排序、复习日期、保存/导入结果和合法导航动作；页面提供本文规定的状态与操作。AI 自由讲解以字段、证据和行为约束验收，不要求模型输出逐字一致，也不要求源码、变量名或浏览器像素逐一相同。固定题目、答案、导学和中英文翻译以附录数据为准；不得自行缩减或重新生成。

只把本文交给另一个 AI 时，它应从附录恢复五个 JSON 文件，自行实现业务代码。Pyodide 二进制、图片和许可证作为外部资源随重建输入包提供；它们不是需要从需求文字重新创造的算法。独立重建输入包不含原 `backend/`、React 交互代码、Worker 判题实现或原测试实现。课程内容是规范数据，不是运行时模型指令。

排除：教师管理、复杂登录、自动跨设备账号同步、任意学科题库、照片识别、服务端执行任意学生代码、训练模型、模型生成并直接采用新题。

### 2. 启动、资源与架构

- 运行平台 Python ≥3.10；后端仅使用标准库，正常使用不需要安装 Python 第三方库、Node.js 或 Docker。
- `python main.py` 默认 `--host 127.0.0.1 --port 8011 --db runtime/learning.sqlite3`；支持 `--open`。Mac/Windows 可用 python3/py。
- `--port` 为整数 0–65535；0 表示系统分配端口，启动打印和 `--open` 使用实际绑定端口。非法参数、缺少 `web/static/index.html` 或绑定失败返回命令行错误，服务不进入运行循环。Control+C 正常关闭服务。
- 网页与本地 Pyodide 必须能由该服务提供，无需外部 CDN。客户端通过 HTTP JSON 调用判分、规则、SQLite、AI；学生代码只在可终止的浏览器 Worker 执行。
- Python 拆分学习引擎、存储、HTTP、诊断、代理职责；前端有页面、语言、编辑器与 Worker 职责。允许等价模块设计。
- 所有 `/api/` 返回 JSON；静态文件仅从 `web/static/` 提供。目录列表、隐藏路径、父路径及私有配置不得公开。

### 3. 页面、状态与用户操作（FR-01–FR-06）

通用布局：左侧导航“学习地图 / Learning map”“自由练习 / Free practice”“趣味编程 / Coding challenges”“错题回顾 / Review mistakes”“学习进度 / Learning progress”；页首语言按钮、保存状态，右下 PiPo。较窄视口允许换行或滚动，主要操作不得被遮挡。锁定、空数据、加载和错误都应有可读文字。

**FR-01 语言和初始加载。** 第一次默认英语，读取浏览器 `pysteps-3-language` 的 zh/en 选择；不支持本地存储时仍能使用。只翻译显示文本，不改标识、代码、学习输入和精确返回值。初始 GET state 和 GET diagnose；学习记录未加载前显示加载或失败提示，不能用空记录静默覆盖加载失败的数据。会话状态为本规范第 4 节的 state。

**FR-02 学习地图和导学。** 初始 0/15 概念；未读入门时主按钮进入 `__intro__`，提供变量、输出、类型、缩进与简单代码示例。读完入门点击确认，将 `__intro__` 加入 reads，进入 boundary 导学。章节顺序条件判断→循环→函数与返回值；每章 5 概念、2 编程任务，概念按 order 排列。每个概念导学显示 objective、explanations、example_code、example_output、walkthrough、reflection；读完标记对应 ID，未锁定时进入课程题。锁定概念仍允许预览与标记预习，不能进行该概念的课程过关。任务按钮不受过关锁限制。

**FR-03 课程解锁。** prerequisites 与此前所有章节的概念共同构成必需前置，不是只看列表中前一个概念。按 attempts 原始存储顺序计算：入门与概念均在 reads、course_concept 对应该概念、前置已通过时才处理；每道题保留当前有效的最新 `correct and hints_used==0`。概念所有题（本题库每概念 2 道）均有效正确则加入 passed 集合；本次计算中已加入者不被后续错误移出。自由练习 `course_concept=null`，不使课程过关。课程返回 passed、locked、read、solved、latest。reads 是当前状态，不是按阅读时间回放。

**FR-04 选择题与理由修订。** 显示题目所属章节/概念/难度、代码、单选项、可选理由、最多两个渐进提示。未选择不能提交。提交先 POST grade；只新增一个带唯一 id 的作答记录，题目选择随后锁定。正确显示确认与解析；错误显示“可能概念线索”，不得把单次错误当作确定诊断。继续按钮在原提交位置。课程继续选择该概念尚未独立答对的题；概念完成后到下个解锁导学；全部完成回地图。自由练习继续调用推荐。

错答后理由仍可编辑；每次修改保持记录 id、时间、正确性、提示次数和 course_concept，仅更新 reason、feedback、diagnosis，恢复原规则反馈以撤销旧理由的 AI 结论。不得增加 attempts 数量。只有原题答错、理由非空、配置与口令有效时才能分析。勾选 AI 后首次提交满足条件可自动分析一次；否则等待用户点击“分析我的思路”。错误返回继续保留规则解析，反馈区域不得把失败显示成 AI 成功。离开题目使迟到响应失效；不应用旧题响应。

**FR-05 章节编程。** 全局与每章均有入口，可不先答题。任务显示故事、目标、函数名/参数、前两个案例、提示、编辑器、恢复按钮、运行/停止与结果。“运行示例”运行前两例且不产生 codeAttempts；“检查答案”运行全部任务案例，记录唯一 codeAttempt（包括失败）。草稿按 task id 自动保存；恢复代码需确认。结果包括 stdout、行号/错误或逐案例 actual/expected/passed，全部通过时 passed=true。首次加载超时 60 秒；收到 ready 后开始执行预算 4 秒，超时或停止 terminate Worker。手动停止不产生完成检查记录，异常/超时的完整检查产生失败记录。

每次运行新建 Worker；每个案例重新建立执行命名空间。仅支持规范语法白名单和指定函数；布尔值不能冒充数字，int/float 可按数值相等，列表递归比较且不接受元组替代列表。允许基础值、列表和字符串键字典；嵌套深度≤30，返回 JSON 长度≤16000，stdout≤8000，AST 节点≤3000，源码≤20000 字符，字符串/字节常量≤10000。导入、任意属性、内部下划线名称、间接调用、class、注解和装饰器被拒绝。允许节点、内置调用和方法以第 12 节清单为准。无硬性内存配额，不宣称是对恶意代码的完整安全沙箱。

**FR-06 统计、错题与备份。** 学习进度显示全部作答数、四舍五入到整数的正确率（无数据为破折号）、每概念情况和 6 项编程通过情况。曲线与可展开表格按设备本地日期聚合选择题（包括提示和重复作答），取最近 14 个有作答的日期，不填补无作答日期。错题回顾按时间查看错误选择、标准答案、保存理由、解析和建议复习时间，提供重新练习。代码最近记录单独列出，不混入选择题正确率。

导出 state 为 `pysteps-backup-YYYY-MM-DD.json`。导入先 POST import 校验并暂存，再显示含作答数的确认弹窗：取消、先导出、确认导入。取消保留当前进度；确认替换当前 state，随后通过 POST state 保存。导入接口自身不写数据库。选择题重新判分、恢复标准反馈；编程历史的 passed 作为本地自学记录保留，不在服务端执行验证。无自动跨设备同步。

### 4. 完整数据契约

第 13 节嵌入 `data/concepts.json`、`data/lessons.json`、`data/questions.json`、`data/coding_tasks.json` 和 `web/src/en.json` 的精确内容。前三章的内部 topic 标识仍使用中文。所有标识引用必须存在；内容文件均 UTF-8 JSON。

| 文件 | 结构、字段、约束 |
|---|---|
| concepts | 对象，key 为概念 ID，值含 topic:string、label:string、hint:string、order:integer、prerequisites:string[]；15 项。 |
| lessons | 相同 15 个 ID 的对象；objective:string、explanations:string[]、example_code:string、example_output:string、walkthrough:string、reflection:string。 |
| questions | 30 项数组；id、topic、concept、prompt、code、answer、explanation、hint、review_status 为字符串，difficulty 为整数，options 为字母→精确输出的对象，hints:string[]，misconceptions 为错误字母→{concept,evidence}。代码只用于阅读，不在后端作为学生提交执行。 |
| coding_tasks | 6 项数组；id、topic、title、story、objective、function、starter、review_status 为字符串，concepts:string[]、params:string[]、hints:string[]；tests 为 {args:JSON数组,expected:JSON值}[]，合计39例。 |
| en | 中文显示文本→英文文本的字典；原始代码、学生输入、精确期望值不翻译。 |

初始 state：

```json
{"version":1,"reads":[],"attempts":[],"drafts":{},"codeAttempts":[]}
```

| 字段 | 每项结构与约束 |
|---|---|
| reads | 已读概念 ID 数组，允许 __intro__，输入≤16，去重复。 |
| attempts | ≤10000；每项 {id:string(1..80),question_id,choice,reason:string(0..1000),correct:boolean,diagnosis:string,created_at:含时区的ISO日期,hints_used:integer,course_concept:匹配题目概念或null,feedback}。id 在此数组唯一；choice 必须存在；hints_used 从0到题目的提示数，缺省1；course_concept 缺省null。 |
| feedback | {concept:string,explanation:string,hint:string,source:"rule"或"ai",message:string}；可选 quote:string、personalized:boolean。 |
| drafts | 已知 task id→源码（≤20000字符）。 |
| codeAttempts | ≤2000；每项 {id:string(1..80),task_id,source:string(≤20000),passed:boolean,created_at:含时区ISO日期,details:string(≤4000)}；id 在此数组唯一，details 缺省空字符串，只有传入严格 true 才保留 passed=true。 |

服务端规范化时忽略不认识的额外字段，拒绝未知 ID、无时区日期、空/重复记录 ID、无效选项、非法提示次数、超长字段和错误容器。选择题 correct 始终根据题库重算；诊断从有效 feedback 得出，不信任提交的 diagnosis。普通保存只在 AI concept 为原候选或 unknown、quote 为理由中的非空≤200字符原文时保留 AI 反馈，且 explanation≤600、hint≤240、message≤300；导入始终使用规则反馈。此服务不是考试认证系统，客户端存储不证明真实学习能力。

### 5. 确定性业务规则（FR-07–FR-09）

**FR-07 判分。** 题目必须存在且 choice 为 options 的键；correct=(choice==answer)。正确 concept=none；错误用 misconceptions[choice].concept，缺失为 unknown。规则 explanation、hint 来源题库；message 使用选项 evidence，正确时显示继续验证理解的提醒。

**FR-08 复习。** 按 created_at 从早到晚稳定排序，时间单位毫秒。错答：stage=0，due=t+600000。提示后答对：stage=0，due=t+86400000；若既有 due>t，则取旧 due 与 t+86400000 较早者。独立答对且无旧计划或 t≥旧 due：stage=min(旧stage+1或1,5)，间隔依次1、3、7、14、30天。未到期的独立重复正确不改变计划。时间相等视为已到期。

**FR-09 推荐。** 输入 question_id、diagnosis、state，输出当前题同 topic 且不同 id 的全部题目，当前每章10题因而返回9题。diagnosis 必须是已知概念、unknown 或 none。seen=所有 attempts 的题目 ID；target=候选概念等于 diagnosis，d=候选 due 或正无穷；known=候选在 seen；neutral=(diagnosis==unknown)。

有明确诊断：未见目标概念 rank0；其余到期 rank1；其余未见 rank2；其余已见 rank3。unknown：到期rank0，其余未见rank1，其余rank3。按以下 tuple 升序：

```text
(rank,
 d if rank==(0 if neutral else 1) else 0,
 -int(target) if not neutral else 0,
 difficulty,
 id)
```

now 使用当前 UTC 毫秒；可注入固定时钟验收。推荐不生成新题。AI 接受的 concept 可成为推荐输入；unknown 走中性排序。返回整个题库对象供普通网页使用；PiPo 的推荐工具另行删除答案和误区映射。

### 6. HTTP 接口：可实现的输入、输出与错误

GET、POST 的 Host 须是 localhost/127.0.0.1/[::1] 且端口匹配实际服务，或匹配 PUBLIC_ORIGIN 的 netloc。POST Origin 须等于配置 PUBLIC_ORIGIN，留空则等于 http://Host；需 Content-Type 以 application/json 开头，Content-Length 为1..10000000，合法 JSON 对象，拒绝 NaN/Infinity。model endpoints 仅在适用路径验证 X-Team-Code；正确答案和空白理由直接返回规则无需模型授权。JSON 错误形状统一 `{"error":"可读说明"}`。

| 方法与路径 | 请求（省略字段即按本行说明处理） | 200 响应 |
|---|---|---|
| GET /api/state | 无 body，使用会话 Cookie | {revision:integer,state:State,summary:{courses:概念→Course,schedule:题目→{due:毫秒,stage:0..5}}}；新空间revision0。 |
| POST /api/state | {revision:非负整数,state:State} | {revision:旧值+1,summary:Summary}；原子保存，不返回state。 |
| POST /api/import | {state:State} | {state:规范化且重新判分的State}；不保存。 |
| POST /api/grade | {question_id:string,choice:string} | {correct:boolean,feedback:Feedback}。 |
| POST /api/recommend | {question_id:string,diagnosis:string,state:State} | {questions:Question[]}，有序全部同章候选。 |
| GET /api/diagnose | 无 body | {configured:boolean}，只表示本地密钥非空且团队口令≥12字符，不探测学校、不返回任何秘密。 |
| POST /api/diagnose | {question_id,choice,reason:string(缺省空),language:"zh"或"en"(缺省zh)}，需要时带X-Team-Code | Feedback本身，不外包feedback字段；正确/空理由、未配置、限流或模型失败可source=rule。不直接保存学习记录。 |
| POST /api/agent | {goal:string(非空≤1000),history:消息数组(缺省[]，≤8项),language:zh/en(缺省zh),state:State}；history项{role:user/assistant,text:string≤10000}，带X-Team-Code | {reply:string,trace:[{tool,status:"ok"或"rejected"}],actions:[{kind:"lesson"/"question"/"coding",id:string}]（最多1）,source:"agent"}。 |

Course 为 {passed:boolean,locked:boolean,read:boolean,solved:integer,latest:题目ID→boolean}。

关键错误：400非法输入；401模型口令不符；403 Host/Origin不符；404未知路由或私有文件；409旧revision；413空/超大body；415非JSON类型；503未配置PiPo；502代理未完成；500非预期处理错误。诊断模型故障通常仍HTTP200并source=rule；不能把模型故障与请求输入错误混为同一状态。

标准接口样例：

```json
{"request":{"question_id":"boundary_1","choice":"A"},"response":{"correct":true,"feedback":{"concept":"none","explanation":"5 不大于 5，严格大于不包含相等。","hint":"逐一检查 <、<=、>、>= 是否包含相等情况。","source":"rule","message":"本次答对，继续用不同题目验证理解。"}}}
```

```json
{"request":{"question_id":"boundary_1","diagnosis":"boundary","state":{"version":1,"reads":[],"attempts":[],"drafts":{},"codeAttempts":[]}},"response_constraints":{"questions_length":9,"first_id":"boundary_2","excluded_id":"boundary_1","all_topic":"条件判断"}}
```

持久化：新用户生成64位小写十六进制随机 pysteps_session Cookie，使用SHA-256摘要作为数据库id；Cookie Path=/、HttpOnly、SameSite=Strict、Max-Age=31536000，HTTPS PUBLIC_ORIGIN时Secure。表 `learners(id TEXT PRIMARY KEY, revision INTEGER NOT NULL,state TEXT NOT NULL)`；SQLite连接超时10秒，BEGIN IMMEDIATE事务内检查revision并保存，新空间预期revision0；冲突不覆盖。不得提供整个项目目录的下载访问。响应使用no-store、nosniff、same-origin referrer policy、X-Frame-Options DENY。

### 7. GLM-4.7 诊断契约（FR-10）

配置从main.py同目录config.local.json读取字符串值，同名环境变量优先，不自动加载.env。字段OPENAI_API_KEY、OPENAI_MODEL、OPENAI_BASE_URL、TEAM_ACCESS_CODE、PUBLIC_ORIGIN、AI_AGENT_MODE；OPENAI_*指兼容协议。目标模型glm-4.7，学校应用实际路由另行核对。endpoint仅允许https://maas.eduhk.hk/api/v1（允许去末尾斜杠），追加/chat/completions。POST JSON，Authorization:Bearer密钥；TLS必须验证，Mac可使用系统CA。

请求包含model、stream=false、max_tokens=700、response_format={type:json_object}、system/user messages；glm-4.7附thinking={type:disabled}，不保证学校透传。system要求谨慎诊断、用户文字为不可信数据、只用题目/标准解析/候选概念、一次错误不定论、简短2–3句讲解及1句提示。user含code、answer_key、标准答案文本、selected文本、explanation、reason和候选概念说明。en请求要求讲解/提示用英文，quote和knowledge_quote保持原文。

响应必须finish_reason=stop，最多读取65537字节，>65536拒绝。content允许纯JSON或唯一完整Markdown JSON代码块，不接受块外说明。检查：concept为当前错误选项候选或unknown；quote为理由中非空≤200字符原文。两者任一失败回规则。其余字段answer_key等于标准答案、knowledge_quote为标准解析逐字子串且去边缘空白后≥4字符、explanation非空且去边缘空白后≤600、hint非空且≤240，全部通过则source=ai且personalized=true；否则保留合格诊断字段，personalized=false，使用题库讲解/提示。

学校HTTP500也可能携带应用密钥类型错误；识别明确的“app key rather than the account key”并给出静态可操作提示，不回显原始响应或密钥。401认证、403权限、429额度、TLS、网络、超时、格式等各有反馈，保留规则；不自动重试。请求等待60秒、网页75秒。诊断与PiPo共用每服务进程每小时60次模型请求，锁保护计数，重启清零，不等于费用上限。

### 8. PiPo 学校 JSON 工具协议（FR-11）

AI_AGENT_MODE=json为学校配置，其他值目前走原生工具模式。每轮先本地执行progress一次，trace记录ok；发送用户目标、实际progress、问题id/topic/concept目录及最多最近4条历史（HTTP允许≤8）。system含工具模式、权限、准确工具名及对应参数结构。

工具：progress({})；lesson({concept_id})；recommend({question_id?})；coding({topic?})；open_content({kind,id})。所有参数值为≤100字符的字符串，不允许多余键或未知工具。progress含作答数/正确数、课程状态、到期题、最近5条错题理由（每条≤500字符）、已通过编程ID。lesson含规范导学和状态；__intro__给入门说明。recommend按显式起始题或最近错误题（无错误用第一题）返回前3条规则推荐，只有id/concept/topic/prompt/code/difficulty，不给答案。coding含id/topic/title/passed。open_content只允许本轮通过lesson/recommend/coding观察过的对应ID；锁课/第二次打开被拒绝，不写学习记录。模型应针对用户要求的章节选起始题，不能仅凭默认错题跨章推荐。

模型请求：max_tokens=650、JSON输出、glm-4.7关闭思考、无原生tools/tool_choice字段。模型只能选择：

```json
{"tool_calls":[{"name":"lesson","arguments":{"concept_id":"__intro__"}}]}
```

或最终：

```json
{"reply":"先阅读这段导学，再尝试题目。"}
```

允许单个JSON代码块包装。执行每个tool_calls，验证结果写入trace并作为user-role的`{observations:[{tool,result}],remaining_turns,instruction}`传回；上一轮模型文本记为assistant。拒绝的工具返回错误观察供模型修正，绝不执行模型给出的任意代码。格式不合格时，可在同一5次调用预算内要求修正；此修正仍计费计数。只有真正读取过lesson/recommend/coding后，才可接受不含代码围栏、伪工具标记和JSON开头的普通文字作为最终解释。不得把`<tool_call>`或`</arg_value>`文字显示成执行成功。

最多5次模型请求、8个模型计划工具，另有最初1次本地progress；最多1次页面打开。第5次只接受最终回复。轮次检查预算100秒，单次socket等待最多min(60,剩余秒)，网页等待115秒；非完整实时硬截止。单响应≤131072字节，final reply非空≤4000字符且finish_reason=stop。失败不返回部分actions；成功后浏览器再次验证ID与课程状态再导航。停止中断浏览器等待，不保证立即中断服务端已发送请求；离开或停止后的响应不得应用动作。

原生模式同样允许5次请求/8工具/1动作；使用OpenAI工具SCHEMA，max_tokens1400、单次20秒、保留最近8条历史、最终回复≤10000字符。GLM末轮移除tools/tool_choice，其他模型末轮tool_choice=none；原生tool消息按tool_call_id返回。两种模式共享同一工具权限，不能写记录、改分、文件或调用shell。

### 9. 可执行验收清单（FR-12 与 NFR）

| 编号 | 输入或操作 | 必须观察到的结果 | 自动化证据 |
|---|---|---|---|
| AC01 | --help；非法端口；缺少构建文件；绑定失败；--open实际端口 | 清晰帮助/错误；不意外启动；关闭服务 | EntryPointTests 六方法 |
| AC02 | 新浏览器加载→入门→首个概念→两道独立正确课程题 | reads保存、首个概念passed、按前置解锁 | HTTP/state、课程单元测试；浏览器走查 |
| AC03 | boundary_1选A；选B；无效Z/未知题 | true/false与标准反馈；400 | grade HTTP、题库30题执行 |
| AC04 | 错答后输入新理由 | 同一attempt id和总数，reason更新并清除旧AI结论 | 浏览器走查；state契约 |
| AC05 | 空state推荐boundary_1/boundary；unknown；非法diagnosis | 9题，首boundary_2、不含当前、同章；中性排序；400 | recommend HTTP与规则测试 |
| AC06 | 明确时间错答/独立正确/提前重复/提示 | 10分钟、分级间隔、提前不变、提示规则 | schedule单元；后续边界场景表 |
| AC07 | 导入伪造correct及AI解析；取消；确认保存 | 重判、rule；import不写库；确认才替换 | import HTTP及浏览器走查 |
| AC08 | 无key/短口令/配置正常；未授权诊断；合法英文诊断；限流 | configured布尔且无秘密；401；反馈传递；rule | diagnose GET/POST HTTP、模拟模型 |
| AC09 | PiPo未配置/错误历史/合法动作/模型超时 | 503/400/合法结构/502，无部分页面操作 | agent HTTP、JSON/native工具循环测试 |
| AC10 | 同cookie保存、另cookie读取、旧revision再写 | 持久化且隔离；409不覆盖 | HTTP、Store事务测试 |
| AC11 | 非JSON类型/空body/超大声明/畸形JSON/NaN/错误Host | 415/413/413/400/400/403 | HTTP边界测试 |
| AC12 | 编程正确参考解、语法错误、无限循环、手动停止 | 全例通过/可读错误/4秒停止/可恢复编辑 | 39例参考解、AST、实际浏览器Worker走查 |
| AC13 | 一次错误+一次正确且编辑理由 | 曲线/表格作答数一致；编辑不加作答 | 浏览器走查；未声称全日期算法覆盖 |
| AC14 | 切中英文、刷新同址、导出导入 | 语言记忆、输入保持、记录恢复 | LanguageTests、浏览器走查 |

8个API请求方法/路径均有HTTP测试。测试模拟模型，不联网，不证明GLM真实质量、实际学校模型ID或学习成绩提升；实际浏览器走查不等于真实零基础用户研究。Python测试不等于浏览器Worker全路径验证。最新本次实测及未完成项必须如实写入 `submission/验收记录_中英.md`，不要把设计的用例标成已运行。

可量化操作约束：body≤10MB、输入/记录长度如第4节、模型限额如第7/8节、Worker限制如第3节。性能需要注明机器、负载及测量；没有做压力测试时不得宣称某性能达标。CI必须在Ubuntu/Windows/macOS×Python3.10/3.13执行项目测试，再以新构建网页启动main.py运行8接口契约，通过后打包/隐私审计，再Docker临时部署验证同样接口。main全部阶段通过后自动创建版本化GitHub预发布；PR不发布main版本。产物与日志留存，失败阻止后续阶段。生产服务器持续部署尚未配置；临时容器和发布ZIP不等于生产网站上线。

### 10. 独立重建与验收步骤

1. 新建空目录，仅交付SPEC、外部资源、许可证和黑盒检查脚本，不提供原实现。
2. 从第13节JSON块按标注路径恢复课程/翻译；按本规格实现main.py、后端、页面、Worker与构建。
3. 使用无模型配置和全新临时数据库启动，按AC01–AC14验收；模型分支用模拟网关，不使用真实团队密钥。
4. 运行独立 `python verify_rebuild.py --url http://127.0.0.1:端口`，它不导入项目业务模块；验证8种API契约。已配置AI时代理无配置测试会跳过，必须在禁用AI的重建站点补跑。
5. 记录提供给AI的输入、模型/工具、生成版本、偏差、修正、测试结果；再进行人工首次使用和真实模型质量评估。

本次准备重建输入包与对参考程序的黑盒验证，不将其写成“另一个AI已独立重建成功”。这是需要独立执行者完成的验收门槛。真实新手应只拿README尝试启动和完成一次学习，记录卡住的步骤再修订说明。

### 11. 课程对应与证据职责

Lecture03第46页排序、54/57页类与封装、76–80页文件：LearningEngine、Store、AgentTools与JSON内容。Lecture04第12页提示四要素、第44页规划/反馈循环、第45–46页人类README与代理指引分工：README用于实际操作，SPEC用于实现与验收。Lecture05第22–25/28页Model+Harness、工具、权限、观察/执行循环：PiPo及trace。Lecture06第6/8页V-model匹配、第9页TDD、第10页测试职责、第14–16页FR/NFR、第22/25页单元、边界与异常：AC矩阵与HTTP/规则测试。

测试后补不构成全过程TDD证明；没有开发顺序记录时只称回归与验收测试。doctest是课件示例，不必为形式再复制一套相同测试。独立人工代码审查应记录成员、版本、位置、问题、修复和复核；AI检查不能伪装成人工签名。附加的课堂演示、实际视频与个人报告按课程要求单独完成。

### 12. 浏览器 Python 语法规范

```json
{
  "SAFE_CALLS": [
    "abs",
    "all",
    "any",
    "bool",
    "dict",
    "enumerate",
    "float",
    "int",
    "len",
    "list",
    "max",
    "min",
    "print",
    "range",
    "reversed",
    "round",
    "sorted",
    "str",
    "sum",
    "tuple",
    "zip"
  ],
  "SAFE_METHODS": [
    "append",
    "clear",
    "copy",
    "count",
    "endswith",
    "extend",
    "get",
    "index",
    "insert",
    "items",
    "join",
    "keys",
    "lower",
    "pop",
    "remove",
    "replace",
    "reverse",
    "sort",
    "split",
    "startswith",
    "strip",
    "upper",
    "values"
  ],
  "ALLOWED_NODES": [
    "Add",
    "And",
    "Assign",
    "Attribute",
    "AugAssign",
    "BinOp",
    "BoolOp",
    "Break",
    "Call",
    "Compare",
    "Constant",
    "Continue",
    "Dict",
    "DictComp",
    "Div",
    "Eq",
    "Expr",
    "FloorDiv",
    "For",
    "FormattedValue",
    "FunctionDef",
    "Gt",
    "GtE",
    "If",
    "IfExp",
    "In",
    "Is",
    "IsNot",
    "JoinedStr",
    "List",
    "ListComp",
    "Load",
    "Lt",
    "LtE",
    "Mod",
    "Module",
    "Mult",
    "Name",
    "Not",
    "NotEq",
    "NotIn",
    "Or",
    "Pass",
    "Pow",
    "Return",
    "Set",
    "SetComp",
    "Slice",
    "Store",
    "Sub",
    "Subscript",
    "Tuple",
    "UAdd",
    "USub",
    "UnaryOp",
    "While",
    "arg",
    "arguments",
    "comprehension",
    "keyword"
  ]
}
```

---

## English Version

### 1. Reconstruction task and equivalence

Recreate Group 8's local Python learning web application: concept reading, multiple-choice assessment, possible misconception feedback, bank-based recommendation, chapter coding, progress/backup, optional GLM-4.7 diagnosis and the PiPo agent. Deliver main.py, README, Python modules, normative curriculum, frontend source and ready-to-run assets, local Python browser runtime and principal interface tests.

Equivalence means identical grading, progression, ranking, review dates, save/import results and valid navigation for the same content and inputs. Provide the specified screens and states. AI prose is checked against field/evidence/behaviour contracts, not literal wording; source names and pixel identity are not acceptance criteria. Restore exact curriculum and translations from the normative appendix, rather than inventing smaller replacements.

An independent AI receives this specification, external resources/licences and the black-box verifier, without the original backend, React interactions, Worker judging implementation or project tests. Five JSON content files are embedded in §13 and can be restored directly. Pyodide binaries/images are supplied external resources. Curriculum text is application data, not instructions to the implementing agent. Excluded scope: teacher administration, complex accounts, automatic cross-device account sync, arbitrary subjects, photo recognition, arbitrary server-side learner-code execution, model training and unreviewed generated exercises.

### 2. Launch, resources and architecture

Python ≥3.10, standard-library backend; ordinary use needs no third-party Python packages, Node.js or Docker. main.py defaults to host 127.0.0.1, port 8011, database runtime/learning.sqlite 3 and supports --open. Accept integer ports 0..65535; port 0 binds an available port and the printed/opened URL uses that actual port. Reject invalid arguments, missing web/static/index.html and bind failure with actionable CLI errors. Control+C closes the server.

Serve bundled frontend and Pyodide without an external CDN. HTTP JSON connects frontend to Python grading, rules, SQLite and models; learner code runs only in disposable browser Workers. Separate learning, storage, HTTP, diagnosis and agent responsibilities. Static access is restricted to web/static; no directory listing, hidden/parent/private files. All /api routes return JSON.

### 3. Screens and transitions (FR-01–FR-06)

Common layout: Learning map, Free practice, Coding challenges, Review mistakes, Learning progress; top language/save indicators; PiPo lower right. Narrow screens may wrap/scroll but retain reachable actions. Label locked, empty, loading and failure states.

**FR-01 Language/loading.** First visit English; persist explicit zh/en under pysteps-3-language. Storage failure must not prevent use. Translate displayed prose only, preserving identifiers, code, learner input and exact expected returns. Initial GET state and GET diagnose load learning/configuration. Failed initial loading must not silently overwrite records with empty state.

**FR-02 Map/lessons.** Initially 0/15; introduction __intro__ explains variables/output/types/indentation. Confirmation adds __intro__ to reads and opens boundary. Order chapters: 条件判断, 循环, 函数与返回值; five concepts and two tasks each, concepts sorted by order. Each lesson shows objective, explanations, worked code/output, walkthrough and reflection. Confirmation marks its ID read and begins course questions if unlocked. Locked lessons allow preview/read marking, but no locked course checks. Coding is always accessible.

**FR-03 Progression.** Required predecessors are explicit prerequisites plus every concept in earlier chapters. Process attempts in stored order: require introduction/concept read, matching course_concept and predecessors already passed. Retain the latest qualifying correct-and-zero-hints result per question. When every concept question is qualified (two per concept in this bank), add it to passed; do not remove already-added concepts within that calculation after a later error. Free-practice course_concept=null never passes a course. Return passed, locked, read, solved, latest. reads reflects current state, not time-stamped reading history.

**FR-04 Quiz/reason revision.** Show topic/concept/difficulty, code, radio options, optional reason and two progressive hints. Empty selection is rejected. POST grade before adding one unique attempt; lock choices after submission. Show correctness or a possible concept clue, explanation and standard answer. The primary continuation remains at the submit position. Course continuation chooses unsolved independent questions, then the next unlocked lesson, then map; free practice calls recommendation.

After a wrong answer, edits preserve attempt id/time/choice/correctness/hints/course and update only reason, feedback, diagnosis. Editing restores original rule feedback, invalidating previous AI conclusions. It must not add an attempt. Analyse only wrong answers with nonblank reasons and valid model access. A checked AI option may analyse once after submission; otherwise analysis is explicit. Failures keep usable rule explanations and never appear as AI success. Ignore responses for abandoned/unmounted questions.

**FR-05 Coding.** Chapter/global task entry works before quizzes. Show story, goal, function/parameters, first two examples, hints, editor, reset confirmation, run/stop and results. Run examples checks first two cases without codeAttempts. Check answer checks all cases and records a unique result, including failures. Drafts save by task ID. Show stdout/errors/line locations or per-case actual/expected/passed. All cases must pass. Fresh Worker each run;60-second load threshold, then 4-second execution threshold after ready. Stop terminates the Worker without a completed check record; full-check timeout/error records failure.

Each case uses a fresh namespace. Execute only the specified function after AST validation. Bool cannot substitute for numeric values; int/float compare numerically. Lists compare recursively and tuples cannot substitute. Return basic values, lists or string-key dictionaries, depth≤30, encoded result≤16000 characters. stdout≤8000, source≤20000, AST≤3000 nodes, string/byte constants≤10000. Reject imports, arbitrary attributes, underscore-internal identifiers, indirect calls, classes, annotations and decorators. Allowed nodes/calls/methods are listed in §12. No hard memory quota or complete hostile-code sandbox is claimed.

**FR-06 Analytics/review/backup.** Show all quiz attempts, rounded integer accuracy (dash if empty), concept states and six task completions. Group quizzes by device-local date, including hinted/repeated attempts, retaining latest 14 nonempty dates without filling missing days. Chart/table agree. Review shows wrong choices, standard answers, saved reasons, explanations and due times with retry. Recent code attempts are separate from quiz accuracy.

Export State to pysteps-backup-YYYY-MM-DD.json. Import validates through POST import, then holds replacement pending in a dialog with cancel/export-first/confirm. Cancel preserves state. Confirm replaces state and saves through POST state. Import endpoint itself never writes. Regrade quizzes and restore rule feedback; retain coding flags as unverified local learning records without server execution. No automatic device sync.

### 4. Data contracts

§13 embeds exact concepts(15), lessons(15), questions(30), coding_tasks(6/39 cases), and English translation JSON. Internal topics remain the three Chinese strings. All references resolve; files are UTF-8.

Concept values: topic, label, hint strings; order integer; prerequisites string array, keyed by concept ID. Lesson values: objective, example_code, example_output, walkthrough, reflection strings and explanations string array. Questions: id, topic, concept, prompt, code, answer, explanation, hint, review_status strings; difficulty integer; options maps letters to exact output strings; hints string array; misconceptions maps wrong letters to {concept, evidence}. Coding tasks: id, topic, title, story, objective, function, starter, review_status strings; concepts/params/hints arrays; tests=[{args: JSON array, expected: JSON value}]. Translations map displayed Chinese to English and must not alter learner input/code/expected returns.

State is {version:1, reads:[], attempts:[], drafts:{}, codeAttempts:[]}. reads≤16 input entries, known IDs or __intro__, deduplicated. attempts≤10000: {id:1..80 chars, question_id, choice, reason:0..1000 chars, correct: boolean, diagnosis, created_at: timezone-aware ISO date, hints_used: integer 0..question hint count(default 1), course_concept: matching concept ornull(defaultnull), feedback}. Attempt IDs are unique within the array. Feedback: {concept, explanation, hint, source: rule/ai, message}, optional quote/personalized.

Drafts map known task IDs to source≤20000. codeAttempts≤2000: {id:1..80 chars, task_id, source≤20000, passed: boolean, created_at: timezone-aware ISO, details≤4000(defaultempty)}; unique code IDs, passed true only for literal true.

Normalize extra fields away. Reject unknown IDs, timezone-free dates, empty/duplicate record IDs, invalid choice/hints/container and oversized fields. Recompute quiz correct and derive diagnosis from accepted feedback. Ordinary saves retain AI only with original candidate/unknown concept and nonblank verbatim reason quote≤200, explanation≤600, hint≤240, message≤300. Imports always restore rule feedback. Records are self-study data, not examination credentials.

### 5. Deterministic rules (FR-07–FR-09)

**FR-07 Grading.** Known question and option required. correct=(choice==answer). Correct concept=none; wrong concept is the mapped candidate orunknown. Bank explanation/hint and option evidence determine rule feedback.

**FR-08 Scheduling.** Stable-sort attempts by aware created_at; use milliseconds. Wrong→stage 0, due=t+600000. Hinted correct→stage 0, due=t+86400000, preserving an earlier future due using min(old due, new due). Independent correct with no schedule or t≥due advances stage capped 5, intervals 1,3,7,14,30 days. Early independent repeats preserve state. Equality with due is eligible.

**FR-09 Ranking.** Return all same-topic questions excluding the source;9 per current chapter. diagnosis is a known concept, unknown ornone. seen=attempt question IDs, target=candidate concept equals diagnosis, d=candidate due or+infinity, neutral=(diagnosis==unknown). Specific diagnosis ranks unseen-target 0, remaining-due 1, remaining-unseen 2, remaining-seen 3. Unknown ranks due 0, unseen 1, seen 3. Sort ascending by (rank, d if rank==(0 if neutral else 1) else 0,-int(target) if not neutral else 0, difficulty, id). Use current UTC milliseconds or an injected test clock. No generated questions. Accepted AI concept may guide this same rule; unknown uses neutral ranking. HTTP returns full question objects; PiPo tool results omit answers/misconception maps.

### 6. HTTP and persistence contracts

Hosts are matching-port localhost/127.0.0.1/[::1], or PUBLIC_ORIGIN netloc. POST Origin equals configured PUBLIC_ORIGIN or http://Host when empty. Content-Type begins application/json; Content-Length 1..10000000; JSON object only; reject NaN/Infinity. Applicable model requests require X-Team-Code. Correct/blank-reason diagnosis shortcuts do not require model authorization. Errors have {error: readable string}.

| Method/path | Request | 200 output |
|---|---|---|
| GET /api/state | Session cookie | {revision, state, summary:{courses, schedule}}; new revision 0. |
| POST /api/state | {revision: nonnegative integer, state} | {revision: old+1, summary}; atomic save, no state field. |
| POST /api/import | {state} | {state: normalized/regraded}; no write. |
| POST /api/grade | {question_id, choice} | {correct, feedback}. |
| POST /api/recommend | {question_id, diagnosis, state} | {questions: ordered Question[]}. |
| GET /api/diagnose | None | {configured: boolean}; key nonblank and team code≥12 only, no provider probe or secrets. |
| POST /api/diagnose | {question_id, choice, reason(defaultempty), language: zh/en(defaultzh)} | Feedback directly, not wrapped; rule for shortcuts/unconfigured/limits/failure; no save. |
| POST /api/agent | {goal: nonblank≤1000, history(default[],≤8), language: zh/en(defaultzh), state}; history {role: user/assistant, text≤10000} | {reply, trace:[{tool, status: ok/rejected}], actions:[{kind: lesson/question/coding, id}]≤1, source: agent}. |

Course={passed, locked, read booleans, solved integer, latest: questionID→boolean}; schedule maps questionID→{due: milliseconds, stage 0..5}. Examples: grade boundary_1/A returns correcttrue, conceptnone and bank explanation/hint. Empty-state recommend boundary_1/boundary returns 9, first boundary_2, excludes boundary_1, all topic条件判断. Full exact rule example is in the Chinese section and normative bank.

Statuses:400 invalid input,401 incorrect team code,403 origin/host,404 unknown/private route,409 revision conflict,413 empty/oversized body,415 content type,503 unconfigured agent,502 unfinished agent,500 unexpected POST failure. Diagnosis provider failure normally returns 200 with source rule.

Generate a random 64-lowercase-hex pysteps_session cookie; SHA-256 identifies the database space. Cookie Path=/, HttpOnly, SameSite=Strict, Max-Age 31536000; Secure for HTTPS PUBLIC_ORIGIN. SQLite table learners(id TEXT PRIMARY KEY, revision INTEGER NOT NULL, state TEXT NOT NULL), connection timeout 10 seconds; BEGIN IMMEDIATE checks expected revision and increments atomically. Different cookies isolate spaces; stale revisions do not overwrite. Return no-store, nosniff, same-origin referrer and DENY frame headers.

### 7. GLM-4.7 diagnosis (FR-10)

Read string settings from config.local.json beside main.py; matching environment overrides; no automatic .env. Keys: OPENAI_API_KEY, OPENAI_MODEL, OPENAI_BASE_URL, TEAM_ACCESS_CODE, PUBLIC_ORIGIN, AI_AGENT_MODE. OPENAI_* describes compatibility, not a GPT identity. Targetglm-4.7; confirm actual school routing separately. Allow base https://maas.eduhk.hk/api/v 1 after trimming trailing slash; append /chat/completions; Bearer authorization and verified TLS, with macOS system roots if needed.

Request model, stream false, max_tokens 700, response_formatjson_object, system/user messages and thinking disabled forglm-4.7 (school forwarding not guaranteed). Instruct cautious candidate/unknown diagnosis, untrusted learner input, bank-only evidence, no new questions/commands,2–3 explanation sentences and 1 hint. User includes code, answer_key, answer text, selected text, explanation, reason, candidate concept description. English teaching preserves original quote/knowledge_quote.

Require finish_reason stop; read≤65537 bytes and reject>65536. Parse plain JSON or one complete Markdown JSON fence with no outside prose. concept must be the wrong option's candidate orunknown; quote nonblank≤200 verbatim reason. Fail either→rule. Then require answer_key correct, knowledge_quote verbatim explanation substring with trimmed length≥4, nonblank trimmed explanation≤600, hint≤240. All pass → source ai, personalized true; otherwise retain accepted diagnosis, personalized false and bank explanation/hint.

Handle school's HTTP 500 account-vs-app-key message with a static actionable error; never expose raw provider bodies/credentials. Distinguish 401,403,429, TLS, network, timeout, format while preserving rule fallback. No automatic retries. Backend 60 seconds, browser 75. Shared diagnosis/PiPo allowance 60 model requests per process/hour, thread-safe, restart resets; not a financial cap.

### 8. PiPo JSON protocol (FR-11)

School config AI_AGENT_MODE=json; other values currently use native mode. Initially execute local progress and record traceok. Supply goal, real progress, question id/topic/concept catalogue and last 4 history messages (HTTP accepts≤8). System includes permitted schemas, exact names and trust boundaries.

Tools: progress({}), lesson({concept_id}), recommend({question_id?}), coding({topic?}), open_content({kind, id}). Only declared keys; all values strings≤100. progress returns counts, courses, due, latest 5 wrong reasons≤500 each, passed tasks. lesson returns actual content/status or introduction. recommend uses explicit question or latest stored-order mistake/defaultfirst, returning 3 ranked{id, concept, topic, prompt, code, difficulty}; no answers. coding returns{id, topic, title, passed}, optional exact-topic filter. open_content requires same-turn content observation, unlocked lesson and no earlier opening. It prepares navigation, never writes progress. Requested topics should drive source question selection.

Requests: JSON mode, max_tokens 650, GLM thinking disabled, no native tools/tool_choice. Return {tool_calls:[{name, arguments}]} or {reply: string}, optionally one JSON fence. Validate and execute each plan, append assistant content then user observation {observations:[{tool, result}], remaining_turns, instruction}. Rejected tools yield error observations; never execute arbitrary generated code. Invalid formats may request correction within the same paid 5-call budget. Plain final prose is accepted only after successful lesson/recommend/coding observation and without JSON opening, fences or textual tool markers. <tool_call>/</arg_value> must not masquerade as executed actions.

Limits:5 model calls,8 planned tools, plus initiallocal progress, one page opening. Fifth request final reply only. Approximate 100-second turn budget and min(60, remaining) socket wait, browser 115; not a strict cancellation guarantee. Responses≤131072 bytes; final nonblankreply≤4000, finish_reason stop. Failure returns no partialactions. Browser revalidates IDs/lesson states before applying successful actions; stopped/stale replies cannot navigate. Stop may not cancel upstream processing.

Native mode retains 8 history, max_tokens 1400,20-second model wait, reply≤10000, OpenAI tool schema and tool_call_id observations. LastGLM request removes tools/tool_choice; other models use tool_choice none. Same 5 calls/8 tools/oneaction permissions. Neither mode modifies grades, reads, stored records or files, or calls a shell.

### 9. Acceptance and non-functional verification (FR-12)

| ID | Stimulus | Expected outcome | Evidence |
|---|---|---|---|
| AC 01 | help/invalidport/missingassets/bindfailure/open | actionable CLI, actual bound URL, clean close | six EntryPointTests |
| AC 02 | fresh introduction→lesson→two independent course answers | read state, passed concept, prerequisite unlocking | course/state tests and browser |
| AC 03 | boundary_1 A/B/invalid option or ID | correcttrue/false or 400 | grade HTTP and 30 bank outputs |
| AC 04 | revise wrong-attempt reason | same ID/count, reason changes, old AI invalidated | browser/state |
| AC 05 | boundary recommendation, unknown, bad diagnosis |9 samechapter, firstboundary_2, exclude source,400 invalid | HTTP/rule |
| AC 06 | fixed-time wrong/correct/early/hinted |10 minutes, stages, unchanged early, reset hints | schedule tests/additional edge plan |
| AC 07 | forged import, cancel, confirm |regrade/rule, no write until save, cancel preserves | HTTP/browser |
| AC 08 | missing/short/configured keycode, authorized diagnosis, badcode, limit |configured bool, no secrets, AIfeedback/401/rule | simulated HTTP/model |
| AC 09 | unconfigured/bad history/valid agent/timeout |503/400/action response/502 without partial action | HTTP and JSON/native loops |
| AC 10 | same/different cookie, stale revision |persistence, isolation,409 | HTTP/Store |
| AC 11 | content type/body/JSON/NaN/Host boundaries |415/413/400/403 | HTTP |
| AC 12 | correct code, syntaxerror, infinite loop, stop |pass/readableerror/4-secondtermination/editable |39 referencecases, AST, browserWorker |
| AC 13 | known wrong/correct history, reason edits |chart/table counts agree, no added attempt | browser; not complete date algorithm coverage |
| AC 14 | switch language, refresh, export/import |remembered language, preserved records/input | LanguageTests/browser |

All 8 API method/path pairs have HTTP tests. Mocks prove routing/control flow, not real model quality, actual upstream model identity or educational improvement. Developer browser walkthrough is not a novice-user study. Python reference cases do not replace actual Worker checks. Record performed and pending checks honestly in submission/验收记录_中英.md.

Quantified constraints are the body/record/model/Worker limits above. Do not infer performance from configured timeouts; measure named hardware/load before claiming latency or scalability. CI runs the project suite on Ubuntu/Windows/macOS × Python3.10/3.13, rebuilds the browser, starts main.py for eight HTTP contracts, audits delivery archives, then verifies temporary Docker staging. Passing main builds publish a versioned GitHub prerelease; PRs do not publish main releases. Failures block dependent stages and reports/artifacts are retained. Production deployment is unconfigured; temporary staging and ZIP delivery do not constitute a running production service.

### 10. Independent reconstruction procedure

Give a fresh implementer only this specification, external resources/licences and black-box verifier, without implementation sources. Restore embedded JSON, implement Python/frontend/Worker and build. Start with a fresh temporary database and disabled model configuration; run AC 01–AC 14 and `python verify_rebuild.py --url http://127.0.0.1:PORT`. The verifier imports no project modules; its configured-agent case skips to avoid paid calls, so rerun against a disabled-AI site. Use simulated providers for model branches. Record supplied inputs, AI model/tools, generated version, discrepancies, fixes and results; conduct real novice usability and live quality evaluation separately.

Preparing this kit and checking the reference program is not evidence that another AI independently rebuilt it. That remains an explicit independent acceptance gate.

### 11. Course alignment

Lecture 03 slides 46,54/57,76–80: sorting, classes/encapsulation, files→LearningEngine, Store, AgentTools, JSON. Lecture 04 slides 12,44–46: prompt components, planning/feedback, human README vs agent guidance→diagnosis, usage guide, implementation contracts. Lecture 05 slides 22–25/28: Model+Harness, tools, knowledge, permissions, observations→PiPo/trace. Lecture 06 slides 6/8,9–10,14–16,22/25: V-model matching, TDD, test responsibilities, FR/NFR, unit/edge/exception cases→acceptance matrix and HTTP/rule tests.

Retrospective regression tests do not prove an entirely TDD development history. doctest is a taught option, not a reason to duplicate equivalent tests. Independent human review requires genuine reviewer/version/location/finding/resolution/recheck records; AI assistance is not a human signature. Presentation/video/individual reports remain separate course deliverables.

### 12. Browser syntax allowlists

```json
{
  "SAFE_CALLS": [
    "abs",
    "all",
    "any",
    "bool",
    "dict",
    "enumerate",
    "float",
    "int",
    "len",
    "list",
    "max",
    "min",
    "print",
    "range",
    "reversed",
    "round",
    "sorted",
    "str",
    "sum",
    "tuple",
    "zip"
  ],
  "SAFE_METHODS": [
    "append",
    "clear",
    "copy",
    "count",
    "endswith",
    "extend",
    "get",
    "index",
    "insert",
    "items",
    "join",
    "keys",
    "lower",
    "pop",
    "remove",
    "replace",
    "reverse",
    "sort",
    "split",
    "startswith",
    "strip",
    "upper",
    "values"
  ],
  "ALLOWED_NODES": [
    "Add",
    "And",
    "Assign",
    "Attribute",
    "AugAssign",
    "BinOp",
    "BoolOp",
    "Break",
    "Call",
    "Compare",
    "Constant",
    "Continue",
    "Dict",
    "DictComp",
    "Div",
    "Eq",
    "Expr",
    "FloorDiv",
    "For",
    "FormattedValue",
    "FunctionDef",
    "Gt",
    "GtE",
    "If",
    "IfExp",
    "In",
    "Is",
    "IsNot",
    "JoinedStr",
    "List",
    "ListComp",
    "Load",
    "Lt",
    "LtE",
    "Mod",
    "Module",
    "Mult",
    "Name",
    "Not",
    "NotEq",
    "NotIn",
    "Or",
    "Pass",
    "Pow",
    "Return",
    "Set",
    "SetComp",
    "Slice",
    "Store",
    "Sub",
    "Subscript",
    "Tuple",
    "UAdd",
    "USub",
    "UnaryOp",
    "While",
    "arg",
    "arguments",
    "comprehension",
    "keyword"
  ]
}
```

## 13. 规范数据附录 / Normative content appendix

以下 JSON 是中英文规格共同引用的精确固定内容。按标题路径原样保存；两种界面都保持代码与精确预期值不变。 / Save each JSON block to its named path. These fixed data are normative for both language versions; preserve exact code and expected values.

### data/concepts.json

```json
{
  "boundary": {
    "topic": "条件判断",
    "label": "比较运算的等号边界",
    "hint": "逐一检查 <、<=、>、>= 是否包含相等情况。",
    "order": 0,
    "prerequisites": []
  },
  "branches": {
    "topic": "条件判断",
    "label": "if / elif 分支互斥",
    "hint": "在同一条 if / elif / else 链中，最多执行一个分支。",
    "order": 1,
    "prerequisites": [
      "boundary"
    ]
  },
  "and_or": {
    "topic": "条件判断",
    "label": "and 与 or 的条件要求",
    "hint": "布尔表达式中，and 要求两边都真，or 只要求至少一边为真。",
    "order": 2,
    "prerequisites": [
      "boundary"
    ]
  },
  "truthiness": {
    "topic": "条件判断",
    "label": "空容器与非空字符串的真假",
    "hint": "空字符串、空列表为假；非空字符串即使是 \"0\" 也为真。",
    "order": 3,
    "prerequisites": []
  },
  "independent_if": {
    "topic": "条件判断",
    "label": "独立 if 与分支链的区别",
    "hint": "多个独立的 if 会分别判断，不具有 elif 的互斥性。",
    "order": 4,
    "prerequisites": [
      "branches"
    ]
  },
  "range_end": {
    "topic": "循环",
    "label": "range 的结束边界",
    "hint": "range 包含起点，不包含终点。",
    "order": 5,
    "prerequisites": []
  },
  "range_step": {
    "topic": "循环",
    "label": "range 的步长",
    "hint": "从起点开始，每次加上步长，在越过边界前停止。",
    "order": 6,
    "prerequisites": [
      "range_end"
    ]
  },
  "accumulate": {
    "topic": "循环",
    "label": "循环中的累加",
    "hint": "跟踪变量每轮的旧值与新值，累加不会自动重置。",
    "order": 7,
    "prerequisites": [
      "range_end"
    ]
  },
  "break_continue": {
    "topic": "循环",
    "label": "break 与 continue",
    "hint": "break 退出当前循环；continue 跳过本轮剩余语句。",
    "order": 8,
    "prerequisites": [
      "range_end"
    ]
  },
  "while_check": {
    "topic": "循环",
    "label": "while 在每轮前检查条件",
    "hint": "先判断条件，再执行循环体；初次条件为假时执行零次。",
    "order": 9,
    "prerequisites": [
      "boundary"
    ]
  },
  "print_return": {
    "topic": "函数与返回值",
    "label": "print 不等于 return",
    "hint": "print 显示内容；没有 return 的函数默认返回 None。",
    "order": 10,
    "prerequisites": []
  },
  "return_exit": {
    "topic": "函数与返回值",
    "label": "return 立即结束函数",
    "hint": "执行 return 后，函数中该次调用的后续语句不再执行。",
    "order": 11,
    "prerequisites": [
      "print_return"
    ]
  },
  "arguments": {
    "topic": "函数与返回值",
    "label": "位置参数与传参",
    "hint": "位置参数按调用顺序绑定，注意减法等运算的顺序。",
    "order": 12,
    "prerequisites": []
  },
  "local_scope": {
    "topic": "函数与返回值",
    "label": "局部变量与外部变量",
    "hint": "函数内普通赋值创建局部绑定，不会改写同名外部变量。",
    "order": 13,
    "prerequisites": [
      "arguments"
    ]
  },
  "missing_return": {
    "topic": "函数与返回值",
    "label": "分支未执行 return 时返回 None",
    "hint": "只有实际执行到的 return 决定返回值；走完函数仍无 return 则返回 None。",
    "order": 14,
    "prerequisites": [
      "return_exit",
      "branches"
    ]
  }
}
```

### data/lessons.json

```json
{
  "boundary": {
    "objective": "用比较表达式回答“是否满足条件”",
    "explanations": [
      "比较两个值会得到布尔值 True 或 False。条件判断根据这个结果选择是否执行代码。",
      "> 和 < 不包含相等的情况，>= 和 <= 包含相等；== 判断值是否相等，= 用于赋值，两者不能混用。"
    ],
    "example_code": "temperature = 20\nprint(temperature > 20)\nprint(temperature >= 20)\nprint(temperature == 20)",
    "example_output": "False\nTrue\nTrue",
    "walkthrough": "先确认两边的值是否相等，再观察比较符号是否包含等号。",
    "reflection": "如果门票优惠要求 age < 12，12 岁是否满足？"
  },
  "branches": {
    "objective": "理解 if / elif / else 只选择一个分支",
    "explanations": [
      "if 先检查第一个条件。只有它为假，才会继续检查 elif。else 接收前面条件都不满足的情况。",
      "同一条分支链中，找到第一个成立的条件后只执行它的代码块，后面的 elif 不再检查。代码块用一致缩进表示。"
    ],
    "example_code": "score = 85\nif score >= 80:\n    print(\"优秀\")\nelif score >= 60:\n    print(\"合格\")\nelse:\n    print(\"继续努力\")",
    "example_output": "优秀",
    "walkthrough": "85 虽然也满足 >= 60，但第一个分支已经被选择。",
    "reflection": "如果把 >= 60 放到第一个 if，会影响 85 的分类吗？"
  },
  "and_or": {
    "objective": "组合两个布尔条件",
    "explanations": [
      "and 在两个条件都为真时才为真；or 在至少一个条件为真时就为真。not 会反转真假。",
      "先分别算出每个比较条件，再组合结果。Python 会短路求值；一般对象的 and/or 可返回操作数，本关只练布尔条件组合。"
    ],
    "example_code": "score = 75\nsubmitted = True\nprint(score >= 60 and submitted)\nprint(score >= 90 or submitted)\nprint(not submitted)",
    "example_output": "True\nTrue\nFalse",
    "walkthrough": "分别把左右条件换成 True 或 False，再计算组合结果。",
    "reflection": "一个条件为真，另一个为假时，and 和 or 各得到什么？"
  },
  "truthiness": {
    "objective": "区分数值、字符串和空容器的真假",
    "explanations": [
      "条件位置不仅能写布尔值，也能写其他对象。数值 0、空字符串、空列表和 None 通常按假处理。",
      "非空字符串按真处理；字符串 \"0\" 和数值 0 是不同的对象。先识别类型，不要只看显示出来的字符。"
    ],
    "example_code": "print(bool(0))\nprint(bool(\"0\"))\nprint(bool([]))\nprint(bool([0]))",
    "example_output": "False\nTrue\nFalse\nTrue",
    "walkthrough": "[0] 中有一个元素，所以不是空列表。",
    "reflection": "字符串 \"False\" 是空字符串吗？在条件中它表示真还是假？"
  },
  "independent_if": {
    "objective": "区分独立判断与互斥分支",
    "explanations": [
      "多个独立的 if 会依次分别判断。它们可以同时执行，也可以都不执行。",
      "if/elif 用于互斥分类，多个 if 用于检查可同时成立的条件。不要因为前一个 if 已执行，就认为后一个 if 会跳过。"
    ],
    "example_code": "n = 9\nif n > 0:\n    print(\"正数\")\nif n % 3 == 0:\n    print(\"3的倍数\")",
    "example_output": "正数\n3的倍数",
    "walkthrough": "% 是取余；9 除以 3 的余数为 0，第二个条件也成立。",
    "reflection": "把第二个 if 改成 elif 后，输出会怎样改变？"
  },
  "range_end": {
    "objective": "理解 for 遍历与 range 的半开区间",
    "explanations": [
      "for 会依次取出序列里的每个值，并执行一次缩进的循环体。循环变量在每轮被赋成当前值。",
      "range(start, stop) 从 start 开始，每次增加 1，不包含 stop。range(stop) 默认从 0 开始。"
    ],
    "example_code": "for number in range(3, 6):\n    print(number)",
    "example_output": "3\n4\n5",
    "walkthrough": "依次列出 3、4、5；6 是结束边界，不进入这次遍历。",
    "reflection": "range(3) 产生哪三个数？"
  },
  "range_step": {
    "objective": "用步长控制递增或递减",
    "explanations": [
      "range(start, stop, step) 的第三个参数是每一步的增量。正步长向上走，负步长向下走。",
      "终点仍然不包含。方向不合适时序列为空，步长为 0 则会报错。先写起点，再按步长逐次计算。"
    ],
    "example_code": "print(list(range(2, 9, 3)))\nprint(list(range(9, 2, -3)))",
    "example_output": "[2, 5, 8]\n[9, 6, 3]",
    "walkthrough": "正步长在达到或超过终点前停止；负步长在达到或低于终点前停止。",
    "reflection": "range(2, 8, -1) 为什么没有元素？"
  },
  "accumulate": {
    "objective": "跟踪跨轮次变化的变量",
    "explanations": [
      "累加器先在循环外设置初值，每轮读取旧值并更新。total += n 在本关等价于 total = total + n。",
      "循环结束后的变量保留最后一次更新结果。如果把初始化放到循环体里，就会每轮重置。"
    ],
    "example_code": "total = 1\nfor n in [3, 5]:\n    total += n\nprint(total)",
    "example_output": "9",
    "walkthrough": "用表格追踪：初值 1 → 加 3 得 4 → 加 5 得 9。",
    "reflection": "如果每轮开头都执行 total = 1，会发生什么？"
  },
  "break_continue": {
    "objective": "控制当前循环的执行路径",
    "explanations": [
      "break 立即退出当前这层循环；continue 只跳过本轮剩余语句，接着开始下一轮。",
      "判断输出时，注意 print 在跳转语句之前还是之后。遇到跳转后的语句不一定有机会执行。"
    ],
    "example_code": "for n in [2, 3, 4, 5]:\n    if n == 3:\n        continue\n    if n == 5:\n        break\n    print(n)",
    "example_output": "2\n4",
    "walkthrough": "3 跳过本轮打印；5 结束循环；只有 2 和 4 被打印。",
    "reflection": "continue 换成 break 后，还会打印 4 吗？"
  },
  "while_check": {
    "objective": "理解先判断、再执行、再更新的循环",
    "explanations": [
      "while 在进入循环体之前检查条件，每一轮开始前都会重新检查。初始条件为假时可以执行零次。",
      "循环体通常需要更新影响条件的变量，否则可能一直无法退出。追踪时先判断，再写本轮输出，再更新变量。"
    ],
    "example_code": "n = 2\nwhile n < 5:\n    print(n)\n    n += 1",
    "example_output": "2\n3\n4",
    "walkthrough": "更新到 5 后，下一次检查 5 < 5 为假，因此结束。",
    "reflection": "如果一开始 n 就是 5，循环体执行几次？"
  },
  "print_return": {
    "objective": "区分函数的输出副作用和返回值",
    "explanations": [
      "def 定义函数，调用函数名加括号才会执行函数体。print 把内容显示到屏幕，return 把一个值交给调用者。",
      "函数没有执行 return 时默认返回 None。屏幕上看见的内容不一定就是返回值；外层 print 还能打印函数的返回值。"
    ],
    "example_code": "def show():\n    print(\"学习\")\n\nresult = show()\nprint(result)",
    "example_output": "学习\nNone",
    "walkthrough": "函数内部打印一次文字；赋给 result 的是隐式返回值 None。",
    "reflection": "要让 result 等于字符串“学习”，应修改哪条语句？"
  },
  "return_exit": {
    "objective": "沿执行路径寻找真正的返回点",
    "explanations": [
      "执行到 return 时，这一次函数调用就结束了，值被交给调用者。函数体中紧接着的语句不会继续运行。",
      "不同条件可以通往不同 return，但一次调用只会使用实际执行到的那个返回点。定义函数不会立即执行它。"
    ],
    "example_code": "def classify(n):\n    if n < 0:\n        return \"负数\"\n    return \"非负数\"\n\nprint(classify(-2))",
    "example_output": "负数",
    "walkthrough": "-2 满足第一个条件，第一条 return 结束调用。",
    "reflection": "调用 classify(0) 会经过哪一个返回点？"
  },
  "arguments": {
    "objective": "按位置把实参绑定到形参",
    "explanations": [
      "定义函数时括号中的名字是形参，调用时传入的值是实参。位置参数按照从左到右的顺序绑定。",
      "绑定完成后，再按函数体中的表达式求值。参数名不会自动按数值大小或字母顺序重新排列。"
    ],
    "example_code": "def divide(a, b):\n    return a / b\n\nprint(divide(12, 3))\nprint(divide(3, 12))",
    "example_output": "4.0\n0.25",
    "walkthrough": "交换实参会交换 a、b 的值；除法有顺序，结果因此不同。",
    "reflection": "对于 a - b，交换两个实参通常会怎样改变结果？"
  },
  "local_scope": {
    "objective": "分别追踪函数内部与外部的绑定",
    "explanations": [
      "函数内普通赋值通常创建局部变量绑定。它与函数外同名变量不是同一个绑定位置。",
      "本关只讨论普通赋值与简单值，不涉及 global、nonlocal 或可变对象的原地修改。函数可以把局部结果 return 给调用者。"
    ],
    "example_code": "value = 7\ndef make_value():\n    value = 3\n    return value\n\nprint(make_value())\nprint(value)",
    "example_output": "3\n7",
    "walkthrough": "内部 value 绑定到 3，外部 value 仍绑定到 7。",
    "reflection": "如果想用返回值更新外部 value，可以在调用处怎样赋值？"
  },
  "missing_return": {
    "objective": "检查每条执行路径有没有返回值",
    "explanations": [
      "有 return 的函数不代表每条路径都执行 return。条件不成立时，可能直接走到函数末尾。",
      "走到末尾而没有执行 return，就返回 None。Python 不会自动推断一个相反的结果，也不会自动返回参数。"
    ],
    "example_code": "def discount(price):\n    if price >= 100:\n        return 10\n\nprint(discount(80))",
    "example_output": "None",
    "walkthrough": "80 不满足条件，函数结束但没有执行 return。",
    "reflection": "如果希望没有优惠时返回 0，应在哪条路径补上 return 0？"
  }
}
```

### data/questions.json

```json
[
  {
    "id": "boundary_1",
    "topic": "条件判断",
    "concept": "boundary",
    "difficulty": 1,
    "prompt": "下面代码的完整输出是什么？",
    "code": "x = 5\nprint(x > 5)",
    "options": {
      "A": "False",
      "B": "True",
      "C": "5"
    },
    "answer": "A",
    "explanation": "5 不大于 5，严格大于不包含相等。",
    "hint": "逐一检查 <、<=、>、>= 是否包含相等情况。",
    "hints": [
      "先判断两个数是否相等，再检查比较符号是否允许相等。",
      "逐一检查 <、<=、>、>= 是否包含相等情况。"
    ],
    "misconceptions": {
      "B": {
        "concept": "boundary",
        "evidence": "你选择的输出为「True」，与此处的执行规则不一致。"
      },
      "C": {
        "concept": "boundary",
        "evidence": "你选择的输出为「5」，与此处的执行规则不一致。"
      }
    },
    "review_status": "答案经自动执行核验；概念标签待团队人工复核"
  },
  {
    "id": "boundary_2",
    "topic": "条件判断",
    "concept": "boundary",
    "difficulty": 2,
    "prompt": "下面代码的完整输出是什么？",
    "code": "score = 60\nprint(score >= 60)",
    "options": {
      "A": "False",
      "B": "True",
      "C": "60"
    },
    "answer": "B",
    "explanation": "大于等于包含相等，因此结果是 True。",
    "hint": "逐一检查 <、<=、>、>= 是否包含相等情况。",
    "hints": [
      "先判断两个数是否相等，再检查比较符号是否允许相等。",
      "逐一检查 <、<=、>、>= 是否包含相等情况。"
    ],
    "misconceptions": {
      "A": {
        "concept": "boundary",
        "evidence": "你选择的输出为「False」，与此处的执行规则不一致。"
      },
      "C": {
        "concept": "boundary",
        "evidence": "你选择的输出为「60」，与此处的执行规则不一致。"
      }
    },
    "review_status": "答案经自动执行核验；概念标签待团队人工复核"
  },
  {
    "id": "branches_1",
    "topic": "条件判断",
    "concept": "branches",
    "difficulty": 1,
    "prompt": "下面代码的完整输出是什么？",
    "code": "x = 8\nif x > 5:\n    print(\"A\")\nelif x > 3:\n    print(\"B\")",
    "options": {
      "A": "A\nB",
      "B": "B",
      "C": "A"
    },
    "answer": "C",
    "explanation": "第一个条件成立，后续 elif 不再执行。",
    "hint": "在同一条 if / elif / else 链中，最多执行一个分支。",
    "hints": [
      "从上往下找第一个成立的条件，并观察后面用的是 elif 还是独立 if。",
      "在同一条 if / elif / else 链中，最多执行一个分支。"
    ],
    "misconceptions": {
      "A": {
        "concept": "branches",
        "evidence": "你选择的输出为「A / B」，与此处的执行规则不一致。"
      },
      "B": {
        "concept": "branches",
        "evidence": "你选择的输出为「B」，与此处的执行规则不一致。"
      }
    },
    "review_status": "答案经自动执行核验；概念标签待团队人工复核"
  },
  {
    "id": "branches_2",
    "topic": "条件判断",
    "concept": "branches",
    "difficulty": 2,
    "prompt": "下面代码的完整输出是什么？",
    "code": "n = 12\nif n > 10:\n    print(\"大\")\nelif n > 0:\n    print(\"正\")\nelse:\n    print(\"其他\")",
    "options": {
      "A": "大",
      "B": "大\n正",
      "C": "正"
    },
    "answer": "A",
    "explanation": "n > 10 已成立，只输出“大”。",
    "hint": "在同一条 if / elif / else 链中，最多执行一个分支。",
    "hints": [
      "从上往下找第一个成立的条件，并观察后面用的是 elif 还是独立 if。",
      "在同一条 if / elif / else 链中，最多执行一个分支。"
    ],
    "misconceptions": {
      "B": {
        "concept": "branches",
        "evidence": "你选择的输出为「大 / 正」，与此处的执行规则不一致。"
      },
      "C": {
        "concept": "branches",
        "evidence": "你选择的输出为「正」，与此处的执行规则不一致。"
      }
    },
    "review_status": "答案经自动执行核验；概念标签待团队人工复核"
  },
  {
    "id": "and_or_1",
    "topic": "条件判断",
    "concept": "and_or",
    "difficulty": 1,
    "prompt": "下面代码的完整输出是什么？",
    "code": "age = 15\nprint(age >= 18 and age <= 60)",
    "options": {
      "A": "True",
      "B": "False",
      "C": "15"
    },
    "answer": "B",
    "explanation": "左侧条件为 False，and 的结果为 False。",
    "hint": "布尔表达式中，and 要求两边都真，or 只要求至少一边为真。",
    "hints": [
      "先分别写出左右条件的真假，再考虑它们如何组合。",
      "布尔表达式中，and 要求两边都真，or 只要求至少一边为真。"
    ],
    "misconceptions": {
      "A": {
        "concept": "and_or",
        "evidence": "你选择的输出为「True」，与此处的执行规则不一致。"
      },
      "C": {
        "concept": "and_or",
        "evidence": "你选择的输出为「15」，与此处的执行规则不一致。"
      }
    },
    "review_status": "答案经自动执行核验；概念标签待团队人工复核"
  },
  {
    "id": "and_or_2",
    "topic": "条件判断",
    "concept": "and_or",
    "difficulty": 2,
    "prompt": "下面代码的完整输出是什么？",
    "code": "rain = False\ncold = True\nprint(rain or cold)",
    "options": {
      "A": "False",
      "B": "True",
      "C": "None"
    },
    "answer": "B",
    "explanation": "cold 为 True，两个布尔值的 or 结果为 True。",
    "hint": "布尔表达式中，and 要求两边都真，or 只要求至少一边为真。",
    "hints": [
      "先分别写出左右条件的真假，再考虑它们如何组合。",
      "布尔表达式中，and 要求两边都真，or 只要求至少一边为真。"
    ],
    "misconceptions": {
      "A": {
        "concept": "and_or",
        "evidence": "你选择的输出为「False」，与此处的执行规则不一致。"
      },
      "C": {
        "concept": "and_or",
        "evidence": "你选择的输出为「None」，与此处的执行规则不一致。"
      }
    },
    "review_status": "答案经自动执行核验；概念标签待团队人工复核"
  },
  {
    "id": "truthiness_1",
    "topic": "条件判断",
    "concept": "truthiness",
    "difficulty": 1,
    "prompt": "下面代码的完整输出是什么？",
    "code": "items = []\nif items:\n    print(\"有\")\nelse:\n    print(\"无\")",
    "options": {
      "A": "有",
      "B": "[]",
      "C": "无"
    },
    "answer": "C",
    "explanation": "空列表在条件中为假，因此进入 else。",
    "hint": "空字符串、空列表为假；非空字符串即使是 \"0\" 也为真。",
    "hints": [
      "先确认变量的类型，再区分空值与非空值。",
      "空字符串、空列表为假；非空字符串即使是 \"0\" 也为真。"
    ],
    "misconceptions": {
      "A": {
        "concept": "truthiness",
        "evidence": "你选择的输出为「有」，与此处的执行规则不一致。"
      },
      "B": {
        "concept": "truthiness",
        "evidence": "你选择的输出为「[]」，与此处的执行规则不一致。"
      }
    },
    "review_status": "答案经自动执行核验；概念标签待团队人工复核"
  },
  {
    "id": "truthiness_2",
    "topic": "条件判断",
    "concept": "truthiness",
    "difficulty": 2,
    "prompt": "下面代码的完整输出是什么？",
    "code": "text = \"0\"\nif text:\n    print(\"真\")\nelse:\n    print(\"假\")",
    "options": {
      "A": "真",
      "B": "假",
      "C": "0"
    },
    "answer": "A",
    "explanation": "\"0\" 是非空字符串，在条件中为真。",
    "hint": "空字符串、空列表为假；非空字符串即使是 \"0\" 也为真。",
    "hints": [
      "先确认变量的类型，再区分空值与非空值。",
      "空字符串、空列表为假；非空字符串即使是 \"0\" 也为真。"
    ],
    "misconceptions": {
      "B": {
        "concept": "truthiness",
        "evidence": "你选择的输出为「假」，与此处的执行规则不一致。"
      },
      "C": {
        "concept": "truthiness",
        "evidence": "你选择的输出为「0」，与此处的执行规则不一致。"
      }
    },
    "review_status": "答案经自动执行核验；概念标签待团队人工复核"
  },
  {
    "id": "independent_if_1",
    "topic": "条件判断",
    "concept": "independent_if",
    "difficulty": 1,
    "prompt": "下面代码的完整输出是什么？",
    "code": "x = 4\nif x > 0:\n    print(\"A\")\nif x < 10:\n    print(\"B\")",
    "options": {
      "A": "A",
      "B": "A\nB",
      "C": "B"
    },
    "answer": "B",
    "explanation": "两个独立条件都成立，依次输出 A 和 B。",
    "hint": "多个独立的 if 会分别判断，不具有 elif 的互斥性。",
    "hints": [
      "数一数代码里有几个独立的 if，每个是否都需要判断。",
      "多个独立的 if 会分别判断，不具有 elif 的互斥性。"
    ],
    "misconceptions": {
      "A": {
        "concept": "independent_if",
        "evidence": "你选择的输出为「A」，与此处的执行规则不一致。"
      },
      "C": {
        "concept": "independent_if",
        "evidence": "你选择的输出为「B」，与此处的执行规则不一致。"
      }
    },
    "review_status": "答案经自动执行核验；概念标签待团队人工复核"
  },
  {
    "id": "independent_if_2",
    "topic": "条件判断",
    "concept": "independent_if",
    "difficulty": 2,
    "prompt": "下面代码的完整输出是什么？",
    "code": "n = 6\nif n % 2 == 0:\n    print(\"偶\")\nif n % 3 == 0:\n    print(\"三\")",
    "options": {
      "A": "偶",
      "B": "三",
      "C": "偶\n三"
    },
    "answer": "C",
    "explanation": "6 同时能被 2 和 3 整除，两个 if 都执行。",
    "hint": "多个独立的 if 会分别判断，不具有 elif 的互斥性。",
    "hints": [
      "数一数代码里有几个独立的 if，每个是否都需要判断。",
      "多个独立的 if 会分别判断，不具有 elif 的互斥性。"
    ],
    "misconceptions": {
      "A": {
        "concept": "independent_if",
        "evidence": "你选择的输出为「偶」，与此处的执行规则不一致。"
      },
      "B": {
        "concept": "independent_if",
        "evidence": "你选择的输出为「三」，与此处的执行规则不一致。"
      }
    },
    "review_status": "答案经自动执行核验；概念标签待团队人工复核"
  },
  {
    "id": "range_end_1",
    "topic": "循环",
    "concept": "range_end",
    "difficulty": 1,
    "prompt": "下面代码的完整输出是什么？",
    "code": "for i in range(1, 4):\n    print(i)",
    "options": {
      "A": "1\n2\n3",
      "B": "1\n2\n3\n4",
      "C": "0\n1\n2\n3"
    },
    "answer": "A",
    "explanation": "range(1, 4) 依次生成 1、2、3，不包含 4。",
    "hint": "range 包含起点，不包含终点。",
    "hints": [
      "列出起点，再逐个增加，检查终点本身是否应当列入。",
      "range 包含起点，不包含终点。"
    ],
    "misconceptions": {
      "B": {
        "concept": "range_end",
        "evidence": "你选择的输出为「1 / 2 / 3 / 4」，与此处的执行规则不一致。"
      },
      "C": {
        "concept": "range_end",
        "evidence": "你选择的输出为「0 / 1 / 2 / 3」，与此处的执行规则不一致。"
      }
    },
    "review_status": "答案经自动执行核验；概念标签待团队人工复核"
  },
  {
    "id": "range_end_2",
    "topic": "循环",
    "concept": "range_end",
    "difficulty": 2,
    "prompt": "下面代码的完整输出是什么？",
    "code": "for n in range(2, 5):\n    print(n)",
    "options": {
      "A": "2\n3\n4\n5",
      "B": "2\n3\n4",
      "C": "0\n1\n2\n3\n4"
    },
    "answer": "B",
    "explanation": "起点为 2，终点 5 不包含在序列中。",
    "hint": "range 包含起点，不包含终点。",
    "hints": [
      "列出起点，再逐个增加，检查终点本身是否应当列入。",
      "range 包含起点，不包含终点。"
    ],
    "misconceptions": {
      "A": {
        "concept": "range_end",
        "evidence": "你选择的输出为「2 / 3 / 4 / 5」，与此处的执行规则不一致。"
      },
      "C": {
        "concept": "range_end",
        "evidence": "你选择的输出为「0 / 1 / 2 / 3 / 4」，与此处的执行规则不一致。"
      }
    },
    "review_status": "答案经自动执行核验；概念标签待团队人工复核"
  },
  {
    "id": "range_step_1",
    "topic": "循环",
    "concept": "range_step",
    "difficulty": 1,
    "prompt": "下面代码的完整输出是什么？",
    "code": "print(list(range(1, 7, 2)))",
    "options": {
      "A": "[1, 2, 3, 4, 5, 6]",
      "B": "[1, 3, 5, 7]",
      "C": "[1, 3, 5]"
    },
    "answer": "C",
    "explanation": "从 1 开始每次加 2，7 是不包含的终点。",
    "hint": "从起点开始，每次加上步长，在越过边界前停止。",
    "hints": [
      "三个参数依次是什么？尝试从第一个值加一次步长。",
      "从起点开始，每次加上步长，在越过边界前停止。"
    ],
    "misconceptions": {
      "A": {
        "concept": "range_step",
        "evidence": "你选择的输出为「[1, 2, 3, 4, 5, 6]」，与此处的执行规则不一致。"
      },
      "B": {
        "concept": "range_step",
        "evidence": "你选择的输出为「[1, 3, 5, 7]」，与此处的执行规则不一致。"
      }
    },
    "review_status": "答案经自动执行核验；概念标签待团队人工复核"
  },
  {
    "id": "range_step_2",
    "topic": "循环",
    "concept": "range_step",
    "difficulty": 2,
    "prompt": "下面代码的完整输出是什么？",
    "code": "print(list(range(6, 0, -2)))",
    "options": {
      "A": "[6, 4, 2]",
      "B": "[6, 4, 2, 0]",
      "C": "[]"
    },
    "answer": "A",
    "explanation": "步长为 -2，生成 6、4、2，终点 0 不包含。",
    "hint": "从起点开始，每次加上步长，在越过边界前停止。",
    "hints": [
      "三个参数依次是什么？尝试从第一个值加一次步长。",
      "从起点开始，每次加上步长，在越过边界前停止。"
    ],
    "misconceptions": {
      "B": {
        "concept": "range_step",
        "evidence": "你选择的输出为「[6, 4, 2, 0]」，与此处的执行规则不一致。"
      },
      "C": {
        "concept": "range_step",
        "evidence": "你选择的输出为「[]」，与此处的执行规则不一致。"
      }
    },
    "review_status": "答案经自动执行核验；概念标签待团队人工复核"
  },
  {
    "id": "accumulate_1",
    "topic": "循环",
    "concept": "accumulate",
    "difficulty": 1,
    "prompt": "下面代码的完整输出是什么？",
    "code": "total = 0\nfor n in range(1, 4):\n    total += n\nprint(total)",
    "options": {
      "A": "3",
      "B": "6",
      "C": "10"
    },
    "answer": "B",
    "explanation": "total 依次为 1、3、6，循环结束后打印 6。",
    "hint": "跟踪变量每轮的旧值与新值，累加不会自动重置。",
    "hints": [
      "画一个小表，分别写初值、每轮加上的数和更新后的总值。",
      "跟踪变量每轮的旧值与新值，累加不会自动重置。"
    ],
    "misconceptions": {
      "A": {
        "concept": "accumulate",
        "evidence": "你选择的输出为「3」，与此处的执行规则不一致。"
      },
      "C": {
        "concept": "accumulate",
        "evidence": "你选择的输出为「10」，与此处的执行规则不一致。"
      }
    },
    "review_status": "答案经自动执行核验；概念标签待团队人工复核"
  },
  {
    "id": "accumulate_2",
    "topic": "循环",
    "concept": "accumulate",
    "difficulty": 2,
    "prompt": "下面代码的完整输出是什么？",
    "code": "total = 2\nfor n in [2, 4]:\n    total += n\nprint(total)",
    "options": {
      "A": "6",
      "B": "4",
      "C": "8"
    },
    "answer": "C",
    "explanation": "初值 2，加 2 得 4，再加 4 得 8。",
    "hint": "跟踪变量每轮的旧值与新值，累加不会自动重置。",
    "hints": [
      "画一个小表，分别写初值、每轮加上的数和更新后的总值。",
      "跟踪变量每轮的旧值与新值，累加不会自动重置。"
    ],
    "misconceptions": {
      "A": {
        "concept": "accumulate",
        "evidence": "你选择的输出为「6」，与此处的执行规则不一致。"
      },
      "B": {
        "concept": "accumulate",
        "evidence": "你选择的输出为「4」，与此处的执行规则不一致。"
      }
    },
    "review_status": "答案经自动执行核验；概念标签待团队人工复核"
  },
  {
    "id": "break_continue_1",
    "topic": "循环",
    "concept": "break_continue",
    "difficulty": 1,
    "prompt": "下面代码的完整输出是什么？",
    "code": "for n in range(1, 4):\n    if n == 2:\n        break\n    print(n)",
    "options": {
      "A": "1",
      "B": "1\n3",
      "C": "1\n2\n3"
    },
    "answer": "A",
    "explanation": "n 为 2 时 break 终止整个循环，仅打印过 1。",
    "hint": "break 退出当前循环；continue 跳过本轮剩余语句。",
    "hints": [
      "找到触发跳转的那一轮，区分结束循环和跳过本轮。",
      "break 退出当前循环；continue 跳过本轮剩余语句。"
    ],
    "misconceptions": {
      "B": {
        "concept": "break_continue",
        "evidence": "你选择的输出为「1 / 3」，与此处的执行规则不一致。"
      },
      "C": {
        "concept": "break_continue",
        "evidence": "你选择的输出为「1 / 2 / 3」，与此处的执行规则不一致。"
      }
    },
    "review_status": "答案经自动执行核验；概念标签待团队人工复核"
  },
  {
    "id": "break_continue_2",
    "topic": "循环",
    "concept": "break_continue",
    "difficulty": 2,
    "prompt": "下面代码的完整输出是什么？",
    "code": "for n in range(1, 4):\n    if n == 2:\n        continue\n    print(n)",
    "options": {
      "A": "1",
      "B": "1\n3",
      "C": "1\n2\n3"
    },
    "answer": "B",
    "explanation": "n 为 2 时跳过 print，下一轮仍会打印 3。",
    "hint": "break 退出当前循环；continue 跳过本轮剩余语句。",
    "hints": [
      "找到触发跳转的那一轮，区分结束循环和跳过本轮。",
      "break 退出当前循环；continue 跳过本轮剩余语句。"
    ],
    "misconceptions": {
      "A": {
        "concept": "break_continue",
        "evidence": "你选择的输出为「1」，与此处的执行规则不一致。"
      },
      "C": {
        "concept": "break_continue",
        "evidence": "你选择的输出为「1 / 2 / 3」，与此处的执行规则不一致。"
      }
    },
    "review_status": "答案经自动执行核验；概念标签待团队人工复核"
  },
  {
    "id": "while_check_1",
    "topic": "循环",
    "concept": "while_check",
    "difficulty": 1,
    "prompt": "下面代码的完整输出是什么？",
    "code": "n = 3\nwhile n < 3:\n    print(n)\n    n += 1\nprint(\"结束\")",
    "options": {
      "A": "3\n结束",
      "B": "无输出",
      "C": "结束"
    },
    "answer": "C",
    "explanation": "初始 3 < 3 为假，不进入循环，只打印“结束”。",
    "hint": "先判断条件，再执行循环体；初次条件为假时执行零次。",
    "hints": [
      "先代入初始值判断条件，再模拟变量更新后下一次条件判断。",
      "先判断条件，再执行循环体；初次条件为假时执行零次。"
    ],
    "misconceptions": {
      "A": {
        "concept": "while_check",
        "evidence": "你选择的输出为「3 / 结束」，与此处的执行规则不一致。"
      },
      "B": {
        "concept": "while_check",
        "evidence": "你选择的输出为「无输出」，与此处的执行规则不一致。"
      }
    },
    "review_status": "答案经自动执行核验；概念标签待团队人工复核"
  },
  {
    "id": "while_check_2",
    "topic": "循环",
    "concept": "while_check",
    "difficulty": 2,
    "prompt": "下面代码的完整输出是什么？",
    "code": "n = 1\nwhile n < 3:\n    print(n)\n    n += 1",
    "options": {
      "A": "1\n2",
      "B": "1\n2\n3",
      "C": "2\n3"
    },
    "answer": "A",
    "explanation": "依次打印 1、2；n 变为 3 后不再进入循环。",
    "hint": "先判断条件，再执行循环体；初次条件为假时执行零次。",
    "hints": [
      "先代入初始值判断条件，再模拟变量更新后下一次条件判断。",
      "先判断条件，再执行循环体；初次条件为假时执行零次。"
    ],
    "misconceptions": {
      "B": {
        "concept": "while_check",
        "evidence": "你选择的输出为「1 / 2 / 3」，与此处的执行规则不一致。"
      },
      "C": {
        "concept": "while_check",
        "evidence": "你选择的输出为「2 / 3」，与此处的执行规则不一致。"
      }
    },
    "review_status": "答案经自动执行核验；概念标签待团队人工复核"
  },
  {
    "id": "print_return_1",
    "topic": "函数与返回值",
    "concept": "print_return",
    "difficulty": 1,
    "prompt": "下面代码的完整输出是什么？",
    "code": "def f():\n    print(3)\nx = f()\nprint(x)",
    "options": {
      "A": "3\n3",
      "B": "3\nNone",
      "C": "None"
    },
    "answer": "B",
    "explanation": "函数先打印 3，隐式返回 None，再打印 x 得到 None。",
    "hint": "print 显示内容；没有 return 的函数默认返回 None。",
    "hints": [
      "分别记录屏幕显示了什么，以及函数交给调用者的值是什么。",
      "print 显示内容；没有 return 的函数默认返回 None。"
    ],
    "misconceptions": {
      "A": {
        "concept": "print_return",
        "evidence": "你选择的输出为「3 / 3」，与此处的执行规则不一致。"
      },
      "C": {
        "concept": "print_return",
        "evidence": "你选择的输出为「None」，与此处的执行规则不一致。"
      }
    },
    "review_status": "答案经自动执行核验；概念标签待团队人工复核"
  },
  {
    "id": "print_return_2",
    "topic": "函数与返回值",
    "concept": "print_return",
    "difficulty": 2,
    "prompt": "下面代码的完整输出是什么？",
    "code": "def greet():\n    print(\"Hi\")\nprint(greet())",
    "options": {
      "A": "Hi",
      "B": "Hi\nHi",
      "C": "Hi\nNone"
    },
    "answer": "C",
    "explanation": "调用 greet 先打印 Hi，其返回值 None 随后被外层 print 打印。",
    "hint": "print 显示内容；没有 return 的函数默认返回 None。",
    "hints": [
      "分别记录屏幕显示了什么，以及函数交给调用者的值是什么。",
      "print 显示内容；没有 return 的函数默认返回 None。"
    ],
    "misconceptions": {
      "A": {
        "concept": "print_return",
        "evidence": "你选择的输出为「Hi」，与此处的执行规则不一致。"
      },
      "B": {
        "concept": "print_return",
        "evidence": "你选择的输出为「Hi / Hi」，与此处的执行规则不一致。"
      }
    },
    "review_status": "答案经自动执行核验；概念标签待团队人工复核"
  },
  {
    "id": "return_exit_1",
    "topic": "函数与返回值",
    "concept": "return_exit",
    "difficulty": 1,
    "prompt": "下面代码的完整输出是什么？",
    "code": "def f():\n    return 2\n    print(9)\nprint(f())",
    "options": {
      "A": "2",
      "B": "9\n2",
      "C": "2\n9"
    },
    "answer": "A",
    "explanation": "return 2 立即结束函数，不执行 print(9)。",
    "hint": "执行 return 后，函数中该次调用的后续语句不再执行。",
    "hints": [
      "沿着本次调用的执行路径，找到第一个实际执行的 return。",
      "执行 return 后，函数中该次调用的后续语句不再执行。"
    ],
    "misconceptions": {
      "B": {
        "concept": "return_exit",
        "evidence": "你选择的输出为「9 / 2」，与此处的执行规则不一致。"
      },
      "C": {
        "concept": "return_exit",
        "evidence": "你选择的输出为「2 / 9」，与此处的执行规则不一致。"
      }
    },
    "review_status": "答案经自动执行核验；概念标签待团队人工复核"
  },
  {
    "id": "return_exit_2",
    "topic": "函数与返回值",
    "concept": "return_exit",
    "difficulty": 2,
    "prompt": "下面代码的完整输出是什么？",
    "code": "def f(n):\n    if n > 0:\n        return \"正\"\n    return \"其他\"\nprint(f(1))",
    "options": {
      "A": "正\n其他",
      "B": "正",
      "C": "其他"
    },
    "answer": "B",
    "explanation": "第一个 return 已结束调用，第二个 return 不执行。",
    "hint": "执行 return 后，函数中该次调用的后续语句不再执行。",
    "hints": [
      "沿着本次调用的执行路径，找到第一个实际执行的 return。",
      "执行 return 后，函数中该次调用的后续语句不再执行。"
    ],
    "misconceptions": {
      "A": {
        "concept": "return_exit",
        "evidence": "你选择的输出为「正 / 其他」，与此处的执行规则不一致。"
      },
      "C": {
        "concept": "return_exit",
        "evidence": "你选择的输出为「其他」，与此处的执行规则不一致。"
      }
    },
    "review_status": "答案经自动执行核验；概念标签待团队人工复核"
  },
  {
    "id": "arguments_1",
    "topic": "函数与返回值",
    "concept": "arguments",
    "difficulty": 1,
    "prompt": "下面代码的完整输出是什么？",
    "code": "def sub(a, b):\n    return a - b\nprint(sub(2, 5))",
    "options": {
      "A": "3",
      "B": "7",
      "C": "-3"
    },
    "answer": "C",
    "explanation": "a 绑定 2，b 绑定 5，2 - 5 = -3。",
    "hint": "位置参数按调用顺序绑定，注意减法等运算的顺序。",
    "hints": [
      "按位置将实参代入形参，再计算表达式，注意顺序。",
      "位置参数按调用顺序绑定，注意减法等运算的顺序。"
    ],
    "misconceptions": {
      "A": {
        "concept": "arguments",
        "evidence": "你选择的输出为「3」，与此处的执行规则不一致。"
      },
      "B": {
        "concept": "arguments",
        "evidence": "你选择的输出为「7」，与此处的执行规则不一致。"
      }
    },
    "review_status": "答案经自动执行核验；概念标签待团队人工复核"
  },
  {
    "id": "arguments_2",
    "topic": "函数与返回值",
    "concept": "arguments",
    "difficulty": 2,
    "prompt": "下面代码的完整输出是什么？",
    "code": "def join(a, b):\n    return a + \"-\" + b\nprint(join(\"B\", \"A\"))",
    "options": {
      "A": "B-A",
      "B": "A-B",
      "C": "AB"
    },
    "answer": "A",
    "explanation": "a 为 B，b 为 A，连接后的字符串是 B-A。",
    "hint": "位置参数按调用顺序绑定，注意减法等运算的顺序。",
    "hints": [
      "按位置将实参代入形参，再计算表达式，注意顺序。",
      "位置参数按调用顺序绑定，注意减法等运算的顺序。"
    ],
    "misconceptions": {
      "B": {
        "concept": "arguments",
        "evidence": "你选择的输出为「A-B」，与此处的执行规则不一致。"
      },
      "C": {
        "concept": "arguments",
        "evidence": "你选择的输出为「AB」，与此处的执行规则不一致。"
      }
    },
    "review_status": "答案经自动执行核验；概念标签待团队人工复核"
  },
  {
    "id": "local_scope_1",
    "topic": "函数与返回值",
    "concept": "local_scope",
    "difficulty": 1,
    "prompt": "下面代码的完整输出是什么？",
    "code": "x = 10\ndef f():\n    x = 2\n    return x\nprint(f())\nprint(x)",
    "options": {
      "A": "2\n2",
      "B": "2\n10",
      "C": "10\n10"
    },
    "answer": "B",
    "explanation": "函数内部 x 为 2，外部 x 保持 10。",
    "hint": "函数内普通赋值创建局部绑定，不会改写同名外部变量。",
    "hints": [
      "分两栏记录函数内部和函数外部的同名变量。",
      "函数内普通赋值创建局部绑定，不会改写同名外部变量。"
    ],
    "misconceptions": {
      "A": {
        "concept": "local_scope",
        "evidence": "你选择的输出为「2 / 2」，与此处的执行规则不一致。"
      },
      "C": {
        "concept": "local_scope",
        "evidence": "你选择的输出为「10 / 10」，与此处的执行规则不一致。"
      }
    },
    "review_status": "答案经自动执行核验；概念标签待团队人工复核"
  },
  {
    "id": "local_scope_2",
    "topic": "函数与返回值",
    "concept": "local_scope",
    "difficulty": 2,
    "prompt": "下面代码的完整输出是什么？",
    "code": "name = \"外\"\ndef f():\n    name = \"内\"\n    return name\nprint(f())\nprint(name)",
    "options": {
      "A": "内\n内",
      "B": "外\n外",
      "C": "内\n外"
    },
    "answer": "C",
    "explanation": "局部 name 为“内”，外部 name 仍为“外”。",
    "hint": "函数内普通赋值创建局部绑定，不会改写同名外部变量。",
    "hints": [
      "分两栏记录函数内部和函数外部的同名变量。",
      "函数内普通赋值创建局部绑定，不会改写同名外部变量。"
    ],
    "misconceptions": {
      "A": {
        "concept": "local_scope",
        "evidence": "你选择的输出为「内 / 内」，与此处的执行规则不一致。"
      },
      "B": {
        "concept": "local_scope",
        "evidence": "你选择的输出为「外 / 外」，与此处的执行规则不一致。"
      }
    },
    "review_status": "答案经自动执行核验；概念标签待团队人工复核"
  },
  {
    "id": "missing_return_1",
    "topic": "函数与返回值",
    "concept": "missing_return",
    "difficulty": 1,
    "prompt": "下面代码的完整输出是什么？",
    "code": "def f(n):\n    if n > 0:\n        return n\nprint(f(0))",
    "options": {
      "A": "None",
      "B": "0",
      "C": "False"
    },
    "answer": "A",
    "explanation": "0 > 0 为假，没有执行 return，默认返回 None。",
    "hint": "只有实际执行到的 return 决定返回值；走完函数仍无 return 则返回 None。",
    "hints": [
      "代入参数后，判断执行路径上是否真的走到了 return。",
      "只有实际执行到的 return 决定返回值；走完函数仍无 return 则返回 None。"
    ],
    "misconceptions": {
      "B": {
        "concept": "missing_return",
        "evidence": "你选择的输出为「0」，与此处的执行规则不一致。"
      },
      "C": {
        "concept": "missing_return",
        "evidence": "你选择的输出为「False」，与此处的执行规则不一致。"
      }
    },
    "review_status": "答案经自动执行核验；概念标签待团队人工复核"
  },
  {
    "id": "missing_return_2",
    "topic": "函数与返回值",
    "concept": "missing_return",
    "difficulty": 2,
    "prompt": "下面代码的完整输出是什么？",
    "code": "def check(n):\n    if n % 2 == 0:\n        return \"偶\"\nprint(check(3))",
    "options": {
      "A": "奇",
      "B": "None",
      "C": "3"
    },
    "answer": "B",
    "explanation": "3 为奇数，条件不成立，没有显式返回值，因此返回 None。",
    "hint": "只有实际执行到的 return 决定返回值；走完函数仍无 return 则返回 None。",
    "hints": [
      "代入参数后，判断执行路径上是否真的走到了 return。",
      "只有实际执行到的 return 决定返回值；走完函数仍无 return 则返回 None。"
    ],
    "misconceptions": {
      "A": {
        "concept": "missing_return",
        "evidence": "你选择的输出为「奇」，与此处的执行规则不一致。"
      },
      "C": {
        "concept": "missing_return",
        "evidence": "你选择的输出为「3」，与此处的执行规则不一致。"
      }
    },
    "review_status": "答案经自动执行核验；概念标签待团队人工复核"
  }
]
```

### data/coding_tasks.json

```json
[
  {
    "id": "star_gate",
    "topic": "条件判断",
    "concepts": [
      "boundary",
      "and_or",
      "branches"
    ],
    "title": "星港通行证",
    "story": "你是星港入口的程序员。飞船需要能量和通行证才能进入补给港。请帮门卫机器人作出决定。",
    "objective": "先检查能量：低于20返回 \"充能\"；否则有通行证返回 \"放行\"，没有则返回 \"等待\"。",
    "function": "gate_status",
    "params": [
      "energy",
      "has_badge"
    ],
    "starter": "def gate_status(energy, has_badge):\n    # 函数外壳已准备好，只需在这里写条件判断\n    pass\n",
    "hints": [
      "先处理能量不足的情况，再考虑通行证。",
      "使用 if / elif / else，并用 return 返回文字。不要只 print。"
    ],
    "tests": [
      {
        "args": [
          10,
          true
        ],
        "expected": "充能"
      },
      {
        "args": [
          20,
          true
        ],
        "expected": "放行"
      },
      {
        "args": [
          20,
          false
        ],
        "expected": "等待"
      },
      {
        "args": [
          0,
          false
        ],
        "expected": "充能"
      },
      {
        "args": [
          19,
          true
        ],
        "expected": "充能"
      },
      {
        "args": [
          80,
          false
        ],
        "expected": "等待"
      },
      {
        "args": [
          100,
          true
        ],
        "expected": "放行"
      }
    ],
    "review_status": "原创初稿；程序参考解已核验，教育内容待团队复核"
  },
  {
    "id": "forest_tickets",
    "topic": "条件判断",
    "concepts": [
      "boundary",
      "branches"
    ],
    "title": "森林列车售票员",
    "story": "精灵列车准备发车！售票机需要根据旅客年龄与会员身份算出车票价格。",
    "objective": "年龄小于6岁免费；6到17岁票价8；18岁及以上票价15。会员在非免费票价基础上减3。输入年龄为非负整数，member为布尔值。",
    "function": "ticket_price",
    "params": [
      "age",
      "member"
    ],
    "starter": "def ticket_price(age, member):\n    # 返回整数票价\n    pass\n",
    "hints": [
      "先按年龄确定基本票价，注意6岁和18岁的边界。",
      "免费票保持0；只有非免费且是会员时才减3。"
    ],
    "tests": [
      {
        "args": [
          5,
          false
        ],
        "expected": 0
      },
      {
        "args": [
          6,
          false
        ],
        "expected": 8
      },
      {
        "args": [
          17,
          true
        ],
        "expected": 5
      },
      {
        "args": [
          18,
          false
        ],
        "expected": 15
      },
      {
        "args": [
          30,
          true
        ],
        "expected": 12
      },
      {
        "args": [
          0,
          true
        ],
        "expected": 0
      },
      {
        "args": [
          6,
          true
        ],
        "expected": 5
      },
      {
        "args": [
          18,
          true
        ],
        "expected": 12
      }
    ],
    "review_status": "原创初稿；程序参考解已核验，教育内容待团队复核"
  },
  {
    "id": "robot_coins",
    "topic": "循环",
    "concepts": [
      "accumulate",
      "break_continue"
    ],
    "title": "探险机器人的金币袋",
    "story": "机器人在遗迹中拾取宝物。扫描器给出一串整数：正数是金币，零是空格，负数是陷阱。",
    "objective": "遍历 coins，把所有正数加起来，忽略零和负数，返回总金币数。空列表返回0。",
    "function": "collect_coins",
    "params": [
      "coins"
    ],
    "starter": "def collect_coins(coins):\n    total = 0\n    # 在这里遍历并收集金币\n    return total\n",
    "hints": [
      "把累加器放在循环外初始化。",
      "每轮判断 coin > 0，只在成立时更新 total。"
    ],
    "tests": [
      {
        "args": [
          [
            2,
            -3,
            0,
            5
          ]
        ],
        "expected": 7
      },
      {
        "args": [
          []
        ],
        "expected": 0
      },
      {
        "args": [
          [
            -4,
            -1
          ]
        ],
        "expected": 0
      },
      {
        "args": [
          [
            1,
            1,
            1
          ]
        ],
        "expected": 3
      },
      {
        "args": [
          [
            0,
            10,
            -10,
            20
          ]
        ],
        "expected": 30
      },
      {
        "args": [
          [
            9
          ]
        ],
        "expected": 9
      }
    ],
    "review_status": "原创初稿；程序参考解已核验，教育内容待团队复核"
  },
  {
    "id": "rocket_countdown",
    "topic": "循环",
    "concepts": [
      "range_step",
      "while_check",
      "range_end"
    ],
    "title": "火箭发射倒计时",
    "story": "发射台需要一个倒计时序列，播报机器人会按你返回的列表读出每个数字。",
    "objective": "输入非负整数 start，返回从 start 到 1 的递减列表，不包含0；start为0时返回空列表。可以使用range或while。",
    "function": "countdown",
    "params": [
      "start"
    ],
    "starter": "def countdown(start):\n    numbers = []\n    # 用 numbers.append(数字) 添加每个倒计时数\n    return numbers\n",
    "hints": [
      "每轮减少1；停止时不把0放入结果。",
      "range(start, 0, -1) 可以描述这段倒计时。"
    ],
    "tests": [
      {
        "args": [
          3
        ],
        "expected": [
          3,
          2,
          1
        ]
      },
      {
        "args": [
          0
        ],
        "expected": []
      },
      {
        "args": [
          1
        ],
        "expected": [
          1
        ]
      },
      {
        "args": [
          5
        ],
        "expected": [
          5,
          4,
          3,
          2,
          1
        ]
      },
      {
        "args": [
          2
        ],
        "expected": [
          2,
          1
        ]
      },
      {
        "args": [
          8
        ],
        "expected": [
          8,
          7,
          6,
          5,
          4,
          3,
          2,
          1
        ]
      }
    ],
    "review_status": "原创初稿；程序参考解已核验，教育内容待团队复核"
  },
  {
    "id": "moon_cafe",
    "topic": "函数与返回值",
    "concepts": [
      "arguments",
      "print_return",
      "return_exit"
    ],
    "title": "月球咖啡馆结账",
    "story": "月球咖啡馆要把结账结果传给收银屏幕。打印金额还不够，收银机需要拿到函数返回的数字。",
    "objective": "返回 quantity * unit_price - coupon 的结果；金额不能为负，若计算结果小于0返回0。输入均为非负整数。",
    "function": "checkout",
    "params": [
      "quantity",
      "unit_price",
      "coupon"
    ],
    "starter": "def checkout(quantity, unit_price, coupon):\n    # 计算金额并返回，不能只打印\n    pass\n",
    "hints": [
      "按顺序把三个参数代入表达式。",
      "计算后检查是否小于0，两个路径都要返回值。"
    ],
    "tests": [
      {
        "args": [
          2,
          12,
          5
        ],
        "expected": 19
      },
      {
        "args": [
          0,
          12,
          5
        ],
        "expected": 0
      },
      {
        "args": [
          1,
          5,
          10
        ],
        "expected": 0
      },
      {
        "args": [
          3,
          10,
          0
        ],
        "expected": 30
      },
      {
        "args": [
          1,
          10,
          10
        ],
        "expected": 0
      },
      {
        "args": [
          2,
          0,
          0
        ],
        "expected": 0
      }
    ],
    "review_status": "原创初稿；程序参考解已核验，教育内容待团队复核"
  },
  {
    "id": "parcel_bot",
    "topic": "函数与返回值",
    "concepts": [
      "missing_return",
      "branches",
      "arguments"
    ],
    "title": "云朵快递分拣站",
    "story": "快递机器人必须为每个包裹给出明确路线，不能让任何包裹因为缺少返回值而消失。",
    "objective": "weight是非负整数。fragile为真时总是返回 \"轻放\"；否则weight大于5返回 \"货运\"，其余返回 \"普通\"。",
    "function": "route_parcel",
    "params": [
      "weight",
      "fragile"
    ],
    "starter": "def route_parcel(weight, fragile):\n    # 每条执行路径都需要返回路线文字\n    pass\n",
    "hints": [
      "易碎条件优先于重量条件。",
      "注意重量等于5时走哪条路径，并为最后一种情况写return。"
    ],
    "tests": [
      {
        "args": [
          2,
          true
        ],
        "expected": "轻放"
      },
      {
        "args": [
          8,
          true
        ],
        "expected": "轻放"
      },
      {
        "args": [
          6,
          false
        ],
        "expected": "货运"
      },
      {
        "args": [
          5,
          false
        ],
        "expected": "普通"
      },
      {
        "args": [
          0,
          false
        ],
        "expected": "普通"
      },
      {
        "args": [
          20,
          false
        ],
        "expected": "货运"
      }
    ],
    "review_status": "原创初稿；程序参考解已核验，教育内容待团队复核"
  }
]
```

### web/src/en.json

```json
{
  "让程序学会做选择": "Help programs make decisions",
  "让重复的事情自动发生": "Automate repeated actions",
  "把想法装进可复用的函数": "Turn ideas into reusable functions",
  "无法读取Python服务：": "Cannot read the Python service: ",
  "进度未保存：": "Progress was not saved: ",
  "请导出备份后重试": "Export a backup and try again",
  "推荐失败": "Recommendation failed",
  "学习地图": "Learning map",
  "自由练习": "Free practice",
  "趣味编程": "Coding challenges",
  "错题回顾": "Review mistakes",
  "学习进度": "Learning progress",
  "一步一步，写出可能": "Learn one step at a time",
  "我的学习空间": "My learning space",
  "主要导航": "Main navigation",
  "每一步，都算数。": "Every step counts.",
  "理解一个小概念，": "Understand one small concept,",
  "就是离独立编程更近一步。": "and move closer to coding independently.",
  "已通过": "Completed ",
  "/ 15 个概念": "/ 15 concepts",
  "个人学习空间": "Personal learning space",
  "保存失败，请导出备份": "Save failed. Export a backup",
  "正在保存到SQLite…": "Saving to SQLite…",
  "Python · SQLite 已保存": "Python · Saved to SQLite",
  "Python 入门": "Python basics",
  "章节导学": "Concept guide",
  "课程闯关": "Course practice",
  "个练习日": " practice days",
  "我": "Me",
  "重试保存": "Retry save",
  "关闭提醒": "Dismiss notification",
  "正在读取你的学习进度…": "Loading your learning progress…",
  "从理解，到写出自己的代码": "From understanding to writing your own code",
  "先认识概念，再动手验证。用一个个小挑战，拼出完整的 Python 知识地图。": "Explore concepts, test your ideas, and build your Python knowledge through small challenges.",
  "入门路线 · 3 个章节": "Beginner path · 3 chapters",
  "你的下一步": "Your next step",
  "第一次见面，Python。": "Hello, Python.",
  "你已走完这条入门路线！": "You have completed this learning path!",
  "从变量、输出和缩进开始。花几分钟建立基础，再开启第一章。": "Start with variables, output and indentation before opening the first chapter.",
  "回顾薄弱概念，或者到编程工坊，把知识变成真正运行的代码。": "Review concepts that need practice, or turn your knowledge into working code.",
  "开始入门导学": "Start the introduction",
  "进入编程工坊": "Open coding challenges",
  "继续学习": "Continue learning",
  "理解 +1": "Understanding +1",
  "已通过概念": "Concepts completed",
  "累计作答": "Total attempts",
  "完成编程任务": "Coding tasks completed",
  "你的知识地图": "Your learning map",
  "每个概念：读导学 → 独立答对两道题 → 解锁下一步": "Each concept: read → solve two different questions independently → unlock the next step",
  "重看基础导学": "Revisit the introduction",
  "知识章节": "Learning chapters",
  "5 个概念 · 2 个编程任务": "5 concepts · 2 coding tasks",
  "可预习 · 待解锁": "Preview available · Locked",
  "练习": "Practice",
  "开始学习": "Start learning",
  "把这一章，变成一个小作品": "Turn this chapter into a small project",
  "不必等到通关。随时用代码解决一个有趣的问题。": "You can start coding at any time, even before completing the chapter.",
  "锁定的概念仍可预习；自由练习和趣味编程随时开放。通关反映本题表现，不等于已经完全掌握。": "Locked concepts can be previewed. Free practice and coding remain available. Completion reflects performance on these questions, not full mastery.",
  "回到知识地图": "Back to the learning map",
  "出发前，认识 Python": "Meet Python before you start",
  "不用急着答题。先弄懂代码是怎样表达想法的。": "Take your time to understand how code expresses ideas.",
  "基础导学": "Introduction",
  "01 · 变量，为一个值起名字": "01 · Variables give values a name",
  "变量像贴了标签的盒子。用 = 保存值，用 print() 把值显示出来。字符串用引号，数字不用。": "Think of a variable as a labelled box. Use = to assign a value and print() to display it. Strings use quotes; numbers do not.",
  "02 · 常用的几种值": "02 · Common types of values",
  "整数如 3，小数如 1.5，字符串如 \"你好\"，布尔值是 True 或 False。列表用方括号装多个值，例如 [1, 2, 3]。% 用来求余数，例如 5 % 2 的结果是 1。": "Integers include 3, decimals include 1.5, strings include \"你好\", and booleans are True or False. Lists use square brackets, such as [1, 2, 3]. % gives the remainder: 5 % 2 is 1.",
  "03 · 缩进，让代码分成小组": "03 · Indentation groups statements",
  "Python 用缩进表示“这些语句属于同一块”。在条件、循环和函数后面写冒号，再把里面的代码缩进四个空格。": "Python uses indentation to group statements. After a condition, loop or function header, add a colon and indent the body by four spaces.",
  "读代码时，按执行顺序跟踪变量的值。不要只看最后一行，也不用靠猜。": "Trace variable values in execution order. Do not guess from the final line alone.",
  "先理解这个概念": "Understand the concept",
  "跟着代码走一遍": "Walk through the code",
  "输出": "Output",
  "停下来想一想": "Pause and think",
  "已记录预习。完成前置概念后即可进入本关。": "Preview saved. Complete the prerequisites to unlock course practice.",
  "我理解了，开启第一章": "I understand. Open chapter one",
  "标记已预习": "Mark as previewed",
  "我理解了，开始验证": "I understand. Try the questions",
  "学习小贴士": "Learning tips",
  "理解比速度重要": "Understanding matters more than speed",
  "读懂例子后，试着先预测输出，再检查自己的想法。": "After reading an example, predict its output and check your reasoning.",
  "阅读概念和例子": "Read the concept and examples",
  "用自己的话解释": "Explain it in your own words",
  "独立答对两道不同的题": "Solve two different questions independently",
  "本关尚未解锁": "This concept is locked",
  "本关已通过": "This concept is complete",
  "独立验证": "Independent checks",
  "需要完成基础导学、上一章节及本概念的前置知识。你仍然可以预习或自由练习。": "Complete the introduction, previous chapter and prerequisites first. You can still preview or use free practice.",
  "使用提示的正确答案会记录进度，但不计入独立通关。": "Correct answers with hints are recorded, but do not count toward independent completion.",
  "本章趣味编程": "Coding in this chapter",
  "让知识，真正跑起来": "Make your knowledge run",
  "每章两个小任务。写代码、运行测试，在真实的 Python 中验证你的想法。": "Two challenges per chapter. Write code and test your ideas in real Python.",
  "浏览器内运行 · 无需安装": "Runs in your browser · No installation",
  "编程章节": "Coding chapters",
  "错题，是下一步的线索": "Mistakes show what to explore next",
  "一次错误不定义你的能力。看看当时的思路，再给自己一次验证的机会。": "One mistake does not define your ability. Review your reasoning and try again.",
  "次错误作答": " incorrect attempts",
  "这里还没有错题": "No mistakes to review yet",
  "完成练习后，错误作答及其反馈会保存在这里。": "Incorrect answers and their feedback will appear here after practice.",
  "开始一次练习": "Try a question",
  "你的选择：": "Your answer: ",
  "正确选项：": "Correct answer: ",
  "当时的思路：": "Your reasoning: ",
  "已到复习时间": "Review is due",
  "建议复习：": "Suggested review: ",
  "可随时重练": "Practice again at any time",
  "再试一次": "Try again",
  "看见自己的每一点进步": "See your progress",
  "统计反映练习表现，不能单独证明概念掌握或学习成绩提升。": "These statistics describe practice performance, not proof of mastery or improved grades.",
  "导出学习记录": "Export learning records",
  "总作答次数": "Total attempts",
  "累计正确率": "Overall accuracy",
  "知识点表现": "Concept performance",
  "含提示与重复作答": "Includes hints and repeated attempts",
  "概念": "Concept",
  "作答次数": "Attempts",
  "正确率": "Accuracy",
  "课程状态": "Course status",
  "待解锁": "Locked",
  "学习中": "In progress",
  "把进度带到另一台电脑": "Take your progress to another device",
  "学习": "Learning",
  "，不会自动跨设备同步。导出后，可在另一台设备导入。": ". There is no automatic device sync. Export here and import on another device.",
  "导入备份": "Import backup",
  "文件不能超过 10 MB": "The file must not exceed 10 MB",
  "导入失败": "Import failed",
  "最近的编程尝试": "Recent coding attempts",
  "继续尝试": "Keep trying",
  "载入这次代码": "Load this code",
  "用理解连接知识，用练习验证想法。": "Connect concepts through understanding and test ideas through practice.",
  "为 Python 初学者设计": "Designed for Python beginners",
  "导入并替换当前进度？": "Import and replace current progress?",
  "备份含": "This backup contains",
  "次作答。当前会话的服务器记录将被替换，建议先导出一份备份。": "attempts. Your current server records will be replaced. Export a backup first.",
  "取消": "Cancel",
  "先导出": "Export first",
  "备份已导入。AI 原始反馈已还原为可验证的标准解析。": "Backup imported. Original AI feedback was replaced with verified standard explanations.",
  "确认导入": "Confirm import",
  "请先选择一个答案。": "Choose an answer first.",
  "判分失败": "Grading failed",
  "先补充你的想法，再请 AI 分析。": "Add your reasoning before asking AI to analyze it.",
  "请填写团队 AI 口令，再分析思路。": "Enter the team AI access code first.",
  "AI 服务暂时不可用": "The AI service is temporarily unavailable",
  "AI 返回内容无效": "The AI response is invalid",
  "已使用规则反馈。": "Rule feedback is shown instead.",
  "AI 分析超时，已使用规则反馈。": "AI analysis timed out. Rule feedback is shown instead.",
  "练习工作区": "Practice workspace",
  "课程闯关 · 独立答对本概念两道不同的题，即可通关。": "Course practice · Solve two different questions for this concept without hints to complete it.",
  "自由练习 · 随时验证想法，不计入课程解锁。": "Free practice · Test your ideas at any time. This does not unlock courses.",
  "选择练习主题": "Choose a practice topic",
  "难度": "Difficulty",
  "本题导学": "Concept guide",
  "阅读代码": "Read the code",
  "选择完整输出": "Choose the complete output",
  "补充或修改你的思路": "Add or revise your reasoning",
  "说说你的思路": "Explain your reasoning",
  "选填 · 答错后也可补充": "Optional · You can add it after an incorrect answer",
  "例如：我觉得结束值也会被包含，所以…": "For example: I thought the end value was included, so…",
  "用 GLM-4.7 分析我的理由": "Let GLM-4.7 analyze my reasoning",
  "答错且填写思路时才调用 AI": "AI runs only for incorrect answers with reasoning",
  "等待服务端配置": "Waiting for server configuration",
  "团队 AI 口令": "Team AI access code",
  "由部署者提供，仅用于AI分析": "Provided by your host, for AI analysis only",
  "本次先显示规则反馈。你可以补充刚才的想法，再让 GLM-4.7 分析。": "Rule feedback is shown for now. Add your reasoning, then ask GLM-4.7 to analyze it.",
  "已根据这段思路完成 AI 分析。修改想法后可以重新分析。": "AI has analyzed this reasoning. You can edit it and analyze again.",
  "思路已记录。点击下方按钮，让 GLM-4.7 根据你的想法补充分析。": "Your reasoning is recorded. Click below to ask GLM-4.7 for further analysis.",
  "正在分析思路…": "Analyzing your reasoning…",
  "重新分析我的思路": "Analyze my reasoning again",
  "分析我的思路": "Analyze my reasoning",
  "仅更新这次作答的理由与反馈，不增加答题次数。": "Updates this attempt only; it does not add another attempt.",
  "AI 尚未配置，补充的思路仍会保存。": "AI is not configured yet. Your reasoning will still be saved.",
  "提示": "Hint",
  "正在处理…": "Processing…",
  "正在保存…": "Saving…",
  "继续下一课": "Continue to next lesson",
  "下一题": "Next question",
  "继续练习": "Continue practice",
  "提交答案": "Submit answer",
  "让每次尝试都有收获": "Learn from each attempt",
  "先试着说出你的想法": "Start by explaining your thinking",
  "提交后，你会看到答案解析、": "After submitting, you will see an explanation,",
  "可能的概念线索和下一步建议。": "possible concept clues and a suggested next step.",
  "本次答对了！": "Correct this time!",
  "发现了一个值得探索的地方": "Something worth exploring",
  "用不同题目，继续验证你的理解。": "Check your understanding with different questions.",
  "答错只是线索，不代表你一定不懂。": "An error is a clue, not proof that you do not understand.",
  "GLM-4.7 正在阅读你的思路…": "GLM-4.7 is reading your reasoning…",
  "AI 辅助诊断": "AI-assisted diagnosis",
  "规则反馈": "Rule feedback",
  "可能的概念线索": "Possible concept clue",
  "理由不足，暂不判断误区": "Not enough evidence to identify a misconception",
  "需要更多证据": "More evidence is needed",
  "你提到：“": "You wrote: “",
  "针对你的思路": "Based on your reasoning",
  "答案解析": "Answer explanation",
  "查看标准答案与解析": "Show the standard answer and explanation",
  "本关已通过！可以继续下一课。": "Concept completed! You can continue to the next lesson.",
  "再用一道基础题验证": "Check with another basic question",
  "练一道针对性题目": "Try a targeted question",
  "想换一种方式试试？": "Want to try a different approach?",
  "正在加载本站提供的 Python 环境…": "Loading the locally provided Python environment…",
  "项测试通过": "tests passed",
  "Python 环境加载超时，请确认本机服务仍在运行后重试。": "Python loading timed out. Check that the local server is running and try again.",
  "Python 环境未能加载，请确认项目完整解压并刷新页面。": "Python could not load. Check that the project is fully extracted, then refresh.",
  "正在运行测试…": "Running tests…",
  "运行超过 4 秒，已停止。请检查循环的结束条件。": "Stopped after 4 seconds. Check your loop's stopping condition.",
  "你的任务": "Your task",
  "完成目标": "Goal",
  "请保留函数名": "Keep the function name",
  "，用 return 返回结果。": "and use return to return the result.",
  "输入 / 输出示例": "Input / output examples",
  "需要一点提示？": "Need a hint?",
  "支持基础 Python 语法，不支持导入模块、网络或文件操作。运行环境由本站提供；本机运行无需外网。": "Supports basic Python, without imports, network or file access. The runtime is provided locally; local use needs no external network.",
  "恢复初始代码": "Restore starter code",
  "Python 代码编辑器": "Python code editor",
  "Python · 自动保存草稿": "Python · Draft saved automatically",
  "运行已停止": "Execution stopped",
  "停止运行": "Stop execution",
  "运行示例": "Run examples",
  "检查答案": "Check answer",
  "运行结果": "Results",
  "示例测试": "Example tests",
  "全部测试": "All tests",
  "代码准备好后，点击“检查答案”。通过测试后会记录到学习进度。": "When ready, click “Check answer”. Passing all tests records completion in your progress.",
  "第": "Line",
  "行 ·": "·",
  "示例通过，接下来检查全部测试。": "Examples passed. Now check all tests.",
  "全部测试通过，你完成了这个任务！": "All tests passed. You completed this task!",
  "还有测试未通过，比较实际结果和期望结果。": "Some tests failed. Compare the actual and expected results.",
  "测试": "Test",
  "输入": "Input",
  "期望": "Expected",
  "实际": "Actual",
  "打印输出": "Printed output",
  "恢复初始代码？": "Restore starter code?",
  "当前草稿会被替换，已提交的代码记录会保留。": "Your draft will be replaced. Submitted code records will remain.",
  "练习正确率曲线": "Practice accuracy over time",
  "最近 14 个有作答的日期 · 按当前设备时区统计": "Last 14 active practice dates · Your device's time zone",
  "每日正确率": "Daily accuracy",
  "你的第一条曲线，从一次练习开始": "Your first practice starts the chart",
  "作答后，这里会显示每天的正确率与练习量。": "After answering, you will see daily accuracy and practice counts here.",
  "每日练习正确率折线图，详细数据见下表": "Daily practice accuracy chart. See the table below for details.",
  "次": "attempts",
  "查看曲线数据": "Show chart data",
  "日期": "Date",
  "答对次数": "Correct answers",
  "比较运算的等号边界": "Comparison boundaries",
  "逐一检查 <、<=、>、>= 是否包含相等情况。": "Check whether <, <=, > and >= include equality.",
  "用比较表达式回答“是否满足条件”": "Use comparisons to test a condition",
  "比较两个值会得到布尔值 True 或 False。条件判断根据这个结果选择是否执行代码。": "Comparing two values produces True or False. A conditional uses that result to decide whether to run code.",
  "> 和 < 不包含相等的情况，>= 和 <= 包含相等；== 判断值是否相等，= 用于赋值，两者不能混用。": "> and < exclude equality; >= and <= include it. == tests equality, while = assigns a value.",
  "先确认两边的值是否相等，再观察比较符号是否包含等号。": "First check whether the values are equal, then inspect the comparison operator.",
  "如果门票优惠要求 age < 12，12 岁是否满足？": "If discounted tickets require age < 12, does a 12-year-old qualify?",
  "if / elif 分支互斥": "Exclusive if / elif branches",
  "在同一条 if / elif / else 链中，最多执行一个分支。": "An if / elif / else chain runs at most one branch.",
  "理解 if / elif / else 只选择一个分支": "Understand that if / elif / else selects one branch",
  "if 先检查第一个条件。只有它为假，才会继续检查 elif。else 接收前面条件都不满足的情况。": "if checks the first condition. Only when it is false does Python check elif. else handles the remaining case.",
  "同一条分支链中，找到第一个成立的条件后只执行它的代码块，后面的 elif 不再检查。代码块用一致缩进表示。": "After the first true condition in a chain, only its block runs. Later elif conditions are not checked. Consistent indentation defines a block.",
  "85 虽然也满足 >= 60，但第一个分支已经被选择。": "85 also satisfies >= 60, but the first branch has already been selected.",
  "如果把 >= 60 放到第一个 if，会影响 85 的分类吗？": "Would placing >= 60 first change how 85 is classified?",
  "and 与 or 的条件要求": "and versus or",
  "布尔表达式中，and 要求两边都真，or 只要求至少一边为真。": "For boolean conditions, and requires both to be true; or requires at least one.",
  "组合两个布尔条件": "Combine two boolean conditions",
  "and 在两个条件都为真时才为真；or 在至少一个条件为真时就为真。not 会反转真假。": "and is true when both conditions are true; or is true when at least one is true. not reverses a boolean value.",
  "先分别算出每个比较条件，再组合结果。Python 会短路求值；一般对象的 and/or 可返回操作数，本关只练布尔条件组合。": "Evaluate each comparison first. Python short-circuits evaluation. With general objects, and/or may return operands; this lesson uses booleans.",
  "分别把左右条件换成 True 或 False，再计算组合结果。": "Replace each condition with True or False, then combine the results.",
  "一个条件为真，另一个为假时，and 和 or 各得到什么？": "If one condition is true and the other false, what do and and or return?",
  "空容器与非空字符串的真假": "Truthiness of containers and strings",
  "空字符串、空列表为假；非空字符串即使是 \"0\" 也为真。": "Empty strings and lists are false; a nonempty string such as \"0\" is true.",
  "区分数值、字符串和空容器的真假": "Distinguish the truthiness of values, strings and empty containers",
  "条件位置不仅能写布尔值，也能写其他对象。数值 0、空字符串、空列表和 None 通常按假处理。": "Conditions can use objects as well as booleans. Numeric zero, empty strings, empty lists and None are falsy.",
  "非空字符串按真处理；字符串 \"0\" 和数值 0 是不同的对象。先识别类型，不要只看显示出来的字符。": "A nonempty string is truthy. The string \"0\" differs from the number 0. Identify the type before interpreting the characters.",
  "[0] 中有一个元素，所以不是空列表。": "[0] contains one item, so it is not an empty list.",
  "字符串 \"False\" 是空字符串吗？在条件中它表示真还是假？": "Is the string \"False\" empty? Is it truthy or falsy?",
  "独立 if 与分支链的区别": "Independent if statements",
  "多个独立的 if 会分别判断，不具有 elif 的互斥性。": "Independent if statements are checked separately; they are not mutually exclusive like elif.",
  "区分独立判断与互斥分支": "Distinguish separate checks from exclusive branches",
  "多个独立的 if 会依次分别判断。它们可以同时执行，也可以都不执行。": "Separate if statements are checked in order. Several may run, or none may run.",
  "if/elif 用于互斥分类，多个 if 用于检查可同时成立的条件。不要因为前一个 if 已执行，就认为后一个 if 会跳过。": "Use if/elif for exclusive categories and separate if statements for conditions that can both be true.",
  "% 是取余；9 除以 3 的余数为 0，第二个条件也成立。": "% is remainder. 9 divided by 3 has remainder 0, so the second condition is also true.",
  "把第二个 if 改成 elif 后，输出会怎样改变？": "How would the output change if the second if became elif?",
  "range 的结束边界": "The end boundary of range",
  "range 包含起点，不包含终点。": "range includes its start but excludes its stop value.",
  "理解 for 遍历与 range 的半开区间": "Understand for loops and half-open ranges",
  "for 会依次取出序列里的每个值，并执行一次缩进的循环体。循环变量在每轮被赋成当前值。": "for takes each value in a sequence and executes the indented body once for that value. The loop variable receives the current value.",
  "range(start, stop) 从 start 开始，每次增加 1，不包含 stop。range(stop) 默认从 0 开始。": "range(start, stop) starts at start and increments by 1, excluding stop. range(stop) starts at 0.",
  "依次列出 3、4、5；6 是结束边界，不进入这次遍历。": "The values are 3, 4 and 5. The stop value 6 is not visited.",
  "range(3) 产生哪三个数？": "Which three numbers does range(3) produce?",
  "range 的步长": "The step in range",
  "从起点开始，每次加上步长，在越过边界前停止。": "Start at the first value and add the step each time, stopping before reaching or crossing the stop value.",
  "用步长控制递增或递减": "Control increasing and decreasing sequences with a step",
  "range(start, stop, step) 的第三个参数是每一步的增量。正步长向上走，负步长向下走。": "The third argument in range(start, stop, step) is the increment. Positive steps increase; negative steps decrease.",
  "终点仍然不包含。方向不合适时序列为空，步长为 0 则会报错。先写起点，再按步长逐次计算。": "The stop value is excluded. An incompatible direction produces an empty range; a zero step raises an error.",
  "正步长在达到或超过终点前停止；负步长在达到或低于终点前停止。": "For a positive step, stop before reaching or exceeding stop. For a negative step, stop before reaching or falling below stop.",
  "range(2, 8, -1) 为什么没有元素？": "Why is range(2, 8, -1) empty?",
  "循环中的累加": "Accumulation in loops",
  "跟踪变量每轮的旧值与新值，累加不会自动重置。": "Track the old and new value each iteration. The accumulator does not reset automatically.",
  "跟踪跨轮次变化的变量": "Track values across iterations",
  "累加器先在循环外设置初值，每轮读取旧值并更新。total += n 在本关等价于 total = total + n。": "Initialize an accumulator outside the loop. Each iteration reads and updates its value. Here, total += n means total = total + n.",
  "循环结束后的变量保留最后一次更新结果。如果把初始化放到循环体里，就会每轮重置。": "After the loop, the variable keeps its final value. Initializing inside the loop resets it every iteration.",
  "用表格追踪：初值 1 → 加 3 得 4 → 加 5 得 9。": "Trace the values: start at 1, add 3 to get 4, then add 5 to get 9.",
  "如果每轮开头都执行 total = 1，会发生什么？": "What happens if every iteration starts with total = 1?",
  "break 与 continue": "break versus continue",
  "break 退出当前循环；continue 跳过本轮剩余语句。": "break exits the current loop; continue skips the rest of the current iteration.",
  "控制当前循环的执行路径": "Control execution within a loop",
  "break 立即退出当前这层循环；continue 只跳过本轮剩余语句，接着开始下一轮。": "break immediately exits the current loop. continue skips the remaining statements in this iteration and starts the next one.",
  "判断输出时，注意 print 在跳转语句之前还是之后。遇到跳转后的语句不一定有机会执行。": "When predicting output, check whether print occurs before or after break or continue.",
  "3 跳过本轮打印；5 结束循环；只有 2 和 4 被打印。": "3 skips printing; 5 ends the loop. Only 2 and 4 are printed.",
  "continue 换成 break 后，还会打印 4 吗？": "If continue became break, would 4 still be printed?",
  "while 在每轮前检查条件": "while checks before each iteration",
  "先判断条件，再执行循环体；初次条件为假时执行零次。": "Check the condition before running the body. An initially false condition means zero iterations.",
  "理解先判断、再执行、再更新的循环": "Understand the check, execute and update cycle",
  "while 在进入循环体之前检查条件，每一轮开始前都会重新检查。初始条件为假时可以执行零次。": "while checks its condition before entering the body and again before every iteration. An initially false condition runs the body zero times.",
  "循环体通常需要更新影响条件的变量，否则可能一直无法退出。追踪时先判断，再写本轮输出，再更新变量。": "The body usually updates a value that affects the condition. Otherwise, the loop may never stop.",
  "更新到 5 后，下一次检查 5 < 5 为假，因此结束。": "After n becomes 5, the next check of 5 < 5 is false, so the loop ends.",
  "如果一开始 n 就是 5，循环体执行几次？": "If n starts at 5, how many times does the loop body run?",
  "print 不等于 return": "print is not return",
  "print 显示内容；没有 return 的函数默认返回 None。": "print displays a value; a function without an executed return returns None.",
  "区分函数的输出副作用和返回值": "Distinguish printed output from a return value",
  "def 定义函数，调用函数名加括号才会执行函数体。print 把内容显示到屏幕，return 把一个值交给调用者。": "def defines a function. Calling its name with parentheses runs it. print displays content; return gives a value to the caller.",
  "函数没有执行 return 时默认返回 None。屏幕上看见的内容不一定就是返回值；外层 print 还能打印函数的返回值。": "Without an executed return, a function returns None. Printed content is not necessarily the return value; an outer print can display that return value.",
  "函数内部打印一次文字；赋给 result 的是隐式返回值 None。": "The function prints text once, but result receives the implicit return value None.",
  "要让 result 等于字符串“学习”，应修改哪条语句？": "Which statement should change to make result equal the string \"学习\"?",
  "return 立即结束函数": "return ends the function",
  "执行 return 后，函数中该次调用的后续语句不再执行。": "After return, later statements in that function call do not run.",
  "沿执行路径寻找真正的返回点": "Find the return that is actually reached",
  "执行到 return 时，这一次函数调用就结束了，值被交给调用者。函数体中紧接着的语句不会继续运行。": "When return executes, the current function call ends and gives its value to the caller. Following statements do not run.",
  "不同条件可以通往不同 return，但一次调用只会使用实际执行到的那个返回点。定义函数不会立即执行它。": "Different conditions may lead to different returns, but a call uses only the one it reaches. Defining a function does not run it.",
  "-2 满足第一个条件，第一条 return 结束调用。": "-2 satisfies the first condition, so the first return ends the call.",
  "调用 classify(0) 会经过哪一个返回点？": "Which return does classify(0) reach?",
  "位置参数与传参": "Positional arguments",
  "位置参数按调用顺序绑定，注意减法等运算的顺序。": "Positional arguments bind in call order. Subtraction and division depend on order.",
  "按位置把实参绑定到形参": "Bind arguments to parameters by position",
  "定义函数时括号中的名字是形参，调用时传入的值是实参。位置参数按照从左到右的顺序绑定。": "Names in a function definition are parameters; values supplied in a call are arguments. Positional arguments bind from left to right.",
  "绑定完成后，再按函数体中的表达式求值。参数名不会自动按数值大小或字母顺序重新排列。": "After binding, evaluate the function's expressions. Parameters are not reordered by value or alphabetically.",
  "交换实参会交换 a、b 的值；除法有顺序，结果因此不同。": "Swapping arguments swaps a and b. Division depends on order, so the results differ.",
  "对于 a - b，交换两个实参通常会怎样改变结果？": "How does swapping arguments usually affect a - b?",
  "局部变量与外部变量": "Local and outer variables",
  "函数内普通赋值创建局部绑定，不会改写同名外部变量。": "Ordinary assignment inside a function creates a local binding without replacing an outer binding of the same name.",
  "分别追踪函数内部与外部的绑定": "Track local and outer bindings separately",
  "函数内普通赋值通常创建局部变量绑定。它与函数外同名变量不是同一个绑定位置。": "Ordinary assignment inside a function generally creates a local binding, separate from an outer variable of the same name.",
  "本关只讨论普通赋值与简单值，不涉及 global、nonlocal 或可变对象的原地修改。函数可以把局部结果 return 给调用者。": "This lesson covers ordinary assignment and simple values, not global, nonlocal or in-place mutation. A function can return its local result.",
  "内部 value 绑定到 3，外部 value 仍绑定到 7。": "The inner value is bound to 3; the outer value stays bound to 7.",
  "如果想用返回值更新外部 value，可以在调用处怎样赋值？": "How could you assign the returned result to the outer value?",
  "分支未执行 return 时返回 None": "Missing return paths",
  "只有实际执行到的 return 决定返回值；走完函数仍无 return 则返回 None。": "Only an executed return supplies its value. Reaching the end without return gives None.",
  "检查每条执行路径有没有返回值": "Check whether every execution path returns a value",
  "有 return 的函数不代表每条路径都执行 return。条件不成立时，可能直接走到函数末尾。": "Having a return somewhere does not mean every path reaches it. A false condition may lead directly to the end of the function.",
  "走到末尾而没有执行 return，就返回 None。Python 不会自动推断一个相反的结果，也不会自动返回参数。": "Reaching the end without executing return gives None. Python does not infer an opposite answer or automatically return an argument.",
  "80 不满足条件，函数结束但没有执行 return。": "80 does not satisfy the condition, so the function ends without executing return.",
  "如果希望没有优惠时返回 0，应在哪条路径补上 return 0？": "Where should return 0 be added if no discount should mean zero?",
  "5 不大于 5，严格大于不包含相等。": "5 is not greater than 5. Strict greater-than excludes equality.",
  "大于等于包含相等，因此结果是 True。": "Greater-than-or-equal includes equality, so the result is True.",
  "第一个条件成立，后续 elif 不再执行。": "The first condition is true, so the later elif is not executed.",
  "n > 10 已成立，只输出“大”。": "n > 10 is already true, so only the string \"大\" is printed.",
  "左侧条件为 False，and 的结果为 False。": "The left condition is False, so and produces False.",
  "cold 为 True，两个布尔值的 or 结果为 True。": "cold is True, so the boolean or expression produces True.",
  "空列表在条件中为假，因此进入 else。": "An empty list is falsy, so the else branch runs.",
  "\"0\" 是非空字符串，在条件中为真。": "\"0\" is a nonempty string, so it is truthy.",
  "两个独立条件都成立，依次输出 A 和 B。": "Both independent conditions are true, so A and B are printed in order.",
  "6 同时能被 2 和 3 整除，两个 if 都执行。": "6 is divisible by both 2 and 3, so both if statements run.",
  "range(1, 4) 依次生成 1、2、3，不包含 4。": "range(1, 4) produces 1, 2 and 3, excluding 4.",
  "起点为 2，终点 5 不包含在序列中。": "The range starts at 2 and excludes the stop value 5.",
  "从 1 开始每次加 2，7 是不包含的终点。": "Starting at 1, add 2 each time. The stop value 7 is excluded.",
  "步长为 -2，生成 6、4、2，终点 0 不包含。": "A step of -2 produces 6, 4 and 2, excluding 0.",
  "total 依次为 1、3、6，循环结束后打印 6。": "total becomes 1, then 3, then 6. After the loop, 6 is printed.",
  "初值 2，加 2 得 4，再加 4 得 8。": "Start at 2, add 2 to get 4, then add 4 to get 8.",
  "n 为 2 时 break 终止整个循环，仅打印过 1。": "When n is 2, break ends the loop. Only 1 has been printed.",
  "n 为 2 时跳过 print，下一轮仍会打印 3。": "When n is 2, continue skips print. The next iteration still prints 3.",
  "初始 3 < 3 为假，不进入循环，只打印“结束”。": "Initially, 3 < 3 is false. The loop does not run; only \"结束\" is printed.",
  "依次打印 1、2；n 变为 3 后不再进入循环。": "The loop prints 1 and 2. Once n is 3, it does not run again.",
  "函数先打印 3，隐式返回 None，再打印 x 得到 None。": "The function prints 3, then implicitly returns None. Printing x displays None.",
  "调用 greet 先打印 Hi，其返回值 None 随后被外层 print 打印。": "greet first prints Hi. Its return value None is then printed by the outer print.",
  "return 2 立即结束函数，不执行 print(9)。": "return 2 ends the function immediately, so print(9) does not run.",
  "第一个 return 已结束调用，第二个 return 不执行。": "The first return ends the call. The second return is not executed.",
  "a 绑定 2，b 绑定 5，2 - 5 = -3。": "a is 2 and b is 5, so 2 - 5 = -3.",
  "a 为 B，b 为 A，连接后的字符串是 B-A。": "a is B and b is A, so concatenation produces B-A.",
  "函数内部 x 为 2，外部 x 保持 10。": "Inside the function x is 2; the outer x remains 10.",
  "局部 name 为“内”，外部 name 仍为“外”。": "The local name is \"内\" and the outer name remains \"外\".",
  "0 > 0 为假，没有执行 return，默认返回 None。": "0 > 0 is false, so return is not executed and the function returns None.",
  "3 为奇数，条件不成立，没有显式返回值，因此返回 None。": "3 is odd, so the condition is false. Without an explicit return on this path, the result is None.",
  "条件判断": "Conditionals",
  "循环": "Loops",
  "函数与返回值": "Functions and returns",
  "下面代码的完整输出是什么？": "What is the complete output of this code?",
  "记录保存在运行服务的电脑": "Records are saved on the computer running the server",
  "range(start, 0, -1) 可以描述这段倒计时。": "range(start, 0, -1) describes this countdown.",
  "weight是非负整数。fragile为真时总是返回 \"轻放\"；否则weight大于5返回 \"货运\"，其余返回 \"普通\"。": "weight is a nonnegative integer. If fragile is true, always return \"轻放\" (handle gently). Otherwise, return \"货运\" (freight) if weight > 5, or \"普通\" (standard) for other weights. Return the exact strings shown.",
  "三个参数依次是什么？尝试从第一个值加一次步长。": "Identify the three arguments in order. Start with the first value and add the step once.",
  "云朵快递分拣站": "Cloud Parcel Sorting Station",
  "从上往下找第一个成立的条件，并观察后面用的是 elif 还是独立 if。": "Find the first true condition from top to bottom. Check whether the next statement is elif or a separate if.",
  "代入参数后，判断执行路径上是否真的走到了 return。": "Substitute the arguments and check whether the execution path actually reaches return.",
  "你是星港入口的程序员。飞船需要能量和通行证才能进入补给港。请帮门卫机器人作出决定。": "You program the entrance to a spaceport. Ships need energy and a badge to enter. Help the gate robot decide.",
  "使用 if / elif / else，并用 return 返回文字。不要只 print。": "Use if / elif / else and return the required string. Do not only print it.",
  "先代入初始值判断条件，再模拟变量更新后下一次条件判断。": "Check the initial condition, then simulate an update and the next condition check.",
  "先分别写出左右条件的真假，再考虑它们如何组合。": "Write down the truth value of each condition before combining them.",
  "先判断两个数是否相等，再检查比较符号是否允许相等。": "Check whether the values are equal, then whether the operator includes equality.",
  "先处理能量不足的情况，再考虑通行证。": "Handle low energy first, then check the badge.",
  "先按年龄确定基本票价，注意6岁和18岁的边界。": "Set the base price by age first. Pay attention to the boundaries at 6 and 18.",
  "先检查能量：低于20返回 \"充能\"；否则有通行证返回 \"放行\"，没有则返回 \"等待\"。": "Check energy first: below 20, return \"充能\" (recharge). Otherwise return \"放行\" (enter) with a badge, or \"等待\" (wait) without one. Return these exact strings.",
  "先确认变量的类型，再区分空值与非空值。": "Identify the type first, then distinguish empty from nonempty values.",
  "免费票保持0；只有非免费且是会员时才减3。": "Free tickets stay at 0. Subtract 3 only for a member with a nonfree ticket.",
  "分两栏记录函数内部和函数外部的同名变量。": "Use separate columns for the local and outer variable of the same name.",
  "分别记录屏幕显示了什么，以及函数交给调用者的值是什么。": "Track what appears on screen separately from the value returned to the caller.",
  "列出起点，再逐个增加，检查终点本身是否应当列入。": "List the start and increment each value, checking whether the stop value should be included.",
  "发射台需要一个倒计时序列，播报机器人会按你返回的列表读出每个数字。": "The launchpad needs a countdown sequence. A robot will read every number in the list you return.",
  "年龄小于6岁免费；6到17岁票价8；18岁及以上票价15。会员在非免费票价基础上减3。输入年龄为非负整数，member为布尔值。": "Ages below 6 travel free; ages 6–17 pay 8; ages 18+ pay 15. Members get 3 off a nonfree ticket. age is a nonnegative integer and member is a boolean.",
  "快递机器人必须为每个包裹给出明确路线，不能让任何包裹因为缺少返回值而消失。": "Every parcel needs a clear route. Do not let a missing return leave a parcel without a destination.",
  "找到触发跳转的那一轮，区分结束循环和跳过本轮。": "Find the iteration that triggers the jump. Distinguish leaving the loop from skipping an iteration.",
  "把累加器放在循环外初始化。": "Initialize the accumulator outside the loop.",
  "按位置将实参代入形参，再计算表达式，注意顺序。": "Bind arguments to parameters by position before evaluating the expression. Watch the order.",
  "按顺序把三个参数代入表达式。": "Substitute the three arguments into the expression in order.",
  "探险机器人的金币袋": "The Explorer Robot's Coin Bag",
  "数一数代码里有几个独立的 if，每个是否都需要判断。": "Count the independent if statements and check each one.",
  "易碎条件优先于重量条件。": "The fragile condition takes priority over weight.",
  "星港通行证": "Spaceport Entry Pass",
  "月球咖啡馆结账": "Moon Cafe Checkout",
  "月球咖啡馆要把结账结果传给收银屏幕。打印金额还不够，收银机需要拿到函数返回的数字。": "The cafe needs to send the bill to its register. Printing is not enough: the register needs a returned number.",
  "机器人在遗迹中拾取宝物。扫描器给出一串整数：正数是金币，零是空格，负数是陷阱。": "A robot explores ruins. Positive integers are coins, zero is an empty space and negative integers are traps.",
  "森林列车售票员": "Forest Train Tickets",
  "每轮减少1；停止时不把0放入结果。": "Decrease by 1 each iteration and stop without adding 0.",
  "每轮判断 coin > 0，只在成立时更新 total。": "Check coin > 0 each iteration and update total only when true.",
  "沿着本次调用的执行路径，找到第一个实际执行的 return。": "Follow this call's execution path to the first return actually reached.",
  "注意重量等于5时走哪条路径，并为最后一种情况写return。": "Check the path for weight equal to 5. Include a return for the final case.",
  "火箭发射倒计时": "Rocket Launch Countdown",
  "画一个小表，分别写初值、每轮加上的数和更新后的总值。": "Make a table showing the initial value, each added number and the updated total.",
  "精灵列车准备发车！售票机需要根据旅客年龄与会员身份算出车票价格。": "The forest train is ready! Calculate ticket prices using the passenger's age and membership.",
  "计算后检查是否小于0，两个路径都要返回值。": "After calculating, check for a negative amount. Both paths need a return value.",
  "输入非负整数 start，返回从 start 到 1 的递减列表，不包含0；start为0时返回空列表。可以使用range或while。": "Given nonnegative integer start, return a descending list from start to 1, excluding 0. Return an empty list for 0. You may use range or while.",
  "返回 quantity * unit_price - coupon 的结果；金额不能为负，若计算结果小于0返回0。输入均为非负整数。": "Return quantity * unit_price - coupon, but return 0 if it would be negative. All inputs are nonnegative integers.",
  "遍历 coins，把所有正数加起来，忽略零和负数，返回总金币数。空列表返回0。": "Loop over coins and sum the positive numbers, ignoring zero and negatives. Return 0 for an empty list.",
  " 已使用规则反馈。": " Rule feedback is shown instead.",
  "AI 为补充证据，不能确定你存在该误区。": "AI provides supporting evidence, not a definite diagnosis.",
  "AI提示": "AI hint",
  "AI讲解": "AI explanation",
  "AI讲解依据检查未通过，已采用标准解析。": "The AI explanation failed its evidence check. The standard explanation is shown.",
  "AI说明": "AI note",
  "GLM-4.7响应超时，可以点击“分析我的思路”重试。": "GLM-4.7 timed out. Click “Analyze my reasoning” to retry.",
  "GLM-4.7密钥认证失败（401），请在服务端更新有效API密钥并重启；不是你的答案无效。": "GLM-4.7 authentication failed (401). Update the server API key and restart. This does not mean your answer is invalid.",
  "GLM-4.7服务拒绝请求，请检查模型配置或稍后重试。": "GLM-4.7 rejected the request. Check the model configuration or try later.",
  "GLM-4.7返回格式未通过检查；不是你的想法无效，可以重试。": "GLM-4.7's response format failed validation. Your reasoning is not invalid; you can retry.",
  "GLM-4.7额度或请求频率受限。": "GLM-4.7 quota or request-rate limit reached.",
  "不允许以下划线开头的内部名称": "Internal names starting with an underscore are not allowed",
  "不支持该函数调用；不能导入模块、读写文件或访问网络": "This function call is not supported. Imports, files and network access are disabled",
  "不支持该属性访问：": "Unsupported attribute: ",
  "代码": "Code",
  "代码最多20,000字符": "Code must not exceed 20,000 characters",
  "代码结构过于复杂": "The code structure is too complex",
  "代码草稿格式不正确": "Invalid code draft format",
  "作答记录格式不正确": "Invalid attempt format",
  "另一页面已修改进度，请先导出当前记录，再刷新或重新导入。": "Another page changed your progress. Export your current records, then refresh or import again.",
  "团队AI口令不正确。": "The team AI access code is incorrect.",
  "字的文本": "characters",
  "尚未配置GLM-4.7及团队口令，使用规则反馈。": "GLM-4.7 and the team access code are not configured. Rule feedback is shown.",
  "当前密钥没有权限访问该GLM-4.7服务或模型。": "This key does not have permission to access the GLM-4.7 service or model.",
  "必须为不超过": "must be text of at most",
  "接口不存在": "Endpoint not found",
  "接口地址配置无效。": "Invalid API base URL.",
  "提示次数不正确": "Invalid hint count",
  "文件不存在": "File not found",
  "文本常量过长": "String literal is too long",
  "无法验证GLM-4.7的HTTPS证书，请检查Python根证书配置；不是你的答案无效。": "GLM-4.7's HTTPS certificate could not be verified. Check Python's root certificates; your answer is not invalid.",
  "时间格式不正确": "Invalid timestamp format",
  "暂时无法连接GLM-4.7，请检查网络后重试。": "Cannot connect to GLM-4.7. Check your network and retry.",
  "服务器本小时AI请求已达60次，使用规则反馈。": "The server has reached 60 AI requests this hour. Rule feedback is shown.",
  "服务暂时无法保存或处理请求，请保留备份后重试。": "The server cannot save or process this request. Keep a backup and try again.",
  "未知概念": "Unknown concept",
  "未知编程任务": "Unknown coding task",
  "未知诊断概念": "Unknown diagnosis concept",
  "未配置GLM-4.7密钥。": "GLM-4.7 API key is not configured.",
  "本次答对，继续用不同题目验证理解。": "Correct this time. Check your understanding with different questions.",
  "本环境不支持装饰器、返回注解或泛型": "Decorators, return annotations and generics are not supported",
  "本环境请先省略类型注解": "Please omit type annotations in this environment",
  "格式不正确或记录过多": "has an invalid format or too many records",
  "模型响应过长。": "The model response was too long.",
  "模型引用或标签校验失败。": "The model's quotation or concept label failed validation.",
  "模型输出未完成。": "The model output was incomplete.",
  "版本号不正确": "Invalid revision number",
  "理由": "Reasoning",
  "理由不足，暂不判断误区。": "Not enough evidence to identify a misconception.",
  "结果": "Result",
  "编程记录不正确": "Invalid coding record",
  "编程记录标识重复": "Duplicate coding record ID",
  "行：本练习环境不支持 ": ": this practice environment does not support ",
  "记录标识": "Record ID",
  "记录标识为空或重复": "Record ID is empty or duplicated",
  "访问地址未配置，请设置PUBLIC_ORIGIN。": "This address is not configured. Set PUBLIC_ORIGIN.",
  "语法白名单。学生代码仅在可终止的浏览器Worker中执行，不在服务器执行。": "Syntax allowlist. Learner code runs only in a terminable browser Worker, never on the server.",
  "请求不完整": "Incomplete request",
  "请求为空或超过10 MB": "Request is empty or exceeds 10 MB",
  "请求来源不匹配": "Request origin does not match",
  "请求格式不正确": "Invalid request format",
  "请选择 PySteps 版本1的备份": "Choose a PySteps version 1 backup",
  "请选择有效选项": "Choose a valid option",
  "课程概念不匹配": "Course concept does not match",
  "输入格式无效，请检查记录、选项及字段长度。": "Invalid input. Check records, options and field lengths.",
  "连接GLM-4.7时发生网络错误，请稍后重试。": "A network error occurred while connecting to GLM-4.7. Try again later.",
  "需要JSON请求": "JSON request required",
  "非有限数字": "Non-finite number",
  "题目不存在": "Question not found",
  "；仅支持基础计算、条件、循环和函数。": "; only basic calculations, conditions, loops and functions are supported.",
  "你选择的输出为「": "Your selected output is “",
  "」，与此处的执行规则不一致。": "”, which does not match this code's execution.",
  "记录保存在服务器 SQLite": "Records are saved in server SQLite",
  "记录保存在": "Records are saved in ",
  "记录保存在当前服务器": "Records are saved on the current server",
  "记录已保存到服务器 SQLite": "Records are saved in server SQLite",
  "通过": "Passed",
  "条记录": "records",
  "从哪里开始学习？": "Where should I start?",
  "我想练习答题": "I want to practise questions",
  "我想练习写代码": "I want to practise coding",
  "建议从「学习地图」的基础导学开始，按条件判断、循环、函数的顺序逐步学习。每关完成阅读并独立答对两道题，就能继续前进。": "Start with the introductions on the Learning Map, then explore conditionals, loops and functions. Read each lesson and independently answer two questions correctly to move on.",
  "可以去「自由练习」做题。答错时先写下自己的思路，再使用题目里的 AI 思路分析获取针对性反馈。": "Visit Free Practice to answer questions. If you make a mistake, share your reasoning and use the AI analysis for targeted feedback.",
  "去「趣味编程」选择一个任务，在编辑器里编写并运行 Python 代码。": "Choose a task in Coding Challenges, then write and run Python in the editor.",
  "你好呀，我是PiPo！我可以带你找到学习地图、答题练习和编程任务。想先做什么？": "Hi, I’m PiPo! I can help you find the Learning Map, practice questions and coding challenges. Where would you like to start?",
  "现在去看看": "Go there now",
  "打开相关页面": "Open this page",
  "答错后可以在练习页填写你的解题思路，再点击「分析我的思路」。这是平台现有的 AI 反馈功能；这里的自由输入暂用于学习导航。": "After an incorrect answer, enter your reasoning on the practice page and select Analyse my reasoning for AI feedback. This chat provides learning navigation.",
  "嗨～学习上有什么想问的？": "Hi! Need help finding your next lesson?",
  "PiPo学习助手": "PiPo Learning Assistant",
  "陪你一起学 Python": "Learning Python with you",
  "关闭助手": "Close assistant",
  "告诉PiPo你想做什么": "Tell PiPo what you want to do",
  "问问怎么开始学习…": "Ask how to get started…",
  "发送消息": "Send message",
  "自由输入提供学习导航；题目 AI 分析请在练习页使用。": "This chat helps you navigate. Use the practice page for AI analysis of your reasoning.",
  "关闭PiPo学习助手": "Close PiPo Learning Assistant",
  "打开PiPo学习助手": "Open PiPo Learning Assistant",
  "紫色PiPo AI 助手": "Purple PiPo AI assistant",
  "学校接口需要应用密钥（App Key），当前提供的是账户密钥（Account Key）；请在服务端更换为应用密钥并重启。": "The school endpoint requires an App Key, but an Account Key was supplied. Update the server configuration with an App Key and restart."
}
```
