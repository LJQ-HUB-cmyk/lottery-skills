---
name: 排列3
description: 排列3走势数据分析工具。中彩网 jc.zhcw.com API 数据抓取（对应走势图 zhcw.com/sjtb/pl3/），多维度分析（遗漏值、冷热号、奇偶比、大小比、跨度、和值、012路、组选形态），生成智能号码推荐。Trigger: "分析排列三" "分析排列3" "推荐排列三号码" "排列三走势" "排列三冷热号" "排列3预测" "排列三预测" "排列3分析"
metadata: {"openclaw": {"requires": {"bins": ["python"]}, "os": ["win32"]}}
---

# 排列三

概率 1/1,000。所有计算由 Python 完成，Claude 只做解读，绝不自行运算。

## 环境

复用双色球 Conda 环境：
```cmd
D:\Conda\envs\ssq-lottery-analysis\python.exe -c "import requests,bs4; print('就绪')"
```

## 彩种规则

- 每期开奖 3 位数字（百位、十位、个位），每位 0-9
- **直选**：3 位全中，奖金 1,040 元
- **组选三**：有两位相同，如 112，奖金 346 元
- **组选六**：三位全不同，如 123，奖金 173 元
- **豹子**：三位相同，如 111（极罕见）
- **开奖时间**：每天一期，约 21:15

## 工作流路由

| 用户说 | 执行 |
|--------|------|
| 分析 / 看数据 / 最新走势 | Step 2 |
| 推荐号码 / 帮我选 / 出号 | Step 2 → Step 3 |
| 更新 / 抓最新 / 今天开奖了吗 | Step 1 → 2 → 3 |
| 复盘 / 中了吗 / 上期结果 | Step 4 |
| 全部 / 一键 | Step 1 → 2 → 3 |

## Step 1：联网抓取

```cmd
D:\Conda\envs\ssq-lottery-analysis\python.exe {baseDir}/scripts/pick3.py fetch [--periods 30|50|100]
```

支持 `--periods` 参数：30（默认）、50、100 期。

抓取中彩网 API 数据，新浪备用。自动处理翻页（每页30条）。

抓取新浪排列三基本走势数据，自动保存到 `~/.pl3_data/history.json`。

## Step 2：统计分析

```cmd
D:\Conda\envs\ssq-lottery-analysis\python.exe {baseDir}/scripts/pick3.py analyze
```

**必须解读的字段：**
- `red_anom` → 统计异常沉寂号码（z-score < -2σ，最重要信号）
- `miss_top3_pos` → 各位置遗漏 TOP3
- `hot/cold_by_pos` → 各位置近 20 期冷热号
- `sum_p20_p80` → 和值 60% 概率区间
- `top_odd/size` → 最常见奇偶比、大小比
- `span_trend` → 跨度走势
- `group_ratio` → 组三/组六比例
- `path_012` → 012 路分布

## Step 3：生成推荐

```cmd
D:\Conda\envs\ssq-lottery-analysis\python.exe {baseDir}/scripts/pick3.py recommend
```

输出：3 注直选号码 + 置信度评分 + 各维度得分明细。

必须说明：置信度评分及主要得分来源、该注的统计逻辑、最强信号维度。

## Step 4：开奖复盘

```cmd
D:\Conda\envs\ssq-lottery-analysis\python.exe {baseDir}/scripts/pick3.py review <期号> <百位> <十位> <个位>
```

## 一键全流程

```cmd
D:\Conda\envs\ssq-lottery-analysis\python.exe {baseDir}/scripts/pick3.py all
```

## 数据存储

| 文件 | 内容 |
|------|------|
| `~/.pl3_data/history.json` | 全量历史开奖数据 |
| `~/.pl3_data/latest_stats.json` | 最近一次统计结果 |
| `~/.pl3_data/predictions.json` | 预测存档 + 复盘记录 |

## 数据源

| 来源 | URL | 用途 |
|------|-----|------|
| 中彩网开奖API | `https://jc.zhcw.com/port/client_json.php?gameNo=35` | 主数据源（对应走势图页 zhcw.com/sjtb/pl3/），JSON格式，支持翻页 |
| 中彩网专家预测 | `https://www.zhcw.com/czfw/sjfx/pl3/` | 数据分析参考，专家胆码/杀码趋势 |
| 新浪基本走势 | `https://lotto.sina.cn/trend/qxc_qlc_proxy.d.html?lottoType=p3&actionType=chzs` | 备用数据源，固定50期 |

## 故障处理

| 症状 | 解决 |
|------|------|
| 缺少依赖 | `pip install requests beautifulsoup4` |
| 无本地数据 | 先运行 `pick3.py fetch` |
| FETCH_FAILED | 用 web_fetch 抓备用 URL |
| HTTP 503 | 等 1-2 分钟重试 |
