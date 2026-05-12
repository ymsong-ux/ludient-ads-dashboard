"""대시보드 데이터 제공자 (실데이터 전용).

토큰 있으면 실데이터 fetch. 없거나 실패하면 빈 DataFrame/None 반환.
UI에서 빈 상태 처리 (Mock fallback 없음).
"""

import pandas as pd
import streamlit as st

from . import config


# ───────── 헬퍼 ─────────


def _empty_df():
    return pd.DataFrame()


def _try_real(real_fn, label):
    """실데이터 시도. 실패 시 빈 DataFrame + 상태 기록."""
    from datetime import datetime as _dt
    if "data_status" not in st.session_state:
        st.session_state["data_status"] = {}
    try:
        result = real_fn()
        if result is None or (hasattr(result, "empty") and result.empty):
            st.session_state["data_status"][label] = {
                "source": "empty",
                "msg": "API 응답 비어있음",
                "ts": _dt.now().strftime("%H:%M:%S"),
            }
            return result if result is not None else _empty_df()
        st.session_state["data_status"][label] = {
            "source": "real",
            "msg": f"{len(result) if hasattr(result, '__len__') else 1}개",
            "ts": _dt.now().strftime("%H:%M:%S"),
        }
        return result
    except Exception as e:
        st.session_state["data_status"][label] = {
            "source": "error",
            "msg": str(e)[:150],
            "ts": _dt.now().strftime("%H:%M:%S"),
        }
        return _empty_df()


# ───────── Meta ─────────


@st.cache_data(ttl=600, show_spinner=False)
def get_meta_kpi():
    if not config.has_meta_credentials():
        return None
    from . import meta_client
    try:
        return meta_client.fetch_kpi()
    except Exception as e:
        st.sidebar.error(f"❌ Meta KPI: {str(e)[:100]}")
        return None


@st.cache_data(ttl=600, show_spinner=False)
def get_meta_campaigns():
    if not config.has_meta_credentials():
        return _empty_df()
    from . import meta_client
    return _try_real(meta_client.fetch_campaigns, "Meta 캠페인")


@st.cache_data(ttl=600, show_spinner=False)
def get_meta_adsets():
    if not config.has_meta_credentials():
        return _empty_df()
    from . import meta_client
    return _try_real(meta_client.fetch_adsets, "Meta 광고세트")


@st.cache_data(ttl=600, show_spinner=False)
def get_meta_ads():
    if not config.has_meta_credentials():
        return _empty_df()
    from . import meta_client
    return _try_real(meta_client.fetch_ads, "Meta 광고")


@st.cache_data(ttl=600, show_spinner=False)
def get_meta_timeseries():
    if not config.has_meta_credentials():
        return _empty_df()
    from . import meta_client
    return _try_real(meta_client.fetch_timeseries, "Meta 시계열")


def get_meta_actions():
    """추후 진단 엔진과 연결. 현재는 빈 리스트."""
    return []


# ───────── Naver ─────────


@st.cache_data(ttl=600, show_spinner=False)
def get_naver_kpi():
    if not config.has_naver_credentials():
        return None
    from . import naver_client
    try:
        return naver_client.fetch_kpi()
    except Exception as e:
        st.sidebar.error(f"❌ Naver KPI: {str(e)[:100]}")
        return None


@st.cache_data(ttl=600, show_spinner=False)
def get_naver_campaigns():
    if not config.has_naver_credentials():
        return _empty_df()
    from . import naver_client
    return _try_real(naver_client.fetch_campaigns, "Naver 캠페인")


@st.cache_data(ttl=600, show_spinner=False)
def get_naver_adgroups():
    if not config.has_naver_credentials():
        return _empty_df()
    from . import naver_client
    return _try_real(naver_client.fetch_adgroups, "Naver 광고그룹")


@st.cache_data(ttl=600, show_spinner=False)
def get_naver_keywords():
    if not config.has_naver_credentials():
        return _empty_df()
    from . import naver_client
    return _try_real(naver_client.fetch_keywords, "Naver 키워드")


@st.cache_data(ttl=600, show_spinner=False)
def get_naver_timeseries():
    if not config.has_naver_credentials():
        return _empty_df()
    from . import naver_client
    return _try_real(naver_client.fetch_timeseries, "Naver 시계열")


@st.cache_data(ttl=3600, show_spinner=False)
def get_naver_time_heatmap():
    """요일×시간 히트맵."""
    if not config.has_naver_credentials():
        return None
    from . import naver_client
    try:
        return naver_client.fetch_time_heatmap()
    except Exception as e:
        st.sidebar.error(f"❌ 시간대 분석: {str(e)[:100]}")
        return None


@st.cache_data(ttl=3600, show_spinner=False)
def get_search_query_report(days=7):
    """검색어 보고서."""
    if not config.has_naver_credentials():
        return _empty_df()
    from . import naver_client
    try:
        return naver_client.fetch_search_query_report(days=days)
    except Exception as e:
        st.sidebar.error(f"❌ 검색어 보고서: {str(e)[:100]}")
        return _empty_df()


@st.cache_data(ttl=3600, show_spinner=False)
def get_keyword_research(hint_keywords_str):
    """키워드 도구."""
    if not config.has_naver_credentials():
        return _empty_df()
    from . import naver_client
    try:
        return naver_client.keyword_tool(hint_keywords_str)
    except Exception as e:
        st.sidebar.error(f"❌ 키워드 도구: {str(e)[:100]}")
        return _empty_df()


def get_naver_actions():
    """추후 진단 엔진과 연결. 현재는 빈 리스트."""
    return []


# ───────── 미구현 API (Mock 제거) ─────────
# GFA, 브랜드검색, 쇼핑검색, 검색 트렌드, SERP 경쟁사,
# 키워드 기회 — 각각 별도 API 또는 크롤링 필요.
# 현재 빈 데이터 반환 → UI에서 "🔌 미구현" 메시지 표시.


def get_gfa_kpi():
    return None  # GFA API 미발급


def get_gfa_campaigns():
    return _empty_df()  # GFA API 미발급


def get_gfa_actions():
    return []


def get_naver_brand_search():
    """브랜드검색 — Naver Search Ads API에 별도 엔드포인트 필요."""
    return None


def get_naver_shopping():
    """쇼핑검색 — 별도 API."""
    return _empty_df()


def get_naver_keyword_opportunity():
    """신규 키워드 기회 — 키워드 도구 + 자체 알고리즘."""
    return _empty_df()


def get_naver_search_trend():
    """네이버 데이터랩 트렌드 — 별도 API."""
    return _empty_df()


def get_serp_competitors():
    """SERP 크롤링 — BrightData/Firecrawl 통합 필요."""
    return _empty_df()


def get_bid_estimate(keyword, device="PC"):
    """키워드 순위별 예상 입찰가."""
    if not config.has_naver_credentials():
        return None
    from . import naver_client
    try:
        return naver_client.get_bid_estimate(keyword, device)
    except Exception as e:
        return None


# ───────── 액션 실행 ─────────


def execute_add_keyword(adgroup_id, keyword, bid_amt=None):
    if not config.has_naver_credentials():
        return {"success": False, "error": "Naver API 연결 안 됨"}
    from . import naver_client
    return naver_client.add_keyword(adgroup_id, keyword, bid_amt)


def execute_block_keyword(adgroup_id, keyword):
    if not config.has_naver_credentials():
        return {"success": False, "error": "Naver API 연결 안 됨"}
    from . import naver_client
    return naver_client.add_negative_keyword(adgroup_id, keyword)


def execute_update_keyword_bid(keyword_id, new_bid):
    if not config.has_naver_credentials():
        return {"success": False, "error": "Naver API 연결 안 됨"}
    from . import naver_client
    return naver_client.update_keyword_bid(keyword_id, new_bid)


def execute_update_adgroup_bid(adgroup_id, new_bid):
    if not config.has_naver_credentials():
        return {"success": False, "error": "Naver API 연결 안 됨"}
    from . import naver_client
    return naver_client.update_adgroup_bid(adgroup_id, new_bid)


def log_action(action_type, payload, result):
    """감사용 로그."""
    from datetime import datetime as _dt
    if "action_log" not in st.session_state:
        st.session_state["action_log"] = []
    st.session_state["action_log"].insert(0, {
        "ts": _dt.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": action_type,
        "payload": payload,
        "result": result,
    })
    st.session_state["action_log"] = st.session_state["action_log"][:50]


def clear_cache():
    st.cache_data.clear()
