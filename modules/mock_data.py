"""실제 API 연결 전 시연용 가짜 데이터."""

from datetime import datetime, timedelta
import pandas as pd


def meta_kpi():
    """4월 실제 광고비 1,307,313원 반영. 4/17부터 OFF."""
    return {
        "광고비_30일": 1_307_313,
        "매출_30일": 3_268_283,
        "roas": 250,
        "cpa": 81_707,
        "신규고객": 16,
        "광고비_증감": -47.8,  # 3월 250만 → 4월 130만 (감소)
        "매출_증감": -42.0,
        "roas_증감": 12,
        "cpa_증감": -8.4,
        "신규고객_증감": -7,
        "운영_상태": "⏸ 4/17부터 전면 OFF — 뉴욕 팝업 준비, 재고 부족",
    }


def gfa_kpi():
    """GFA — Meta보다 성과 좋은 채널. 5/6 OFF."""
    return {
        "광고비_30일": 1_552_372,
        "매출_30일": 4_036_167,
        "roas": 260,
        "cpa": 64_682,
        "전환": 24,
        "광고비_증감": 146.2,  # 3월 63만 → 4월 155만 (증가)
        "매출_증감": 158.0,
        "roas_증감": 8,
        "cpa_증감": -4.5,
        "전환_증감": 14,
        "운영_상태": "⏸ 5/6부터 전면 OFF — 뉴욕 팝업 준비, 재고 부족",
        "목표_roas": 250,  # 200~300% 중앙값
    }


def gfa_campaigns():
    """GFA 4가지 캠페인 종류."""
    rows = [
        ("ADVoost 쇼핑 (전환)", "전환", 20000, 620000, 12, 51_667, 285, 1.45, 5.2, "유지", "🟢"),
        ("웹사이트 전환 (전환)", "전환", 20000, 580000, 8, 72_500, 240, 1.21, 3.8, "관찰", "🟡"),
        ("인지도 및 트래픽 (트래픽)", "트래픽", 20000, 215000, None, None, None, 2.1, None, "관찰", "🟡"),
        ("카탈로그 판매 (트래픽)", "트래픽", 10000, 137372, 4, 34_343, 195, 1.85, 4.5, "유지", "🟢"),
    ]
    cols = ["name", "type", "daily_budget", "spend", "conversions",
            "cpa", "roas", "ctr", "cvr", "status", "diag_color"]
    df = pd.DataFrame(rows, columns=cols)
    df.insert(0, "active", False)
    return df


def gfa_actions():
    return [
        {
            "id": "g1",
            "icon": "⏸",
            "title": "운영 재개 시 ADVoost 우선 ON",
            "reason": "ROAS 285%로 채널 내 1위. 목표 ROAS 250 초과 + CVR 5.2%.",
            "impact": "재고 확보 후 즉시 재개. 일 2만원 → 3만원 증액 검토.",
            "type": "REOPEN",
        },
        {
            "id": "g2",
            "icon": "🟡",
            "title": "웹사이트 전환 — 소재 교체 후 재개",
            "reason": "ROAS 240으로 손익분기 근처. CTR 1.21%로 평균 수준.",
            "impact": "전환 소재 5종(공감/경험/차별점/B&A/후기) 중 미사용 패턴 추가.",
            "type": "REPLACE",
        },
        {
            "id": "g3",
            "icon": "🟢",
            "title": "GFA Meta 대비 우위 — 예산 비중 재검토",
            "reason": "GFA ROAS 260 vs Meta 250. GFA가 성과 좋음. 재근님 인수인계도 동일 의견.",
            "impact": "재개 시 Meta 60% / GFA 40% → Meta 50% / GFA 50% 검토.",
            "type": "STRATEGY",
        },
    ]


def naver_brand_search():
    """네이버 브랜드검색 — 월 계약형."""
    return {
        "계약기간": "2026.04.17 ~ 2026.05.18",
        "PC_월비용": 682_000,
        "MO_월비용": 902_000,
        "총_월비용": 1_584_000,
        "노출": 18_400,
        "클릭": 412,
        "ctr": 2.24,
        "전환": 22,
        "cvr": 5.34,
        "방어_키워드": ["루디언트", "루디언트크림", "ludient", "Ludient PDRN"],
        "운영_상태": "🟢 운영 중 (월 계약 자동 갱신 검토 5/18 전)",
    }


def naver_shopping():
    """네이버 쇼핑검색 — 네이버 쇼핑 영역 노출."""
    rows = [
        ("PDRN 앰플", 8200, 124, 1.51, 7, 5.65, 850, 5_950, "유지", "🟢"),
        ("재생 크림", 11500, 138, 1.20, 5, 3.62, 1100, 5_500, "관찰", "🟡"),
        ("시술 후 마스크팩", 4200, 81, 1.93, 5, 6.17, 720, 3_600, "증액 권장", "🟢"),
        ("안티에이징 세럼", 3800, 38, 1.00, 1, 2.63, 1050, 1_050, "OFF 권장", "🔴"),
    ]
    cols = ["product", "impressions", "clicks", "ctr", "purchases",
            "cvr", "cpc", "spend", "status", "diag_color"]
    return pd.DataFrame(rows, columns=cols)


def company_thresholds():
    """재근님 인수인계 기준 — 회사 표준 ON/OFF 임계값."""
    return {
        "OFF_검토": {
            "CTR_미달": 1.0,  # CTR < 1%
            "전환_없는_기간": 14,  # 1~2주
            "ROAS_기준": "목표 미달",
            "소재_장기운영": 30,  # 1개월
        },
        "증액_유지": {
            "CTR_우수": 3.0,  # CTR > 3%
            "ROAS_목표": "목표 이상",
            "CPA_안정화": True,
        },
        "GFA_목표_ROAS": (200, 300),
        "Meta_목표_ROAS": (200, 300),  # 가정 — 합의 필요
    }


def meta_campaigns():
    return pd.DataFrame([
        {"id": "c_260406_2", "active": False, "name": "260406_전환_카드뉴스(2)", "objective": "판매",
         "spend": 449_738, "purchases": 4, "cpa": 112_435, "roas": 178,
         "ctr": 1.2, "cvr": 0.9, "frequency": 4.2, "learning": "완료",
         "status": "OFF 권장", "diag_color": "🔴"},
        {"id": "c_260406_1", "active": False, "name": "260406_전환_카드뉴스(1)", "objective": "판매",
         "spend": 456_935, "purchases": 6, "cpa": 76_156, "roas": 263,
         "ctr": 1.8, "cvr": 1.4, "frequency": 3.5, "learning": "완료",
         "status": "유지", "diag_color": "🟢"},
        {"id": "c_260327_2", "active": False, "name": "260327_전환_파트너(2)", "objective": "판매",
         "spend": 348_782, "purchases": 2, "cpa": 174_391, "roas": 115,
         "ctr": 0.9, "cvr": 0.6, "frequency": 2.8, "learning": "미완료",
         "status": "OFF 권장", "diag_color": "🔴"},
        {"id": "c_260320_1", "active": False, "name": "260320_전환_파트너(1)", "objective": "판매",
         "spend": 319_099, "purchases": 0, "cpa": None, "roas": 0,
         "ctr": 0.7, "cvr": 0, "frequency": 2.1, "learning": "미완료",
         "status": "OFF 권장", "diag_color": "🔴"},
        {"id": "c_260312_v", "active": False, "name": "260312_트래픽_영상", "objective": "트래픽",
         "spend": 234_687, "purchases": None, "cpa": None, "roas": None,
         "ctr": 2.4, "cvr": None, "frequency": 1.8, "learning": "—",
         "status": "관찰", "diag_color": "🟡"},
    ])


def meta_adsets():
    rows = [
        # campaign_id, name, target, daily_budget, spend, purchases, cpa, roas, ctr, cvr, frequency, learning, status, diag
        ("c_260406_2", "1A_25-40여성_스킨케어관심", "핵심타겟", 50000, 220000, 1, 220000, 95, 0.9, 0.7, 4.5, "완료", "OFF 권장", "🔴"),
        ("c_260406_2", "1B_Lookalike1%_구매자", "유사타겟", 50000, 229738, 3, 76579, 215, 1.4, 1.1, 3.8, "완료", "유지", "🟢"),
        ("c_260406_1", "1A_25-40여성_스킨케어관심", "핵심타겟", 50000, 230000, 3, 76667, 245, 1.6, 1.2, 3.5, "완료", "유지", "🟢"),
        ("c_260406_1", "1B_Lookalike1%_구매자", "유사타겟", 50000, 226935, 3, 75645, 281, 1.9, 1.6, 3.4, "완료", "증액 권장", "🟢"),
        ("c_260327_2", "2A_30-50_안티에이징", "핵심타겟", 30000, 180000, 1, 180000, 105, 0.8, 0.5, 2.5, "미완료", "OFF 권장", "🔴"),
        ("c_260327_2", "2B_고객리스트_리타겟팅", "맞춤타겟", 30000, 168782, 1, 168782, 125, 0.9, 0.7, 2.9, "미완료", "OFF 권장", "🔴"),
        ("c_260320_1", "3A_파트너_광범위", "핵심타겟", 30000, 319099, 0, None, 0, 0.7, 0, 2.0, "미완료", "OFF 권장", "🔴"),
        ("c_260312_v", "4A_25-40여성_트래픽", "핵심타겟", 30000, 234687, None, None, None, 2.4, None, 1.8, "—", "관찰", "🟡"),
    ]
    cols = ["campaign_id", "name", "target", "daily_budget", "spend", "purchases",
            "cpa", "roas", "ctr", "cvr", "frequency", "learning", "status", "diag_color"]
    df = pd.DataFrame(rows, columns=cols)
    df.insert(0, "active", False)
    return df


def meta_ads():
    rows = [
        # adset_idx (campaign_id + adset name 조합), name, format, spend, impressions, clicks, ctr, purchases, cvr, status, diag
        ("c_260406_2|1A", "A1_PDRN_비포애프터_15s", "영상", 110000, 9200, 78, 0.85, 1, 1.28, "OFF 권장", "🔴"),
        ("c_260406_2|1A", "A2_PDRN_의사추천_15s", "영상", 110000, 9000, 86, 0.96, 0, 0, "OFF 권장", "🔴"),
        ("c_260406_2|1B", "A1_PDRN_비포애프터_15s", "영상", 115000, 9800, 132, 1.35, 2, 1.52, "유지", "🟢"),
        ("c_260406_2|1B", "A2_PDRN_의사추천_15s", "영상", 114738, 9600, 142, 1.48, 1, 0.70, "관찰", "🟡"),
        ("c_260406_1|1A", "A1_PDRN_비포애프터_15s_v2", "영상", 115000, 8800, 145, 1.65, 2, 1.38, "유지", "🟢"),
        ("c_260406_1|1A", "A2_PDRN_임상결과_15s", "영상", 115000, 8500, 158, 1.86, 1, 0.63, "관찰", "🟡"),
        ("c_260406_1|1B", "A1_PDRN_비포애프터_15s_v2", "영상", 113000, 8900, 165, 1.85, 2, 1.21, "유지", "🟢"),
        ("c_260406_1|1B", "A2_PDRN_임상결과_15s", "영상", 113935, 8700, 178, 2.05, 1, 0.56, "관찰", "🟡"),
        ("c_260327_2|2A", "B1_재생크림_비포애프터", "이미지", 90000, 5400, 41, 0.76, 0, 0, "OFF 권장", "🔴"),
        ("c_260327_2|2A", "B2_재생크림_연령후기", "이미지", 90000, 5200, 47, 0.90, 1, 2.13, "OFF 권장", "🔴"),
        ("c_260327_2|2B", "B1_재생크림_비포애프터", "이미지", 84000, 6100, 55, 0.90, 0, 0, "OFF 권장", "🔴"),
        ("c_260327_2|2B", "B2_재생크림_연령후기", "이미지", 84782, 5900, 51, 0.86, 1, 1.96, "관찰", "🟡"),
        ("c_260320_1|3A", "P1_파트너_브랜드스토리", "카루셀", 160000, 11200, 78, 0.70, 0, 0, "OFF 권장", "🔴"),
        ("c_260320_1|3A", "P2_파트너_제품라인", "카루셀", 159099, 10800, 71, 0.66, 0, 0, "OFF 권장", "🔴"),
        ("c_260312_v|4A", "V1_트러블해결_30s", "영상", 117000, 4800, 122, 2.54, None, None, "유지", "🟢"),
        ("c_260312_v|4A", "V2_시술비교_30s", "영상", 117687, 4600, 105, 2.28, None, None, "관찰", "🟡"),
    ]
    cols = ["adset_idx", "name", "format", "spend", "impressions", "clicks",
            "ctr", "purchases", "cvr", "status", "diag_color"]
    df = pd.DataFrame(rows, columns=cols)
    df.insert(0, "active", False)
    return df


def meta_timeseries():
    days = pd.date_range(end=datetime.now(), periods=30, freq="D")
    import numpy as np
    np.random.seed(42)
    return pd.DataFrame({
        "date": days,
        "광고비": np.random.normal(60000, 15000, 30).clip(20000),
        "매출": np.random.normal(150000, 50000, 30).clip(50000),
        "ROAS": np.random.normal(250, 60, 30).clip(80),
        "CTR": np.random.normal(1.5, 0.4, 30).clip(0.5),
    })


def meta_actions():
    return [
        {
            "id": "m1",
            "icon": "🔴",
            "title": "카드뉴스(2) OFF",
            "reason": "학습 종료. CPA ₩112K (손익분기 ₩50K의 2.2배). CTR/CVR 둘 다 (1)보다 낮음.",
            "impact": "월 ₩4.5M 광고비 절감. 같은 예산 (1)에 재할당 시 신규 고객 +30% 추정.",
            "type": "OFF",
        },
        {
            "id": "m2",
            "icon": "🔴",
            "title": "파트너(1)·(2) OFF",
            "reason": "둘 다 학습 미완료 + ROAS 손익분기 절반 미달. (1)은 30만원 쓰고 0건.",
            "impact": "월 ₩2.7M 절감. 파트너 가설 폐기 후 새 페르소나 타겟 권장.",
            "type": "OFF",
        },
        {
            "id": "m3",
            "icon": "🟢",
            "title": "카드뉴스(1) 예산 +20%",
            "reason": "ROAS 263% (손익분기 250 초과). CTR 1.8% (양호). 학습 완료.",
            "impact": "현재 일 5만원 → 6만원. 예상 매출 +₩1.2M/월.",
            "type": "INCREASE",
        },
        {
            "id": "m4",
            "icon": "🟡",
            "title": "신규 캠페인 — 카드뉴스 A'' 변형",
            "reason": "(1)이 위너로 검증됨. 후킹만 다른 변형으로 새 학습 가설 권장.",
            "impact": "—",
            "type": "CREATE",
        },
    ]


def naver_campaigns():
    rows = [
        # id, name, type, daily_budget, spend, impressions, clicks, ctr, conv, cvr, status, diag
        ("nc1", "루디언트_PDRN", "파워링크", 30000, 78000, 11200, 198, 1.77, 12, 6.06, "유지", "🟢"),
        ("nc2", "루디언트_시즌_재생", "파워링크", 25000, 32000, 5800, 105, 1.81, 4, 3.81, "관찰", "🟡"),
        ("nc3", "루디언트_안티에이징", "파워링크", 15000, 12438, 1600, 31, 1.94, 1, 3.23, "OFF 권장", "🔴"),
    ]
    cols = ["id", "name", "type", "daily_budget", "spend", "impressions",
            "clicks", "ctr", "conversions", "cvr", "status", "diag_color"]
    df = pd.DataFrame(rows, columns=cols)
    df.insert(0, "active", True)
    return df


def naver_adgroups():
    rows = [
        # campaign_id, name, default_bid, spend, impressions, clicks, ctr, conv, cvr, status, diag
        ("nc1", "PDRN_핵심", 1300, 52000, 7200, 138, 1.92, 9, 6.52, "증액 권장", "🟢"),
        ("nc1", "시술후_롱테일", 800, 26000, 4000, 60, 1.50, 3, 5.00, "유지", "🟢"),
        ("nc2", "재생크림_빅", 2200, 24000, 4200, 71, 1.69, 2, 2.82, "관찰", "🟡"),
        ("nc2", "재생크림_롱테일", 1100, 8000, 1600, 34, 2.13, 2, 5.88, "유지", "🟢"),
        ("nc3", "안티에이징_빅", 1900, 10000, 1100, 13, 1.18, 0, 0, "OFF 권장", "🔴"),
        ("nc3", "주름개선_확장", 2500, 2438, 500, 18, 3.60, 1, 5.56, "관찰", "🟡"),
    ]
    cols = ["campaign_id", "name", "default_bid", "spend", "impressions",
            "clicks", "ctr", "conversions", "cvr", "status", "diag_color"]
    df = pd.DataFrame(rows, columns=cols)
    df.insert(0, "active", True)
    df.insert(0, "id", [f"nag-mock-{i:03d}" for i in range(len(df))])
    return df


def naver_timeseries():
    days = pd.date_range(end=datetime.now(), periods=30, freq="D")
    import numpy as np
    np.random.seed(11)
    return pd.DataFrame({
        "date": days,
        "노출": np.random.normal(2700, 600, 30).clip(1000),
        "클릭": np.random.normal(48, 12, 30).clip(15),
        "전환": np.random.normal(2.4, 0.9, 30).clip(0),
        "광고비": np.random.normal(17500, 3500, 30).clip(5000),
    })


def naver_kpi():
    return {
        "노출": 18_600,
        "클릭": 334,
        "전환": 17,
        "ctr": 1.80,
        "cvr": 5.09,
        "비즈머니_잔액": 557_780,
        "광고비_7일": 122_438,
        "노출_증감": 8.2,
        "클릭_증감": 12.1,
        "전환_증감": 41.7,
    }


def naver_keywords():
    """Mock 키워드 데이터. 실데이터에는 nccKeywordId 포함됨."""
    rows = [
        ("PDRN 크림", "구문", 1500, 8000, 4200, 84, 2.0, 5, 5.95, 2.8, 5, "유지", "🟢"),
        ("시술 후 크림", "구문", 800, 3000, 1800, 38, 2.1, 4, 10.5, 1.5, 6, "증액 권장", "🟢"),
        ("재생 크림", "확장", 2200, 50000, 9500, 142, 1.5, 5, 3.5, 4.2, 4, "관찰", "🟡"),
        ("안티에이징 크림", "구문", 1800, 22000, 2800, 24, 0.86, 1, 4.17, 5.8, 3, "OFF 권장", "🔴"),
        ("주름 개선 크림", "확장", 2500, 35000, 1200, 8, 0.67, 0, 0, 6.4, 2, "OFF 권장", "🔴"),
        ("PDRN 효과", "구문", 900, 6500, 2100, 52, 2.48, 3, 5.77, 1.9, 6, "유지", "🟢"),
        ("피부 진정 크림", "확장", 1300, 18000, 3400, 41, 1.21, 2, 4.88, 4.5, 4, "관찰", "🟡"),
        ("레이저 후 진정", "구문", 700, 3200, 980, 28, 2.86, 3, 10.71, 1.2, 6, "증액 권장", "🟢"),
        ("색소침착 케어", "확장", 1600, 14000, 1800, 22, 1.22, 1, 4.55, 5.1, 3, "관찰", "🟡"),
        ("탄력 앰플", "구문", 1100, 4800, 1450, 31, 2.14, 2, 6.45, 2.4, 5, "유지", "🟢"),
        ("기미 케어", "확장", 1900, 28000, 2100, 18, 0.86, 0, 0, 6.2, 2, "OFF 권장", "🔴"),
        ("모공 앰플", "구문", 1400, 15000, 2600, 35, 1.35, 2, 5.71, 3.8, 4, "관찰", "🟡"),
        ("센텔라 크림", "확장", 1200, 12000, 1900, 28, 1.47, 1, 3.57, 4.3, 4, "관찰", "🟡"),
        ("히알루론산 앰플", "확장", 1500, 19000, 2200, 26, 1.18, 1, 3.85, 5.2, 3, "관찰", "🟡"),
        ("보습 크림", "확장", 2100, 80000, 1800, 12, 0.67, 0, 0, 7.1, 2, "OFF 권장", "🔴"),
        ("비타민C 앰플", "구문", 1700, 24000, 2400, 32, 1.33, 2, 6.25, 4.0, 4, "관찰", "🟡"),
        ("나이아신아마이드", "확장", 1300, 9500, 1100, 18, 1.64, 1, 5.56, 3.5, 4, "관찰", "🟡"),
        ("PDRN 토너", "구문", 850, 2200, 720, 15, 2.08, 1, 6.67, 2.0, 5, "유지", "🟢"),
        ("재생 마스크팩", "확장", 1400, 11000, 1300, 17, 1.31, 1, 5.88, 4.8, 3, "관찰", "🟡"),
        ("피부 결 개선", "확장", 1100, 7800, 940, 11, 1.17, 0, 0, 5.5, 3, "OFF 권장", "🔴"),
    ]
    cols = ["keyword", "match", "bid", "monthly_search", "impressions", "clicks",
            "ctr", "purchases", "cvr", "rank_avg", "quality", "status", "diag_color"]
    df = pd.DataFrame(rows, columns=cols)
    df.insert(0, "active", True)
    df.insert(0, "id", [f"nkw-mock-{i:03d}" for i in range(len(df))])
    return df


def naver_keyword_opportunity():
    """검색량은 높은데 우리가 안 잡는 키워드."""
    return pd.DataFrame([
        {"keyword": "여드름 흉터 크림", "monthly_search": 12000, "예상_cpc": 1400, "competitive": "중", "score": 8.5},
        {"keyword": "PDRN 효과", "monthly_search": 6500, "예상_cpc": 900, "competitive": "낮음", "score": 9.1},
        {"keyword": "레이저 후 진정", "monthly_search": 3200, "예상_cpc": 700, "competitive": "낮음", "score": 8.8},
        {"keyword": "탄력 앰플", "monthly_search": 4800, "예상_cpc": 1100, "competitive": "중", "score": 7.2},
        {"keyword": "시술 후 진정 크림", "monthly_search": 2800, "예상_cpc": 800, "competitive": "낮음", "score": 8.3},
    ])


def naver_search_trend():
    """데이터랩 스타일 검색 트렌드 (상대 지수)."""
    days = pd.date_range(end=datetime.now(), periods=90, freq="D")
    import numpy as np
    np.random.seed(7)
    base = np.linspace(40, 70, 90) + np.random.normal(0, 8, 90)
    return pd.DataFrame({
        "date": days,
        "PDRN 크림": base.clip(20, 100),
        "재생 크림": (base * 0.8 + np.random.normal(0, 5, 90)).clip(20, 100),
        "시술 후 크림": (base * 0.4 + np.random.normal(0, 3, 90)).clip(10, 100),
    })


def naver_actions():
    return [
        {
            "id": "n1",
            "icon": "🟢",
            "title": "\"시술 후 크림\" 입찰가 800→1100",
            "reason": "현재 1.5등 노출. CVR 10.5%로 압도적. 입찰가 ↑로 1등 점령 시 매출 +60% 예상.",
            "impact": "월 광고비 +₩50K, 예상 매출 +₩400K.",
            "type": "BID_UP",
        },
        {
            "id": "n2",
            "icon": "🔴",
            "title": "\"주름 개선 크림\" OFF",
            "reason": "8주 운영 중 전환 0건. CTR 0.67% (시장 평균 1.5%). 품질지수 2단계.",
            "impact": "월 ₩60K 광고비 절감.",
            "type": "OFF",
        },
        {
            "id": "n3",
            "icon": "🟡",
            "title": "신규 키워드 5개 추가",
            "reason": "검색량 ↑ + 우리 USP 매칭 + CPC 저렴. 특히 \"PDRN 효과\" 9.1점.",
            "impact": "예상 신규 매출 ₩600K~1.2M/월.",
            "type": "ADD_KEYWORDS",
        },
        {
            "id": "n4",
            "icon": "🟢",
            "title": "\"PDRN 크림\" 품질지수 개선",
            "reason": "현재 5단계. 광고 제목·랜딩에 PDRN 키워드 강화 시 6단계 가능 → 같은 입찰가로 1등.",
            "impact": "CPC 1500→1100원 (-27%) 추정.",
            "type": "QUALITY_UP",
        },
    ]


def search_query_report():
    """검색어 보고서 Mock — 우리 키워드 → 실제 노출된 사용자 검색어."""
    rows = [
        # (우리 키워드, 실제 검색어, 노출, 클릭, 구매, 광고비, 광고그룹ID)
        ("PDRN 크림", "PDRN 크림 효과", 234, 8, 1, 9_600, "ag_mock_1"),
        ("PDRN 크림", "PDRN 크림 가격", 156, 12, 0, 14_400, "ag_mock_1"),
        ("PDRN 크림", "PDRN 크림 추천", 89, 3, 0, 3_600, "ag_mock_1"),
        ("PDRN 크림", "PDRN 크림 무료배송", 42, 5, 0, 6_000, "ag_mock_1"),
        ("PDRN 크림", "PDRN 크림 사용법", 38, 2, 0, 2_400, "ag_mock_1"),
        ("PDRN 크림", "PDRN 크림 후기", 71, 6, 1, 7_200, "ag_mock_1"),
        ("PDRN 크림", "PDRN 크림 부작용", 28, 1, 0, 1_200, "ag_mock_1"),
        ("재생 크림", "재생 크림 추천 더마", 178, 15, 2, 33_000, "ag_mock_2"),
        ("재생 크림", "재생 크림 비교", 92, 3, 0, 6_600, "ag_mock_2"),
        ("재생 크림", "재생 크림 무료배송", 65, 8, 0, 17_600, "ag_mock_2"),
        ("재생 크림", "재생 크림 30대", 54, 4, 1, 8_800, "ag_mock_2"),
        ("재생 크림", "재생 크림 순위", 41, 2, 0, 4_400, "ag_mock_2"),
        ("시술 후 크림", "시술 후 크림 진정", 88, 9, 2, 7_200, "ag_mock_3"),
        ("시술 후 크림", "시술 후 크림 추천", 67, 5, 1, 4_000, "ag_mock_3"),
        ("시술 후 크림", "레이저 후 크림", 52, 7, 1, 5_600, "ag_mock_3"),
        ("시술 후 크림", "필러 후 크림", 31, 2, 0, 1_600, "ag_mock_3"),
        ("안티에이징 크림", "안티에이징 크림 추천", 124, 4, 0, 7_200, "ag_mock_4"),
        ("안티에이징 크림", "40대 안티에이징", 88, 2, 0, 3_600, "ag_mock_4"),
        ("안티에이징 크림", "안티에이징 크림 비교", 56, 1, 0, 1_800, "ag_mock_4"),
        ("안티에이징 크림", "안티에이징 크림 50대", 42, 3, 1, 5_400, "ag_mock_4"),
        ("모공 앰플", "모공 앰플 추천", 76, 6, 1, 6_600, "ag_mock_5"),
        ("모공 앰플", "모공 줄이는법", 92, 4, 0, 4_400, "ag_mock_5"),
        ("모공 앰플", "모공 앰플 효과", 58, 3, 0, 3_300, "ag_mock_5"),
        ("모공 앰플", "코 모공 앰플", 45, 2, 0, 2_200, "ag_mock_5"),
    ]

    def _diagnose(imp, clk, purchases, spend):
        """판정 로직."""
        if clk == 0:
            return "관찰", "🟡 노출만"
        cvr = (purchases / clk * 100) if clk else 0
        cpa = (spend / purchases) if purchases else None
        if purchases >= 1 and cvr >= 5:
            return "신규 등록 권장", "🟢"
        if purchases == 0 and clk >= 5 and spend >= 5000:
            return "노출 제외 권장", "🔴"
        if purchases >= 1:
            return "관찰", "🟢"
        return "관찰", "🟡"

    out = []
    for our_kw, query, imp, clk, purchases, spend, agid in rows:
        ctr = (clk / imp * 100) if imp else 0
        cvr = (purchases / clk * 100) if clk else 0
        cpa = (spend / purchases) if purchases else None
        status, color = _diagnose(imp, clk, purchases, spend)
        out.append({
            "our_keyword": our_kw,
            "search_query": query,
            "adgroup_id": agid,
            "impressions": imp,
            "clicks": clk,
            "ctr": ctr,
            "purchases": purchases,
            "cvr": cvr,
            "spend": spend,
            "cpa": cpa,
            "status": status,
            "diag_color": color,
        })

    df = pd.DataFrame(out)
    # 효율 좋은 검색어 우선 (구매 > 클릭 > 노출 순)
    return df.sort_values(
        ["purchases", "clicks", "impressions"], ascending=[False, False, False]
    ).reset_index(drop=True)


def keyword_research(hint_keywords):
    """키워드 도구 Mock — 더마/스킨케어 가상 데이터."""
    if isinstance(hint_keywords, str):
        hints = [k.strip() for k in hint_keywords.split(",") if k.strip()]
    else:
        hints = list(hint_keywords)

    base = {
        "PDRN": (12000, 35000, "🟢 낮음", "🟢 우리에게 유리 (롱테일)"),
        "PDRN 크림": (8000, 24000, "🟡 중간", "🟢 우리에게 유리 (롱테일)"),
        "PDRN 효과": (3500, 12000, "🟢 낮음", "🟢 우리에게 유리 (롱테일)"),
        "PDRN 부작용": (1200, 4500, "🟢 낮음", "🟢 우리에게 유리 (롱테일)"),
        "재생 크림": (15000, 42000, "🔴 높음", "🔴 빅키워드 (대기업과 경쟁)"),
        "안티에이징 크림": (8500, 28000, "🔴 높음", "🔴 빅키워드 (대기업과 경쟁)"),
        "시술 후 크림": (2200, 8500, "🟢 낮음", "🟢 우리에게 유리 (롱테일)"),
        "기미 크림": (12000, 38000, "🔴 높음", "🔴 빅키워드"),
        "모공 앰플": (4500, 16000, "🟡 중간", "🟡 검토 가치"),
        "주름 개선": (18000, 55000, "🔴 높음", "🔴 빅키워드"),
        "센텔라 크림": (3200, 9800, "🟡 중간", "🟡 검토 가치"),
        "비타민C 앰플": (5500, 18000, "🟡 중간", "🟡 검토 가치"),
    }

    rows = []
    seen = set()

    # 입력 키워드 우선
    for h in hints:
        if h in seen:
            continue
        seen.add(h)
        if h in base:
            pc, mo, comp, attr = base[h]
        else:
            pc, mo, comp, attr = (1000, 3000, "🟡 중간", "🟡 검토 가치")
        total = pc + mo
        rows.append({
            "keyword": h,
            "monthly_pc": pc,
            "monthly_mo": mo,
            "monthly_total": total,
            "mobile_ratio": (mo / total * 100) if total else 0,
            "avg_pc_clicks": int(pc * 0.015),
            "avg_mo_clicks": int(mo * 0.012),
            "competition": comp,
            "avg_rank": 3.5,
            "attractiveness": attr,
        })

    # 연관 키워드 추가 (입력에 없는 것)
    for k, (pc, mo, comp, attr) in base.items():
        if k in seen:
            continue
        # 입력 키워드와 연관 있는 것만 (대충 hint의 일부 포함)
        if any(h in k or k in h for h in hints):
            total = pc + mo
            rows.append({
                "keyword": k,
                "monthly_pc": pc,
                "monthly_mo": mo,
                "monthly_total": total,
                "mobile_ratio": (mo / total * 100) if total else 0,
                "avg_pc_clicks": int(pc * 0.015),
                "avg_mo_clicks": int(mo * 0.012),
                "competition": comp,
                "avg_rank": 4.2,
                "attractiveness": attr,
            })

    df = pd.DataFrame(rows)
    if df.empty:
        return df
    return df.sort_values("monthly_total", ascending=False).reset_index(drop=True)


def naver_time_heatmap():
    """요일×시간 ROAS·노출 mock heatmap."""
    import numpy as np
    np.random.seed(42)

    days = ["월", "화", "수", "목", "금", "토", "일"]
    hours = list(range(24))

    # 노출 패턴 (낮은 새벽, 높은 저녁)
    base_imp = np.array([20, 10, 5, 5, 5, 10, 30, 80, 120, 140, 150, 160,
                         180, 200, 180, 160, 180, 220, 280, 320, 280, 200, 120, 60])
    impressions = []
    for d in range(7):
        # 평일 더 높음, 주말 살짝 다른 패턴
        mult = 1.0 if d < 5 else 1.1
        row = (base_imp * mult * np.random.uniform(0.85, 1.15, 24)).astype(int)
        impressions.append(row)

    # ROAS 패턴 (구매 시간대: 점심+저녁 높음)
    base_roas = np.array([180, 150, 120, 100, 100, 120, 200, 260, 320, 380, 420, 400,
                          360, 320, 300, 320, 360, 400, 440, 480, 460, 380, 280, 220])
    roas = []
    for d in range(7):
        mult = 1.0 if d < 5 else 1.05
        row = (base_roas * mult * np.random.uniform(0.9, 1.1, 24)).astype(int)
        roas.append(row)

    return {
        "impressions": pd.DataFrame(impressions, index=days, columns=hours),
        "roas": pd.DataFrame(roas, index=days, columns=hours),
    }


def serp_competitors(keyword="PDRN 크림"):
    return pd.DataFrame([
        {"rank": 1, "advertiser": "닥터지", "headline": "PDRN 재생 앰플 - 8주 임상시험 결과", "description": "피부과 임상으로 입증된 효과. 첫 구매 30% 할인", "url": "drg.co.kr", "is_us": False},
        {"rank": 2, "advertiser": "Ludient", "headline": "Ludient PDRN 크림 - 시술 후 케어", "description": "피부과 시술 후 진정에 도움. 구매 후기 1,200건+", "url": "ludient.co.kr", "is_us": True},
        {"rank": 3, "advertiser": "셀퓨전씨", "headline": "PDRN 함유 안티에이징 크림", "description": "주름 개선 + 탄력 부여. 50대 여성 만족도 92%", "url": "cellfusionc.com", "is_us": False},
        {"rank": 4, "advertiser": "리얼베리어", "headline": "민감 피부 PDRN 케어", "description": "저자극 처방 + EWG 그린 등급. 무료 샘플 신청", "url": "realbarrier.com", "is_us": False},
        {"rank": 5, "advertiser": "메디큐브", "headline": "PDRN 부스터 앰플 신제품", "description": "5월 한정 1+1 이벤트. 파우치 무료 증정", "url": "medicube.co.kr", "is_us": False},
    ])
