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

此修复尚需提交并推送后在Windows重新验证，不能把本机通过写成所有系统通过。当前没有上传产物或自动部署步骤。此前文档中的“远端结果未验证”是旧检查时点；本记录提供后来取得的真实远端结果。

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

The change still needs committing/pushing and a fresh Windows run. Local success does not prove all-platform success. Artifact upload and automatic deployment are not implemented. Earlier documents describing remote results as unverified reflect an earlier checkpoint; this record adds the subsequently retrieved evidence.
