# kavita-hermes-recs

[中文](./README.zh-CN.md) | [English](./README.en.md)

`kavita-hermes-recs` 是一个面向 `Kavita` 的本地优先阅读推荐系统，使用 `Hermes` 作为交互层和自动化层。

它面向的部署模型是：

- 一台共享的 `Kavita` 服务器
- 每个用户一份本地 `Hermes`
- 每个用户一份本地 SQLite 推荐状态

这个模型适合家庭或小规模多人场景：

- 共享的是书库
- 个性化的是推荐
- 各自反馈不会污染其他人的偏好

## 它现在能做什么

当前仓库已经具备这些能力：

- 从 `Kavita` 同步 libraries 和 series 快照
- 基于同步结果推导本地阅读进度状态
- 跟踪 `want-to-read` 和 `continue point`
- 在本地生成规则驱动的“今日阅读推荐”
- 记录反馈和短期阅读心情
- 生成适合进入 `Hermes memory` 的稀疏偏好摘要候选
- 把当前保存在本地日志中的推荐结果写回 `Kavita Reading List`
- 生成原生 `Hermes cron` 的每日推荐与每周偏好摘要自动化配置

## 为什么这样设计

系统被刻意拆成两个平面：

- 共享内容平面：`Kavita`
  - 负责书、元数据、阅读进度、阅读列表
- 个人决策平面：本地 `Hermes + SQLite`
  - 负责推荐历史、反馈、短期偏好、今日推荐

这样设计的原因是：

- `Kavita` 已经很好地解决了共享书库管理问题
- 推荐状态天然应该是个人私有状态
- `Hermes memory` 是稀缺资源，只适合放压缩后的长期偏好摘要
- 原始推荐日志、权重和反馈应保存在 SQLite，而不是 `USER.md`

## 当前使用流程

1. 运行 `/readingsync`，从 `Kavita` 拉取本地快照。
2. 运行 `/todayread`，生成本地推荐。
3. 运行 `/readingfeedback` 和 `/readingmood`，让后续推荐逐步贴近你的习惯。
4. 如果你想把推荐结果带回 `Kavita UI`，运行 `/readinglist`。
5. 如果你想每天自动跑，运行 `/readingcron` 或 `python scripts/setup_daily_cron.py`。
6. 如果你想把零散反馈压缩成少量可进入 `Hermes memory` 的摘要候选，运行 `/readingmemory`。
7. 如果你想每周自动生成一份可复查的偏好摘要，运行 `/readingmemorycron` 或 `python scripts/setup_weekly_summary_cron.py`。

## 命令一览

当前 Hermes 插件命令：

- `/readingsync`
- `/todayread [分钟数]`
- `/readingfeedback <series_id> <liked|disliked|skipped> [原因]`
- `/readingmood <light|serious|continue|explore> [天数]`
- `/readinglist [标题]`
- `/readingcron`
- `/readingmemory`
- `/readingmemorycron`

## 快速开始

```bash
git clone git@github.com:EisenJi/kavita-hermes-recs.git
cd kavita-hermes-recs

mkdir -p ~/.config/kavita-hermes-recs
cp .env.example ~/.config/kavita-hermes-recs/config.env

python scripts/install_plugin.py --link
python scripts/bootstrap_db.py

hermes plugins enable kavita-recs
```

然后在 Hermes 中执行：

```text
/readingsync
/todayread 45
```

## 文档

- [安装说明](./docs/setup.zh-CN.md)
- [使用说明](./docs/usage.zh-CN.md)
- [架构说明](./docs/architecture.md)

## 仓库结构

```text
plugin/kavita-recs/    Hermes 插件包
docs/                  安装、使用、架构文档
scripts/               初始化与 cron 辅助脚本
tests/                 测试目录
```

## 当前状态

这个项目仍处于持续迭代阶段。现在已经能作为本地原型使用，但推荐排序逻辑和元数据补全仍会继续增强。

## 许可证

MIT
