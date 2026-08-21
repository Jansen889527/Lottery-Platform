#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
服务端抓取中彩网双色球最近 N 期开奖数据，归一化为 data.json。
与 index.html 中 FALLBACK 结构保持一致：
  [{code, date, week, red:[...], blue, p1:{count,money}, p2:{count,money}}]
仅在 GitHub Actions 云端运行（无浏览器跨域限制）。本地也可直接运行生成初始 data.json。
"""
import json
import sys
import urllib.request

CWL_URL = "https://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/findDrawNotice?name=ssq&issueCount=120"
OUT = "data.json"


def fetch_raw():
    req = urllib.request.Request(CWL_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=25) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data.get("result", [])


def normalize(raw):
    out = []
    for r in raw:
        pg = r.get("prizegrades") or []
        p1 = {"count": 0, "money": 0}
        p2 = {"count": 0, "money": 0}
        for g in pg:
            try:
                t = int(g.get("type", 0))
                c = int(g.get("typenum") or 0)
                m = int(g.get("typemoney") or 0)
            except (TypeError, ValueError):
                continue
            if t == 1:
                p1 = {"count": c, "money": m}
            elif t == 2:
                p2 = {"count": c, "money": m}
        date = (r.get("date") or "").split("(")[0]
        week = (r.get("date") or "").split("(")[-1].replace(")", "")
        red = [s.strip() for s in (r.get("red") or "").split(",") if s.strip()]
        out.append(
            {
                "code": str(r.get("code")),
                "date": date,
                "week": week,
                "red": red,
                "blue": str(r.get("blue")),
                "p1": p1,
                "p2": p2,
            }
        )
    return out


def main():
    raw = fetch_raw()
    if not raw:
        print("未获取到数据，跳过写入")
        sys.exit(0)
    data = normalize(raw)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    print("已写入 %d 期，最新一期 %s（%s）" % (len(data), data[0]["code"], data[0]["date"]))


if __name__ == "__main__":
    main()
