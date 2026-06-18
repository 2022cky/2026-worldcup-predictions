# 新电脑设置指南

在新电脑上 clone 仓库后，执行以下步骤：

## 1. 恢复 Memory 文件

Memory 文件是 Claude Code 的"长期记忆"，记录着模型参数和复盘经验。
在新电脑上，Claude Code 会为这个项目创建一个新的 memory 目录。

**步骤**:
- 在 Claude Code 中打开本项目，让它自动创建 memory 目录
- 然后运行: Claude Code 第一次对话后，会说 "已创建 memory 目录"
- 把 `memory_backup/` 里的 `.md` 文件复制到 Claude Code 自动创建的 memory 目录中

**或者**，在新电脑上打开 Claude Code，让它读取 CLAUDE.md 和 memory_backup/
里的内容即可重建上下文。

## 2. 重新授权

- 旧电脑的 `.claude/settings.local.json` 没有上传到 GitHub
- 新电脑上运行预测脚本时，Claude Code 会重新询问权限
- 也可以手动创建 `.claude/settings.local.json` 添加白名单

## 3. 重新创建定时任务

旧电脑的定时任务（每天20:00获取最新阵容）不会同步。
在新电脑的 Claude Code 中运行：
```
/cron "0 20 * * *" "搜索2026世界杯最新赛前阵容..."
```

## 4. Python 环境

如果要用 Python 脚本（predict_v7.py 等），需要：
- Python 3.7+
- 脚本使用标准库，无需额外安装包

## 5. 路径说明

- Python 脚本全部使用相对路径（`os.path.dirname(__file__)`）
- 所以项目放在任何目录都能正常运行
- 不需要像旧电脑一样放在 `E:\ai\世界杯\`

## 新旧电脑对比

| 项目 | 旧电脑 | 新电脑 | 如何解决 |
|------|--------|--------|---------|
| 项目文件 | E:\ai\世界杯 | 任意路径 | Git clone |
| Memory | 自动同步 | 需手动复制 | 用 memory_backup/ |
| 权限配置 | 已授权 | 重新授权 | 首次使用点允许 |
| 定时任务 | 每天20:00 | 需重新创建 | /cron 命令 |
| Python | 已安装 | 需安装 | pip/python.org |
