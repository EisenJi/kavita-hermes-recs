# 使用说明

这份文档说明 `kavita-hermes-recs` 当前的日常使用方式。

## 基本流程

### 1. 从 Kavita 同步

```text
/readingsync
```

它会：

- 验证 `Kavita` 连通性
- 在需要时初始化本地 SQLite
- 同步 libraries 和 series 快照
- 推导本地 progress 条目
- 同步 `want-to-read`

新机器第一次使用时应先执行它。

### 2. 请求推荐

```text
/todayread
/todayread 45
```

它会基于本地快照返回：

- 一个主推
- 最多两个备选
- 主推的一句原因

可选整数参数表示分钟数预算。

### 3. 记录反馈

```text
/readingfeedback 123 liked
/readingfeedback 123 disliked 工作日太重了
/readingfeedback 123 skipped
```

它会更新：

- `feedback_log`
- `preference_features`

反馈是本地的、个人化的。

### 4. 设置短期阅读心情

```text
/readingmood light 7
/readingmood continue 3
/readingmood explore 5
```

它会创建一个临时偏好特征，并影响后续推荐排序。

支持的 mood：

- `light`
- `serious`
- `continue`
- `explore`

### 5. 把最近一次推荐写回 Kavita

```text
/readinglist
/readinglist Weekend Picks
```

它会把最近一次本地推荐写成一个 `Kavita Reading List`。

如果你想让推荐结果直接出现在 `Kavita UI` 里，就用这个命令。

### 6. 查看适合进入 Memory 的稀疏摘要候选

```text
/readingmemory
```

它**不会**自动写入 Hermes memory。

它只会返回少量压缩过的偏好摘要句子，这些句子适合未来手动或自动写入 `Hermes memory`。

## 每日自动化

### 先预览 Cron 任务

```bash
python scripts/setup_daily_cron.py
python scripts/setup_daily_cron.py --writeback
```

### 再创建 Cron 任务

```bash
python scripts/setup_daily_cron.py --schedule "0 8 * * *" --time-budget 45 --writeback --apply
```

它直接使用 Hermes 原生的 cron，并把当前仓库设为 cron 的工作目录。

## 实践建议

- 向 `Kavita` 新增大量书后，重新运行 `/readingsync`。
- 要积极使用 `/readingfeedback`。这套系统从明确的负反馈里学得比从沉默里更快。
- 对 `/readingmemory` 要保持克制。如果一条内容细到不适合长期用户画像，它大概率就应该留在 SQLite，而不是进入 Hermes memory。
