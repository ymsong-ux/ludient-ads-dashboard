"""Naver Search Ads API 클라이언트.

HMAC-SHA256 서명 인증 + 캠페인/광고그룹/키워드/통계 조회.
GFA·브랜드검색·쇼핑검색은 별도 API라 일부만 지원.
"""

import base64
import hashlib
import hmac
import json
import time
from datetime import datetime, timedelta

import pandas as pd
import requests

from . import config

BASE = "https://api.searchad.naver.com"


class NaverAPIError(Exception):
    pass


def _sign(method, uri, timestamp_ms):
    secret = config.get_naver_secret_key()
    message = f"{timestamp_ms}.{method}.{uri}"
    return base64.b64encode(
        hmac.new(secret.encode("utf-8"), message.encode("utf-8"), hashlib.sha256).digest()
    ).decode("utf-8")


def _call(method, uri, params=None, json_body=None, timeout=30):
    timestamp = str(int(time.time() * 1000))
    headers = {
        "X-Timestamp": timestamp,
        "X-API-KEY": config.get_naver_api_key(),
        "X-Customer": str(config.get_naver_customer_id()),
        "X-Signature": _sign(method, uri, timestamp),
        "Content-Type": "application/json; charset=UTF-8",
    }
    url = BASE + uri
    try:
        if method == "GET":
            r = requests.get(url, headers=headers, params=params, timeout=timeout)
        else:
            r = requests.request(method, url, headers=headers, json=json_body, timeout=timeout)
        if r.status_code >= 400:
            raise NaverAPIError(f"{r.status_code} {uri}: {r.text[:300]}")
        return r.json()
    except requests.RequestException as e:
        raise NaverAPIError(f"{uri}: {e}")


def _translate_campaign_type(tp):
    return {
        "WEB_SITE": "파워링크",
        "SHOPPING": "쇼핑검색",
        "POWER_CONTENTS": "콘텐츠검색",
        "BRAND_SEARCH": "브랜드검색",
        "PLACE": "플레이스",
    }.get(tp, tp or "기타")


def _diagnose_keyword(ctr, cvr, conv, quality):
    """회사 기준 진단."""
    q = quality or 4
    if (ctr or 0) < 1.0 and (conv or 0) == 0:
        return ("OFF 권장", "🔴")
    if q <= 2:
        return ("OFF 권장", "🔴")
    if (ctr or 0) > 3.0 and (conv or 0) > 0:
        return ("증액 권장", "🟢")
    if (ctr or 0) >= 1.0 and (conv or 0) >= 1:
        return ("유지", "🟢")
    return ("관찰", "🟡")


def fetch_bizmoney():
    """비즈머니 잔액."""
    try:
        data = _call("GET", "/billing/bizmoney")
        if isinstance(data, dict):
            return data.get("bizmoney", 0)
        return 0
    except Exception:
        return 0


def fetch_campaigns_raw():
    """원시 캠페인 데이터."""
    return _call("GET", "/ncc/campaigns") or []


def fetch_adgroups_raw(campaign_id=None):
    """원시 광고그룹 (캠페인 ID로 필터)."""
    params = {"nccCampaignId": campaign_id} if campaign_id else None
    return _call("GET", "/ncc/adgroups", params=params) or []


def fetch_keywords_raw(adgroup_id):
    """원시 키워드 (광고그룹 ID로)."""
    return _call("GET", "/ncc/keywords", params={"nccAdgroupId": adgroup_id}) or []


def _aggregate_stats(ids, fields, since, until):
    """Stats API 호출. ids 빈 리스트면 빈 dict 반환."""
    if not ids:
        return {}
    try:
        result = _call("GET", "/stats", params={
            "ids": json.dumps(ids),
            "fields": json.dumps(fields),
            "timeRange": json.dumps({"since": since, "until": until}),
        })
        return {row.get("id"): row for row in result} if isinstance(result, list) else {}
    except Exception:
        return {}


def fetch_campaigns(days=30):
    """캠페인 + 통계 병합."""
    camps = fetch_campaigns_raw()
    if not camps:
        return pd.DataFrame()

    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    until = datetime.now().strftime("%Y-%m-%d")
    ids = [c.get("nccCampaignId") for c in camps]
    stats = _aggregate_stats(ids, ["impCnt", "clkCnt", "salesAmt", "ccnt", "convAmt"], since, until)

    rows = []
    for c in camps:
        cid = c.get("nccCampaignId")
        s = stats.get(cid, {})
        imp = int(s.get("impCnt", 0))
        clk = int(s.get("clkCnt", 0))
        conv = int(s.get("ccnt", 0))
        spend = float(s.get("salesAmt", 0))
        ctr = (clk / imp * 100) if imp else 0
        cvr = (conv / clk * 100) if clk else 0

        if conv == 0 and clk > 50:
            status, color = ("OFF 권장", "🔴")
        elif ctr > 3 and conv > 0:
            status, color = ("증액 권장", "🟢")
        elif ctr >= 1:
            status, color = ("유지", "🟢")
        else:
            status, color = ("관찰", "🟡")

        rows.append({
            "id": cid,
            "active": c.get("status") in ("ELIGIBLE", "EXAMINING"),
            "name": c.get("name"),
            "type": _translate_campaign_type(c.get("campaignTp")),
            "daily_budget": int(c.get("dailyBudget") or 0),
            "spend": spend,
            "impressions": imp,
            "clicks": clk,
            "ctr": ctr,
            "conversions": conv,
            "cvr": cvr,
            "status": status,
            "diag_color": color,
        })
    return pd.DataFrame(rows)


def fetch_adgroups(days=30):
    """모든 광고그룹 + 통계 병합."""
    camps = fetch_campaigns_raw()
    if not camps:
        return pd.DataFrame()

    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    until = datetime.now().strftime("%Y-%m-%d")

    all_groups = []
    for c in camps:
        try:
            groups = fetch_adgroups_raw(c.get("nccCampaignId"))
            for g in groups:
                g["_campaign_id"] = c.get("nccCampaignId")
                all_groups.append(g)
        except Exception:
            continue

    if not all_groups:
        return pd.DataFrame()

    ids = [g.get("nccAdgroupId") for g in all_groups]
    stats = _aggregate_stats(ids, ["impCnt", "clkCnt", "salesAmt", "ccnt"], since, until)

    rows = []
    for g in all_groups:
        gid = g.get("nccAdgroupId")
        s = stats.get(gid, {})
        imp = int(s.get("impCnt", 0))
        clk = int(s.get("clkCnt", 0))
        conv = int(s.get("ccnt", 0))
        ctr = (clk / imp * 100) if imp else 0
        cvr = (conv / clk * 100) if clk else 0
        status, color = _diagnose_keyword(ctr, cvr, conv, 4)

        rows.append({
            "campaign_id": g.get("_campaign_id"),
            "active": g.get("status") in ("ELIGIBLE", "EXAMINING"),
            "name": g.get("name"),
            "default_bid": int(g.get("bidAmt") or 0),
            "spend": float(s.get("salesAmt", 0)),
            "impressions": imp,
            "clicks": clk,
            "ctr": ctr,
            "conversions": conv,
            "cvr": cvr,
            "status": status,
            "diag_color": color,
        })
    return pd.DataFrame(rows)


def fetch_keywords(days=30):
    """모든 키워드 + 통계 병합."""
    camps = fetch_campaigns_raw()
    if not camps:
        return pd.DataFrame()

    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    until = datetime.now().strftime("%Y-%m-%d")

    all_keywords = []
    for c in camps:
        try:
            groups = fetch_adgroups_raw(c.get("nccCampaignId"))
            for g in groups:
                try:
                    kws = fetch_keywords_raw(g.get("nccAdgroupId"))
                    for k in kws:
                        k["_default_bid"] = g.get("bidAmt", 0)
                        all_keywords.append(k)
                except Exception:
                    continue
        except Exception:
            continue

    if not all_keywords:
        return pd.DataFrame()

    ids = [k.get("nccKeywordId") for k in all_keywords]
    # Naver stats max 100 IDs per call — chunk
    stats = {}
    for i in range(0, len(ids), 100):
        chunk = ids[i:i+100]
        stats.update(_aggregate_stats(chunk, ["impCnt", "clkCnt", "salesAmt", "ccnt", "convAmt", "ctr", "cpc"], since, until))

    rows = []
    for k in all_keywords:
        kid = k.get("nccKeywordId")
        s = stats.get(kid, {})
        imp = int(s.get("impCnt", 0))
        clk = int(s.get("clkCnt", 0))
        conv = int(s.get("ccnt", 0))
        ctr = (clk / imp * 100) if imp else 0
        cvr = (conv / clk * 100) if clk else 0
        quality = int(k.get("qi") or 4)
        status, color = _diagnose_keyword(ctr, cvr, conv, quality)

        rows.append({
            "active": k.get("status") in ("ELIGIBLE", "EXAMINING"),
            "keyword": k.get("keyword"),
            "match": "구문",  # API에 매칭 타입 별도 정보 없음 — 기본값
            "bid": int(k.get("bidAmt") or k.get("_default_bid") or 0),
            "monthly_search": 0,  # 별도 키워드 도구 API 호출 필요
            "impressions": imp,
            "clicks": clk,
            "ctr": ctr,
            "purchases": conv,
            "cvr": cvr,
            "rank_avg": 0,  # API에 평균 순위 없음 — 별도 계산
            "quality": quality,
            "status": status,
            "diag_color": color,
        })
    return pd.DataFrame(rows)


def fetch_kpi(days=7):
    """대시보드 상단 KPI 카드."""
    camps = fetch_campaigns_raw()
    if not camps:
        return None

    cids = [c.get("nccCampaignId") for c in camps]
    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    until = datetime.now().strftime("%Y-%m-%d")
    prev_since = (datetime.now() - timedelta(days=days * 2)).strftime("%Y-%m-%d")
    prev_until = (datetime.now() - timedelta(days=days + 1)).strftime("%Y-%m-%d")

    cur = _aggregate_stats(cids, ["impCnt", "clkCnt", "salesAmt", "ccnt"], since, until)
    prev = _aggregate_stats(cids, ["impCnt", "clkCnt", "salesAmt", "ccnt"], prev_since, prev_until)

    def _sum(d, key):
        return sum(row.get(key, 0) or 0 for row in d.values())

    cur_imp = _sum(cur, "impCnt")
    cur_clk = _sum(cur, "clkCnt")
    cur_conv = _sum(cur, "ccnt")
    cur_spend = _sum(cur, "salesAmt")
    prev_imp = _sum(prev, "impCnt")
    prev_clk = _sum(prev, "clkCnt")
    prev_conv = _sum(prev, "ccnt")

    def _delta(c, p):
        return ((c - p) / p * 100) if p else 0

    bizmoney = fetch_bizmoney()

    return {
        "노출": int(cur_imp),
        "클릭": int(cur_clk),
        "전환": int(cur_conv),
        "ctr": (cur_clk / cur_imp * 100) if cur_imp else 0,
        "cvr": (cur_conv / cur_clk * 100) if cur_clk else 0,
        "비즈머니_잔액": int(bizmoney),
        "광고비_7일": int(cur_spend),
        "노출_증감": _delta(cur_imp, prev_imp),
        "클릭_증감": _delta(cur_clk, prev_clk),
        "전환_증감": _delta(cur_conv, prev_conv),
    }


def fetch_timeseries(days=30):
    """일별 시계열. /stats?datePreset 사용."""
    camps = fetch_campaigns_raw()
    if not camps:
        return pd.DataFrame()

    cids = [c.get("nccCampaignId") for c in camps]
    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    until = datetime.now().strftime("%Y-%m-%d")

    try:
        rows = _call("GET", "/stats", params={
            "ids": json.dumps(cids),
            "fields": json.dumps(["impCnt", "clkCnt", "salesAmt", "ccnt"]),
            "timeRange": json.dumps({"since": since, "until": until}),
            "datePreset": "TODAY",
            "breakdown": "day",
        })
    except Exception:
        return pd.DataFrame()

    by_date = {}
    for r in (rows or []):
        d = r.get("statDt") or r.get("date")
        if not d:
            continue
        if d not in by_date:
            by_date[d] = {"노출": 0, "클릭": 0, "전환": 0, "광고비": 0}
        by_date[d]["노출"] += r.get("impCnt", 0)
        by_date[d]["클릭"] += r.get("clkCnt", 0)
        by_date[d]["전환"] += r.get("ccnt", 0)
        by_date[d]["광고비"] += r.get("salesAmt", 0)

    out = [{"date": pd.to_datetime(k), **v} for k, v in sorted(by_date.items())]
    return pd.DataFrame(out)
