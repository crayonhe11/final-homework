# PySteps 使用说明 / User Guide

## 中文版

### 1. 这个程序用来做什么？

PySteps 是第 8 组制作的 Python 入门学习网页。你可以阅读概念、完成选择题、补充答题想法、练习本章编程，并查看学习记录。内容包括条件判断、循环、函数与返回值，共 15 个概念、30 道选择题和 6 项编程任务。

第一次打开默认显示英语。点击页面上方的 **Switch language / 切换语言**，即可切换中文；程序会记住你的选择。代码、你的输入和题目要求的返回值不会被翻译。

### 2. 开始前准备

你需要一台装有 **Python 3.10 或更新版本**的 Windows 或 Mac 电脑，以及浏览器。先把项目压缩包完整解压；找到同一文件夹里的 `main.py` 和本说明。不要在压缩包内部直接运行。

正常使用不需要安装 Node.js、npm、Docker 或其他 Python 库。随项目提供的 `web/static/` 文件夹必须保留。没有模型密钥也能完成导学、答题、规则反馈、推荐、编程和备份。

### 3. 在 Windows / Mac 上启动

1. 打开解压后的项目文件夹。
2. Windows：在文件夹空白处右键，选择“在终端中打开”（若菜单没有，可打开终端并用 `cd` 进入该文件夹）。Mac：打开“终端”，输入 `cd `，把项目文件夹拖入终端，然后按回车。
3. 按你的系统，在同一个终端输入下面相应的一条命令：

| 系统 | 启动命令 |
|---|---|
| Windows | `py main.py --port 8011 --open` |
| Mac | `python3 main.py --port 8011 --open` |
| 已经可以使用 `python` 的电脑 | `python main.py --port 8011 --open` |

4. 浏览器通常会自动打开。若没有，手动访问 **http://127.0.0.1:8011/**。最终以终端显示的网址为准。
5. **使用期间保留终端窗口运行。** 关闭网页不会关闭服务；停止服务请回到终端按 `Control+C`。Mac 这里同样使用 Control，不是 Command。

`main.py` 默认端口就是 **8011**。如果显示 `Address already in use`，先检查是否已经开着旧服务；也可以把命令中的 `8011` 换为 `8012`，再访问对应网址。不要重复启动多个窗口解决同一个端口占用。

如果终端说找不到 `py`、`python3` 或 `python`，说明 Python 尚未安装或命令未配置。若提示找不到 `main.py`，说明终端尚未进入正确的项目文件夹。双击 `打开网页版.html` 只会显示启动说明，不会启动 Python 服务。

### 4. 第一次学习：跟着完成一次完整流程

1. 在“学习地图”点击“开始入门导学”，了解变量、输出与缩进。
2. 阅读后点击“我理解了，开启第一章”，进入第一个概念“比较运算的等号边界”。
3. 阅读概念、示例代码与输出，点击“我理解了，开始验证”。
4. 选择一个答案，点击“提交答案”；未选答案时会提示你先选择。
5. 查看反馈和标准解析。答对后，原提交按钮的位置会出现继续操作；答错后，可在“补充或修改你的思路”中补充想法。补充同一次作答不会增加作答次数。
6. 点击“练一道针对性题目”继续练习，或点击“本章趣味编程”直接动手写代码。
7. 在左侧“学习进度”查看作答数、正确率、概念状态和曲线；“错题回顾”可以查看刚才的理由和解析。

完成一个课程概念需要先读导学，再独立答对该概念的两道不同题目，且未使用提示。自由练习和使用提示的作答仍会保存，但不算课程过关。锁定的概念允许预览；课程验证需先满足前置条件。

### 5. 怎样做编程练习？

点击左侧“趣味编程”，选择章节，再选本章任务。每章有两个任务，**不用先完成选择题**。

1. 阅读“完成目标”和输入/输出示例。
2. 在编辑器补全代码，保留题目指定函数名，按要求使用 `return`。
3. “运行示例”只运行前两个案例，供你检查思路；它不记录任务通过。
4. “检查答案”运行该任务全部案例，并记录本次结果。全部通过才显示本次任务通过。
5. 出错时查看错误说明和行号，修改后再检查。“停止运行”可以中止正在执行的代码；“恢复初始代码”会先询问你是否确认。

编辑中的代码会自动保存。运行环境支持基础计算、条件、循环、函数和部分集合操作，不支持导入模块、文件或网络操作。首次加载最多等待 60 秒，代码运行超过 4 秒会被停止。请按题目原样返回文字；即使界面为英语，任务要求的中文返回值也不能自行改成英语。

### 6. GLM-4.7 和 PiPo 怎么使用？（可选）

**使用团队已经配置好的服务时：** 只需向服务维护者获取“团队 AI 口令”，在网页的相应输入框填写；不需要获取 API 密钥。

答错后补充理由，点击“分析我的思路”，GLM-4.7 会尝试根据你的原话提供概念线索、讲解和提示。模型不会改变标准答案。一次错误只代表可能的误区。

右下角打开 PiPo，填写同一个团队口令，再输入例如“我不懂循环，帮我挑一道循环练习并打开”。PiPo 可以查看真实进度、读取课程、挑选现有练习并打开一项内容。回复中可展开查看执行的工具。模型生成新练习、改分或代替你完成课程不属于该功能。

学校平台较慢时，诊断可能等待约一分钟。超时会保留规则反馈；不要连续反复点击重试，每次新请求可能再次扣积分。PiPo 的“停止本轮”停止网页等待与后续页面操作，不能保证取消学校已经受理的请求。

**维护者配置：** 如果还没有 `config.local.json`，复制 `config.example.json` 并改名为 `config.local.json`；如果已有，直接修改原文件，不要覆盖已有密钥或团队口令。文件放在 `main.py` 同一目录。

```json
{
  "OPENAI_API_KEY": "",
  "OPENAI_MODEL": "glm-4.7",
  "OPENAI_BASE_URL": "https://maas.eduhk.hk/api/v1",
  "AI_AGENT_MODE": "json",
  "TEAM_ACCESS_CODE": "",
  "PUBLIC_ORIGIN": ""
}
```

- `OPENAI_API_KEY`：学校该应用的 **App Key**，不要添加 `Bearer `。当前 `/api/v1/chat/completions` 应用接口曾明确拒绝 Account Key；接口类型以学校管理员说明为准。
- `TEAM_ACCESS_CODE`：自行设置至少 12 字符的团队口令，网页填的是这个值。
- `OPENAI_MODEL`：配置目标为智谱 `glm-4.7`，通过学校 OpenAI 兼容协议访问。学校应用也可能有自己的模型设置，应在平台确认实际路由。
- `AI_AGENT_MODE`：学校网关使用 `json`；只有确认网关支持原生工具调用时才使用 `native`。
- `PUBLIC_ORIGIN`：本机使用留空。

保存后先停止服务，再用原命令启动并刷新网页。“等待服务端配置”表示服务未读取到密钥或合格的团队口令；确认已配置不等于已验证学校连通性。若仍出现此提示，检查键名是否为 `OPENAI_API_KEY`，并检查环境变量是否覆盖本地文件。程序不会自动读取 `.env`。

密钥只保留在本地配置或服务端环境变量中；不要发给同学或放进提交包。学校将收到诊断所需的题目和理由，或 PiPo 的学习目标、对话片段及工具读取的学习摘要。页面刷新后需重新填写团队口令，PiPo 对话也会清空。

### 7. 保存、备份和换设备

学习记录保存在项目的 `runtime/learning.sqlite3`，页面显示“保存到 SQLite”时表示当前服务保存完成。相同电脑仍需使用相同浏览器和相同网址；端口、浏览器或设备改变都可能显示另一个学习空间。

在“学习进度”点击“导出学习记录”，会下载 `pysteps-backup-日期.json`。换设备后，在新服务的“学习进度”点击“导入备份”，选择文件，检查提示后点击“确认导入”。**导入会替换当前空间的记录，建议先导出当前进度。** 取消不会替换。导入时选择题重新判分，AI 反馈恢复为标准解析。

项目没有账号登录或自动跨设备同步。若页面提示保存冲突，先导出当前记录，再刷新处理；不要反复覆盖。停止程序后保留整个 `runtime/` 文件夹，即可保留服务端数据。

### 8. 常见问题

| 看到的情况 | 怎么处理 |
|---|---|
| 地址打不开 | 确认终端还在运行，按终端打印的端口打开；本机不需要 VPN。 |
| `Address already in use` | 使用已运行的页面，或停止旧服务，或换端口。 |
| “缺少网页文件” | 完整解压项目，保留 `web/static/`；普通用户不需要重新构建。 |
| “等待服务端配置” | 检查本地配置字段、团队口令长度和环境变量；重启服务并刷新。 |
| App Key / Account Key 错误 | 使用学校此接口要求的应用密钥，或向管理员确认账户密钥的正确调用入口。 |
| AI 超时或返回不合格 | 阅读已有规则反馈；稍后手动重试；每次请求可能收费。 |
| Python 编程环境无法加载 | 保留完整项目及本地 Pyodide 文件，刷新网页重试。 |
| 保存冲突 | 先导出，再刷新；避免同时在两个页面修改同一空间。 |
| 改代码后还是旧界面 | 开发者需重新构建前端；普通用户刷新收到的最新版即可。 |

同学在另一台电脑访问你的 `127.0.0.1` 地址无法连接；这是各自电脑的本机地址。团队远程使用需要一台可连接的服务器。局域网演示由维护者配置 `PUBLIC_ORIGIN` 为准确来源，并以 `--host 0.0.0.0` 启动；不要把未配置的本机启动当作已部署网站。

### 9. 开发、测试与作业材料

运行测试：

```bash
python -m unittest discover -s tests -t . -v
```

Mac 可把 `python` 换为 `python3`，Windows 可换为 `py`。测试使用临时数据库和模拟模型，不会调用学校付费模型。`tests/test_http.py` 测试主要 HTTP 接口；`test_core.py` 测试规则与数据；`test_agent.py` 测试 PiPo 工具；`test_language.py` 测试语言；`test_main.py` 测试真实启动入口。最新数量、逐项用途及实际验收结果见 [验收记录](submission/验收记录_中英.md)。

只有修改前端源码的开发者才需要 Node.js 22 和 npm：

```bash
cd web
npm ci
npm run check
npm run build
```

项目文件：`main.py` 是入口，`backend/` 是 Python 实现，`data/` 是题库和导学，`web/` 是网页源码与已构建文件，`tests/` 是测试，`SPEC.md` 是可重建的功能规格。完整数据也嵌入 SPEC 的规范附录。运行 `python scripts/package_rebuild.py` 生成不含原实现的独立 AI 重建输入包 `dist/group8_rebuild_inputs.zip`，并校验规范数据。测试验收需按规格的输入和预期结果执行。

打包作业：

```bash
python scripts/package_submission.py --group 8
```

生成 `dist/group8_project.zip`；打包脚本排除本地密钥、数据库、Git 历史和开发依赖。项目旁的旧版完整备份属于私有恢复材料，包含本地配置，**不要把旧版备份当作作业提交**。课堂 PPT、实际视频、个人报告和真实代码审查记录仍需按课程要求由组员完成或确认。

课程联系：Lecture03 的函数、类、集合与排序用于学习引擎；Lecture04 的提示词要素用于诊断，README 面向人；Lecture05 的模型与工具循环用于 PiPo；Lecture06 的功能/非功能需求及验收匹配用于 SPEC 和测试。具体页码、测试映射、独立重建步骤见 SPEC。引用与许可证在 `licenses/`；使用 React、Lucide、Pyodide 等外部组件，不宣称从零实现这些组件。

### 10. 自动检查与交付（CI/CD）

每次推送、PR更新或手动触发Actions会运行：三系统×两Python版本测试→网页重新构建→用本次构建启动真实服务并运行8个黑盒契约→打包与隐私检查→Docker临时部署与同样8接口验收。失败保留日志并阻止后续阶段。测试服务明确清空模型密钥和口令，不消耗学校积分。

打开仓库的Actions，选择本次运行：各系统的tests-*、integration-reports、container-reports可下载日志；group8-delivery包含作业包、重建包和SHA256SUMS。日志保留7天，交付包14天。只有main分支通过全部检查后才自动创建GitHub预发布版本，便于较长期下载。PR只测试和产生交付物，不发布main版本。

这里完成的是持续集成、临时验收环境部署与可部署交付物发布。生产服务器尚未配置；GitHub预发布不是运行中的学习网站。维护者部署容器时，先解压最新版作业包，在目录中运行：

```bash
docker build -t pysteps:group8 .
docker run -d --name pysteps -p 8011:8000 -v pysteps-data:/data -e PUBLIC_ORIGIN=http://127.0.0.1:8011 pysteps:group8
```

本机打开http://127.0.0.1:8011/。团队服务器改用实际可达的域名/来源；模型凭据用服务端环境或秘密变量传入，不写入镜像。课程Lecture09的第5–9页对应目标/测试/执行/断言分析，第11/13/16页对应工作流与环境，第19–20页用真实PR检查记录展示。结果须以具体提交SHA的Actions日志为准。

---

## English Version

### 1. What is PySteps?

PySteps is Group 8's Python learning application. Read concepts, answer quizzes, explain your mistakes, try chapter coding tasks and review your progress. The curriculum contains conditionals, loops, and functions/returns: 15 concepts, 30 multiple-choice questions and six coding tasks.

The first visit uses English. Select **Switch language / 切换语言** at the top to change language. The choice is remembered; code, your input and exact expected return values are unchanged.

### 2. Before you start

Use Windows or macOS with **Python 3.10 or later** and a modern browser. Extract the whole project first and find `main.py` beside this document. Do not run it inside the ZIP.

Normal use requires no Node.js, npm, Docker or third-party Python packages. Keep the supplied `web/static/` folder. Lessons, quizzes, standard feedback, recommendations, coding and backups work without a model key.

### 3. Start on Windows or Mac

1. Open the extracted project folder.
2. On Windows, right-click inside it and choose “Open in Terminal”, if available. Otherwise open a terminal and use `cd` to enter that folder. On Mac, open Terminal, type `cd `, drag the project folder into Terminal and press Return.
3. Run the appropriate command:

| System | Command |
|---|---|
| Windows | `py main.py --port 8011 --open` |
| Mac | `python3 main.py --port 8011 --open` |
| A computer with the `python` command | `python main.py --port 8011 --open` |

4. A browser normally opens automatically. Otherwise open **http://127.0.0.1:8011/**. Always follow the address printed by your terminal.
5. **Keep Terminal running while learning.** Closing the webpage does not stop the server. Press `Control+C` in Terminal to stop, including on Mac.

The default port is **8011**. For `Address already in use`, check whether your existing server is already running. Alternatively change `8011` to `8012` in the command and use the new address. Repeatedly opening terminals does not resolve a port conflict.

If `py`, `python3` or `python` is unavailable, install/configure Python first. If `main.py` cannot be found, enter the correct project directory. Double-clicking `打开网页版.html` displays instructions; it does not start Python.

### 4. Complete your first learning session

1. On **Learning map**, select **Start the introduction** and read about variables, output and indentation.
2. Select **I understand. Open chapter one** to enter **Comparison boundaries**.
3. Read its explanation, code and output, then select **I understand. Try the questions**.
4. Choose an option and select **Submit answer**. An empty selection produces a reminder.
5. Read the feedback. The submit position becomes a continuation control. After a wrong answer, use **Add or revise your reasoning**; this edits the same attempt without increasing the count.
6. Select **Try a targeted question**, or **Coding in this chapter** to write code immediately.
7. Open **Learning progress** to see counts, accuracy, concept states and the chart. **Review mistakes** shows your saved reason and the explanation.

Course completion requires reading the concept and independently answering both distinct concept questions correctly, without hints. Free practice and hinted answers are recorded but do not establish course completion. Locked lessons can be previewed; course checks require their prerequisites.

### 5. Try a coding challenge

Select **Coding challenges**, a chapter, then a task. Each chapter has two tasks. You can start without completing quizzes.

1. Read the goal and input/output examples.
2. Complete the editor code, retain the required function name and use `return` as requested.
3. **Run examples** executes the first two cases and does not record task completion.
4. **Check answer** executes every case and records the result; all cases must pass for that submission to pass.
5. Inspect errors and line numbers, edit and check again. **Stop execution** terminates running code. **Restore starter code** asks for confirmation.

Drafts save automatically. Supported features include basic computation, conditions, loops, functions and selected collection operations. Imports, files and network operations are unavailable. Runtime loading has a 60-second threshold; execution stops after four seconds. Keep exact return strings, including Chinese strings required by some English task instructions.

### 6. Use GLM-4.7 and PiPo (optional)

**For a service already configured by your team:** obtain its **team AI access code** from the operator and enter it on the webpage. You do not need the provider API key.

After a wrong answer, add a reason and select **Analyze my reasoning**. GLM-4.7 attempts to provide a possible concept clue, explanation and hint grounded in your text. It cannot change the standard answer. One mistake is not proof of a misconception.

Open PiPo at the lower right, enter the same team code and try “I do not understand loops. Pick a loop question and open it.” PiPo can inspect progress, read lessons, select existing practice and open one activity. Expand its tool trace to see executed calls. It cannot generate new bank questions, change grades or complete the course for you.

The school may take about a minute. Timeouts preserve standard feedback. Avoid repeated retries: each new request may consume credits. **Stop turn** ends browser waiting and pending page actions; it cannot guarantee cancellation of a request already accepted by the school.

**Operator configuration:** if `config.local.json` does not exist, copy `config.example.json` and rename the copy. If it already exists, edit it without replacing existing credentials. Keep it beside `main.py`.

```json
{
  "OPENAI_API_KEY": "",
  "OPENAI_MODEL": "glm-4.7",
  "OPENAI_BASE_URL": "https://maas.eduhk.hk/api/v1",
  "AI_AGENT_MODE": "json",
  "TEAM_ACCESS_CODE": "",
  "PUBLIC_ORIGIN": ""
}
```

- `OPENAI_API_KEY`: the school's application **App Key**, without `Bearer `. This application endpoint previously rejected an Account Key; confirm the correct key/endpoint type with the school.
- `TEAM_ACCESS_CODE`: choose at least 12 characters. This is the value entered on the webpage.
- `OPENAI_MODEL`: the configured Z.ai model is `glm-4.7`, accessed via an OpenAI-compatible school gateway. Verify actual routing in the school application settings.
- `AI_AGENT_MODE`: use `json` for the school gateway; use `native` only for verified native tool-call support.
- `PUBLIC_ORIGIN`: leave empty for local use.

Save, stop the server, restart with your original command and refresh. “Waiting for server configuration” means the server has not loaded a key and a valid team code. A configured flag does not prove provider connectivity. Check the exact `OPENAI_API_KEY` name and environment overrides. `.env` is not loaded automatically.

Keep credentials in local configuration or server environment variables; never distribute them or include them in submissions. The provider receives the required question/reason, or PiPo goal, bounded history and selected learning observations. Refreshing clears the page's team code and PiPo conversation.

### 7. Save, back up and change devices

The project saves learning data to `runtime/learning.sqlite3`. The saved indicator reflects this server. Reuse the same browser and address; changing browser, port or device can produce a different learning space.

In **Learning progress**, select **Export learning records** to download `pysteps-backup-date.json`. On another device, select **Import backup**, choose that file, review the dialog and select **Confirm import**. **Import replaces the current space; export it first if needed.** Cancel preserves it. Imported quiz answers are regraded and AI feedback is replaced by standard explanations.

There is no account login or automatic device synchronisation. For a save conflict, export before refreshing and reconciling changes. Retain `runtime/` after stopping the application to preserve server data.

### 8. Troubleshooting

| Symptom | Action |
|---|---|
| Address does not open | Keep Terminal running and follow its printed port; local use needs no VPN. |
| `Address already in use` | Use the existing server, stop it, or choose another port. |
| Missing browser distribution | Extract the whole project and keep `web/static/`; normal users need no build step. |
| Waiting for server configuration | Check local field names, code length and environment overrides; restart and refresh. |
| App Key / Account Key error | Obtain the key required by this endpoint or ask the administrator for the account-key endpoint. |
| AI timeout or rejected output | Use the standard feedback; retry manually later. New requests may consume credits. |
| Python runtime does not load | Keep the complete project/local Pyodide files and refresh. |
| Save conflict | Export before refreshing; avoid editing the same space in two tabs. |
| Old interface after source edits | Developers rebuild; ordinary users refresh the supplied latest distribution. |

Another computer cannot access your server through its own `127.0.0.1`. Remote teamwork needs a reachable server. For LAN demos, the operator sets `PUBLIC_ORIGIN` to the exact origin and starts with `--host 0.0.0.0`; a local launch is not a public deployment.

### 9. Development, tests and submission

Run:

```bash
python -m unittest discover -s tests -t . -v
```

Use `python3` on Mac or `py` on Windows if appropriate. Tests use temporary databases and simulated models, without paid school requests. `test_http.py` checks principal endpoints; `test_core.py` checks rules/data; `test_agent.py` checks PiPo tools; `test_language.py` checks translation/prompt handling; `test_main.py` checks the real entry point. See the [validation record](submission/验收记录_中英.md) for current counts, responsibilities and actual results.

Only frontend developers need Node.js 22 and npm:

```bash
cd web
npm ci
npm run check
npm run build
```

`main.py` is the entry point, `backend/` implements Python behaviour, `data/` supplies curriculum, `web/` contains source and bundled UI, and `tests/` contains verification. `SPEC.md` defines reconstruction contracts and embeds the exact content data in its normative appendix. Run `python scripts/package_rebuild.py` to create the source-free `dist/group8_rebuild_inputs.zip` and validate the embedded data. Validate against its inputs and expected outcomes.

Package Group 8's submission with:

```bash
python scripts/package_submission.py --group 8
```

This produces `dist/group8_project.zip`, excluding local credentials, databases, Git history and development dependencies. The adjacent old-version backup is a private recovery copy that includes local configuration: **do not submit it**. The actual video, individual reports and genuine human review records still need completion/confirmation by members under course requirements.

Course alignment: Lecture03 functions/classes/collections/sorting inform the engine; Lecture04 prompt elements inform diagnosis and human-facing documentation; Lecture05 model/tool loops inform PiPo; Lecture06 FR/NFR and matching verification inform SPEC/tests. SPEC records exact slides, traceability and independent reconstruction steps. Upstream licences are in `licenses/`; React, Lucide and Pyodide are external components, not original reimplementations.

### 10. Automated checks and delivery (CI/CD)

Pushes, PR updates and manual Actions runs trigger: three OSes × two Python versions; fresh browser build; main.py plus eight black-box HTTP contracts against that build; archive/privacy checks; then temporary Docker staging and eight HTTP contracts again. Failures retain reports and stop dependent stages. Staging explicitly disables provider credentials, avoiding school-model charges.

In an Actions run, download tests-*, integration-reports and container-reports for evidence. group8-delivery contains both ZIPs and SHA256SUMS. Reports remain seven days; delivery artifacts remain14days. After every gate passes on main, a versioned GitHub prerelease is published for longer-term downloads. PRs produce tests/artifacts but do not publish main releases.

This provides CI, temporary staging deployment and deployable release delivery. A production server is not configured; a GitHub release is not a running learning website. To deploy an extracted verified project with Docker:

```bash
docker build -t pysteps:group8 .
docker run -d --name pysteps -p 8011:8000 -v pysteps-data:/data -e PUBLIC_ORIGIN=http://127.0.0.1:8011 pysteps:group8
```

Openhttp://127.0.0.1:8011/. On a team server, use its reachable origin and supply model secrets through server variables, never an image. Lecture09 slides5–9 map to objectives/design/execution/assertion analysis;11/13/16to workflow/environments;19–20to actualPR checks. Verify results for the exact commitSHA in Actions.
