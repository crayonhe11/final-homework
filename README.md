# PySteps

Python 入门学习、错题反馈与练习推荐 / Python learning, mistake feedback and practice recommendation

[中文](#中文使用说明) · [English](#english-guide) · [软件规格 / SRS](SPEC.md)

## 中文使用说明

### 1. 项目用途

PySteps 帮助 Python 初学者完成“阅读概念 → 答题 → 解释思路 → 查看反馈 → 继续练习”的流程。当前内容包括条件判断、循环、函数与返回值，共 3 章、15 个概念、30 道选择题及 6 个编程任务（39 个参考测试案例）。

Python 后端负责判分、课程规则、推荐、复习计划和 SQLite 存储；浏览器提供 React 界面与 Pyodide 编程环境。可选 Kimi 分析只辅助解释错题理由，不决定标准答案。PiPo 小精灵通过预设回复和关键词提供导航，不是大模型聊天或自主代理。

### 2. 快速开始

需要 Python 3.10+、现代浏览器和完整解压的项目。使用随包网页成品时，无需安装 Python 第三方依赖、Node.js 或 Docker。

在包含 `main.py` 的文件夹打开终端：

```bash
python main.py --open
```

macOS 的 Python 命令若为 `python3`，使用 `python3 main.py --open`；Windows 也可以使用 `py main.py --open`。

默认地址为 **http://127.0.0.1:8010/**，以终端实际输出为准。保持终端运行，按 Ctrl+C 停止。不要直接双击静态网页替代启动服务。

```bash
# 端口冲突时使用另一端口
python main.py --port 8011 --open
# 指定数据库位置
python main.py --db runtime/learning.sqlite3
```

默认只监听本机。更换端口不会停止旧服务。`web/static/index.html` 缺失时应完整解压项目，或由开发成员重新构建前端。

### 3. 使用流程

1. 首次访问默认英语；右上角可切换中英文。
2. 阅读学习地图中的入门导学，再进入概念课程。课程按前置关系解锁；当前题库中，每个概念需完成阅读并无提示答对两道不同题。自由练习不计入课程解锁。
3. 提交选择题，可填写理由。错答后可修改理由并重新分析，更新原记录，不新增一次作答。
4. 进入推荐练习。推荐限定当前章节、排除当前题，优先考虑目标概念未做题和到期复习。它是规则排序，不是模型生成新题或能力自适应算法。
5. 编程任务可直接进入；运行示例检查前两例，检查答案执行全部任务案例。代码在浏览器 Worker 内运行。
6. 查看进度、错题及最近 14 个有作答日期的统计，定期导出 JSON 备份。

一次答错只提供可能的概念线索；课程过关不代表全面掌握知识。题库内容和反馈仍需要人工复核。

### 4. 可选 AI 配置

不配置 AI 仍可判题、查看固定反馈、推荐练习及进行编程。若启用，在项目根目录复制 `config.example.json` 为 `config.local.json`，填写后重启服务。也可以设置同名环境变量；环境变量优先，程序不自动加载 `.env`。

| 配置项 | 用途 |
|---|---|
| `MOONSHOT_API_KEY` | 服务端密钥，不加 `Bearer ` 前缀 |
| `MOONSHOT_MODEL` | 账户可用模型；代码默认 `kimi-k2.6`，默认名称不保证账户可用 |
| `MOONSHOT_BASE_URL` | `https://api.moonshot.cn/v1` 或 `https://api.moonshot.ai/v1`，与密钥对应 |
| `TEAM_ACCESS_CODE` | 至少 12 字符；在网页中输入此口令，而非 API 密钥 |
| `PUBLIC_ORIGIN` | 本机运行留空；外部访问时设置准确来源地址 |

只有错答且理由非空时才需要模型分析。请求会将题目代码、答案、标准解析、所选选项、理由和候选概念发送给配置的 Kimi 服务。密钥保留在服务端，不放入前端、截图或提交包。

后端请求超时参数为 30 秒，前端取消等待阈值为 40 秒；网络整体耗时不以此获得严格保证。每进程每小时最多受理 60 次模型请求，重启重置计数；这不是费用上限。没有自动重试或显式提示缓存，手动重试可能再次收费。无配置、服务故障或输出不合格时保留规则反馈；错误团队口令返回授权错误。

AI 输出需满足候选标签、理由原文引用和格式限制。若标签/理由引用无效，返回规则反馈；若标签和引文有效但答案或知识依据无效，保留通过校验的诊断字段，讲解与提示改用题库内容。校验不等于证明生成内容正确。

### 5. 保存与限制

默认数据库是 `runtime/learning.sqlite3`。随机浏览器 Cookie 对应独立学习空间，没有账号登录和自动跨设备同步。清除 Cookie、更换浏览器或访问主机名可能进入新空间。

通过 JSON 导出/导入迁移记录。导入经确认后替换当前空间，不合并；后端重新判分，并恢复规则反馈。保存发生版本冲突时，先备份当前内容再刷新处理。

每空间最多 10,000 条选择题记录、2,000 条代码记录；理由限 1,000 字符、代码限 20,000 字符；请求体限 10,000,000 字节。没有自动归档。

编程环境限制可用语法，禁用导入、文件操作等；Worker 加载和执行阈值分别为 60 秒与 4 秒，没有硬性内存配额。学习记录不是防篡改考试成绩。应用适合课程演示和小团队，未验证生产级负载。

### 6. 测试与贡献

在项目根目录运行：

```bash
python -m unittest discover -s tests -t . -v
```

2026-10-28 在 macOS/Python 3.12 环境重新执行，**21 个测试方法全部通过**。模型响应为模拟数据，HTTP 测试使用本地临时服务和数据库，不调用付费 API。方法数量不是测试场景数，也不是覆盖率；30 道选择题和 39 个编程参考案例包含在部分方法中。

本次未重新执行浏览器验收、真实模型评估或 Windows/Linux 测试。CI 已配置多系统矩阵，配置存在不等于远端运行通过。完整映射与待验收项见 [SPEC.md](SPEC.md)。

贡献步骤：先确定受影响的需求 ID 和预期结果，再修改代码与相关测试；运行回归检查；请另一位成员审查并复核问题；同步更新文档。新缺陷优先补能复现问题的测试，不追溯声称整个项目采用了测试先行。

只有修改前端源码时需要 Node.js 22（与 CI 配置一致）及 npm：

```bash
cd web
npm ci
npm run check
npm run build
```

普通启动使用 `web/static`；修改 `web/src`、`web/public` 或前端导入的数据后需要重新构建。后端和配置修改需要重启服务。

### 7. 文件导航与常见问题

| 路径 | 作用 |
|---|---|
| `main.py` | 统一启动入口与命令行参数 |
| `backend/domain.py` | 判分、课程状态、推荐、复习、输入校验 |
| `backend/ai.py` | 可选模型请求、输出校验与规则回退 |
| `backend/storage.py`, `backend/server.py` | SQLite 存储、HTTP 接口及访问检查 |
| `data/` | 题目、概念、导学与编程任务 |
| `web/src/`, `web/public/`, `web/static/` | 前端源代码、公开资源与构建产物 |
| `tests/`, `.github/workflows/` | 自动测试与持续集成配置 |
| `SPEC.md` | 需求、接口、约束、验收和测试对应关系 |
| `submission/`, `licenses/` | 提交辅助材料及依赖许可证 |

| 问题 | 处理 |
|---|---|
| 端口占用 | 停止旧进程或指定其他端口 |
| AI 不可用 | 检查服务端配置、团队口令和网络，修改后重启；固定反馈仍可使用 |
| HTTPS 证书错误 | 修复系统/Python 证书，不关闭证书校验 |
| 页面仍是旧版 | 检查构建产物后刷新；不要只改前端源码 |
| 编程环境加载失败 | 保持后端运行并保留完整的 `web/static/pyodide/` 资源 |
| 保存冲突 | 导出当前备份，再刷新协调版本 |

### 8. 提交与资源说明

用实际组号替换下列示例中的 `N`：

```bash
python scripts/package_submission.py --group N
```

输出 `dist/groupN_project.zip`。打包脚本排除本地密钥、学习数据库、Git 历史及 `node_modules`。提交前仍应解压检查入口、运行资源、测试和文档；PPT、视频和个人报告按 Moodle 的要求提交。

运行依赖与开发工具包括 [Python 标准库](https://docs.python.org/3/library/)、[React](https://github.com/facebook/react)、[Lucide](https://github.com/lucide-icons/lucide)、[Pyodide](https://github.com/pyodide/pyodide)、[TypeScript](https://github.com/microsoft/TypeScript) 和 [esbuild](https://github.com/evanw/esbuild)。原始许可见 `licenses/`。现有项目记录将 [Exercism](https://github.com/exercism/python) 列为学习结构参考；这不代表复制代码。若实际使用了外部代码或素材，应补充具体来源和许可。

项目使用了生成式 AI 辅助开发及文档整理；团队负责核对实现、测试结果与贡献归属。小精灵是设计成果，运行时采用规则导航。AI 自查不能替代组员独立代码审查。

## English guide

### 1. Purpose

PySteps supports the cycle of reading a concept, answering a question, explaining a mistake and practising again. The current bank contains 3 chapters, 15 concepts, 30 multiple-choice questions and 6 coding tasks with 39 reference cases. The topics are conditionals, loops, and functions and return values.

Python implements grading, progression, recommendation, review scheduling and SQLite persistence. React supplies the browser interface and Pyodide runs coding exercises. Optional Kimi analysis supplements feedback; fixed answer keys determine correctness. PiPo uses predefined replies and keywords for navigation, not live model chat or an autonomous agent loop.

### 2. Quick start

Use Python 3.10+, a modern browser and the fully extracted distribution. Running bundled assets requires no third-party Python packages, Node.js or Docker.

```bash
python main.py --open
```

Run from the directory containing `main.py`. Use `python3` on macOS or `py` on Windows where appropriate. The default URL is **http://127.0.0.1:8010/**; follow the actual terminal output. Keep the terminal running and stop with Ctrl+C. Do not open the static HTML directly.

```bash
python main.py --port 8011 --open
python main.py --db runtime/learning.sqlite3
```

The default listener is local-only. Another port does not stop an old process. Missing `web/static/index.html` requires a complete distribution or a frontend rebuild.

### 3. Learning workflow

1. Select English or Chinese; first visits default to English.
2. Read the introduction and concept lesson. Prerequisites control course access. In the current bank, passing requires both distinct concept questions to be answered correctly without hints after reading. Free practice does not unlock courses.
3. Submit a choice and optionally a reason. After a mistake, edit the reason and reanalyse the same attempt without increasing the attempt count.
4. Follow a same-chapter recommendation excluding the current question. Targeted unseen items and due reviews take priority. This is deterministic ranking, not generated questions or estimated ability.
5. Open a coding task directly. Run Example checks the first two cases; Check Answer runs all task cases in a browser Worker.
6. Review history and statistics for the latest 14 dates containing attempts, and export a JSON backup.

An incorrect choice is a clue rather than a confirmed misconception. Passing this bank is not proof of general mastery. Educational content requires independent review.

### 4. Optional AI

Copy `config.example.json` to `config.local.json` at the project root, fill it and restart. Environment variables override matching file values; `.env` is not automatically loaded.

| Setting | Meaning |
|---|---|
| `MOONSHOT_API_KEY` | Server-side API key without a `Bearer ` prefix |
| `MOONSHOT_MODEL` | A model available to the account; the code default `kimi-k2.6` is not an availability guarantee |
| `MOONSHOT_BASE_URL` | Either `https://api.moonshot.cn/v1` or `https://api.moonshot.ai/v1`, matching the key |
| `TEAM_ACCESS_CODE` | At least 12 characters; enter this in the UI, not the API key |
| `PUBLIC_ORIGIN` | Empty for local use; exact external origin when configured |

Only incorrect answers with non-empty reasons require analysis. The configured provider receives the question code, correct and selected answers, standard explanation, learner reason and candidate concept. Keep credentials out of frontend assets and submissions.

The server request uses a 30-second timeout parameter; the UI cancels its wait at 40 seconds. These are not a strict end-to-end latency guarantee. The per-process allowance is 60 requests per hour and resets on restart, not a monetary budget. There is no automatic retry or explicit prompt cache. Manual retries may incur charges.

Missing configuration, service failure or invalid output leaves rule feedback available. An incorrect team code produces an authorisation error. Invalid labels or reason quotations cause rule fallback. If those fields pass but the answer or knowledge evidence fails, accepted diagnostic fields are retained while explanations and hints revert to bank content. Structural checks do not establish factual accuracy.

### 5. Data and boundaries

The default database is `runtime/learning.sqlite3`. A random browser cookie identifies a learning space; there are no accounts or automatic device synchronisation. Clearing cookies or changing browsers/hostnames may create a new space.

Confirmed imports replace rather than merge the current space. The server regrades answers and restores rule feedback. Export before resolving a save conflict. Limits are 10,000 quiz attempts, 2,000 coding attempts, 1,000-character reasons, 20,000-character source and 10,000,000-byte request bodies. There is no automatic archiving.

Learner code runs in a restricted browser Worker, not on the Python server. The runtime-loading and execution thresholds are 60 and 4 seconds. There is no hard memory quota; learning records are not tamper-proof exam credentials. Production load has not been validated.

### 6. Tests and contributions

```bash
python -m unittest discover -s tests -t . -v
```

On 2026-10-28, all **21 test methods** passed on macOS/Python 3.12. AI responses were mocked; HTTP tests used a temporary local server and database. No paid model call was made. Method count is neither input-case count nor coverage: some methods loop through 30 questions or 39 reference coding cases.

Browser acceptance, live model quality and Windows/Linux execution were not rerun. A configured CI matrix does not establish successful remote runs. See [SPEC.md](SPEC.md) for traceability and outstanding acceptance checks.

Before a change, identify its requirement ID and expected behaviour. Update the implementation and tests, run regressions, obtain another member's review and update documentation. Prefer a reproducing test for a new defect; do not retroactively claim that all existing code was developed test-first.

Frontend contributors use Node.js 22, matching CI, and npm:

```bash
cd web
npm ci
npm run check
npm run build
```

Rebuild after editing frontend source, public assets or imported data. Normal execution uses `web/static`. Restart after backend/configuration changes.

### 7. Structure and troubleshooting

`main.py` starts the service. `backend/domain.py` contains learning rules; `ai.py` handles the model boundary; `storage.py` and `server.py` handle persistence and HTTP. `data/` holds content. `web/src`, `web/public` and `web/static` contain source, resources and built assets. `tests/` and `.github/workflows/` contain checks. `SPEC.md` defines requirements and verification; `submission/` and `licenses/` contain delivery materials and licences.

For an occupied port, stop the old process or select another port. For unavailable AI, check server settings, team code and connectivity, then restart. Repair certificate configuration instead of disabling TLS checks. Rebuild stale frontend assets. Keep the bundled Pyodide directory intact. On a save conflict, export before refreshing.

### 8. Packaging and attribution

```bash
python scripts/package_submission.py --group N
```

Replace `N` with the actual group number. The output is `dist/groupN_project.zip`. The packager excludes private settings, learning databases, Git history and `node_modules`. Extract and check the final archive; submit slides, video and individual reports through the required Moodle entries.

Dependencies and tools include Python, React, Lucide, Pyodide, TypeScript and esbuild; upstream links are listed in the Chinese section and licence texts are in `licenses/`. Existing project records identify Exercism as a learning-structure reference, not evidence of copied code. Attribute any actually reused code or assets specifically.

Generative AI assisted implementation and documentation; the team remains responsible for verification and accurate contribution statements. PiPo is a design contribution with rule-based runtime navigation. AI inspection is not independent teammate review.
