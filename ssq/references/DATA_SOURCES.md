# 双色球数据来源说明

## 唯一数据源

### 中国福利彩票官网（cwl.gov.cn）✅

**URL：** `http://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/findDrawNotice`

**状态：** ✅ 已实现，唯一可信源

**请求方式：** GET

**请求参数：**
- `name=ssq` — 品种名称
- `issueCount=N` — 返回期数（建议 100）

**请求头：**
```python
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Mobile Safari/537.36",
    "Accept": "application/json",
}
```

**返回字段（每条记录）：**
- `code` — 期号（如 "2026019"）
- `red` — 红球，逗号分隔（如 "07,08,16,17,18,30"）
- `blue` — 蓝球（如 "01"）
- `week` — 开奖星期
- `date` — 开奖日期
- `sales` — 销售额
- `poolmoney` — 奖池金额
- `prizegrades` — 各等奖注数

**特点：**
- 官方权威，数据零滞后
- 无需 Cookie / Referer / Origin
- HTTP（80端口）比 HTTPS 更稳定
- 更新及时，开奖后 1-2 分钟内可获取

---

## 数据更新频率

### 官方开奖时间
- **周二：** 21:15
- **周四：** 21:15
- **周日：** 21:15

**建议：** 开奖后等待 2-3 分钟再抓取数据，确保数据已完全写入。

---

## 废弃数据源（永远不要再使用）

| 废弃源 | URL | 废弃原因 |
|--------|-----|---------|
| 新浪彩票 | `lotto.sina.cn` | 停更，滞后至少 2 期 |
| 中彩网 | `zhcw.com` | 缓存严重，数据不准确 |
| 500.com | `datachart.500.com` | 已停更 |

---

## 脚本说明

**脚本：** `scripts/ssq.py`

```bash
# 抓取最新 100 期数据
python scripts/ssq.py fetch

# 统计分析（最近 30 期）
python scripts/ssq.py analyze

# 生成推荐（4 注 + 蓝球 TOP3）
python scripts/ssq.py recommend

# 一键全流程
python scripts/ssq.py all

# 复盘
python scripts/ssq.py review <期号> <红1>...<红6> <蓝>
```

---

## 数据存储

| 文件 | 内容 |
|------|------|
| `~/.ssq_data/history.json` | 全量历史开奖数据 |
| `~/.ssq_data/latest_stats.json` | 最近一次统计结果 |
| `~/.ssq_data/predictions.json` | 预测存档 + 复盘记录 |

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v6.2 | 2026-04 | 完全迁移至 cwl.gov.cn 官方 API，删除所有废弃数据源 |
| v6.1 | 2026-02 | 分位分析、蓝球独立预测、多窗口分析 |

---

**最后更新：** 2026-05-01
