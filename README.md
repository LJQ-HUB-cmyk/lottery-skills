# 彩票分析工具集

三个独立的 Python 工具，分别分析中国福利彩票和体育彩票的开奖数据。

## 工具列表

| 工具 | 彩种 | 官方接口 | 版本 |
|------|------|----------|------|
| `ssq/` | 双色球 | cwl.gov.cn (GET) | v6.2 |
| `daletou/` | 大乐透 | webapi.sporttery.cn | v2.0 |
| `pl3/` | 排列3 | webapi.sporttery.cn (gameNo=35) | v3.0 |

## 数据源

全部迁移至**官方原生API**，无第三方缓存：
- 双色球：福彩中心 `http://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/findDrawNotice`
- 大乐透/排列3：体彩中心 `https://webapi.sporttery.cn/gateway/lottery/getHistoryPageListV1.qry`

## 快速开始

### 依赖安装
```bash
pip install requests beautifulsoup4
```

### 抓取最新开奖数据
```bash
# 双色球
python ssq/scripts/ssq.py fetch

# 大乐透
python daletou/scripts/dlt.py fetch

# 排列3
python pl3/scripts/pick3.py fetch
```

### 分析走势
```bash
python ssq/scripts/ssq.py analyze
python daletou/scripts/dlt.py analyze
python pl3/scripts/pick3.py analyze
```

### 生成推荐
```bash
python ssq/scripts/ssq.py recommend
python daletou/scripts/dlt.py recommend
python pl3/scripts/pick3.py recommend
```

## 数据存储

各自存储在用户目录下的 `.ssq_data`、`.dlt_data`、`.pl3_data` 文件夹中。

## 许可证

MIT License
