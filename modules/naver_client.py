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
    """비즈머니 잔액. 에러는 그대로 propagate (silent fail 금지)."""
    data = _call("GET", "/billing/bizmoney")
    if isinstance(data, dict):
        return data.get("bizmoney", 0)
    return 0


def debug_signature(method="GET", uri="/ncc/campaigns"):
    """서명 디버깅용 — 실제 호출 없이 서명 정보만 반환."""
    timestamp = str(int(time.time() * 1000))
    secret = config.get_naver_secret_key()
    api_key = config.get_naver_api_key()
    customer = config.get_naver_customer_id()

    message = f"{timestamp}.{method}.{uri}"
    signature = _sign(method, uri, timestamp)

    return {
        "timestamp": timestamp,
        "method": method,
        "uri": uri,
        "message_to_sign": message,
        "secret_key_length": len(secret) if secret else 0,
        "secret_key_preview": f"{secret[:8]}...{secret[-8:]}" if secret and len(secret) > 16 else "(짧음)",
        "secret_key_has_whitespace": secret != secret.strip() if secret else False,
        "api_key_length": len(api_key) if api_key else 0,
        "api_key_preview": f"{api_key[:12]}...{api_key[-8:]}" if api_key and len(api_key) > 20 else "(짧음)",
        "customer_id": customer,
        "signature": signature,
    }


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


def add_keyword(adgroup_id, keyword, bid_amt=None):
    """광고그룹에 키워드 추가. POST /ncc/keywords."""
    if not adgroup_id or not keyword:
        raise NaverAPIError("광고그룹 ID 또는 키워드 누락")
    body = {
        "nccAdgroupId": adgroup_id,
        "keyword": keyword,
        "useGroupBidAmt": bid_amt is None,
    }
    if bid_amt is not None:
        body["bidAmt"] = int(bid_amt)
    try:
        result = _call("POST", "/ncc/keywords", json_body=body)
        return {"success": True, "keyword_id": result.get("nccKeywordId"), "data": result}
    except NaverAPIError as e:
        return {"success": False, "error": str(e)}


def delete_keyword(keyword_id):
    """키워드 삭제. DELETE /ncc/keywords/{id}."""
    try:
        _call("DELETE", f"/ncc/keywords/{keyword_id}")
        return {"success": True}
    except NaverAPIError as e:
        return {"success": False, "error": str(e)}


def add_negative_keyword(adgroup_id, keyword):
    """노출 제외 키워드 추가. POST /ncc/adgroups/{id}/restricted-keyword.

    Naver는 광고그룹별 제외 키워드를 별도 엔드포인트로 관리.
    """
    if not adgroup_id or not keyword:
        raise NaverAPIError("광고그룹 ID 또는 키워드 누락")
    try:
        # Naver Search Ads 제외 키워드는 광고그룹 설정 일부
        # 정확한 엔드포인트: PUT /ncc/adgroups/{id} 에 keywordPlusEnabled + restrictedKeywords 업데이트
        # 또는 별도 엔드포인트가 있을 수 있음 — 여기는 일반화된 시도
        result = _call("POST", f"/ncc/adgroups/{adgroup_id}/restricted-keyword",
                       json_body={"keyword": keyword})
        return {"success": True, "data": result}
    except NaverAPIError as e:
        # 폴백: 광고그룹 자체 업데이트로 시도
        return {"success": False, "error": str(e)}


def update_keyword_status(keyword_id, on=True):
    """키워드 ON/OFF. PUT /ncc/keywords/{id}."""
    try:
        result = _call("PUT", f"/ncc/keywords/{keyword_id}",
                       json_body={"userLock": not on})
        return {"success": True, "data": result}
    except NaverAPIError as e:
        return {"success": False, "error": str(e)}


def update_keyword_bid(keyword_id, bid_amt):
    """키워드 입찰가 변경. PUT /ncc/keywords/{id}."""
    try:
        result = _call("PUT", f"/ncc/keywords/{keyword_id}",
                       json_body={"bidAmt": int(bid_amt), "useGroupBidAmt": False})
        return {"success": True, "data": result}
    except NaverAPIError as e:
        return {"success": False, "error": str(e)}


def fetch_search_query_report(days=7, max_wait=30):
    """검색어 보고서 (실제 노출된 사용자 검색어).

    Master Reports API 사용 — 비동기 작업:
    1. POST /master-reports (작업 생성)
    2. GET /master-reports/{id} (상태 폴링)
    3. downloadUrl로 결과 다운로드 (TSV)

    Naver Search Ads API의 master-reports는 reportTp='AD_DETAIL'로
    키워드별 검색어 정보를 받음.
    """
    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    # 1. 보고서 생성 요청
    try:
        job = _call("POST", "/master-reports", json_body={
            "reportTp": "AD_DETAIL",
            "statDt": since,
        })
    except Exception as e:
        raise NaverAPIError(f"보고서 생성 실패: {e}")

    report_id = (job or {}).get("id")
    if not report_id:
        raise NaverAPIError("보고서 ID 없음")

    # 2. 완료 대기 (폴링)
    for _ in range(max_wait):
        time.sleep(1)
        try:
            status_resp = _call("GET", f"/master-reports/{report_id}")
        except Exception:
            continue
        status = (status_resp or {}).get("status")
        if status == "BUILT" or status == "DONE":
            download_url = status_resp.get("downloadUrl")
            if not download_url:
                raise NaverAPIError("downloadUrl 없음")
            break
        if status in ("FAILED", "ERROR", "REGISTERED_FAILED"):
            raise NaverAPIError(f"보고서 생성 실패 status={status}")
    else:
        raise NaverAPIError("보고서 대기 시간 초과")

    # 3. 파일 다운로드 (서명 별도 — token=API_KEY 헤더 필요)
    try:
        timestamp = str(int(time.time() * 1000))
        headers = {
            "X-Timestamp": timestamp,
            "X-API-KEY": config.get_naver_api_key(),
            "X-Customer": str(config.get_naver_customer_id()),
            "X-Signature": _sign("GET", "/report-download", timestamp),
        }
        r = requests.get(download_url, headers=headers, timeout=60)
        if r.status_code >= 400:
            raise NaverAPIError(f"다운로드 실패 {r.status_code}")
    except requests.RequestException as e:
        raise NaverAPIError(f"다운로드 실패: {e}")

    # 4. TSV 파싱
    import io
    df = pd.read_csv(io.StringIO(r.text), sep="\t")

    # 컬럼 정규화 — Naver TSV의 실제 컬럼명에 따라 매핑 필요
    # AD_DETAIL 리포트는 보통: 일자, 캠페인ID, 광고그룹ID, 키워드ID, 키워드, 검색어, 노출수, 클릭수, 비용, 전환수, 전환매출
    column_map = {
        "키워드": "our_keyword",
        "검색어": "search_query",
        "노출수": "impressions",
        "클릭수": "clicks",
        "비용": "spend",
        "전환수": "purchases",
        "전환매출": "conv_value",
    }
    df = df.rename(columns=column_map)

    if "search_query" not in df.columns:
        # 컬럼명이 다르면 일단 그대로 반환
        return df

    # 진단 로직
    def _diagnose(row):
        clk = row.get("clicks", 0) or 0
        purchases = row.get("purchases", 0) or 0
        spend = row.get("spend", 0) or 0
        if clk == 0:
            return ("관찰", "🟡 노출만")
        cvr = (purchases / clk * 100) if clk else 0
        if purchases >= 1 and cvr >= 5:
            return ("신규 등록 권장", "🟢")
        if purchases == 0 and clk >= 5 and spend >= 5000:
            return ("노출 제외 권장", "🔴")
        if purchases >= 1:
            return ("관찰", "🟢")
        return ("관찰", "🟡")

    diags = df.apply(_diagnose, axis=1)
    df["status"] = [d[0] for d in diags]
    df["diag_color"] = [d[1] for d in diags]
    df["ctr"] = (df["clicks"] / df["impressions"] * 100).fillna(0)
    df["cvr"] = (df["purchases"] / df["clicks"] * 100).fillna(0)
    df["cpa"] = df.apply(
        lambda r: (r["spend"] / r["purchases"]) if r["purchases"] else None, axis=1
    )

    return df.sort_values(
        ["purchases", "clicks", "impressions"], ascending=[False, False, False]
    ).reset_index(drop=True)


def keyword_tool(hint_keywords, include_hints=True):
    """네이버 키워드 도구 API.

    입력: hint_keywords (str 또는 list, 1~5개)
    반환: DataFrame [keyword, monthly_pc, monthly_mo, avg_cpc, comp_idx, avg_rank, ...]
    """
    if isinstance(hint_keywords, str):
        kws = [k.strip() for k in hint_keywords.split(",") if k.strip()]
    else:
        kws = list(hint_keywords)
    kws = kws[:5]  # 최대 5개
    if not kws:
        return pd.DataFrame()

    try:
        data = _call("GET", "/keywordstool", params={
            "hintKeywords": ",".join(kws),
            "includeHintKeywords": "1" if include_hints else "0",
            "showDetail": "1",
        })
    except Exception:
        return pd.DataFrame()

    items = (data or {}).get("keywordList", [])
    if not items:
        return pd.DataFrame()

    def _num(v):
        """Naver는 '<10' 같은 마스킹 값을 반환할 수 있음."""
        if isinstance(v, (int, float)):
            return int(v)
        if isinstance(v, str):
            if v.startswith("<"):
                return 5  # < 10이면 대략 5로 추정
            try:
                return int(float(v))
            except ValueError:
                return 0
        return 0

    rows = []
    for k in items:
        pc = _num(k.get("monthlyPcQcCnt", 0))
        mo = _num(k.get("monthlyMobileQcCnt", 0))
        total = pc + mo
        # 평균 CPC는 PC·MO 클릭률·검색량으로 추정 (정확치는 입찰 시뮬 별도)
        pc_clk = _num(k.get("monthlyAvePcClkCnt", 0))
        mo_clk = _num(k.get("monthlyAveMobileClkCnt", 0))
        # 경쟁 정도
        comp = k.get("compIdx", "중간")
        comp_kr = {"높음": "🔴 높음", "중간": "🟡 중간", "낮음": "🟢 낮음"}.get(comp, comp)

        # 추천 점수 (검색량 ↑ + 경쟁도 ↓ + 의도 명확 = 우리에게 유리)
        comp_score = {"낮음": 3, "중간": 2, "높음": 1}.get(comp, 2)
        if total < 100:
            attractiveness = "검색량 부족"
        elif total > 50000 and comp == "높음":
            attractiveness = "🔴 빅키워드 (대기업과 경쟁)"
        elif total > 1000 and comp == "낮음":
            attractiveness = "🟢 우리에게 유리 (롱테일)"
        elif comp_score >= 2 and total > 500:
            attractiveness = "🟡 검토 가치"
        else:
            attractiveness = "🟡 관찰"

        rows.append({
            "keyword": k.get("relKeyword"),
            "monthly_pc": pc,
            "monthly_mo": mo,
            "monthly_total": total,
            "mobile_ratio": (mo / total * 100) if total else 0,
            "avg_pc_clicks": pc_clk,
            "avg_mo_clicks": mo_clk,
            "competition": comp_kr,
            "avg_rank": float(k.get("plAvgDepth") or 0),
            "attractiveness": attractiveness,
        })
    df = pd.DataFrame(rows)
    # 검색량 많은 순서로
    return df.sort_values("monthly_total", ascending=False).reset_index(drop=True)


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
