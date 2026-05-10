"""토큰 + 설정 해석.

우선순위:
1. Streamlit session_state (사용자가 사이드바에서 입력)
2. Streamlit secrets (st.secrets — Cloud 배포 시)
3. 환경변수 (로컬 개발용)
4. ~/.claude/.env 파일 (로컬 백업)
"""

import os
from pathlib import Path

try:
    import streamlit as st
    HAS_ST = True
except ImportError:
    HAS_ST = False


def _load_env_file():
    """~/.claude/.env 파일이 있으면 환경변수로 로드."""
    p = Path.home() / ".claude" / ".env"
    if not p.exists():
        return
    for line in p.read_text().splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_load_env_file()


def _from_session(key):
    if HAS_ST:
        try:
            return st.session_state.get(key)
        except Exception:
            pass
    return None


def _from_secrets(section, key):
    if HAS_ST:
        try:
            return st.secrets[section][key]
        except Exception:
            pass
    return None


# ───── Meta ─────
def get_meta_token():
    return (
        _from_session("META_ACCESS_TOKEN")
        or _from_secrets("meta", "access_token")
        or os.environ.get("META_ACCESS_TOKEN")
    )


def get_meta_account_id():
    """광고 계정 ID. 'act_' 접두사 자동 처리."""
    raw = (
        _from_session("META_AD_ACCOUNT_ID")
        or _from_secrets("meta", "account_id")
        or os.environ.get("META_AD_ACCOUNT_ID")
        or "1964326457797"  # 기본값: Ludient (재근님 인수인계 확인 필요)
    )
    raw = str(raw).strip()
    return raw if raw.startswith("act_") else f"act_{raw}"


def has_meta_credentials():
    return bool(get_meta_token())


# ───── Naver Search Ads ─────
def get_naver_api_key():
    return (
        _from_session("NAVER_API_KEY")
        or _from_secrets("naver", "api_key")
        or os.environ.get("NAVER_API_KEY")
    )


def get_naver_secret_key():
    return (
        _from_session("NAVER_SECRET_KEY")
        or _from_secrets("naver", "secret_key")
        or os.environ.get("NAVER_SECRET_KEY")
    )


def get_naver_customer_id():
    return (
        _from_session("NAVER_CUSTOMER_ID")
        or _from_secrets("naver", "customer_id")
        or os.environ.get("NAVER_CUSTOMER_ID")
    )


def has_naver_credentials():
    return bool(
        get_naver_api_key()
        and get_naver_secret_key()
        and get_naver_customer_id()
    )


# ───── 통합 ─────
def data_source_status():
    """대시보드 표시용."""
    return {
        "meta": "🟢 실데이터" if has_meta_credentials() else "🟡 Mock 데이터",
        "naver": "🟢 실데이터" if has_naver_credentials() else "🟡 Mock 데이터",
    }
