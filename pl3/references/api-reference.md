# 中彩网排列三API接入说明

## 概述

中彩网（zhcw.com）的排列三开奖数据页面是JS动态渲染的，无法通过简单的HTML抓取获取数据。需要找到其底层API接口直接调用。

**API端点：** `https://jc.zhcw.com/port/client_json.php`

---

## 1. 发现API的过程

### 1.1 页面结构分析

访问 `https://www.zhcw.com/kjxx/pl3/`，页面源码中引入了多个JS文件：

```
/static/js/kjsj.min.js        ← 核心数据请求逻辑
/static/unjs/kj-wq.js?2026    ← 页面数据渲染逻辑（avalon.js MVVM）
/static/js/zhcwDemo.min.js    ← 工具函数
/static/js/avalon.js          ← 前端MVVM框架
```

### 1.2 逆向JS找到API

在 `kj-wq.js` 中找到数据请求调用：

```javascript
// 初始加载：请求30期
kjsjdq.sj1001(kjsjdq.czid[czxx.czname].id, 0, 1, 30, 30, "", "", "", "", callback)

// 按钮点击：请求30/50/100期
// 按钮的 data-z 属性存储期数值
$(this).attr("data-z")  // 值为 30、50、100
```

在 `kjsj.min.js` 中找到API函数定义：

```javascript
var kjsjdq = {
    urlDz: urlDz ? urlDz : "/port/client_json.php",  // API基础URL
    czid: {
        pl3: {id: "283", jc: "排列三"},               // 彩种ID映射
        pl5: {id: "284", jc: "排列五"},
        ssq: {id: "1", jc: "双色球"},
        d3:  {id: "2", jc: "福彩3D"},
        // ...
    },
    sj1001: function(d, h, g, j, l, a, i, b, f, k) {
        var c = {};
        c.transactionType = "10001001";
        c.lotteryId = d;        // 彩种ID，排列三=283
        c.issueCount = l;       // 请求数量（30/50/100）
        c.startIssue = a;       // 起始期号
        c.endIssue = i;         // 结束期号
        c.startDate = b;        // 起始日期
        c.endDate = f;          // 结束日期
        c.type = h;             // 查询类型：0=按数量，1=按期号，2=按日期
        c.pageNum = g;          // 页码
        c.pageSize = j;         // 每页条数（固定30）
        c.tt = Math.random();   // 防缓存随机数

        $.ajax({
            url: this.urlDz,
            data: c,
            dataType: "jsonp",
            jsonp: "callback",
            success: function(m) { ... }
        });
    }
};
```

---

## 2. API参数详解

### 2.1 请求URL

```
GET https://jc.zhcw.com/port/client_json.php
```

**注意：** 必须用 `jc.zhcw.com` 子域名。`www.zhcw.com/port/client_json.php` 会返回HTML 404页面。

### 2.2 请求参数

| 参数 | 类型 | 说明 | 可选值 |
|------|------|------|--------|
| `transactionType` | string | 交易类型 | 固定 `10001001` |
| `lotteryId` | string | 彩种ID | `283`（排列三） |
| `type` | string | 查询方式 | `0`=按期数，`1`=按期号范围，`2`=按日期范围 |
| `pageNum` | string | 页码 | `1`, `2`, `3`, ... |
| `pageSize` | string | 每页条数 | 固定 `30` |
| `issueCount` | string | 请求期数 | `30`, `50`, `100` |
| `startIssue` | string | 起始期号（type=1时用） | 空或期号如 `26050` |
| `endIssue` | string | 结束期号（type=1时用） | 空或期号如 `26077` |
| `startDate` | string | 起始日期（type=2时用） | 空或 `2026-01-01` |
| `endDate` | string | 结束日期（type=2时用） | 空或 `2026-03-29` |
| `tt` | float | 防缓存随机数 | 任意小数 |

### 2.3 返回格式（JSON）

```json
{
  "resCode": "000000",
  "resCodeMsg": "",
  "pageNum": "1",
  "pageSize": "30",
  "total": "100",
  "pages": "4",
  "data": [
    {
      "issue": "26077",
      "openTime": "2026-03-28",
      "frontWinningNum": "7 8 0",
      "backWinningNum": "",
      "seqFrontWinningNum": "7 8 0",
      "seqBackWinningNum": "",
      "saleMoney": "20198744",
      "prizePoolMoney": "0",
      "winnerDetails": [
        {
          "baseBetWinner": {
            "awardNum": "2633",
            "awardMoney": "2738320"
          },
          "addToBetWinner": null
        },
        {
          "baseBetWinner": {
            "awardNum": "25790",
            "awardMoney": "8923720"
          },
          "addToBetWinner": null
        },
        {
          "baseBetWinner": {
            "awardNum": "52199",
            "awardMoney": "9080626"
          },
          "addToBetWinner": null
        }
      ]
    }
  ]
}
```

**关键字段：**
- `resCode`: `000000` 表示成功，`9998` 表示参数不全
- `frontWinningNum`: 前区开奖号码（空格分隔的3位数字，如 `"7 8 0"`），排列三只用前区
- `backWinningNum`: 后区号码（排列三为空）
- `total`: 总记录数
- `pages`: 总页数
- `winnerDetails[0]`: 直选中奖详情
- `winnerDetails[1]`: 组选3中奖详情
- `winnerDetails[2]`: 组选6中奖详情

---

## 3. 翻页机制

API每页固定返回30条，超过30期需要翻页：

```
请求30期：1页  → pageNum=1
请求50期：2页  → pageNum=1 (30条) + pageNum=2 (20条)
请求100期：4页 → pageNum=1~3 (各30条) + pageNum=4 (10条)
```

翻页逻辑伪代码：
```python
total_to_fetch = 100
page = 1
all_records = []

while len(all_records) < total_to_fetch:
    data = api_call(pageNum=page, issueCount=total_to_fetch)
    all_records.extend(data["data"])
    if len(all_records) >= int(data["total"]):
        break
    page += 1
```

---

## 4. Python实现

### 4.1 核心请求代码

```python
import requests

url = "https://jc.zhcw.com/port/client_json.php"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Referer": "https://www.zhcw.com/kjxx/pl3/",
}

params = {
    "transactionType": "10001001",
    "lotteryId": "283",       # 排列三
    "type": "0",              # 按期数查询
    "pageNum": "1",           # 第1页
    "pageSize": "30",         # 每页30条
    "issueCount": "30",       # 请求数
}

resp = requests.get(url, params=params, headers=headers)
data = resp.json()

if data["resCode"] == "000000":
    for item in data["data"]:
        issue = item["issue"]                          # 期号，如 "26077"
        nums = item["frontWinningNum"].split()         # ["7", "8", "0"]
        h, t, u = int(nums[0]), int(nums[1]), int(nums[2])
        open_time = item["openTime"]                   # 日期，如 "2026-03-28"
```

### 4.2 解析开奖号码

`frontWinningNum` 格式为空格分隔的3位数字（百位 十位 个位）：

```python
nums = item["frontWinningNum"].strip().split()  # "7 8 0" → ["7", "8", "0"]
hundreds = int(nums[0])  # 百位 = 7
tens     = int(nums[1])  # 十位 = 8
units    = int(nums[2])  # 个位 = 0
```

### 4.3 计算派生字段

```python
sum_val = hundreds + tens + units           # 和值 = 15
span = max(hundreds, tens, units) - min(hundreds, tens, units)  # 跨度 = 8

# 形态判断
if hundreds == tens == units:
    group_type = "豹子"
elif hundreds == tens or tens == units or hundreds == units:
    group_type = "组三"
else:
    group_type = "组六"
```

### 4.4 星期计算

API返回日期（`openTime`），需自行计算星期：

```python
from datetime import datetime

dt = datetime.strptime("2026-03-28", "%Y-%m-%d")
weekday = (dt.weekday() + 1) % 7 or 7  # Python周一=0 → 周一=1
# 结果：周六=6
```

---

## 5. 注意事项

### 5.1 域名区别

| 域名 | 行为 |
|------|------|
| `jc.zhcw.com/port/client_json.php` | ✅ 返回JSON/JSONP |
| `www.zhcw.com/port/client_json.php` | ❌ 返回HTML 404 |
| `www.zhcw.com/kjxx/pl3/` | 前端页面（JS渲染） |

### 5.2 Referer

建议设置 `Referer: https://www.zhcw.com/kjxx/pl3/`，不设也能返回数据但可能被限制。

### 5.3 JSONP vs JSON

原页面用 jQuery JSONP 调用（`dataType: "jsonp"`），但直接用纯JSON请求也正常工作（不传 `callback` 参数即可）。

### 5.4 resCode 错误码

| code | 含义 |
|------|------|
| `000000` | 成功 |
| `9998` | 请求参数不全（缺少必填参数） |
| `000014` | 页面校验不通过（可能需签名） |

### 5.5 彩种ID对照

| 彩种 | lotteryId |
|------|-----------|
| 双色球 | 1 |
| 福彩3D | 2 |
| 七乐彩 | 3 |
| 大乐透 | 281 |
| **排列三** | **283** |
| 排列五 | 284 |

---

## 6. 实测结果

| 请求期数 | total | pages | 实际返回 | 数据范围 |
|----------|-------|-------|----------|----------|
| 30 | 30 | 1 | 30条 | 26048~26077 |
| 50 | 50 | 2 | 50条 | 26028~26077 |
| 100 | 100 | 4 | 100条 | 25978~26077 |

---

## 7. 与新浪数据源对比

| 对比项 | 中彩网API | 新浪走势 |
|--------|-----------|----------|
| 数据格式 | JSON/JSONP | HTML表格 |
| 解析难度 | 低（直接取字段） | 高（需解析65列+class标记） |
| 期数控制 | 支持30/50/100 | 固定返回约50期 |
| 翻页 | 自动处理 | 不支持 |
| 数据字段 | 开奖号+奖金+中奖人数 | 开奖号+走势分析 |
| 稳定性 | 高（官方API） | 中（依赖HTML结构） |

**结论：中彩网API更适合作为主数据源。**

---

*生成时间：2026-03-29*
*接入方式：通过逆向分析 zhcw.com 前端JS（kjsj.min.js）获取API参数*

