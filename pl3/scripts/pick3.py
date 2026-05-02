#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
排列三（排列3）数据分析工具 v3.0 数据分析工具 v3.0 (2026-04 官方接口迁移)
用法:
  python pick3.py fetch      # 联网抓取最新数据
  python pick3.py analyze    # 分析最近30期，输出统计
  python pick3.py recommend  # 生成5注推荐+置信度+投注类型
  python pick3.py all        # 一键全流程
  python pick3.py review <期号> <百位> <十位> <个位>

依赖: pip install requests beautifulsoup4
复用 Conda 环境: D:\Conda\envs\ssq-lottery-analysis\
数据存储: C:\\Users\\用户名\\.pl3_data\\

列结构（65列/行）:
  [0]=期号 [2]=星期 [4]=奖号(3位连写如"499") [6]=和值
  [8-17]=百位走势(chartball01标记=百位数字)
  [19-28]=十位走势(chartball02标记=十位数字)
  [30-39]=个位走势(chartball01标记=个位数字)
"""

import sys, os, json, math, random, statistics, argparse
from datetime import datetime
from collections import Counter
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError as e:
    print(f"缺少依赖: {e}\n请运行: pip install requests beautifulsoup4")
    sys.exit(1)

TOTAL_COMBOS   = 1000
ANALYZE_WINDOW = 30
RECOMMEND_N    = 5
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Mobile Safari/537.36",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Referer": "https://static.sporttery.cn/",
}
NO_PROXY = {"http": "", "https": ""}
DATA_DIR  = Path.home() / ".pl3_data"
HIST_FILE = DATA_DIR / "history.json"
ARCHIVE_FILE = DATA_DIR / "predictions.json"


# ── 1. 数据抓取 ──────────────────────────────────────

def fetch_from_sporttery(page_size=100, timeout=20):
    """体彩官方API（排列3 gameNo=35）"""
    url = "https://webapi.sporttery.cn/gateway/lottery/getHistoryPageListV1.qry"
    params = {
        "gameNo": "35",       # 35 = 排列3
        "provinceId": "0",
        "pageSize": str(page_size),
        "isVerify": "1",
        "pageNo": "1",
    }
    try:
        resp = requests.get(url, params=params, headers=HEADERS,
                           timeout=timeout, proxies=NO_PROXY)
        resp.raise_for_status()
        data = resp.json()
        if data.get("errorCode") != "0":
            raise Exception(data.get("errorMsg", "API返回异常"))

        records = []
        for item in data.get("value", {}).get("list", []):
            period = item.get("lotteryDrawNum", "")
            result_str = item.get("lotteryDrawResult", "")
            nums = [int(x) for x in result_str.split() if x.isdigit()]
            if len(nums) == 3:
                h, t, u = nums[0], nums[1], nums[2]
                sum_val = h + t + u
                span = max(h, t, u) - min(h, t, u)
                if h == t == u:
                    group_type = "豹子"
                elif h == t or t == u or h == u:
                    group_type = "组三"
                else:
                    group_type = "组六"
                records.append({
                    "period": period,
                    "hundreds": h,
                    "tens": t,
                    "units": u,
                    "sum_val": sum_val,
                    "span": span,
                    "group_type": group_type,
                    "date": item.get("lotteryDrawTime", "")[:10],
                })
        print(f"  sporttery.cn: 拉取 {len(records)} 期")
        return records
    except Exception as e:
        print(f"  sporttery.cn 抓取失败: {e}")
        return []


def cmd_fetch(_):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print("=" * 58)
    print("  [Step 1] 联网抓取")
    print("=" * 58)

    records = fetch_from_sporttery(100)
    if not records:
        print("FETCH_FAILED")
        return

    existing  = _load_history()
    exist_set = {r["period"] for r in existing}
    new_n     = 0
    for r in records:
        if r["period"] not in exist_set:
            existing.append(r); new_n += 1
    existing.sort(key=lambda x: x["period"], reverse=True)
    _save_history(existing)

    lat = existing[0]
    nums = f"{lat['hundreds']} {lat['tens']} {lat['units']}"
    print(f"新增 {new_n} 期，本地共 {len(existing)} 期")
    print(f"最新: {lat['period']}  开奖号 {nums}  [{lat['group_type']}]")
def _load_history():
    if HIST_FILE.exists():
        try: return json.loads(HIST_FILE.read_text(encoding="utf-8"))
        except: pass
    return []

def _save_history(r):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    HIST_FILE.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")

def _load_archive():
    if ARCHIVE_FILE.exists():
        try: return json.loads(ARCHIVE_FILE.read_text(encoding="utf-8"))
        except: pass
    return []

def _save_archive(d):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ARCHIVE_FILE.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


# ── 6. 入口 ──────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description="Pick 3（排列三）数据分析工具 v3.0 (2026-04 官方接口迁移)")
    sub = p.add_subparsers(dest="cmd")
    sub.add_parser("fetch").add_argument("--periods", type=int, default=100, choices=[30, 50, 100])
    sub.add_parser("analyze")
    sub.add_parser("recommend")
    sub.add_parser("all")
    rv = sub.add_parser("review")
    rv.add_argument("nums", nargs="+")
    args = p.parse_args()

    if args.cmd == "fetch":       cmd_fetch(args)
    elif args.cmd == "analyze":   cmd_analyze(args)
    elif args.cmd == "recommend": cmd_recommend(args)
    elif args.cmd == "all":
        cmd_fetch(args); print(); cmd_analyze(args); print(); cmd_recommend(args)
    elif args.cmd == "review":    cmd_review(args)
    else: p.print_help()

if __name__ == "__main__":
    main()
