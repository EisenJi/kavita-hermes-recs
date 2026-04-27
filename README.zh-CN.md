# kavita-hermes-recs

[中文](./README.zh-CN.md) | [English](./README.en.md)

一个面向 `Kavita` 的本地优先阅读推荐系统，交互层使用 `Hermes`。

这个仓库的目标是提供：

- 共享的 `Kavita` 书库访问
- 每个用户独立的本地推荐状态
- 每个用户独立的 `Hermes` 集成
- 适合家庭或小规模多人场景的可复现本地部署方式

## 当前状态

当前处于骨架阶段，已经包含：

- 中英双语 README 入口
- 项目目录结构
- 初版架构文档
- 用于对接 Hermes 的插件骨架

## 核心思路

把系统拆成两个平面：

- 共享内容平面：`Kavita`
  - 负责书籍、元数据、阅读进度、阅读列表
- 个人决策平面：每个用户自己电脑上的 `Hermes + SQLite`
  - 负责偏好、反馈、推荐历史、今日推荐

```text
共享 Kavita
  -> 书籍、元数据、进度、阅读列表

每用户本地 Hermes + SQLite
  -> 偏好、推荐历史、反馈、今日推荐
```

这样可以做到：

- 书库共享
- 推荐个性化
- 家庭成员之间偏好互不污染
- 开源后其他用户也容易复现

## 仓库结构

```text
plugin/kavita-recs/    Hermes 插件包
docs/                  架构与安装文档
scripts/               本地初始化脚本
tests/                 测试目录
```

## 下一阶段计划

1. 实现 `Kavita` adapter。
2. 加入本地 SQLite schema 和同步逻辑。
3. 实现 Hermes tools 与 slash commands。
4. 通过 Hermes cron 打通每日推荐。

## 许可证

MIT
