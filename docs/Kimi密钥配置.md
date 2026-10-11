# 团队使用：直接填写项目配置

当前配置方式：打开项目根目录api_config.json，填写MOONSHOT_API_KEY，其他字段默认无需修改。不要把真实密钥发到聊天。

```json
{
  "EDU_AI_PROVIDER": "kimi",
  "MOONSHOT_API_KEY": "在这里填写团队专用密钥",
  "MOONSHOT_MODEL": "kimi-k2.6",
  "MOONSHOT_BASE_URL": "https://api.moonshot.cn/v1"
}
```

保存为有效JSON（英文双引号，末项无逗号）。重新双击启动.command即可，不需要设置终端环境变量。AI默认关闭，进入练习区手动勾选后，答错且理由非空才调用；真实调用计入此密钥所属账户。

分享给团队：代码可以正常提交Git。api_config.json被Git忽略，团队成员可以将api_config.example.json复制为api_config.json并填写自己的密钥；若使用共享团队密钥，通过团队私密渠道分发配置文件。该配置为明文文件，拿到它的人可使用密钥，建议使用独立的团队密钥。Git忽略不阻止文件夹压缩打包，提交作业/公开仓库时也应排除真实配置。

程序优先使用文件里的配置。只有文件不存在时才兼容旧环境变量；文件为空密钥或JSON无效时，不会偷偷使用环境变量中的其他密钥。项目仍不读取.env。

真实连接验证（最多一次API请求）：

```sh
cd ~/Downloads/EDU/Python/final-homework
python3 evaluation/check_connection.py --live
```

质量评估见《AI功能与验证》。此更新只改变配置方式，没有执行真实API调用。旧.env未被读取或覆盖；如其中曾保存密钥，打包时也需排除。
