"""Meta Marketing API 클라이언트.

mock_data.py의 함수와 동일한 형식의 DataFrame을 반환하도록 정규화.
"""

from datetime import datetime, timedelta

import pandas as pd
import requests

from . import config

API_VERSION = "v19.0"
BASE = f"https://graph.facebook.com/{API_VERSION}"


class MetaAPIError(Exception):
    pass


def _call(path, params=None, timeout=30):
    params = dict(params or {})
    params["access_token"] = config.get_meta_token()
    url = f"{BASE}/{path}"
    try:
        r = requests.get(url, params=params, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except requests.HTTPError as e:
        try:
            body = e.response.json()
            msg = body.get("error", {}).get("message", str(e))
        except Exception:
            msg = str(e)
        raise MetaAPIError(f"{path}: {msg}")
    except requests.RequestException as e:
        raise MetaAPIError(f"{path}: {e}")


def _get_all(path, params=None, max_pages=10):
    """페이지네이션 자동 처리."""
    out = []
    next_url = None
    for _ in range(max_pages):
        if next_url:
            r = requests.get(next_url, timeout=30)
            data = r.json()
        else:
            data = _call(path, params)
        out.extend(data.get("data", []))
        paging = data.get("paging", {})
        next_url = paging.get("next")
        if not next_url:
            break
    return out


def _extract_action(actions, action_type):
    """actions 리스트에서 특정 액션 값 추출."""
    if not actions:
        return 0
    for a in actions:
        if a.get("action_type") == action_type:
            return float(a.get("value", 0))
    return 0


# ───────── 공개 API ─────────


def fetch_account_info():
    aid = config.get_meta_account_id()
    return _call(aid, {
        "fields": "id,name,account_status,currency,timezone_name,amount_spent,balance,disable_reason"
    })


def fetch_campaigns(days=30):
    """캠페인 목록 + 인사이트 병합. mock.meta_campaigns()와 동일 스키마."""
    aid = config.get_meta_account_id()

    # 캠페인 메타데이터
    campaigns_raw = _get_all(f"{aid}/campaigns", {
        "fields": "id,name,objective,status,effective_status,daily_budget,lifetime_budget,configured_status",
        "limit": 100
    })
    if not campaigns_raw:
        return pd.DataFrame()

    # 인사이트 (30일)
    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    until = datetime.now().strftime("%Y-%m-%d")
    insights_raw = _get_all(f"{aid}/insights", {
        "level": "campaign",
        "fields": "campaign_id,spend,impressions,clicks,ctr,cpc,frequency,actions,action_values,purchase_roas",
        "time_range": f'{{"since":"{since}","until":"{until}"}}',
        "limit": 100
    })

    # 매핑
    by_id = {}
    for row in insights_raw:
        cid = row.get("campaign_id")
        purchases = _extract_action(row.get("actions", []), "purchase")
        purchase_value = _extract_action(row.get("action_values", []), "purchase")
        roas_list = row.get("purchase_roas") or []
        roas = float(roas_list[0]["value"]) * 100 if roas_list else None
        spend = float(row.get("spend", 0))
        by_id[cid] = {
            "spend": spend,
            "purchases": int(purchases) if purchases else 0,
            "cpa": (spend / purchases) if purchases else None,
            "roas": roas,
            "ctr": float(row.get("ctr", 0)),
            "cvr": (purchases / float(row.get("clicks", 1)) * 100) if row.get("clicks") else 0,
            "frequency": float(row.get("frequency", 0)),
        }

    rows = []
    for c in campaigns_raw:
        ins = by_id.get(c["id"], {})
        spend = ins.get("spend", 0)
        purchases = ins.get("purchases", 0)
        roas = ins.get("roas")
        diag = _diagnose_campaign(roas, ins.get("ctr"), ins.get("cvr"), purchases)
        rows.append({
            "id": c["id"],
            "active": c.get("effective_status") in ("ACTIVE", "DELIVERING"),
            "name": c["name"],
            "objective": _translate_objective(c.get("objective", "")),
            "spend": spend,
            "purchases": purchases,
            "cpa": ins.get("cpa"),
            "roas": roas,
            "ctr": ins.get("ctr"),
            "cvr": ins.get("cvr"),
            "frequency": ins.get("frequency"),
            "learning": _learning_status(purchases, c.get("effective_status")),
            "status": diag["status"],
            "diag_color": diag["color"],
        })
    return pd.DataFrame(rows)


def fetch_adsets(days=30):
    """광고세트 목록 + 인사이트."""
    aid = config.get_meta_account_id()

    adsets_raw = _get_all(f"{aid}/adsets", {
        "fields": "id,campaign_id,name,status,effective_status,daily_budget,targeting,optimization_goal,learning_stage_info",
        "limit": 100
    })
    if not adsets_raw:
        return pd.DataFrame()

    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    until = datetime.now().strftime("%Y-%m-%d")
    insights_raw = _get_all(f"{aid}/insights", {
        "level": "adset",
        "fields": "adset_id,spend,impressions,clicks,ctr,frequency,actions,purchase_roas",
        "time_range": f'{{"since":"{since}","until":"{until}"}}',
        "limit": 200
    })
    by_id = {row["adset_id"]: row for row in insights_raw}

    rows = []
    for s in adsets_raw:
        ins = by_id.get(s["id"], {})
        purchases = int(_extract_action(ins.get("actions", []), "purchase"))
        roas_list = ins.get("purchase_roas") or []
        roas = float(roas_list[0]["value"]) * 100 if roas_list else None
        spend = float(ins.get("spend", 0))
        ctr = float(ins.get("ctr", 0))
        cvr = (purchases / float(ins.get("clicks", 1)) * 100) if ins.get("clicks") else 0
        diag = _diagnose_campaign(roas, ctr, cvr, purchases)

        ls_info = s.get("learning_stage_info", {}) or {}
        learning = ls_info.get("status", "—")

        rows.append({
            "campaign_id": s.get("campaign_id"),
            "active": s.get("effective_status") in ("ACTIVE", "DELIVERING"),
            "name": s["name"],
            "target": _extract_target_summary(s.get("targeting", {})),
            "daily_budget": int(s.get("daily_budget", 0)) // 100 if s.get("daily_budget") else 0,
            "spend": spend,
            "purchases": purchases,
            "cpa": (spend / purchases) if purchases else None,
            "roas": roas,
            "ctr": ctr,
            "cvr": cvr,
            "frequency": float(ins.get("frequency", 0)),
            "learning": "완료" if learning == "SUCCESS" else "미완료" if learning == "LEARNING" else "—",
            "status": diag["status"],
            "diag_color": diag["color"],
        })
    return pd.DataFrame(rows)


def fetch_ads(days=30):
    """광고(소재) 목록 + 인사이트."""
    aid = config.get_meta_account_id()

    ads_raw = _get_all(f"{aid}/ads", {
        "fields": "id,adset_id,campaign_id,name,status,effective_status,creative",
        "limit": 100
    })
    if not ads_raw:
        return pd.DataFrame()

    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    until = datetime.now().strftime("%Y-%m-%d")
    insights_raw = _get_all(f"{aid}/insights", {
        "level": "ad",
        "fields": "ad_id,spend,impressions,clicks,ctr,actions",
        "time_range": f'{{"since":"{since}","until":"{until}"}}',
        "limit": 500
    })
    by_id = {row["ad_id"]: row for row in insights_raw}

    rows = []
    for a in ads_raw:
        ins = by_id.get(a["id"], {})
        purchases = int(_extract_action(ins.get("actions", []), "purchase"))
        spend = float(ins.get("spend", 0))
        clicks = int(ins.get("clicks", 0))
        ctr = float(ins.get("ctr", 0))
        cvr = (purchases / clicks * 100) if clicks else 0
        diag = _diagnose_ad(ctr, cvr, purchases, spend)

        rows.append({
            "adset_idx": f"{a.get('campaign_id', '')}|{a.get('adset_id', '')}",
            "active": a.get("effective_status") in ("ACTIVE", "DELIVERING"),
            "name": a["name"],
            "format": "—",  # creative 객체 별도 조회 필요
            "spend": spend,
            "impressions": int(ins.get("impressions", 0)),
            "clicks": clicks,
            "ctr": ctr,
            "purchases": purchases,
            "cvr": cvr,
            "status": diag["status"],
            "diag_color": diag["color"],
        })
    return pd.DataFrame(rows)


def fetch_kpi(days=30):
    """대시보드 상단 KPI 카드용 집계."""
    aid = config.get_meta_account_id()
    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    until = datetime.now().strftime("%Y-%m-%d")
    prev_since = (datetime.now() - timedelta(days=days * 2)).strftime("%Y-%m-%d")
    prev_until = (datetime.now() - timedelta(days=days + 1)).strftime("%Y-%m-%d")

    def _agg(s, u):
        rows = _get_all(f"{aid}/insights", {
            "level": "account",
            "fields": "spend,impressions,clicks,actions,action_values,purchase_roas",
            "time_range": f'{{"since":"{s}","until":"{u}"}}',
        })
        if not rows:
            return None
        r = rows[0]
        spend = float(r.get("spend", 0))
        purchases = _extract_action(r.get("actions", []), "purchase")
        value = _extract_action(r.get("action_values", []), "purchase")
        roas_list = r.get("purchase_roas") or []
        roas = float(roas_list[0]["value"]) * 100 if roas_list else 0
        return {"spend": spend, "purchases": purchases, "value": value, "roas": roas}

    cur = _agg(since, until) or {"spend": 0, "purchases": 0, "value": 0, "roas": 0}
    prev = _agg(prev_since, prev_until) or {"spend": 0, "purchases": 0, "value": 0, "roas": 0}

    def _delta(c, p):
        if not p:
            return 0
        return (c - p) / p * 100

    return {
        "광고비_30일": cur["spend"],
        "매출_30일": cur["value"],
        "roas": cur["roas"],
        "cpa": (cur["spend"] / cur["purchases"]) if cur["purchases"] else 0,
        "신규고객": int(cur["purchases"]),
        "광고비_증감": _delta(cur["spend"], prev["spend"]),
        "매출_증감": _delta(cur["value"], prev["value"]),
        "roas_증감": int(cur["roas"] - prev["roas"]),
        "cpa_증감": _delta(
            (cur["spend"] / cur["purchases"]) if cur["purchases"] else 0,
            (prev["spend"] / prev["purchases"]) if prev["purchases"] else 1,
        ),
        "신규고객_증감": int(cur["purchases"] - prev["purchases"]),
        "운영_상태": None,  # 실데이터는 OFF 상태 자동 감지 별도 필요
    }


def fetch_timeseries(days=30):
    """일별 시계열."""
    aid = config.get_meta_account_id()
    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    until = datetime.now().strftime("%Y-%m-%d")
    rows = _get_all(f"{aid}/insights", {
        "level": "account",
        "fields": "spend,impressions,clicks,ctr,actions,action_values,purchase_roas",
        "time_range": f'{{"since":"{since}","until":"{until}"}}',
        "time_increment": 1,
        "limit": 100
    })
    out = []
    for r in rows:
        value = _extract_action(r.get("action_values", []), "purchase")
        roas_list = r.get("purchase_roas") or []
        roas = float(roas_list[0]["value"]) * 100 if roas_list else 0
        out.append({
            "date": pd.to_datetime(r["date_start"]),
            "광고비": float(r.get("spend", 0)),
            "매출": value,
            "ROAS": roas,
            "CTR": float(r.get("ctr", 0)),
        })
    return pd.DataFrame(out)


# ───────── 유틸 ─────────


def _diagnose_campaign(roas, ctr, cvr, purchases, target_roas=200):
    """회사 ON/OFF 기준 (재근님 표준).

    OFF: CTR < 1% / 1~2주 0건 / ROAS 목표 미달
    유지/증액: CTR > 3% / ROAS 목표 이상
    """
    if roas is None or roas == 0:
        if (purchases or 0) == 0:
            return {"status": "OFF 권장", "color": "🔴"}
        return {"status": "관찰", "color": "🟡"}
    if (ctr or 0) < 1.0:
        return {"status": "OFF 권장", "color": "🔴"}
    if roas < target_roas * 0.7:
        return {"status": "OFF 권장", "color": "🔴"}
    if roas < target_roas:
        return {"status": "관찰", "color": "🟡"}
    if roas >= target_roas * 1.5 and (ctr or 0) >= 3.0:
        return {"status": "증액 권장", "color": "🟢"}
    return {"status": "유지", "color": "🟢"}


def _diagnose_ad(ctr, cvr, purchases, spend):
    if (ctr or 0) < 1.0:
        return {"status": "OFF 권장", "color": "🔴"}
    if (ctr or 0) > 3.0 and (cvr or 0) > 1.0:
        return {"status": "유지", "color": "🟢"}
    if (purchases or 0) == 0 and spend > 100000:
        return {"status": "OFF 권장", "color": "🔴"}
    return {"status": "관찰", "color": "🟡"}


def _translate_objective(obj):
    return {
        "OUTCOME_SALES": "판매",
        "OUTCOME_TRAFFIC": "트래픽",
        "OUTCOME_AWARENESS": "인지도",
        "OUTCOME_LEADS": "리드",
        "OUTCOME_ENGAGEMENT": "참여",
        "OUTCOME_APP_PROMOTION": "앱",
        "LINK_CLICKS": "트래픽",
        "CONVERSIONS": "판매",
        "REACH": "도달",
    }.get(obj, obj)


def _extract_target_summary(targeting):
    if not targeting:
        return "—"
    age = f"{targeting.get('age_min', '')}-{targeting.get('age_max', '')}"
    genders = targeting.get("genders", [])
    gender = "여성" if genders == [2] else "남성" if genders == [1] else "전체"
    return f"{age}/{gender}"


def _learning_status(purchases, effective_status):
    if effective_status not in ("ACTIVE", "DELIVERING"):
        return "—"
    if purchases >= 50:
        return "완료"
    return "미완료"
