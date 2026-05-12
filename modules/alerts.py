"""알람 생성 — 캘린더·결재·데이터 이상 자동 감지."""

from datetime import datetime, timedelta


def generate_alerts(now=None, data=None):
    """현재 시점 기준 모든 알람 생성. data는 dashboard data provider 모듈."""
    if now is None:
        now = datetime.now()

    alerts = []

    # ───── 캘린더 알람 ─────

    if now.day == 15:
        alerts.append({
            "level": "warning",
            "icon": "📅",
            "title": "오늘은 브랜드검색 계약 갱신일",
            "body": "매월 15일 — 브랜드검색 (PC + MO 약 158만원/월) 갱신 여부 결정 + 페이북 결제 + 전자결재 (기안 X).",
            "category": "calendar",
        })
    elif now.day == 14:
        alerts.append({
            "level": "info",
            "icon": "📅",
            "title": "내일 브랜드검색 계약 갱신일",
            "body": "내일(15일) 브랜드검색 갱신 검토. 미리 운영 효과·신제품·이벤트 일정 확인.",
            "category": "calendar",
        })
    elif now.day == 16:
        alerts.append({
            "level": "info",
            "icon": "📅",
            "title": "어제 브랜드검색 갱신 진행 됐는지?",
            "body": "어제(15일) 갱신일이었음. 결제·전자결재 마무리 확인.",
            "category": "calendar",
        })

    if 1 <= now.day <= 10:
        alerts.append({
            "level": "warning",
            "icon": "💸",
            "title": f"Naver 결재 기간 ({now.day}/10일째)",
            "body": "매월 1~10일 — ludient 메일로 Naver 영수증·세금계산서 발행. 영역별 비용 리체크 → 전자결재 (기안 X).",
            "category": "billing",
        })

    if now.weekday() == 0:
        alerts.append({
            "level": "warning",
            "icon": "💸",
            "title": "Meta 인보이스 결재일 (월요일)",
            "body": "재무팀 이종현님 위클리 법인카드 내역 (지난주 일~토) → 메타 인보이스 대조 → 다우 결재 (지출결의만).",
            "category": "billing",
        })

    # ───── 데이터 기반 알람 ─────
    if data is None:
        return alerts

    # 비즈머니 잔액
    try:
        kpi = data.get_naver_kpi()
        balance = kpi.get("비즈머니_잔액", 0) if isinstance(kpi, dict) else 0
        if balance and balance < 100_000:
            alerts.append({
                "level": "error",
                "icon": "💰",
                "title": "Naver 비즈머니 잔액 부족",
                "body": f"현재 잔액 ₩{balance:,}. 10만원 미만 — 즉시 충전 검토.",
                "category": "balance",
            })
        elif balance and balance < 300_000:
            alerts.append({
                "level": "warning",
                "icon": "💰",
                "title": "Naver 비즈머니 잔액 임박",
                "body": f"현재 잔액 ₩{balance:,}. 1~2주 후 부족 가능 — 충전 일정 확인.",
                "category": "balance",
            })
    except Exception:
        pass

    # OFF 권장 캠페인
    try:
        campaigns = data.get_naver_campaigns()
        if not campaigns.empty:
            bad = campaigns[campaigns["status"] == "OFF 권장"]
            if len(bad) > 0:
                alerts.append({
                    "level": "warning",
                    "icon": "📉",
                    "title": f"Naver OFF 권장 캠페인 {len(bad)}개",
                    "body": " · ".join(bad["name"].head(3).tolist())
                            + (f" 외 {len(bad)-3}개" if len(bad) > 3 else ""),
                    "category": "campaign",
                })
    except Exception:
        pass

    # 학습 미완료 광고세트 (Meta)
    try:
        adsets = data.get_meta_adsets()
        if not adsets.empty and "learning" in adsets.columns:
            unfinished = adsets[adsets["learning"] == "미완료"]
            if len(unfinished) > 0:
                alerts.append({
                    "level": "warning",
                    "icon": "🎓",
                    "title": f"Meta 학습 미완료 광고세트 {len(unfinished)}개",
                    "body": "학습 7일/50건 룰 미달 — 예산 증액 또는 광고세트 통합 검토.",
                    "category": "campaign",
                })
    except Exception:
        pass

    # 키워드 OFF 권장
    try:
        keywords = data.get_naver_keywords()
        if not keywords.empty:
            kw_bad = keywords[keywords["status"] == "OFF 권장"]
            if len(kw_bad) > 0:
                alerts.append({
                    "level": "info",
                    "icon": "🔑",
                    "title": f"Naver OFF 권장 키워드 {len(kw_bad)}개",
                    "body": "효율 낮은 키워드 정리 검토 — 키워드 센터에서 노출 제외 또는 입찰가 ↓",
                    "category": "keyword",
                })
    except Exception:
        pass

    return alerts


def alerts_summary(alerts):
    """알람 카운트 요약."""
    counts = {"error": 0, "warning": 0, "info": 0}
    for a in alerts:
        counts[a.get("level", "info")] = counts.get(a.get("level", "info"), 0) + 1
    return counts
