"""Lululab 광고 운영 대시보드.

미팅 시연용 골격 — Mock 데이터 기반.
실제 API 연결은 modules/api_clients.py에 추가 예정.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime

from modules import mock_data as mock
from modules import data, config


# ───────────────── 페이지 설정 ─────────────────
st.set_page_config(
    page_title="Lululab 광고 운영 대시보드",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 커스텀 CSS — 카드 디자인
st.markdown("""
<style>
.metric-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 16px;
}
.action-card {
    background: #f8fafc;
    border-left: 4px solid #4338ca;
    border-radius: 4px;
    padding: 12px;
    margin: 8px 0;
}
.status-good { color: #059669; font-weight: 700; }
.status-warn { color: #d97706; font-weight: 700; }
.status-bad { color: #dc2626; font-weight: 700; }
.section-title {
    font-size: 18px;
    font-weight: 700;
    color: #1e293b;
    margin: 16px 0 8px;
}
</style>
""", unsafe_allow_html=True)


# ───────────────── 사이드바 ─────────────────
with st.sidebar:
    st.title("📊 Lululab")
    st.caption("광고 운영 대시보드")
    st.divider()

    page = st.radio(
        "페이지",
        ["Meta", "Naver", "🔑 키워드 도구", "통합", "리포트"],
        label_visibility="collapsed"
    )
    st.divider()

    period = st.selectbox(
        "기간",
        ["최근 7일", "최근 14일", "최근 30일", "사용자 정의"],
        index=2
    )

    if st.button("🔄 데이터 새로고침", width="stretch"):
        data.clear_cache()
        st.success("캐시 비움")
        st.rerun()

    st.divider()

    # 데이터 소스 상태
    src = config.data_source_status()
    st.caption("**데이터 소스**")
    st.caption(f"Meta · {src['meta']}")
    st.caption(f"Naver · {src['naver']}")

    # 토큰 입력
    with st.expander("🔐 API 토큰 연결"):
        st.caption("입력 시 즉시 실데이터로 전환")
        meta_tok = st.text_input(
            "Meta Access Token",
            value=st.session_state.get("META_ACCESS_TOKEN", ""),
            type="password",
            help="developers.facebook.com/tools/explorer (ads_read 권한)"
        )
        meta_aid = st.text_input(
            "Meta 광고 계정 ID",
            value=st.session_state.get("META_AD_ACCOUNT_ID", "1964326457797"),
        )
        if st.button("Meta 연결", width="stretch", key="connect_meta"):
            st.session_state["META_ACCESS_TOKEN"] = meta_tok.strip()
            st.session_state["META_AD_ACCOUNT_ID"] = meta_aid.strip()
            data.clear_cache()
            st.success("연결 시도")
            st.rerun()

        st.divider()
        n_api = st.text_input("Naver API Key",
                              value=st.session_state.get("NAVER_API_KEY", ""), type="password")
        n_sec = st.text_input("Naver Secret Key",
                              value=st.session_state.get("NAVER_SECRET_KEY", ""), type="password")
        n_cid = st.text_input("Naver Customer ID",
                              value=st.session_state.get("NAVER_CUSTOMER_ID", ""))
        if st.button("Naver 연결", width="stretch", key="connect_naver"):
            st.session_state["NAVER_API_KEY"] = n_api.strip()
            st.session_state["NAVER_SECRET_KEY"] = n_sec.strip()
            st.session_state["NAVER_CUSTOMER_ID"] = n_cid.strip()
            data.clear_cache()
            st.success("연결 시도")
            st.rerun()

    st.divider()
    st.caption("마지막 갱신")
    st.caption(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    st.caption("캐시 TTL: 10분")


# ───────────────── 공통 헬퍼 ─────────────────
def format_won(n):
    if n is None:
        return "—"
    if n >= 1_000_000:
        return f"₩{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"₩{n/1_000:.0f}K"
    return f"₩{n:,}"


def status_pill(text, color):
    colors = {"🟢": "#059669", "🟡": "#d97706", "🔴": "#dc2626"}
    return f'<span style="background:{colors.get(color, "#64748b")};color:white;padding:2px 8px;border-radius:10px;font-size:12px;font-weight:600">{text}</span>'


def render_action_card(action, key_prefix):
    with st.container(border=True):
        st.markdown(f"**{action['icon']} {action['title']}**")
        with st.expander("근거 보기"):
            st.markdown(f"**근거**\n\n{action['reason']}")
            st.markdown(f"**예상 효과**\n\n{action['impact']}")
        c1, c2 = st.columns(2)
        if c1.button("✅ 실행", key=f"{key_prefix}_exec_{action['id']}", width="stretch"):
            st.success(f"실행됨: {action['title']}")
        if c2.button("✕ 무시", key=f"{key_prefix}_skip_{action['id']}", width="stretch"):
            st.info("무시됨")


# ═════════════════ META 페이지 ═════════════════
def render_meta_page():
    st.title("Meta 광고")
    st.caption("Ludient 계정 · 페이스북·인스타그램 광고 · 4월 데이터 · % = 직전 30일 대비 증감")

    kpi = data.get_meta_kpi()

    # 운영 상태 알림
    if kpi.get("운영_상태"):
        st.warning(f"**운영 상태**: {kpi['운영_상태']}")

    # KPI 카드 5개
    cols = st.columns(5)
    cols[0].metric("광고비 (30일)", format_won(kpi["광고비_30일"]), f"{kpi['광고비_증감']:+.1f}%")
    cols[1].metric("매출 (30일)", format_won(kpi["매출_30일"]), f"{kpi['매출_증감']:+.1f}%")
    cols[2].metric("ROAS", f"{kpi['roas']}%", f"{kpi['roas_증감']:+}%p")
    cols[3].metric("CPA", format_won(kpi["cpa"]), f"{kpi['cpa_증감']:+.1f}%", delta_color="inverse")
    cols[4].metric("신규 고객", f"{kpi['신규고객']}명", f"{kpi['신규고객_증감']:+}")

    # 회사 운영 기준 알림
    with st.expander("📐 회사 ON/OFF 기준 (재근님 인수인계 기준)"):
        c1, c2 = st.columns(2)
        c1.markdown("**OFF 검토 조건**")
        c1.markdown("- CPM 과도 상승\n- CTR < 1%\n- 1~2주 구매전환 0건\n- ROAS 목표 미달\n- 동일 소재 1개월 이상 운영")
        c2.markdown("**증액·유지 조건**")
        c2.markdown("- CPA 안정화 (꾸준한 전환)\n- ROAS 목표 이상\n- CTR > 3%")

    st.divider()

    # 메인 + 액션 사이드바
    main_col, action_col = st.columns([2.5, 1])

    with main_col:
        campaigns = data.get_meta_campaigns()
        adsets = data.get_meta_adsets()
        ads = data.get_meta_ads()

        # 시계열 차트 (탭 위, 항상 보임)
        st.subheader("📈 시계열 트렌드 (30일)")
        ts = data.get_meta_timeseries()
        ct1, ct2 = st.tabs(["광고비·매출", "ROAS·CTR"])
        with ct1:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=ts["date"], y=ts["광고비"], name="광고비", marker_color="#94a3b8"))
            fig.add_trace(go.Bar(x=ts["date"], y=ts["매출"], name="매출", marker_color="#4338ca"))
            fig.update_layout(height=260, margin=dict(t=20, b=20, l=20, r=20), barmode="group")
            st.plotly_chart(fig, width="stretch")
        with ct2:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=ts["date"], y=ts["ROAS"], name="ROAS (%)", line=dict(color="#059669", width=2)))
            fig.add_trace(go.Scatter(x=ts["date"], y=ts["CTR"]*100, name="CTR (%×100)", line=dict(color="#dc2626", width=2), yaxis="y2"))
            fig.add_hline(y=250, line_dash="dash", line_color="orange", annotation_text="손익분기 250%")
            fig.update_layout(height=260, margin=dict(t=20, b=20, l=20, r=20),
                              yaxis=dict(title="ROAS"),
                              yaxis2=dict(title="CTR", overlaying="y", side="right"))
            st.plotly_chart(fig, width="stretch")

        st.divider()

        st.subheader("🔬 단계별 진단")
        tab_camp, tab_set, tab_ad = st.tabs([
            f"📁 캠페인 ({len(campaigns)})",
            f"🎯 광고세트 ({len(adsets)})",
            f"🎨 광고 ({len(ads)})"
        ])

        # ────────── 캠페인 탭 ──────────
        with tab_camp:
            st.caption("**캠페인 = 무엇을·왜?** 목표·예산. 캠페인 OFF면 하위 다 OFF")

            df_camp = campaigns.copy()
            df_camp["진단"] = df_camp["diag_color"]
            df_camp["ON/OFF"] = df_camp["active"]
            df_camp = df_camp[[
                "진단", "ON/OFF", "name", "objective", "spend",
                "purchases", "cpa", "roas", "ctr", "cvr", "frequency", "learning", "status"
            ]]

            st.data_editor(
                df_camp,
                column_config={
                    "진단": st.column_config.TextColumn("진단", width="small"),
                    "ON/OFF": st.column_config.CheckboxColumn("ON/OFF"),
                    "name": st.column_config.TextColumn("캠페인", width="large"),
                    "objective": st.column_config.TextColumn("목표"),
                    "spend": st.column_config.NumberColumn("지출", format="₩%d"),
                    "purchases": st.column_config.NumberColumn("구매"),
                    "cpa": st.column_config.NumberColumn("CPA", format="₩%d"),
                    "roas": st.column_config.NumberColumn("ROAS", format="%d%%"),
                    "ctr": st.column_config.NumberColumn("CTR", format="%.2f%%"),
                    "cvr": st.column_config.NumberColumn("CVR", format="%.2f%%"),
                    "frequency": st.column_config.NumberColumn("빈도", format="%.1f"),
                    "learning": st.column_config.TextColumn("학습"),
                    "status": st.column_config.TextColumn("권장"),
                },
                hide_index=True, width="stretch", height=280,
                disabled=["진단", "name", "objective", "spend", "purchases", "cpa",
                          "roas", "ctr", "cvr", "frequency", "learning", "status"],
                key="meta_camp_table"
            )

            with st.expander("💡 캠페인 단계 진단 가이드"):
                st.markdown("""
- **캠페인 ROAS 손익분기 미만** → 그 캠페인의 광고세트 탭으로 이동해서 어느 세트가 문제인지 봄
- **학습 미완료**: 캠페인 전체 전환 50건 미달이면 알고리즘 학습 못 함. 예산 증액 또는 광고세트 통합
- **빈도(Frequency) 5 이상** → 광고 피로 (한 사람이 5번 이상 봄). 새 소재 추가 또는 타겟 확장
- **캠페인 목표(전환·트래픽·인지)별 평가 지표가 다름**: 인지 캠페인은 ROAS로 평가하지 말 것
                """)

        # ────────── 광고세트 탭 ──────────
        with tab_set:
            st.caption("**광고세트 = 누구·어디·얼마?** 타겟·예산·노출 위치. 효율 안 나오면 타겟 문제일 가능성")

            camp_options = ["전체"] + campaigns["name"].tolist()
            sel_camp = st.selectbox("캠페인 필터", camp_options, key="filt_camp")

            df_set = adsets.merge(
                campaigns[["id", "name"]].rename(columns={"name": "campaign_name"}),
                left_on="campaign_id", right_on="id", how="left"
            )
            if sel_camp != "전체":
                df_set = df_set[df_set["campaign_name"] == sel_camp]

            df_set["진단"] = df_set["diag_color"]
            df_set["ON/OFF"] = df_set["active"]
            df_set_view = df_set[[
                "진단", "ON/OFF", "campaign_name", "name", "target", "daily_budget",
                "spend", "purchases", "cpa", "roas", "ctr", "cvr",
                "frequency", "learning", "status"
            ]]

            st.data_editor(
                df_set_view,
                column_config={
                    "진단": st.column_config.TextColumn("진단", width="small"),
                    "ON/OFF": st.column_config.CheckboxColumn("ON/OFF"),
                    "campaign_name": st.column_config.TextColumn("소속 캠페인", width="medium"),
                    "name": st.column_config.TextColumn("광고세트", width="medium"),
                    "target": st.column_config.TextColumn("타겟"),
                    "daily_budget": st.column_config.NumberColumn("일예산", format="₩%d"),
                    "spend": st.column_config.NumberColumn("지출", format="₩%d"),
                    "purchases": st.column_config.NumberColumn("구매"),
                    "cpa": st.column_config.NumberColumn("CPA", format="₩%d"),
                    "roas": st.column_config.NumberColumn("ROAS", format="%d%%"),
                    "ctr": st.column_config.NumberColumn("CTR", format="%.2f%%"),
                    "cvr": st.column_config.NumberColumn("CVR", format="%.2f%%"),
                    "frequency": st.column_config.NumberColumn("빈도", format="%.1f"),
                    "learning": st.column_config.TextColumn("학습"),
                    "status": st.column_config.TextColumn("권장"),
                },
                hide_index=True, width="stretch", height=420,
                disabled=["진단", "campaign_name", "name", "target", "daily_budget",
                          "spend", "purchases", "cpa", "roas", "ctr", "cvr",
                          "frequency", "learning", "status"],
                key="meta_set_table"
            )

            with st.expander("💡 광고세트 단계 진단 가이드"):
                st.markdown("""
- **같은 캠페인 안에서 광고세트 ROAS 차이 큼** → 타겟 문제. 효율 좋은 타겟에 예산 몰기
- **모든 광고세트 ROAS 낮음** → 캠페인 가설 자체 재검토 (제품·메시지·타겟군)
- **학습 미완료**: 광고세트당 7일 50건 미달이면 학습 못 끝남. 예산 증액 또는 광고세트 통합
- **빈도(Frequency) 5 이상** → 광고 피로. 새 소재 추가
- **오디언스 오버랩 의심**: 같은 캠페인 내 광고세트 두 개 ROAS 비슷한데 CPM 점점 ↑ → 오버랩 진단 도구로 확인
                """)

        # ────────── 광고 탭 ──────────
        with tab_ad:
            st.caption("**광고 = 뭘 보여줄까?** 소재·카피·CTA. 같은 광고세트에서 소재별 CTR 차이 = 소재 문제")

            f1, f2 = st.columns(2)
            sel_camp2 = f1.selectbox("캠페인 필터", ["전체"] + campaigns["name"].tolist(), key="filt_camp2")
            adset_options = ["전체"] + adsets["name"].unique().tolist()
            sel_set = f2.selectbox("광고세트 필터", adset_options, key="filt_set")

            df_ad = ads.copy()
            adset_map = adsets.copy()
            adset_map["adset_idx"] = adset_map["campaign_id"] + "|" + adset_map["name"].str.split("_").str[0]
            df_ad = df_ad.merge(
                adset_map[["adset_idx", "campaign_id", "name"]].rename(columns={"name": "adset_name"}),
                on="adset_idx", how="left"
            )
            df_ad = df_ad.merge(
                campaigns[["id", "name"]].rename(columns={"name": "campaign_name"}),
                left_on="campaign_id", right_on="id", how="left"
            )
            if sel_camp2 != "전체":
                df_ad = df_ad[df_ad["campaign_name"] == sel_camp2]
            if sel_set != "전체":
                df_ad = df_ad[df_ad["adset_name"] == sel_set]

            df_ad["진단"] = df_ad["diag_color"]
            df_ad["ON/OFF"] = df_ad["active"]
            df_ad_view = df_ad[[
                "진단", "ON/OFF", "campaign_name", "adset_name", "name", "format",
                "spend", "impressions", "clicks", "ctr", "purchases", "cvr", "status"
            ]]

            st.data_editor(
                df_ad_view,
                column_config={
                    "진단": st.column_config.TextColumn("진단", width="small"),
                    "ON/OFF": st.column_config.CheckboxColumn("ON/OFF"),
                    "campaign_name": st.column_config.TextColumn("캠페인", width="medium"),
                    "adset_name": st.column_config.TextColumn("광고세트", width="medium"),
                    "name": st.column_config.TextColumn("광고 소재", width="large"),
                    "format": st.column_config.TextColumn("형식"),
                    "spend": st.column_config.NumberColumn("지출", format="₩%d"),
                    "impressions": st.column_config.NumberColumn("노출"),
                    "clicks": st.column_config.NumberColumn("클릭"),
                    "ctr": st.column_config.NumberColumn("CTR", format="%.2f%%"),
                    "purchases": st.column_config.NumberColumn("구매"),
                    "cvr": st.column_config.NumberColumn("CVR", format="%.2f%%"),
                    "status": st.column_config.TextColumn("권장"),
                },
                hide_index=True, width="stretch", height=520,
                disabled=["진단", "campaign_name", "adset_name", "name", "format",
                          "spend", "impressions", "clicks", "ctr", "purchases", "cvr", "status"],
                key="meta_ad_table"
            )

            with st.expander("💡 광고 소재 단계 진단 가이드"):
                st.markdown("""
- **같은 광고세트에서 소재별 CTR 큰 차이** → 소재 문제. 약한 소재 OFF + 새 변형(A')
- **모든 소재 CTR 낮음** → 타겟이 메시지에 안 맞음 (광고세트 단계로 돌아가기)
- **CTR 좋은데 CVR 낮음** → 낚시 카피 의심. 후킹과 랜딩 정합성 점검
- **A vs A' vs A''**: 한 번에 한 변수만 바꾸기 (썸네일·카피·CTA 중 하나)
- **소재 형식 비교**: 영상 vs 이미지 vs 카루셀 — 어느 형식이 우리 페르소나에 맞나
                """)

    with action_col:
        st.markdown("### 🔔 오늘 추천 액션")
        st.caption("본인이 검토 후 실행")

        for action in data.get_meta_actions():
            render_action_card(action, "meta")


# ═════════════════ NAVER 페이지 ═════════════════
def render_naver_page():
    st.title("Naver 광고")
    st.caption("루디언트 계정 · 검색광고 + GFA + 브랜드검색 + 쇼핑검색")

    # 회사 ON/OFF 기준 알림
    with st.expander("📐 회사 ON/OFF 기준 (재근님 인수인계 기준)"):
        c1, c2 = st.columns(2)
        c1.markdown("**OFF 검토**")
        c1.markdown("- CTR < 1%\n- 1~2주 구매전환 0건\n- CPC 과도 상승\n- ROAS 목표 미달")
        c2.markdown("**증액·유지**")
        c2.markdown("- CPA 안정화\n- ROAS > 200~300%\n- CTR > 3%")

    # 4개 광고 유형 서브탭
    n_search, n_gfa, n_brand, n_shop = st.tabs([
        "🔑 검색광고 (파워링크)",
        "🖼️ GFA (디스플레이)",
        "🏷️ 브랜드검색",
        "🛒 쇼핑검색"
    ])

    # ─────────────── GFA 탭 ───────────────
    with n_gfa:
        gfa = data.get_gfa_kpi()
        if gfa.get("운영_상태"):
            st.warning(f"**운영 상태**: {gfa['운영_상태']}")
        st.caption(f"성과형 디스플레이 광고 · 목표 ROAS {gfa['목표_roas']}%")

        gc = st.columns(5)
        gc[0].metric("광고비 (30일)", format_won(gfa["광고비_30일"]), f"{gfa['광고비_증감']:+.1f}%")
        gc[1].metric("매출 (30일)", format_won(gfa["매출_30일"]), f"{gfa['매출_증감']:+.1f}%")
        gc[2].metric("ROAS", f"{gfa['roas']}%", f"{gfa['roas_증감']:+}%p")
        gc[3].metric("CPA", format_won(gfa["cpa"]), f"{gfa['cpa_증감']:+.1f}%", delta_color="inverse")
        gc[4].metric("전환", f"{gfa['전환']}건", f"{gfa['전환_증감']:+}")

        st.subheader("GFA 캠페인 4종")
        gfa_df = data.get_gfa_campaigns()
        gfa_df["진단"] = gfa_df["diag_color"]
        gfa_df["ON/OFF"] = gfa_df["active"]
        gfa_view = gfa_df[["진단", "ON/OFF", "name", "type", "daily_budget",
                           "spend", "conversions", "cpa", "roas", "ctr", "cvr", "status"]]
        st.data_editor(
            gfa_view,
            column_config={
                "진단": st.column_config.TextColumn("진단", width="small"),
                "ON/OFF": st.column_config.CheckboxColumn("ON/OFF"),
                "name": st.column_config.TextColumn("캠페인", width="large"),
                "type": st.column_config.TextColumn("유형"),
                "daily_budget": st.column_config.NumberColumn("일예산", format="₩%d"),
                "spend": st.column_config.NumberColumn("지출", format="₩%d"),
                "conversions": st.column_config.NumberColumn("전환"),
                "cpa": st.column_config.NumberColumn("CPA", format="₩%d"),
                "roas": st.column_config.NumberColumn("ROAS", format="%d%%"),
                "ctr": st.column_config.NumberColumn("CTR", format="%.2f%%"),
                "cvr": st.column_config.NumberColumn("CVR", format="%.2f%%"),
                "status": st.column_config.TextColumn("권장"),
            },
            hide_index=True, width="stretch", height=200,
            disabled=["진단", "name", "type", "daily_budget", "spend",
                      "conversions", "cpa", "roas", "ctr", "cvr", "status"],
            key="gfa_campaigns_table"
        )

        st.subheader("🔔 GFA 추천 액션")
        for action in data.get_gfa_actions():
            render_action_card(action, "gfa")

        with st.expander("💡 GFA 운영 인사이트"):
            st.markdown("""
- **재근님 인수인계**: GFA가 Meta보다 성과 좋은 편 (목표 ROAS 200~300%)
- **현재 OFF**: 5/6부터 뉴욕 팝업 준비로 재고 부족 → 전면 중단
- **재개 시 우선순위**: ADVoost 쇼핑(전환) → 카탈로그 판매 → 웹사이트 전환 → 인지도/트래픽
- **전환 추적**: 스마트스토어 추적코드 연동 / 자사몰 픽셀
- **재고 회복 시점**: 즉시 재개 검토. Meta보다 GFA 비중 ↑ 권장
            """)

    # ─────────────── 브랜드검색 탭 ───────────────
    with n_brand:
        brand = data.get_naver_brand_search()
        st.success(f"**계약**: {brand['계약기간']}")
        st.caption("브랜드명 검색 시 단독 노출 · 월 계약형 (조회수 ↑ → 광고비 ↑)")

        bc = st.columns(5)
        bc[0].metric("월 비용 (총)", format_won(brand["총_월비용"]))
        bc[1].metric("PC", format_won(brand["PC_월비용"]))
        bc[2].metric("MO", format_won(brand["MO_월비용"]))
        bc[3].metric("CTR", f"{brand['ctr']}%")
        bc[4].metric("CVR", f"{brand['cvr']}%")

        st.subheader("방어 키워드")
        st.write(" · ".join([f"`{k}`" for k in brand["방어_키워드"]]))

        bc2 = st.columns(2)
        bc2[0].metric("노출 (월)", f"{brand['노출']:,}")
        bc2[1].metric("클릭", f"{brand['클릭']:,}")
        bc2[0].metric("전환", f"{brand['전환']}건")

        with st.expander("💡 브랜드검색 운영 가이드"):
            st.markdown("""
- **운영 목적**:
  - 브랜드 신뢰 확보
  - 브랜드 키워드 점유 (경쟁사 침투 방지)
  - 신제품·이벤트 진행 시 노출
- **관리 항목**:
  - 모바일/PC 문구 + 이미지 점검
  - 링크 정상 연결 확인
  - 브랜드 검색량 증가 여부 추적
- **결제**: 법인카드 수령 → 페이북 결제 → 최도현 팀장님 요청 → 충전 → 전자결제
- **갱신 검토**: 5/18 계약 종료 전 갱신 여부 결정
            """)

    # ─────────────── 쇼핑검색 탭 ───────────────
    with n_shop:
        st.caption("네이버 쇼핑탭 노출 · 공식몰+스마트스토어 등록 가능")

        shop_df = data.get_naver_shopping()
        shop_df["진단"] = shop_df["diag_color"]
        shop_view = shop_df[["진단", "product", "impressions", "clicks", "ctr",
                              "purchases", "cvr", "cpc", "spend", "status"]]
        st.data_editor(
            shop_view,
            column_config={
                "진단": st.column_config.TextColumn("진단", width="small"),
                "product": st.column_config.TextColumn("제품", width="medium"),
                "impressions": st.column_config.NumberColumn("노출"),
                "clicks": st.column_config.NumberColumn("클릭"),
                "ctr": st.column_config.NumberColumn("CTR", format="%.2f%%"),
                "purchases": st.column_config.NumberColumn("구매"),
                "cvr": st.column_config.NumberColumn("CVR", format="%.2f%%"),
                "cpc": st.column_config.NumberColumn("CPC", format="₩%d"),
                "spend": st.column_config.NumberColumn("지출", format="₩%d"),
                "status": st.column_config.TextColumn("권장"),
            },
            hide_index=True, width="stretch", height=200,
            disabled=["진단", "product", "impressions", "clicks", "ctr",
                      "purchases", "cvr", "cpc", "spend", "status"],
            key="naver_shop_table"
        )

        with st.expander("💡 쇼핑검색 운영 가이드"):
            st.markdown("""
- **예산 확대 운영 기준**: 노출/클릭/전환 좋음 + 리뷰 반응 좋음 + CTR 높음
- **예산 축소 운영 기준**: 클릭만 발생, 구매 전환 0 / CPC 과도 상승
- **관리 항목**: 경쟁사 대비 가격 / 썸네일 / 리뷰·평점·배송
            """)

    # ─────────────── 검색광고 (파워링크) 탭 ───────────────
    with n_search:

        kpi = data.get_naver_kpi()

        cols = st.columns(6)
        cols[0].metric("노출 (7일)", f"{kpi['노출']:,}", f"{kpi['노출_증감']:+.1f}%")
        cols[1].metric("클릭", f"{kpi['클릭']:,}", f"{kpi['클릭_증감']:+.1f}%")
        cols[2].metric("전환", f"{kpi['전환']}건", f"+{kpi['전환_증감']:.0f}%")
        cols[3].metric("CTR", f"{kpi['ctr']:.2f}%")
        cols[4].metric("CVR", f"{kpi['cvr']:.2f}%")
        cols[5].metric("비즈머니 잔액", format_won(kpi["비즈머니_잔액"]))

        st.divider()

        main_col, action_col = st.columns([2.5, 1])

        with main_col:
            # 시계열 차트 (탭 위, 항상 보임)
            st.subheader("📈 시계열 트렌드 (30일)")
            nts = data.get_naver_timeseries()
            nct1, nct2 = st.tabs(["노출·클릭", "전환·광고비"])
            with nct1:
                fig = go.Figure()
                fig.add_trace(go.Bar(x=nts["date"], y=nts["노출"], name="노출", marker_color="#94a3b8"))
                fig.add_trace(go.Scatter(x=nts["date"], y=nts["클릭"]*30, name="클릭 (×30)", line=dict(color="#dc2626", width=2), yaxis="y2"))
                fig.update_layout(height=260, margin=dict(t=20, b=20, l=20, r=20),
                                  yaxis=dict(title="노출"),
                                  yaxis2=dict(title="클릭", overlaying="y", side="right"))
                st.plotly_chart(fig, width="stretch")
            with nct2:
                fig = go.Figure()
                fig.add_trace(go.Bar(x=nts["date"], y=nts["광고비"], name="광고비", marker_color="#0891b2"))
                fig.add_trace(go.Scatter(x=nts["date"], y=nts["전환"]*5000, name="전환 (×5000)", line=dict(color="#059669", width=2), yaxis="y2"))
                fig.update_layout(height=260, margin=dict(t=20, b=20, l=20, r=20),
                                  yaxis=dict(title="광고비"),
                                  yaxis2=dict(title="전환", overlaying="y", side="right"))
                st.plotly_chart(fig, width="stretch")

            st.divider()

            st.subheader("🔬 단계별 진단")
            ncamps = data.get_naver_campaigns()
            nadgroups = data.get_naver_adgroups()
            nkeywords = data.get_naver_keywords()

            ntab_camp, ntab_grp, ntab_kw = st.tabs([
                f"📁 캠페인 ({len(ncamps)})",
                f"🎯 광고그룹 ({len(nadgroups)})",
                f"🔑 키워드 ({len(nkeywords)})"
            ])

            # ── 네이버 캠페인 탭 ──
            with ntab_camp:
                st.caption("**캠페인 = 광고 종류 + 일예산.** 파워링크/쇼핑/브랜드별로 분리")
                df_nc = ncamps.copy()
                df_nc["진단"] = df_nc["diag_color"]
                df_nc["ON/OFF"] = df_nc["active"]
                df_nc_view = df_nc[[
                    "진단", "ON/OFF", "name", "type", "daily_budget",
                    "spend", "impressions", "clicks", "ctr", "conversions", "cvr", "status"
                ]]
                st.data_editor(
                    df_nc_view,
                    column_config={
                        "진단": st.column_config.TextColumn("진단", width="small"),
                        "ON/OFF": st.column_config.CheckboxColumn("ON/OFF"),
                        "name": st.column_config.TextColumn("캠페인", width="medium"),
                        "type": st.column_config.TextColumn("유형"),
                        "daily_budget": st.column_config.NumberColumn("일예산", format="₩%d"),
                        "spend": st.column_config.NumberColumn("지출", format="₩%d"),
                        "impressions": st.column_config.NumberColumn("노출"),
                        "clicks": st.column_config.NumberColumn("클릭"),
                        "ctr": st.column_config.NumberColumn("CTR", format="%.2f%%"),
                        "conversions": st.column_config.NumberColumn("전환"),
                        "cvr": st.column_config.NumberColumn("CVR", format="%.2f%%"),
                        "status": st.column_config.TextColumn("권장"),
                    },
                    hide_index=True, width="stretch", height=200,
                    disabled=["진단", "name", "type", "daily_budget", "spend",
                              "impressions", "clicks", "ctr", "conversions", "cvr", "status"],
                    key="naver_camp_table"
                )

            # ── 네이버 광고그룹 탭 ──
            with ntab_grp:
                st.caption("**광고그룹 = 입찰가 기본값 + 노출 매체 + 시간대.** 같은 캠페인 내 효율 비교")
                ncamp_options = ["전체"] + ncamps["name"].tolist()
                sel_ncamp = st.selectbox("캠페인 필터", ncamp_options, key="filt_ncamp")

                df_grp = nadgroups.merge(
                    ncamps[["id", "name"]].rename(columns={"name": "campaign_name"}),
                    left_on="campaign_id", right_on="id", how="left"
                )
                if sel_ncamp != "전체":
                    df_grp = df_grp[df_grp["campaign_name"] == sel_ncamp]

                df_grp["진단"] = df_grp["diag_color"]
                df_grp["ON/OFF"] = df_grp["active"]
                df_grp_view = df_grp[[
                    "진단", "ON/OFF", "campaign_name", "name", "default_bid",
                    "spend", "impressions", "clicks", "ctr",
                    "conversions", "cvr", "status"
                ]]
                st.data_editor(
                    df_grp_view,
                    column_config={
                        "진단": st.column_config.TextColumn("진단", width="small"),
                        "ON/OFF": st.column_config.CheckboxColumn("ON/OFF"),
                        "campaign_name": st.column_config.TextColumn("캠페인", width="medium"),
                        "name": st.column_config.TextColumn("광고그룹", width="medium"),
                        "default_bid": st.column_config.NumberColumn("기본 입찰가", format="₩%d"),
                        "spend": st.column_config.NumberColumn("지출", format="₩%d"),
                        "impressions": st.column_config.NumberColumn("노출"),
                        "clicks": st.column_config.NumberColumn("클릭"),
                        "ctr": st.column_config.NumberColumn("CTR", format="%.2f%%"),
                        "conversions": st.column_config.NumberColumn("전환"),
                        "cvr": st.column_config.NumberColumn("CVR", format="%.2f%%"),
                        "status": st.column_config.TextColumn("권장"),
                    },
                    hide_index=True, width="stretch", height=300,
                    disabled=["진단", "campaign_name", "name", "default_bid", "spend",
                              "impressions", "clicks", "ctr", "conversions", "cvr", "status"],
                    key="naver_grp_table"
                )

                with st.expander("💡 광고그룹 단계 진단 가이드"):
                    st.markdown("""
    - **같은 캠페인 광고그룹 간 CVR 차이 큼** → 키워드 의도 차이. 효율 좋은 그룹 위주로 예산 분배
    - **빅키워드 그룹 ROAS 낮고 롱테일 그룹 ROAS 높음** → 빅키워드 OFF, 롱테일 강화
    - **노출 매체별 분리 검토**: PC vs 모바일 / 통합검색 vs 콘텐츠
    - **시간대별 입찰가 가중**: 전환 잘 나오는 시간대 (저녁 8~12시 + 주말 오후) 가중치 ↑
                    """)

            # ── 네이버 키워드 탭 ──
            with ntab_kw:
                st.caption("**키워드 = 검색어별 입찰가.** 가장 세부 단계")
                filt_col, btn_col = st.columns([4, 1])

                df_kw = nkeywords.copy()
                df_kw["진단"] = df_kw["diag_color"]
                df_kw["ON/OFF"] = df_kw["active"]
                df_kw_view = df_kw[[
                    "진단", "ON/OFF", "keyword", "match", "bid",
                    "monthly_search", "impressions", "clicks", "ctr",
                    "purchases", "cvr", "rank_avg", "quality", "status"
                ]]

                diag_filter = filt_col.selectbox(
                    "진단 필터",
                    ["전체", "🟢 유지/증액", "🟡 관찰", "🔴 OFF 권장"],
                    key="kw_filter"
                )
                if diag_filter == "🟢 유지/증액":
                    df_kw_view = df_kw_view[df_kw_view["진단"] == "🟢"]
                elif diag_filter == "🟡 관찰":
                    df_kw_view = df_kw_view[df_kw_view["진단"] == "🟡"]
                elif diag_filter == "🔴 OFF 권장":
                    df_kw_view = df_kw_view[df_kw_view["진단"] == "🔴"]

                if btn_col.button("🔍 전체 화면", key="naver_fullscreen", width="stretch"):
                    st.session_state["naver_full"] = True

                column_config_naver = {
                    "진단": st.column_config.TextColumn("진단", width="small"),
                    "ON/OFF": st.column_config.CheckboxColumn("ON/OFF"),
                    "keyword": st.column_config.TextColumn("키워드", width="medium"),
                    "match": st.column_config.TextColumn("매칭"),
                    "bid": st.column_config.NumberColumn("입찰가", format="₩%d"),
                    "monthly_search": st.column_config.NumberColumn("월 검색량"),
                    "impressions": st.column_config.NumberColumn("노출"),
                    "clicks": st.column_config.NumberColumn("클릭"),
                    "ctr": st.column_config.NumberColumn("CTR", format="%.2f%%"),
                    "purchases": st.column_config.NumberColumn("구매"),
                    "cvr": st.column_config.NumberColumn("CVR", format="%.2f%%"),
                    "rank_avg": st.column_config.NumberColumn("평균 순위", format="%.1f"),
                    "quality": st.column_config.NumberColumn("품질"),
                    "status": st.column_config.TextColumn("권장"),
                }
                disabled_cols = ["진단", "keyword", "match", "monthly_search", "impressions",
                                  "clicks", "ctr", "purchases", "cvr", "rank_avg", "quality", "status"]

                st.data_editor(
                    df_kw_view,
                    column_config=column_config_naver,
                    hide_index=True,
                    width="stretch",
                    height=420,
                    disabled=disabled_cols,
                    key="naver_keyword_table"
                )

                if st.session_state.get("naver_full"):
                    @st.dialog("키워드 전체 화면", width="large")
                    def show_full():
                        st.data_editor(
                            df_kw_view,
                            column_config=column_config_naver,
                            hide_index=True,
                            width="stretch",
                            height=700,
                            disabled=disabled_cols,
                            key="naver_keyword_table_full"
                        )
                    show_full()
                    st.session_state["naver_full"] = False

                with st.expander("💡 키워드 단계 진단 가이드"):
                    st.markdown("""
    - **품질지수 4 미만** → CPC 비효율. 키워드-소재-랜딩 일치도 점검 (광고 제목에 키워드 포함)
    - **빅키워드 검색량↑ but CTR↓** → 의도 모호, 우리와 안 맞음. 롱테일로 전환
    - **롱테일 CVR↑ but 노출 부족** → 입찰가 ↑ 또는 매칭 확장
    - **순위 5등 이하** → 같은 입찰가에서 순위 ↓ = 품질지수 문제. 소재·랜딩 개선
    - **CVR 0% + 노출 多** → 즉시 OFF 또는 키워드 자체 부적합
                    """)

            st.divider()

            # 키워드 기회 + 검색 트렌드 (탭 밖, 항상 보임)
            st.subheader("🔍 키워드 발굴·트렌드")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**신규 키워드 기회**")
                opp = data.get_naver_keyword_opportunity()
                st.caption("검색량 ↑ + 우리 미입찰 + USP 매칭")
                st.dataframe(
                    opp,
                    column_config={
                        "keyword": "키워드",
                        "monthly_search": st.column_config.NumberColumn("월 검색량"),
                        "예상_cpc": st.column_config.NumberColumn("예상 CPC", format="₩%d"),
                        "competitive": "경쟁도",
                        "score": st.column_config.NumberColumn("매력도", format="%.1f"),
                    },
                    hide_index=True,
                    width="stretch",
                )

            with c2:
                st.markdown("**검색 트렌드 (90일)**")
                st.caption("네이버 데이터랩 상대 지수")
                trend = data.get_naver_search_trend()
                fig = go.Figure()
                for col in ["PDRN 크림", "재생 크림", "시술 후 크림"]:
                    fig.add_trace(go.Scatter(x=trend["date"], y=trend[col], name=col, mode="lines"))
                fig.update_layout(height=240, margin=dict(t=20, b=20, l=20, r=20))
                st.plotly_chart(fig, width="stretch")

            st.divider()

            # SERP 경쟁사
            st.subheader('🌐 "PDRN 크림" 검색 결과 모니터링')
            st.caption("매일 자동 SERP 캡처 — 경쟁사 광고 카피 추적")
            comp = data.get_serp_competitors()
            for _, row in comp.iterrows():
                with st.container(border=True):
                    badge = "🟦 우리" if row["is_us"] else f"#{row['rank']}"
                    title = f"**{badge} · {row['advertiser']}** · `{row['url']}`"
                    st.markdown(title)
                    st.markdown(f"📝 **{row['headline']}**")
                    st.caption(row["description"])

        with action_col:
            st.markdown("### 🔔 오늘 추천 액션")
            st.caption("본인이 검토 후 실행")
            for action in data.get_naver_actions():
                render_action_card(action, "naver")


    # ═════════════════ 통합 페이지 ═════════════════
def render_integrated_page():
    st.title("통합 뷰")
    st.caption("Meta + Naver + 자사몰 매출 종합")

    cols = st.columns(4)
    cols[0].metric("총 광고비 (30일)", "₩2.6M")
    cols[1].metric("총 매출 추정", "₩6.2M")
    cols[2].metric("통합 ROAS", "238%")
    cols[3].metric("신규 고객", "35명")

    st.info("ⓘ 어트리뷰션 모델: 데이터 기반 (어트리뷰션 가이드 PDF 참조)")
    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 채널 비중")
        fig = go.Figure(data=[go.Pie(
            labels=["Meta", "Naver Search", "Direct/SEO"],
            values=[1809, 122, 0],
            hole=.4,
        )])
        fig.update_layout(height=320)
        st.plotly_chart(fig, width="stretch")

    with c2:
        st.markdown("### 채널별 ROAS")
        df = pd.DataFrame({
            "채널": ["Meta", "Naver Search"],
            "ROAS": [248, 318],
            "광고비": [1809241, 122438],
        })
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df["채널"], y=df["ROAS"], marker_color=["#4338ca", "#059669"]))
        fig.add_hline(y=250, line_dash="dash", line_color="orange", annotation_text="손익분기")
        fig.update_layout(height=320, yaxis_title="ROAS (%)")
        st.plotly_chart(fig, width="stretch")


# ═════════════════ 리포트 페이지 ═════════════════
def render_report_page():
    st.title("커스텀 리포트")
    st.caption("기간·지표·캠페인 선택 후 다운로드")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.date_input("시작일", value=datetime.now())
    with c2:
        st.date_input("종료일", value=datetime.now())
    with c3:
        st.selectbox("형식", ["Excel", "PDF", "CSV"])

    st.multiselect(
        "포함할 지표",
        ["노출", "클릭", "CTR", "CPC", "CPM", "광고비", "전환", "CVR", "CPA", "매출", "ROAS", "빈도"],
        default=["광고비", "전환", "CPA", "ROAS"]
    )

    st.multiselect(
        "포함할 캠페인",
        mock.meta_campaigns()["name"].tolist() + ["Naver - 루디언트"],
        default=mock.meta_campaigns()["name"].tolist()
    )

    if st.button("📥 리포트 생성", type="primary", width="stretch"):
        st.success("리포트 생성 완료. 다운로드를 시작합니다.")


# ═════════════════ 키워드 센터 페이지 ═════════════════
def render_keyword_tool_page():
    st.title("🔑 키워드 센터")
    st.caption("키워드 발굴·검증·관리 — 재근님 매일 작업 자동화")

    if not config.has_naver_credentials():
        st.warning("⚠️ Naver API 키 미연결 — Mock 데이터로 표시됩니다. 사이드바에서 연결하세요.")

    t1, t2 = st.tabs(["📊 검색량 조회 (외부 키워드)", "🔍 검색어 보고서 (우리 광고 노출 실제 검색어)"])

    with t2:
        render_search_query_report()

    with t1:
        render_keyword_volume_lookup()


def render_keyword_volume_lookup():
    """검색량 조회 (외부 키워드)."""
    st.caption("키워드 입력 → 월 검색량 / 평균 CPC / 경쟁도 + 연관 키워드 조회")

    # 입력
    with st.container(border=True):
        st.markdown("**키워드 입력** (최대 5개, 쉼표 구분)")
        c1, c2 = st.columns([4, 1])
        hint_input = c1.text_input(
            "키워드",
            value=st.session_state.get("kw_input", "PDRN, 재생 크림, 시술 후 크림"),
            label_visibility="collapsed",
            placeholder="예: PDRN, 모공 앰플, 안티에이징"
        )
        search_btn = c2.button("🔍 조회", width="stretch", type="primary")
        st.caption("💡 입력 키워드 + 연관 키워드를 함께 보여드려요. 검색량 많은 순 정렬.")

    if search_btn or hint_input != st.session_state.get("kw_last_input"):
        st.session_state["kw_input"] = hint_input
        st.session_state["kw_last_input"] = hint_input

    # 결과
    if not hint_input.strip():
        st.info("키워드를 입력하고 조회 버튼을 누르세요.")
        return

    with st.spinner("키워드 조회 중..."):
        df = data.get_keyword_research(hint_input)

    if df is None or df.empty:
        st.warning("결과가 없어요. 다른 키워드로 시도해보세요.")
        return

    # 요약 통계
    st.divider()
    sum_pc = df["monthly_pc"].sum()
    sum_mo = df["monthly_mo"].sum()
    sum_total = df["monthly_total"].sum()
    mo_ratio = (sum_mo / sum_total * 100) if sum_total else 0

    sc = st.columns(4)
    sc[0].metric("키워드 수", f"{len(df)}개")
    sc[1].metric("총 월 검색량", f"{sum_total:,}")
    sc[2].metric("PC 검색량", f"{sum_pc:,}")
    sc[3].metric("모바일 비율", f"{mo_ratio:.0f}%")

    # 메인 테이블
    st.subheader("키워드 분석 결과")
    st.dataframe(
        df,
        column_config={
            "keyword": st.column_config.TextColumn("키워드", width="medium"),
            "monthly_pc": st.column_config.NumberColumn("PC 월검색", help="PC에서 월간 검색 횟수"),
            "monthly_mo": st.column_config.NumberColumn("모바일 월검색"),
            "monthly_total": st.column_config.NumberColumn("총 월검색", help="PC + 모바일"),
            "mobile_ratio": st.column_config.NumberColumn("모바일 %", format="%.0f%%"),
            "avg_pc_clicks": st.column_config.NumberColumn("PC 평균 클릭"),
            "avg_mo_clicks": st.column_config.NumberColumn("MO 평균 클릭"),
            "competition": st.column_config.TextColumn("경쟁도"),
            "avg_rank": st.column_config.NumberColumn("평균 순위", format="%.1f"),
            "attractiveness": st.column_config.TextColumn("우리에게 매력도", width="medium"),
        },
        hide_index=True, width="stretch", height=420,
    )

    # 가이드 — 출처 분리
    with st.expander("📘 재근님 인수인계 기준 (직접 인용)"):
        st.markdown("""
2026-05-08 재근님 인수인계 문서 중 키워드·시장조사 관련 원문:

> **시장조사 & 키워드 추출**
> 1. 신제품 출시 / 분기·시즌별 키워드 추출 및 조회수 변경
> 2. 경쟁사 키워드 파악 / 자동완성·연관검색어 키워드 파악
> 3. 블로그, 카페 노출 키워드 파악
> *키워드 도구 활용 조회수 파악 (PC / MO)

> **파워링크 운영 목적**
> - 검색 유입 확보
> - 구매 전환
> - 경쟁사 키워드 선점

> **파워링크 소재 & CPC 관리**
> - 신뢰요소, 후킹문구, 가격강조 등
> - 키워드 별 CPC 단가 상이 (1~3위 조절)

> **파워링크 OFF 기준**
> - 클릭 대비 전환 없음
> - CPC 과도 상승
> - CTR 저조
        """)

    with st.expander("💡 일반 베스트 프랙티스 (참고 — 회사 표준 X)"):
        st.markdown("""
아래는 일반 SEO·SEM 베스트 프랙티스 기반 분석이에요.
**재근님이 명시한 회사 표준이 아니라 참고용**이니까 본인이 의사결정할 때 가중치 조절해주세요.

**매력도 분류 (제가 만든 프레임워크)**:
- 🟢 **우리에게 유리 (롱테일)**: 검색량 1K+ / 경쟁 낮음 = 적은 비용으로 1위 가능
- 🟡 **검토 가치**: 검색량 중간 / 경쟁 중간 = 입찰 시뮬레이션 후 결정
- 🔴 **빅키워드**: 검색량 50K+ / 대기업 경쟁 = 광고비 폭발 위험. 콘텐츠검색광고로 우회 검토

**모바일 비율 해석**:
- 80% 이상 → 모바일 입찰가 우선 ↑ + 모바일 최적화 랜딩

**키워드 등록 전략 권장**:
1. 🟢 매력도 → 즉시 등록 + 구문/정확 매칭
2. 🟡 → 1~2주 테스트 후 결정
3. 🔴 → 보류 또는 콘텐츠검색광고 우회

**시즌·신제품**:
- 신제품 핵심 + 연관 5개 정도를 출시 1~2개월 전 사전 등록
- 시즌 키워드 (예: 선크림 4~7월) 검색량 추이 매월 모니터링

→ 위 내용은 일반론. **재근님께 검증받으면 회사 표준이 될 수 있어요.**
        """)

    # 다운로드
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("📥 CSV 다운로드", csv,
                       file_name=f"keyword_research_{datetime.now().strftime('%Y%m%d')}.csv",
                       mime="text/csv", key="dl_kw_volume")


# ═════════════════ 검색어 보고서 (Search Query Report) ═════════════════
def render_search_query_report():
    """우리 키워드에 실제로 노출된 사용자 검색어 분석."""
    st.caption("우리 광고에 노출된 **실제 사용자 검색어** — 신규 키워드 발굴 + 노출 제외 키워드 식별")

    with st.container(border=True):
        c1, c2 = st.columns([3, 1])
        days = c1.selectbox("기간", [7, 14, 30], format_func=lambda d: f"최근 {d}일", index=0, key="sqr_days")
        refresh = c2.button("🔄 갱신", width="stretch", key="sqr_refresh")
        if refresh:
            data.clear_cache()
            st.rerun()
        st.caption("💡 검색어 보고서는 우리 키워드 + 사용자가 실제 입력한 검색어 페어를 보여줘요. "
                   "이 안에 **숨은 신규 키워드 + 광고비 새는 키워드**가 있어요.")

    with st.spinner("검색어 보고서 조회 중..."):
        df = data.get_search_query_report(days=days)

    if df is None or df.empty:
        st.warning("검색어 데이터가 없어요. 광고가 OFF 상태이거나 기간을 늘려보세요.")
        return

    # 요약
    st.divider()
    total_q = len(df)
    new_count = (df["status"] == "신규 등록 권장").sum()
    block_count = (df["status"] == "노출 제외 권장").sum()
    total_purchases = df["purchases"].sum()

    sc = st.columns(4)
    sc[0].metric("총 검색어", f"{total_q}개")
    sc[1].metric("🟢 신규 등록 권장", f"{new_count}개")
    sc[2].metric("🔴 노출 제외 권장", f"{block_count}개")
    sc[3].metric("총 구매", f"{total_purchases}건")

    # 필터
    st.subheader("검색어 분석")
    fc1, fc2 = st.columns([1, 3])
    filter_status = fc1.selectbox(
        "필터",
        ["전체", "🟢 신규 등록 권장", "🔴 노출 제외 권장", "🟡 관찰"],
        key="sqr_filter"
    )

    display_df = df.copy()
    display_df["진단"] = display_df["diag_color"]

    if filter_status == "🟢 신규 등록 권장":
        display_df = display_df[display_df["status"] == "신규 등록 권장"]
    elif filter_status == "🔴 노출 제외 권장":
        display_df = display_df[display_df["status"] == "노출 제외 권장"]
    elif filter_status == "🟡 관찰":
        display_df = display_df[display_df["status"] == "관찰"]

    display_df = display_df[[
        "진단", "our_keyword", "search_query", "impressions", "clicks",
        "ctr", "purchases", "cvr", "spend", "cpa", "status"
    ]]

    st.data_editor(
        display_df,
        column_config={
            "진단": st.column_config.TextColumn("진단", width="small"),
            "our_keyword": st.column_config.TextColumn("우리 키워드", width="medium"),
            "search_query": st.column_config.TextColumn("실제 검색어", width="large"),
            "impressions": st.column_config.NumberColumn("노출"),
            "clicks": st.column_config.NumberColumn("클릭"),
            "ctr": st.column_config.NumberColumn("CTR", format="%.2f%%"),
            "purchases": st.column_config.NumberColumn("구매"),
            "cvr": st.column_config.NumberColumn("CVR", format="%.2f%%"),
            "spend": st.column_config.NumberColumn("광고비", format="₩%d"),
            "cpa": st.column_config.NumberColumn("CPA", format="₩%d"),
            "status": st.column_config.TextColumn("권장", width="medium"),
        },
        hide_index=True, width="stretch", height=460,
        disabled=display_df.columns.tolist(),
        key="sqr_table"
    )

    # 액션 권장 — Phase N2에서 실제 API 연결 예정
    st.subheader("🎯 권장 액션")
    new_kws = df[df["status"] == "신규 등록 권장"]
    block_kws = df[df["status"] == "노출 제외 권장"]

    if len(new_kws) > 0:
        with st.expander(f"🟢 신규 키워드로 등록 권장 — {len(new_kws)}개"):
            st.caption("아래 검색어들은 이미 우리 광고에 노출돼서 구매까지 발생한 키워드예요. 신규 키워드로 등록하면 직접 입찰 가능.")
            for idx, row in new_kws.head(10).iterrows():
                col_a, col_b = st.columns([4, 1])
                col_a.markdown(
                    f"**`{row['search_query']}`** — "
                    f"구매 {row['purchases']}건 / CVR {row['cvr']:.1f}% / CPA ₩{int(row['cpa']) if pd.notna(row['cpa']) else 0:,} "
                    f"(우리 키워드: `{row['our_keyword']}`)"
                )
                if col_b.button("➕ 등록", key=f"add_kw_{idx}", width="stretch"):
                    st.session_state["pending_add"] = {
                        "search_query": row["search_query"],
                        "our_keyword": row["our_keyword"],
                        "adgroup_id": row.get("adgroup_id", ""),
                        "purchases": int(row["purchases"]),
                        "cvr": float(row["cvr"]),
                    }
                    st.rerun()

    if len(block_kws) > 0:
        with st.expander(f"🔴 노출 제외 권장 — {len(block_kws)}개"):
            st.caption("클릭은 많은데 구매로 안 이어진 검색어. 의도 불일치 가능성. 노출 제외 키워드로 등록하면 광고비 절감.")
            for idx, row in block_kws.head(10).iterrows():
                col_a, col_b = st.columns([4, 1])
                col_a.markdown(
                    f"**`{row['search_query']}`** — "
                    f"클릭 {row['clicks']}회 / 구매 0건 / 광고비 ₩{int(row['spend']):,} 낭비 "
                    f"(우리 키워드: `{row['our_keyword']}`)"
                )
                if col_b.button("🚫 제외", key=f"block_kw_{idx}", width="stretch"):
                    st.session_state["pending_block"] = {
                        "search_query": row["search_query"],
                        "our_keyword": row["our_keyword"],
                        "adgroup_id": row.get("adgroup_id", ""),
                        "clicks": int(row["clicks"]),
                        "spend": int(row["spend"]),
                    }
                    st.rerun()

    # ───── 모달: 키워드 등록 확인 ─────
    if st.session_state.get("pending_add"):
        @st.dialog("키워드 등록 확인", width="large")
        def confirm_add():
            p = st.session_state["pending_add"]
            st.markdown(f"### `{p['search_query']}` 를 신규 키워드로 등록할까요?")
            st.markdown(f"- **소속 광고그룹**: `{p['adgroup_id']}` (우리 키워드: `{p['our_keyword']}`)")
            st.markdown(f"- **검증 데이터**: 구매 {p['purchases']}건, CVR {p['cvr']:.1f}%")
            st.divider()

            bid_col, _ = st.columns([1, 2])
            use_group = bid_col.checkbox("광고그룹 기본 입찰가 사용", value=True, key="add_use_group")
            bid_amt = None
            if not use_group:
                bid_amt = st.number_input("키워드 개별 입찰가 (원)", min_value=70, max_value=100_000,
                                          value=1000, step=10, key="add_bid")
                st.caption("💡 Naver 최소 입찰가 70원. 1~3위 평균은 키워드마다 다름.")

            st.warning("⚠️ 실행하면 즉시 Naver 광고에 키워드가 등록돼요. 광고비가 발생할 수 있어요.")

            c1, c2 = st.columns(2)
            if c1.button("✅ 등록 실행", type="primary", width="stretch"):
                with st.spinner("등록 중..."):
                    result = data.execute_add_keyword(p["adgroup_id"], p["search_query"], bid_amt)
                    data.log_action("ADD_KEYWORD", p, result)
                if result.get("success"):
                    msg = f"등록 완료: {p['search_query']}"
                    if result.get("mock"):
                        msg += " (Mock 모드 — 실제 등록 X)"
                    st.success(msg)
                else:
                    st.error(f"실패: {result.get('error', '알 수 없는 오류')}")
                st.session_state.pop("pending_add", None)
                st.rerun()
            if c2.button("취소", width="stretch"):
                st.session_state.pop("pending_add", None)
                st.rerun()
        confirm_add()

    # ───── 모달: 노출 제외 확인 ─────
    if st.session_state.get("pending_block"):
        @st.dialog("노출 제외 키워드 등록 확인", width="large")
        def confirm_block():
            p = st.session_state["pending_block"]
            st.markdown(f"### `{p['search_query']}` 를 노출 제외 키워드로 등록할까요?")
            st.markdown(f"- **소속 광고그룹**: `{p['adgroup_id']}` (원래 키워드: `{p['our_keyword']}`)")
            st.markdown(f"- **광고비 낭비**: 클릭 {p['clicks']}회 / 구매 0건 / 광고비 ₩{p['spend']:,}")
            st.divider()

            st.info("ℹ️ 노출 제외 등록 후, 이 검색어로는 우리 광고가 더 이상 노출되지 않아요. "
                    "광고비 절감 효과는 즉시 발생.")
            st.warning("⚠️ 실수로 제외하면 매출 영향 가능. 검색어 의도 다시 확인.")

            c1, c2 = st.columns(2)
            if c1.button("✅ 제외 실행", type="primary", width="stretch"):
                with st.spinner("제외 등록 중..."):
                    result = data.execute_block_keyword(p["adgroup_id"], p["search_query"])
                    data.log_action("BLOCK_KEYWORD", p, result)
                if result.get("success"):
                    msg = f"노출 제외 완료: {p['search_query']}"
                    if result.get("mock"):
                        msg += " (Mock 모드 — 실제 등록 X)"
                    st.success(msg)
                else:
                    st.error(f"실패: {result.get('error', '알 수 없는 오류')}")
                st.session_state.pop("pending_block", None)
                st.rerun()
            if c2.button("취소", width="stretch"):
                st.session_state.pop("pending_block", None)
                st.rerun()
        confirm_block()

    # ───── 실행 로그 ─────
    if st.session_state.get("action_log"):
        with st.expander(f"📜 실행 로그 ({len(st.session_state['action_log'])}건)"):
            for entry in st.session_state["action_log"][:20]:
                icon = "➕" if entry["type"] == "ADD_KEYWORD" else "🚫"
                payload = entry["payload"]
                status = "✅" if entry["result"].get("success") else "❌"
                mock_tag = " [Mock]" if entry["result"].get("mock") else ""
                st.markdown(
                    f"`{entry['ts']}` {icon} {status}{mock_tag} "
                    f"**{payload.get('search_query', '?')}** "
                    f"({payload.get('our_keyword', '?')} → {payload.get('adgroup_id', '?')})"
                )

    # 가이드
    with st.expander("📘 검색어 보고서 활용 가이드"):
        st.markdown("""
**검색어 보고서가 특별한 이유**:
- 외부에서 키워드 추출 (자동완성·연관·블로그·카페) = 추측
- 검색어 보고서 = **실제 우리 광고에 노출된 검증된 의도**
- → 즉시 활용 가능한 키워드 광맥

**진단 로직**:
- 🟢 **신규 등록 권장**: 구매 1건 이상 + CVR ≥ 5% — 효율 검증된 검색어. 직접 키워드로 등록해서 입찰가 ↑
- 🔴 **노출 제외 권장**: 클릭 5회+ / 광고비 5,000원+ 썼는데 구매 0건 — 의도 불일치. 노출 제외 키워드로 등록
- 🟡 **관찰**: 1~2주 더 두고 데이터 누적

**활용 워크플로우 (재근님 노하우 + 일반 베스트)**:
1. 매주 검색어 보고서 확인
2. 🟢 신규 키워드 → 즉시 등록 (정확/구문 매칭)
3. 🔴 제외 키워드 → 노출 제외 등록 → 광고비 즉시 절감
4. 🟡 관찰 → 다음 주 재확인
        """)

    # 다운로드
    csv = df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("📥 CSV 다운로드", csv,
                       file_name=f"search_query_report_{datetime.now().strftime('%Y%m%d')}.csv",
                       mime="text/csv", key="dl_sqr")


# ═════════════════ 라우팅 ═════════════════
if page == "Meta":
    render_meta_page()
elif page == "Naver":
    render_naver_page()
elif page == "🔑 키워드 도구":
    render_keyword_tool_page()
elif page == "통합":
    render_integrated_page()
elif page == "리포트":
    render_report_page()
