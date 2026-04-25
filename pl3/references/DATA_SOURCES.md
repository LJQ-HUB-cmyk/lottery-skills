# 数据来源说明

## 中彩网（主数据源）✅ 已实现

**API:** `https://jc.zhcw.com/port/client_json.php`

| 参数 | 值 | 说明 |
|------|-----|------|
| transactionType | 10001001 | 固定值 |
| lotteryId | 283 | 排列三 |
| type | 0 | 按期数查询 |
| pageNum | 1 | 页码（每页30条） |
| pageSize | 30 | 每页条数 |
| issueCount | 30/50/100 | 请求数 |

返回 JSON，`resCode=000000` 成功。`frontWinningNum` 格式 `"7 8 0"`（空格分隔）。

支持期数：30（1页）、50（2页）、100（4页），翻页自动处理。

**注意：** 必须用 `jc.zhcw.com`，`www.zhcw.com` 返回 HTML 404。

## 中彩网专家预测（数据分析参考）✅ 已实现

**URL:** `https://www.zhcw.com/czfw/sjfx/pl3/`

**内容:** 专家预测分析，包括独胆/双胆/三胆、杀码、组选推荐等。

**覆盖范围:** 每期约3位专家（好运王、彩坛盟主、多资多彩等），每页显示最近7期（约20条），如当前 072~078 期。

**用途:** 数据分析参考，对比专家胆码/杀码趋势，辅助统计推荐。

**抓取方式:** 通过 Python HTML 解析（BeautifulSoup），提取 `<a>` 标签中的期号和预测内容。

## 新浪（备用数据源）⚠️ 固定50期

**URL:** `https://lotto.sina.cn/trend/qxc_qlc_proxy.d.html?lottoType=p3&actionType=chzs`

服务端渲染 HTML，`chartball` class 标记号码。**固定50期，所有参数均不能改变返回行数。**

| actionType | 类型 | 列数 |
|------------|------|------|
| chzs | 基本走势 | 65 |
| hzhwzs | 和值和尾 | 74 |
| kdzs | 跨度走势 | 61 |
| 012 | 012路综合 | 73 |
| jqzs | 直选形态 | 63 |
| zhizs | 直选综合 | 68 |
| zxzs | 组选综合 | 57 |
| hwzs | 和尾 | 57 |

**解析方法：** 百位 `[8-17]` 找 `chartball01`，十位 `[19-28]` 找 `chartball02`，个位 `[30-39]` 找 `chartball01`。

## 彩种ID对照

| 彩种 | lotteryId |
|------|-----------|
| 双色球 | 1 |
| 福彩3D | 2 |
| 七乐彩 | 3 |
| 大乐透 | 281 |
| **排列三** | **283** |
| 排列五 | 284 |

---

*生成时间：2026-03-29*
