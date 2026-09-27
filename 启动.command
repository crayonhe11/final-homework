#!/bin/zsh
cd -- "${0:A:h}"
python3 main.py
if [ $? -ne 0 ]; then
  echo '启动失败，请阅读 README.md 中的排错说明。按回车关闭。'
  read
fi
