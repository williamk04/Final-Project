from datetime import datetime, timezone



# Giả sử tổng số slot bãi
TOTAL_SLOTS = 50

def get_dashboard_summary(vehicles):
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")  # dùng UTC vì Firestore lưu +00:00

    # Xe hôm nay vào (dựa trên entry_time)
    today_entries = [
        v for v in vehicles
        if v.get('entry_time') and str(v.get('entry_time')).startswith(today_str)
    ]

    # Xe hôm nay ra (dựa trên exit_time)
    today_exits = [
        v for v in vehicles
        if v.get('exit_time') and str(v.get('exit_time')).startswith(today_str)
    ]

    # Doanh thu hôm nay
    revenue_today = sum(v.get('fee', 0) or 0 for v in today_exits)

    # Xe hiện tại (chưa ra)
    current_vehicles = [
        v for v in vehicles
        if v.get('status') == 'in'
    ]

    # Chỗ trống
    available_slots = TOTAL_SLOTS - len(current_vehicles)

    return {
        "today_entries": len(today_entries),
        "today_exits": len(today_exits),
        "revenue_today": revenue_today,
        "current_vehicles": len(current_vehicles),
        "available_slots": available_slots
    }
