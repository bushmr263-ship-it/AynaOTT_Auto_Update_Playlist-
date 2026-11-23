from datetime import datetime, timezone, timedelta
import json
import os
import requests

M3U_SOURCE_URL = "https://raw.githubusercontent.com/sm-monirulislam/AynaOTT_Auto_Update_Playlist/refs/heads/main/aynaott.m3u"
JSON_SOURCE_URL = "https://raw.githubusercontent.com/sm-monirulislam/AynaOTT_Auto_Update_Playlist/refs/heads/main/aynaott_data.json"

M3U_OUTPUT_FILE = "AynaOTT.m3u"
JSON_OUTPUT_FILE = "AynaOTT_data.json"

OWNER_NAME = "Shawon"
TELEGRAM_LINK = "https://t.me/+VqDOF_-beaQyMWY1"


def build_from_m3u(bd_time):
    resp = requests.get(M3U_SOURCE_URL, timeout=25)
    resp.raise_for_status()
    lines = resp.text.splitlines()

    entries = []
    current_extinf = None

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("#EXTINF:"):
            current_extinf = line
        elif not line.startswith("#") and current_extinf:
            entries.append((current_extinf, line))
            current_extinf = None

    if not entries:
        return None, 0

    out_lines = [
        "#EXTM3U",
        "# ==========================================",
        f"# Developed by: {OWNER_NAME}",
        f"# Telegram: {TELEGRAM_LINK}",
        f"# Last Updated: {bd_time} (BD Time)",
        f"# Channels Count: {len(entries)}",
        "# ==========================================",
        "",
    ]

    for extinf, url in entries:
        out_lines.append(extinf)
        out_lines.append(url)
        out_lines.append("")

    return "\n".join(out_lines).strip() + "\n", len(entries)


def update_aynaott():
    bd_now = datetime.now(timezone(timedelta(hours=6)))
    bd_time = bd_now.strftime("%Y-%m-%d %H:%M:%S")
    json_time = bd_now.strftime("%I:%M:%S %p %d-%m-%Y")

    # 1. JSON ডেটা সিঙ্ক
    try:
        j_resp = requests.get(JSON_SOURCE_URL, timeout=25)
        j_resp.raise_for_status()
        j_data = j_resp.json()
        if isinstance(j_data, dict):
            j_data["owner"] = OWNER_NAME
            j_data["telegram"] = TELEGRAM_LINK
            j_data["last_update_time"] = json_time
        with open(JSON_OUTPUT_FILE, "w", encoding="utf-8") as jf:
            json.dump(j_data, jf, indent=2, ensure_ascii=False)
        print(f"Updated {JSON_OUTPUT_FILE} at {bd_time}")
    except Exception as e:
        print(f"Warning while updating {JSON_OUTPUT_FILE}: {e}")

    # 2. M3U প্লেলিস্ট সিঙ্ক
    m3u_content, count = build_from_m3u(bd_time)
    if not m3u_content or count == 0:
        print(f"No AynaOTT stream entries found at {bd_time}.")
        if not os.path.exists(M3U_OUTPUT_FILE):
            header_only = [
                "#EXTM3U",
                "# ==========================================",
                f"# Developed by: {OWNER_NAME}",
                f"# Telegram: {TELEGRAM_LINK}",
                f"# Last Updated: {bd_time} (BD Time)",
                "# Channels Count: 0",
                "# ==========================================",
                "",
            ]
            with open(M3U_OUTPUT_FILE, "w", encoding="utf-8") as mf:
                mf.write("\n".join(header_only))
        return

    with open(M3U_OUTPUT_FILE, "w", encoding="utf-8") as mf:
        mf.write(m3u_content)

    print(f"Updated {M3U_OUTPUT_FILE} with {count} channels at {bd_time}")


if __name__ == "__main__":
    update_aynaott()
