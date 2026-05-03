#!/usr/bin/env python3
"""写入 AI 资讯到飞书「每日推送收集」表格"""
import json
import sys
import os
import urllib.request
import urllib.error

FEISHU_APP_ID = os.environ.get("FEISHU_APP_ID", "cli_a97b56e706f9dcce")
FEISHU_APP_SECRET = os.environ.get("FEISHU_APP_SECRET", "IAp35s1gBYTUuvwUknSnndS7Kojiwp1u")
SPREADSHEET_TOKEN = "MiqUs4YnPhyNOJt5yuKcQ45wn8c"
SHEET_ID = "4c6f73"

def get_token():
    data = json.dumps({"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET}).encode()
    req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    resp = urllib.request.urlopen(req)
    return json.loads(resp.read())["tenant_access_token"]

def get_last_row(token):
    """Find the last non-empty row in the sheet"""
    url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{SPREADSHEET_TOKEN}/values/{SHEET_ID}!A:G"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read())
    values = data.get("data", {}).get("valueRange", {}).get("values", [])
    return len(values) + 1  # 1-indexed, header is row 1

def write_rows(token, start_row, items, today):
    """Write rows starting at start_row"""
    rows = []
    for i, item in enumerate(items):
        row_num = start_row + i
        title = item.get("title", "").replace('"', "'")
        summary = item.get("summary", "").replace('"', "'")
        source = item.get("source", "").replace('"', "'")
        rows.append([today, item.get("time", "09:00"), title, summary, source, "已推送", ""])

    if not rows:
        print("没有资讯需要写入")
        return

    data = json.dumps({
        "valueRange": {
            "range": f"{SHEET_ID}!A{start_row}:G{start_row + len(rows) - 1}",
            "values": rows,
        }
    }).encode()

    req = urllib.request.Request(
        f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{SPREADSHEET_TOKEN}/values",
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="PUT",
    )
    resp = urllib.request.urlopen(req)
    result = json.loads(resp.read())
    print(f"写入 {len(rows)} 条成功: code={result.get('code')}, updatedRows={result.get('data', {}).get('updatedRows')}", flush=True)


def main():
    if len(sys.argv) <= 1:
        print("Usage: echo 'JSON' | feishu_push_ai_news.py <today_date>", flush=True)
        sys.exit(1)

    today = sys.argv[1]
    input_data = sys.stdin.read().strip()
    if not input_data:
        print("没有输入数据", flush=True)
        return

    try:
        items = json.loads(input_data)
        if not isinstance(items, list):
            items = [items]
    except json.JSONDecodeError as e:
        print(f"JSON 解析失败: {e}", flush=True)
        return

    token = get_token()
    start_row = get_last_row(token)
    write_rows(token, start_row, items, today)
    print("完成！", flush=True)


if __name__ == "__main__":
    main()
