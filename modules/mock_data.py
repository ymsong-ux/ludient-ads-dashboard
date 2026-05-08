"""실제 API 연결 전 시연용 가짜 데이터."""

from datetime import datetime, timedelta
import pandas as pd


def meta_kpi():
    return {
        "광고비_30일": 1_809_241,
        "매출_30일": 4_491_000,
        "roas": 248,
        "cpa": 98_460,
        "신규고객": 18,
        "광고비_증감": 12.3,
        "매출_증감": 18.5,
        "roas_증감": 15,
        "cpa_증감": -5.2,
        "신규고객_증감": 3,
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


def serp_competitors(keyword="PDRN 크림"):
    return pd.DataFrame([
        {"rank": 1, "advertiser": "닥터지", "headline": "PDRN 재생 앰플 - 8주 임상시험 결과", "description": "피부과 임상으로 입증된 효과. 첫 구매 30% 할인", "url": "drg.co.kr", "is_us": False},
        {"rank": 2, "advertiser": "Ludient", "headline": "Ludient PDRN 크림 - 시술 후 케어", "description": "피부과 시술 후 진정에 도움. 구매 후기 1,200건+", "url": "ludient.co.kr", "is_us": True},
        {"rank": 3, "advertiser": "셀퓨전씨", "headline": "PDRN 함유 안티에이징 크림", "description": "주름 개선 + 탄력 부여. 50대 여성 만족도 92%", "url": "cellfusionc.com", "is_us": False},
        {"rank": 4, "advertiser": "리얼베리어", "headline": "민감 피부 PDRN 케어", "description": "저자극 처방 + EWG 그린 등급. 무료 샘플 신청", "url": "realbarrier.com", "is_us": False},
        {"rank": 5, "advertiser": "메디큐브", "headline": "PDRN 부스터 앰플 신제품", "description": "5월 한정 1+1 이벤트. 파우치 무료 증정", "url": "medicube.co.kr", "is_us": False},
    ])
