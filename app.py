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
        ["Meta", "Naver", "통합", "리포트"],
        label_visibility="collapsed"
    )
    st.divider()

    period = st.selectbox(
        "기간",
        ["최근 7일", "최근 14일", "최근 30일", "사용자 정의"],
        index=2
    )

    if st.button("🔄 데이터 새로고침", width="stretch"):
        st.success("갱신 완료")

    st.divider()
    st.caption("마지막 업데이트")
    st.caption(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    st.caption("자동 갱신: 30분")

    st.divider()
    st.caption("⚠️ 시연 모드 (Mock 데이터)")


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
    st.caption("Ludient 계정 · 페이스북·인스타그램 광고 · % = 직전 30일 대비 증감")

    kpi = mock.meta_kpi()

    # KPI 카드 5개
    cols = st.columns(5)
    cols[0].metric("광고비 (30일)", format_won(kpi["광고비_30일"]), f"{kpi['광고비_증감']:+.1f}%")
    cols[1].metric("매출 (30일)", format_won(kpi["매출_30일"]), f"{kpi['매출_증감']:+.1f}%")
    cols[2].metric("ROAS", f"{kpi['roas']}%", f"{kpi['roas_증감']:+}%p")
    cols[3].metric("CPA", format_won(kpi["cpa"]), f"{kpi['cpa_증감']:+.1f}%", delta_color="inverse")
    cols[4].metric("신규 고객", f"{kpi['신규고객']}명", f"+{kpi['신규고객_증감']}")

    st.divider()

    # 메인 + 액션 사이드바
    main_col, action_col = st.columns([2.5, 1])

    with main_col:
        campaigns = mock.meta_campaigns()
        adsets = mock.meta_adsets()
        ads = mock.meta_ads()

        # 시계열 차트 (탭 위, 항상 보임)
        st.subheader("📈 시계열 트렌드 (30일)")
        ts = mock.meta_timeseries()
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

        for action in mock.meta_actions():
            render_action_card(action, "meta")


# ═════════════════ NAVER 페이지 ═════════════════
def render_naver_page():
    st.title("Naver 광고")
    st.caption("루디언트 계정 · 검색광고 (파워링크) · % = 직전 7일 대비 증감")

    kpi = mock.naver_kpi()

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
        nts = mock.naver_timeseries()
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
        ncamps = mock.naver_campaigns()
        nadgroups = mock.naver_adgroups()
        nkeywords = mock.naver_keywords()

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
            opp = mock.naver_keyword_opportunity()
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
            trend = mock.naver_search_trend()
            fig = go.Figure()
            for col in ["PDRN 크림", "재생 크림", "시술 후 크림"]:
                fig.add_trace(go.Scatter(x=trend["date"], y=trend[col], name=col, mode="lines"))
            fig.update_layout(height=240, margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig, width="stretch")

        st.divider()

        # SERP 경쟁사
        st.subheader('🌐 "PDRN 크림" 검색 결과 모니터링')
        st.caption("매일 자동 SERP 캡처 — 경쟁사 광고 카피 추적")
        comp = mock.serp_competitors()
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
        for action in mock.naver_actions():
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


# ═════════════════ 라우팅 ═════════════════
if page == "Meta":
    render_meta_page()
elif page == "Naver":
    render_naver_page()
elif page == "통합":
    render_integrated_page()
elif page == "리포트":
    render_report_page()
