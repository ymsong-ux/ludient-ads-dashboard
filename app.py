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
        st.subheader("캠페인 현황")

        df = mock.meta_campaigns()

        # 컬럼 표시 정리
        display_df = df.copy()
        display_df["진단"] = display_df["diag_color"]
        display_df["ON/OFF"] = display_df["active"]
        display_df = display_df[[
            "진단", "ON/OFF", "name", "objective", "spend",
            "purchases", "cpa", "roas", "ctr", "cvr", "frequency", "learning", "status"
        ]]

        column_config_meta = {
            "진단": st.column_config.TextColumn("진단", width="small"),
            "ON/OFF": st.column_config.CheckboxColumn("ON/OFF", default=False),
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
        }
        disabled_meta = ["진단", "name", "objective", "spend", "purchases", "cpa",
                          "roas", "ctr", "cvr", "frequency", "learning", "status"]

        c1, c2 = st.columns([5, 1])
        if c2.button("🔍 전체 화면", key="meta_fullscreen", width="stretch"):
            st.session_state["meta_full"] = True

        st.data_editor(
            display_df,
            column_config=column_config_meta,
            hide_index=True,
            width="stretch",
            height=320,
            disabled=disabled_meta,
            key="meta_campaign_table"
        )

        if st.session_state.get("meta_full"):
            @st.dialog("캠페인 전체 화면", width="large")
            def show_meta_full():
                st.data_editor(
                    display_df,
                    column_config=column_config_meta,
                    hide_index=True,
                    width="stretch",
                    height=700,
                    disabled=disabled_meta,
                    key="meta_campaign_table_full"
                )
            show_meta_full()
            st.session_state["meta_full"] = False

        # 차트
        st.subheader("시계열 트렌드")

        ts = mock.meta_timeseries()
        chart_tab1, chart_tab2 = st.tabs(["광고비·매출", "ROAS·CTR"])

        with chart_tab1:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=ts["date"], y=ts["광고비"], name="광고비", marker_color="#94a3b8"))
            fig.add_trace(go.Bar(x=ts["date"], y=ts["매출"], name="매출", marker_color="#4338ca"))
            fig.update_layout(height=320, margin=dict(t=20, b=20, l=20, r=20), barmode="group")
            st.plotly_chart(fig, width="stretch")

        with chart_tab2:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=ts["date"], y=ts["ROAS"], name="ROAS (%)", line=dict(color="#059669", width=2)))
            fig.add_trace(go.Scatter(x=ts["date"], y=ts["CTR"]*100, name="CTR (%×100)", line=dict(color="#dc2626", width=2), yaxis="y2"))
            fig.add_hline(y=250, line_dash="dash", line_color="orange", annotation_text="손익분기 ROAS 250%")
            fig.update_layout(
                height=320,
                margin=dict(t=20, b=20, l=20, r=20),
                yaxis=dict(title="ROAS"),
                yaxis2=dict(title="CTR", overlaying="y", side="right"),
            )
            st.plotly_chart(fig, width="stretch")

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
        head_col, btn_col, filt_col = st.columns([2, 1, 1])
        head_col.subheader(f"키워드 현황 ({len(mock.naver_keywords())}개)")

        df = mock.naver_keywords()
        display_df = df.copy()
        display_df["진단"] = display_df["diag_color"]
        display_df["ON/OFF"] = display_df["active"]
        display_df = display_df[[
            "진단", "ON/OFF", "keyword", "match", "bid",
            "monthly_search", "impressions", "clicks", "ctr",
            "purchases", "cvr", "rank_avg", "quality", "status"
        ]]

        # 진단 필터
        diag_filter = filt_col.selectbox(
            "필터",
            ["전체", "🟢 유지/증액", "🟡 관찰", "🔴 OFF 권장"],
            label_visibility="collapsed"
        )
        if diag_filter == "🟢 유지/증액":
            display_df = display_df[display_df["진단"] == "🟢"]
        elif diag_filter == "🟡 관찰":
            display_df = display_df[display_df["진단"] == "🟡"]
        elif diag_filter == "🔴 OFF 권장":
            display_df = display_df[display_df["진단"] == "🔴"]

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
            display_df,
            column_config=column_config_naver,
            hide_index=True,
            width="stretch",
            height=420,
            disabled=disabled_cols,
            key="naver_keyword_table"
        )

        # 전체 화면 다이얼로그
        if st.session_state.get("naver_full"):
            @st.dialog("키워드 전체 화면", width="large")
            def show_full():
                st.data_editor(
                    display_df,
                    column_config=column_config_naver,
                    hide_index=True,
                    width="stretch",
                    height=700,
                    disabled=disabled_cols,
                    key="naver_keyword_table_full"
                )
            show_full()
            st.session_state["naver_full"] = False

        # 키워드 기회 + 검색 트렌드
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("신규 키워드 기회")
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
            st.subheader("검색 트렌드 (90일)")
            st.caption("네이버 데이터랩 상대 지수")
            trend = mock.naver_search_trend()
            fig = go.Figure()
            for col in ["PDRN 크림", "재생 크림", "시술 후 크림"]:
                fig.add_trace(go.Scatter(x=trend["date"], y=trend[col], name=col, mode="lines"))
            fig.update_layout(height=280, margin=dict(t=20, b=20, l=20, r=20))
            st.plotly_chart(fig, width="stretch")

        # SERP 경쟁사
        st.subheader('"PDRN 크림" 검색 결과 모니터링')
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
