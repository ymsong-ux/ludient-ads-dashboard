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


# ───────── Naver (Mock만 — Phase 2) ─────────


def get_naver_kpi():
    return mock_data.naver_kpi()


def get_naver_campaigns():
    return mock_data.naver_campaigns()


def get_naver_adgroups():
    return mock_data.naver_adgroups()


def get_naver_keywords():
    return mock_data.naver_keywords()


def get_naver_timeseries():
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
