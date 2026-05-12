"""대시보드 데이터 제공자.

토큰 있으면 실데이터, 실패하면 Mock fallback.
모든 함수는 mock_data와 동일한 DataFrame 스키마를 반환.
"""

import streamlit as st

from . import config, mock_data


def _try_real(real_fn, mock_fn, label):
    """실데이터 시도 → 실패 시 Mock + 에러 표시 + 상태 기록."""
    from datetime import datetime as _dt
    if "data_status" not in st.session_state:
        st.session_state["data_status"] = {}
    try:
        result = real_fn()
        if result is None or (hasattr(result, "empty") and result.empty):
            st.session_state["data_status"][label] = {
                "source": "mock_empty",
                "msg": "API 응답이 비어있음",
                "ts": _dt.now().strftime("%H:%M:%S"),
            }
            return mock_fn()
        st.session_state["data_status"][label] = {
            "source": "real",
            "msg": f"{len(result) if hasattr(result, '__len__') else 1}개 항목",
            "ts": _dt.now().strftime("%H:%M:%S"),
        }
        return result
    except Exception as e:
        err_msg = str(e)[:150]
        st.session_state["data_status"][label] = {
            "source": "mock_error",
            "msg": err_msg,
            "ts": _dt.now().strftime("%H:%M:%S"),
        }
        return mock_fn()


# ───────── Meta ─────────


@st.cache_data(ttl=600, show_spinner=False)
def get_meta_kpi():
    if config.has_meta_credentials():
        from . import meta_client
        return _try_real(meta_client.fetch_kpi, mock_data.meta_kpi, "Meta KPI")
    return mock_data.meta_kpi()


@st.cache_data(ttl=600, show_spinner=False)
def get_meta_campaigns():
    if config.has_meta_credentials():
        from . import meta_client
        return _try_real(meta_client.fetch_campaigns, mock_data.meta_campaigns, "Meta 캠페인")
    return mock_data.meta_campaigns()


@st.cache_data(ttl=600, show_spinner=False)
def get_meta_adsets():
    if config.has_meta_credentials():
        from . import meta_client
        return _try_real(meta_client.fetch_adsets, mock_data.meta_adsets, "Meta 광고세트")
    return mock_data.meta_adsets()


@st.cache_data(ttl=600, show_spinner=False)
def get_meta_ads():
    if config.has_meta_credentials():
        from . import meta_client
        return _try_real(meta_client.fetch_ads, mock_data.meta_ads, "Meta 광고")
    return mock_data.meta_ads()


@st.cache_data(ttl=600, show_spinner=False)
def get_meta_timeseries():
    if config.has_meta_credentials():
        from . import meta_client
        return _try_real(meta_client.fetch_timeseries, mock_data.meta_timeseries, "Meta 시계열")
    return mock_data.meta_timeseries()


def get_meta_actions():
    return mock_data.meta_actions()  # 진단 엔진은 추후


# ───────── Naver ─────────


@st.cache_data(ttl=600, show_spinner=False)
def get_naver_kpi():
    if config.has_naver_credentials():
        from . import naver_client
        return _try_real(naver_client.fetch_kpi, mock_data.naver_kpi, "Naver KPI")
    return mock_data.naver_kpi()


@st.cache_data(ttl=600, show_spinner=False)
def get_naver_campaigns():
    if config.has_naver_credentials():
        from . import naver_client
        return _try_real(naver_client.fetch_campaigns, mock_data.naver_campaigns, "Naver 캠페인")
    return mock_data.naver_campaigns()


@st.cache_data(ttl=600, show_spinner=False)
def get_naver_adgroups():
    if config.has_naver_credentials():
        from . import naver_client
        return _try_real(naver_client.fetch_adgroups, mock_data.naver_adgroups, "Naver 광고그룹")
    return mock_data.naver_adgroups()


@st.cache_data(ttl=600, show_spinner=False)
def get_naver_keywords():
    if config.has_naver_credentials():
        from . import naver_client
        return _try_real(naver_client.fetch_keywords, mock_data.naver_keywords, "Naver 키워드")
    return mock_data.naver_keywords()


@st.cache_data(ttl=3600, show_spinner=False)
def get_search_query_report(days=7):
    """검색어 보고서 (우리 광고에 노출된 실제 검색어)."""
    if config.has_naver_credentials():
        from . import naver_client
        try:
            result = naver_client.fetch_search_query_report(days=days)
            if result is None or result.empty:
                return mock_data.search_query_report()
            return result
        except Exception as e:
            st.sidebar.error(f"❌ 검색어 보고서: {str(e)[:80]}")
            return mock_data.search_query_report()
    return mock_data.search_query_report()


@st.cache_data(ttl=3600, show_spinner=False)
def get_keyword_research(hint_keywords_str):
    """키워드 도구. hint_keywords_str: 쉼표 구분 문자열."""
    if config.has_naver_credentials():
        from . import naver_client
        try:
            result = naver_client.keyword_tool(hint_keywords_str)
            if result is None or result.empty:
                return mock_data.keyword_research(hint_keywords_str)
            return result
        except Exception as e:
            st.sidebar.error(f"❌ Naver 키워드 도구: {str(e)[:80]}")
            return mock_data.keyword_research(hint_keywords_str)
    return mock_data.keyword_research(hint_keywords_str)


@st.cache_data(ttl=600, show_spinner=False)
def get_naver_timeseries():
    if config.has_naver_credentials():
        from . import naver_client
        return _try_real(naver_client.fetch_timeseries, mock_data.naver_timeseries, "Naver 시계열")
    return mock_data.naver_timeseries()


def get_naver_keyword_opportunity():
    return mock_data.naver_keyword_opportunity()


def get_naver_search_trend():
    return mock_data.naver_search_trend()


def get_serp_competitors():
    return mock_data.serp_competitors()


def get_naver_actions():
    return mock_data.naver_actions()


def get_gfa_kpi():
    return mock_data.gfa_kpi()


def get_gfa_campaigns():
    return mock_data.gfa_campaigns()


def get_gfa_actions():
    return mock_data.gfa_actions()


def get_naver_brand_search():
    return mock_data.naver_brand_search()


def get_naver_shopping():
    return mock_data.naver_shopping()


# ───────── 캐시 무효화 ─────────


def clear_cache():
    st.cache_data.clear()


# ───────── 액션 실행 (Phase N2) ─────────


def execute_add_keyword(adgroup_id, keyword, bid_amt=None):
    """키워드 추가. 실데이터면 API 호출, Mock이면 시뮬레이션."""
    if config.has_naver_credentials():
        from . import naver_client
        return naver_client.add_keyword(adgroup_id, keyword, bid_amt)
    # Mock 모드 — 성공 시뮬레이션
    return {"success": True, "keyword_id": "mock_kw_id", "mock": True}


def execute_block_keyword(adgroup_id, keyword):
    """노출 제외 키워드 추가."""
    if config.has_naver_credentials():
        from . import naver_client
        return naver_client.add_negative_keyword(adgroup_id, keyword)
    return {"success": True, "mock": True}


def execute_update_keyword_bid(keyword_id, new_bid):
    """키워드 입찰가 변경."""
    if config.has_naver_credentials():
        from . import naver_client
        return naver_client.update_keyword_bid(keyword_id, new_bid)
    return {"success": True, "mock": True, "new_bid": new_bid}


def execute_update_adgroup_bid(adgroup_id, new_bid):
    """광고그룹 기본 입찰가 변경."""
    if config.has_naver_credentials():
        from . import naver_client
        return naver_client.update_adgroup_bid(adgroup_id, new_bid)
    return {"success": True, "mock": True, "new_bid": new_bid}


@st.cache_data(ttl=3600, show_spinner=False)
def get_naver_time_heatmap():
    """요일×시간 히트맵 데이터."""
    if config.has_naver_credentials():
        from . import naver_client
        try:
            result = naver_client.fetch_time_heatmap()
            if result is None:
                return mock_data.naver_time_heatmap()
            return result
        except Exception as e:
            st.sidebar.error(f"❌ 시간대 분석: {str(e)[:80]}")
            return mock_data.naver_time_heatmap()
    return mock_data.naver_time_heatmap()


def get_bid_estimate(keyword, device="PC"):
    """키워드 순위별 예상 입찰가."""
    if config.has_naver_credentials():
        from . import naver_client
        return naver_client.get_bid_estimate(keyword, device)
    # Mock fallback — 가상 예상치
    return {
        "estimate": [
            {"keyword": keyword, "device": device, "position": 1, "bid": 2500},
            {"keyword": keyword, "device": device, "position": 2, "bid": 1800},
            {"keyword": keyword, "device": device, "position": 3, "bid": 1300},
            {"keyword": keyword, "device": device, "position": 5, "bid": 900},
        ],
        "mock": True,
    }


def log_action(action_type, payload, result):
    """감사용 로그를 session_state에 저장."""
    from datetime import datetime as _dt
    if "action_log" not in st.session_state:
        st.session_state["action_log"] = []
    st.session_state["action_log"].insert(0, {
        "ts": _dt.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": action_type,
        "payload": payload,
        "result": result,
    })
    # 최근 50개만 유지
    st.session_state["action_log"] = st.session_state["action_log"][:50]
