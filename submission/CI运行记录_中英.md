# CI 与交付运行记录 / CI and Delivery Record

## 中文版

### 1. 已核实的历史结果

2026-11-05只读核实的最近一次历史运行：[2026-10-29运行](https://github.com/crayonhe11/final-homework/actions/runs/40840307773)，提交17e1ed22465dac45b69ed0182a00e5892b943030。六个系统/Python组合及网页任务全部成功；Windows日志明确为43项测试通过。该结果只对应这个旧提交。

### 2. 2026-11-06完善的流水线

1. push、pull_request和workflow_dispatch触发；同分支新版本取消旧运行。
2. Windows/macOS/Ubuntu × Python3.10/3.13运行项目测试；当前本地57项通过，并检查跨平台打包。保留每个组合的文本日志。
3. Node22按锁定依赖重新构建网页，上传browser-distribution。
4. 必须等六个Python任务及网页构建成功，再下载本次构建，启动真实main.py，用临时SQLite执行8个HTTP黑盒契约；本地8项通过。
5. 生成作业ZIP、重建ZIP、SHA256SUMS并拒绝私有文件；上传group8-delivery。
6. 用同一网页构建Docker镜像，临时启动容器并再次执行8个HTTP契约；失败保留日志，完成后清理容器。此项本机无Docker，由GitHub runner实际验证。
7. main分支所有关卡成功才自动创建GitHub版本化预发布。PR不发布main版本。

新增CIPipelineTests三项：失败退出码不会被写日志操作掩盖、验收清空继承的付费密钥、ZIP审计拒绝配置/数据库/Git/路径穿越。原验收记录的54项是2026-11-03快照；本次增加后为57项，没有把同一测试重复算成新功能测试。

### 3. 到哪里看证据

- [GitHub Actions](https://github.com/crayonhe11/final-homework/actions)：选择准确提交SHA的运行，查看任务与日志。
- [Pull Requests](https://github.com/crayonhe11/final-homework/pulls?q=is%3Apr)：分支、PR和自动检查记录；具体PR链接也会附在本次任务中。
- [Releases](https://github.com/crayonhe11/final-homework/releases)：全部检查通过后的main预发布及ZIP/checksum。
- Actions的Artifacts：tests-*、integration-reports、container-reports保留7天；group8-delivery保留14天。

本文编写时的本地证据与实际远端状态分别记录；远端结果以对应PR/提交链接为准，不把本地通过写成所有平台通过。流水线从不使用真实学校密钥；模型网络调用不属于该验收。

### 4. 持续交付与生产部署边界

已实现的机制是CI、临时容器验收环境自动部署及版本化交付物发布。没有配置长期可达的生产服务器，因此不宣称已完成生产网站持续部署。Docker监听8000，宿主端口可映射8011；PUBLIC_ORIGIN必须匹配宿主实际来源。README含启动命令。生产主机、域名、秘密变量、持久卷及上线后检查需要在确定服务器后接入。

Lecture09第5–9页对应测试目标、设计、执行与断言分析；第11/13/16页对应仓库、触发、环境、工作流；第19–20页对应真实PR与查看日志；第12页的持续生产部署仍需服务器。人工成员审查不能由一次自动检查或自己的合并替代。

---

## English Version

### 1. Verified historical result

On 5 November 2026, read-only inspection confirmed [the 29 October run](https://github.com/crayonhe11/final-homework/actions/runs/40840307773) for commit17e1ed22465dac45b69ed0182a00e5892b943030. All six OS/Python jobs and the frontend passed; the Windows log explicitly reported43tests. This evidence applies only to that historical commit.

### 2. Pipeline completed on 6 November 2026

Push, pull_request and workflow_dispatch trigger the pipeline; newer same-branch runs supersede older ones. Windows/macOS/Ubuntu with Python3.10/3.13 run the suite and packaging compatibility checks, retaining per-environment reports. The current local suite has57passing methods. Node22 installs locked dependencies and uploads the freshly built browser distribution.

Integration depends on all Python jobs and the web build. It downloads that exact browser build, starts main.py with temporary SQLite and runs eight implementation-independent HTTP contracts; all eight passed locally. Packaging audits private entries and creates both ZIPs and SHA256 checksums. A subsequent job builds Docker with the same browser artifact, starts temporary staging, executes the eight contracts and cleans up. Docker is unavailable locally, so this gate must be executed on GitHub. Only fully passing main builds publish versioned GitHub prereleases; PRs do not publish main releases.

Three new CIPipelineTests guard nonzero exit propagation, disabling inherited paid credentials and private/traversal ZIP rejection. The54-test validation record is a3November snapshot; the current57includes these three additional CI-focused checks.

### 3. Evidence locations

Use [Actions](https://github.com/crayonhe11/final-homework/actions) for the exact SHA's jobs/logs, [PRs](https://github.com/crayonhe11/final-homework/pulls?q=is%3Apr) for branch/check evidence and [Releases](https://github.com/crayonhe11/final-homework/releases) for verified main deliveries. Artifacts retain tests-*, integration-reports and container-reports for seven days, and group8-delivery for14days. The task also attaches the concrete PR link.

Local results at writing time are distinct from actual remote status. Check the associated PR/commit, rather than treating local success as all-platform success. Test services disable real school credentials and do not exercise paid model access.

### 4. Delivery versus production deployment

Implemented mechanisms are CI, automatic temporary-container staging and versioned deployable delivery. No persistent public production server is configured. Docker listens on8000, usually mapped to host8011, with PUBLIC_ORIGIN matching the host origin. README provides commands. Production host/domain/secrets/persistent storage and post-deployment checks require a chosen server.

Lecture09slides5–9 map to objectives/design/execution/assertion analysis;11/13/16 to repository/triggers/environments/workflow;19–20 to actual PR checks/logs. Slide12's continuous production deployment still needs a server. Automated checks or self-merging do not replace genuine independent human review.
