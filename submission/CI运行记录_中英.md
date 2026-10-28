# 中文版：CI运行记录

## 2026-10-28：首次核对的当前版本运行

运行链接：https://github.com/crayonhe11/final-homework/actions/runs/40643041857

提交：424f5aacb208ef1c43f982221b338a59e57d3eef。整体失败。

- 网页检查/构建：成功。
- Ubuntu + Python 3.10和3.13：成功。
- Windows + Python 3.13：失败；21项测试中出现7个中文输出题目的子案例错误。
- Windows + Python 3.10：任务最终标为取消，但测试步骤已有失败记录。
- macOS两项：任务最终标为取消；步骤日志显示测试与打包成功，不能将整个任务写成成功。

## 本地修复与后续验证

测试子进程的-I隔离模式忽略PYTHONIOENCODING环境变量。改用命令行-X utf8明确启用子进程UTF-8，并保留父进程UTF-8解码；断言附带子进程stderr，方便排查。CI设置fail-fast:false，某环境失败不再联动取消其余矩阵任务。

此修复已推送，后续远端验证结果见下节。当前没有上传产物或自动部署步骤。此前文档中的“远端结果未验证”是旧检查时点；本记录提供后来取得的真实远端结果。

## 第二次远端运行：测试通过，Windows打包日志失败

运行：https://github.com/crayonhe11/final-homework/actions/runs/40643879670

提交：8f64abd22e9be661d32deca274cadee75b022e33。

- 六个 Python 环境的测试步骤全部成功；上次的中文题目输出问题已修复。
- Ubuntu、macOS 的完整任务与网页任务成功。
- Windows 3.10、3.13 在打包步骤失败：ZIP 已生成，但最后打印中文组号提醒时，cp1252 编码触发 UnicodeEncodeError。
- 已在打包脚本中显式将标准输出和错误输出设置为 UTF-8，兼容中文路径及中文提示。无需修改用户系统语言。
- 本地通过 PYTHONIOENCODING=cp1252 复现原错误；修复后验证该编码、ASCII 和 UTF-8 下正常打包，以及非法组号的正常报错。压缩包完整性检查通过。

此轮打包修复仍需推送后取得新的 Windows 绿色运行记录；本地模拟不能替代真实远端验证。CI 成功也不等于已实现 CD 部署。

# English Version: CI Run Record

## 28 October 2026: inspected current-version run

Run: https://github.com/crayonhe11/final-homework/actions/runs/40643041857

Commit: 424f5aacb208ef1c43f982221b338a59e57d3eef. Overall result: failure.

- Frontend checking/building: success.
- Ubuntu with Python 3.10 and 3.13: success.
- Windows/Python3.13: failure, with seven Chinese-output question subcase errors in the21-test suite.
- Windows/Python3.10: final job conclusion cancelled, with a failed test step recorded.
- Both macOS jobs: final conclusions cancelled, although test and packaging steps show success; do not label the entire jobs successful.

## Local fix and remaining verification

The isolated child interpreter (-I) ignores PYTHONIOENCODING. Use explicit -X utf8 for child output and retain UTF-8 decoding in the parent. Failure assertions now expose child stderr. Set matrix fail-fast:false to let all environments finish independently.

The change was pushed; see the follow-up run below. Artifact upload and automatic deployment are not implemented. Earlier documents describing remote results as unverified reflect an earlier checkpoint; this record adds the subsequently retrieved evidence.

## Second remote run: tests pass, Windows packaging logging fails

Run: https://github.com/crayonhe11/final-homework/actions/runs/40643879670

Commit: 8f64abd22e9be661d32deca274cadee75b022e33.

- Test steps passed in all six Python environments, confirming the earlier Unicode question-output fix.
- Ubuntu, macOS and frontend jobs succeeded.
- Both Windows jobs failed during packaging: the ZIP was generated, but printing the Chinese placeholder-group reminder raised UnicodeEncodeError under cp1252.
- The packaging script now explicitly configures stdout and stderr as UTF-8, supporting Unicode paths and messages without changing the system language.
- Local validation reproduced the original failure with PYTHONIOENCODING=cp1252, then verified packaging under cp1252, ASCII and UTF-8, normal invalid-group errors, and ZIP integrity after the fix.

This packaging fix still requires pushing and a fresh successful Windows run. Local simulation does not replace remote verification. Successful CI alone does not establish a CD deployment pipeline.
