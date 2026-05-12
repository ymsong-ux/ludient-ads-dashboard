"""대시보드 데이터 제공자.

토큰 있으면 실데이터, 실패하면 Mock fallback.
모든 함수는 mock_data와 동일한 DataFrame 스키마를 반환.
"""

import streamlit as st

from . import config, mock_data


def _try_real(real_fn, mock_fn, label):
    """실데이터 시도 → 실패 시 Mock + 에러 표시."""
    try:
        result = real_fn()
        if result is None or (hasattr(result, "empty") and result.empty):
            st.sidebar.warning(f"⚠️ {label}: 응답이 비어있음, Mock 사용")
            return mock_fn()
        return result
    except Exception as e:
        st.sidebar.error(f"❌ {label} API 에러: {str(e)[:100]}")
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
