@echo off
setlocal
set PYTHONUTF8=1
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
  py -3 main.py
) else (
  python main.py
)
if errorlevel 1 (
  echo 启动失败，请检查 Python 3.10+ 与 Tkinter 是否已安装。
  pause
)
