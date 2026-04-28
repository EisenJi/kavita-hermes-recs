# 安装说明

这份文档给出第一版可复现的本地安装路径，面向“每个用户在自己的电脑上运行 Hermes，并连接共享的 Kavita”这个场景。

## 前置条件

你需要：

- `Python 3.11+`
- 已安装可运行的 `Hermes`
- 一个可访问的 `Kavita` 服务
- 每个用户自己的 `Kavita API Key`

## 1. 克隆仓库

```bash
git clone git@github.com:EisenJi/kavita-hermes-recs.git
cd kavita-hermes-recs
```

## 2. 创建用户配置

先创建用户配置目录，再复制示例文件：

```bash
mkdir -p ~/.config/kavita-hermes-recs
cp .env.example ~/.config/kavita-hermes-recs/config.env
```

至少修改以下字段：

- `KAVITA_BASE_URL`
- `KAVITA_API_KEY`
- `KAVITA_USER_NAME`

插件会按以下顺序查找配置：

1. `KAVITA_RECS_ENV_FILE`
2. `~/.config/kavita-hermes-recs/config.env`
3. 仓库根目录下的 `.env`

## 3. 安装 Hermes 插件

如果你希望以软链接方式安装到 `~/.hermes/plugins/`：

```bash
python scripts/install_plugin.py --link
```

如果你希望复制安装：

```bash
python scripts/install_plugin.py --copy
```

## 4. 初始化本地数据库

```bash
python scripts/bootstrap_db.py
```

该命令会按照 `KAVITA_RECS_DB_PATH` 创建本地 SQLite 数据库。

## 5. 在 Hermes 中启用插件

直接启用：

```bash
hermes plugins enable kavita-recs
```

或者打开交互界面：

```bash
hermes plugins
```

然后在列表中启用 `kavita-recs`。

## 6. 验证骨架安装

启动 Hermes 后执行：

```text
/todayread
```

当前阶段该命令会返回一个 scaffold 提示，用于确认插件安装成功。

## 7. 后续预期工作流

当 adapter 和同步层完成后，正常流程会是：

1. 同步 Kavita 书库快照
2. 写入本地用户状态
3. 生成每日推荐
4. 可选写回 Kavita Reading List
5. 用 Hermes cron 做每日定时推荐

## 说明

- 每个用户都应使用自己的 `Kavita` 账号或 API key。
- 每个用户都应保留自己本地的 `.env` 和 SQLite 状态文件。
- 共享的是书库，不共享的是偏好和推荐状态。
