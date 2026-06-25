#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import re
from datetime import datetime
from bs4 import BeautifulSoup
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# ---------- 1. 高雄旅遊網 (API) ----------
def fetch_khh():
    print("抓取高雄旅遊網...")
    url = "https://openapi.kcg.gov.tw/Api/Service/Get/80bbbbd3-9ee4-4244-98e9-b4c08deda91b"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        data = resp.json()
    except Exception as e:
        print(f"  失敗: {e}")
        return []
    events = []
    for item in data:
        # 請根據實際 API 欄位調整（先用範例結構）
        events.append({
            "id": item.get("Id", 0),
            "images": [item.get("ImageUrl", "")] if item.get("ImageUrl") else [],
            "title": item.get("Title", "未知活動"),
            "region": "kaohsiung",
            "category": "show",
            "startDate": item.get("StartDate", "")[:10] if item.get("StartDate") else "",
            "endDate": item.get("EndDate", item.get("StartDate", ""))[:10],
            "startTime": item.get("StartTime", "")[:5] if item.get("StartTime") else "",
            "endTime": item.get("EndTime", "")[:5] if item.get("EndTime") else "",
            "location": item.get("Location", ""),
            "tags": item.get("Tags", "").split(",") if item.get("Tags") else [],
            "createdAt": datetime.now().strftime("%Y-%m-%d"),
            "detailUrl": item.get("Url", ""),
            "sponsored": False
        })
    print(f"  抓到 {len(events)} 筆")
    return events

# ---------- 2. 駁二藝術特區 (HTML) ----------
def fetch_pier2():
    print("抓取駁二藝術特區...")
    url = "https://pier2.org/activity/list/all/"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
    except Exception as e:
        print(f"  失敗: {e}")
        return []
    events = []
    # 請用實際 HTML 選擇器（此為示範）
    cards = soup.select(".activity-item") or soup.select(".list-item")
    for card in cards:
        try:
            title = card.select_one(".title").text.strip() if card.select_one(".title") else ""
            img = card.select_one("img")["src"] if card.select_one("img") else ""
            if img and not img.startswith("http"):
                img = "https://pier2.org" + img
            events.append({
                "id": 1000 + len(events),
                "images": [img] if img else [],
                "title": title,
                "region": "kaohsiung",
                "category": "exhibition",
                "startDate": "",
                "endDate": "",
                "startTime": "",
                "endTime": "",
                "location": "駁二藝術特區",
                "tags": [],
                "createdAt": datetime.now().strftime("%Y-%m-%d"),
                "detailUrl": url,
                "sponsored": False
            })
        except:
            continue
    print(f"  抓到 {len(events)} 筆")
    return events

# ---------- 3. 高雄巨蛋 (純文字) ----------
def fetch_kaoarena():
    print("抓取高雄巨蛋...")
    url = "https://www.kaoarena.com.tw/Home/Calendar"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        text = resp.text
    except Exception as e:
        print(f"  失敗: {e}")
        return []
    events = []
    pattern = r"(\d{4}/\d{2}/\d{2})\s+([^\d]+)"
    for date_str, title in re.findall(pattern, text):
        try:
            y, m, d = date_str.split("/")
            iso_date = f"{y}-{m}-{d}"
            events.append({
                "id": 2000 + len(events),
                "images": [],
                "title": title.strip(),
                "region": "kaohsiung",
                "category": "concert",
                "startDate": iso_date,
                "endDate": iso_date,
                "startTime": "",
                "endTime": "",
                "location": "高雄巨蛋",
                "tags": [],
                "createdAt": datetime.now().strftime("%Y-%m-%d"),
                "detailUrl": url,
                "sponsored": False
            })
        except:
            continue
    print(f"  抓到 {len(events)} 筆")
    return events

# ---------- 4. 衛武營 (此處先回傳空，待你後續自訂) ----------
def fetch_weiwuying():
    print("抓取衛武營 (暫未實作，回傳空)...")
    return []

# ---------- 合併與輸出 ----------
def main():
    all_events = []
    all_events.extend(fetch_khh())
    time.sleep(1)
    all_events.extend(fetch_pier2())
    time.sleep(1)
    all_events.extend(fetch_kaoarena())
    time.sleep(1)
    all_events.extend(fetch_weiwuying())

    # 去重 (依 title + startDate)
    seen = set()
    unique = []
    for ev in all_events:
        key = (ev["title"], ev["startDate"])
        if key not in seen:
            seen.add(key)
            unique.append(ev)

    with open("events.json", "w", encoding="utf-8") as f:
        json.dump(unique, f, ensure_ascii=False, indent=2)
    print(f"✅ 共 {len(unique)} 筆，已寫入 events.json")

if __name__ == "__main__":
    main()