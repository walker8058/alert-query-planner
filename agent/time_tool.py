# agent/time_tool.py
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

DEFAULT_TZ = "Asia/Taipei"

def get_current_time() -> str:
    """取得目前時間
    用途:
        -當選用任何計畫前，必須先透過此工具獲得目前時間。
    回傳:
        以 "YYYY-MM-DD HH:MM:SS" 格式表示的目前時間字串。
    """
    print(f"[time_tool] 使用時區: {DEFAULT_TZ}")
    try:
        tz = ZoneInfo(DEFAULT_TZ)
    except Exception:
        # 回退 UTC
        print(f"[time_tool] 無法載入時區 {DEFAULT_TZ} ，改用 UTC")
        tz = timezone.utc
    now = datetime.now(tz)
    current = now.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[time_tool] 目前時間: {current}")
    return current