# Lululab 광고 운영 대시보드

자사 Meta + Naver 광고 운영 의사결정 도구. 시연용 골격 (Mock 데이터 기반).

## 시연 실행 방법

### 1. Streamlit 설치 (한 번만)
```bash
pip3 install -r requirements.txt
```

### 2. 실행
```bash
cd "/Users/youngmin/Desktop/국내마케팅공부/dashboard"
streamlit run app.py
```

자동으로 브라우저에 `http://localhost:8501` 열림.

### 3. 시연 시나리오 (미팅용)

1. **Meta 탭** 보여주며:
   - 5개 KPI 카드 (광고비·매출·ROAS·CPA·신규고객)
   - 캠페인 테이블 — 진단 색상(🟢🟡🔴) + ON/OFF 토글
   - 우측 사이드바 — 오늘 추천 액션 4개 (근거 보기 → 실행/무시)
   - 시계열 차트 (광고비·매출, ROAS·CTR 탭)

2. **Naver 탭** 보여주며:
   - 6개 KPI 카드
   - 키워드 테이블 (입찰가 슬라이더는 추후)
   - 신규 키워드 기회 (검색량 ↑ + 미입찰)
   - 검색 트렌드 (데이터랩 90일)
   - SERP 경쟁사 모니터링 (자사 강조)
   - 우측 — 오늘 추천 액션

3. **통합 탭**:
   - 채널 비중·채널별 ROAS

4. **리포트 탭**:
   - 기간·지표·캠페인 선택 → Excel/PDF/CSV 다운로드

## 구조

```
dashboard/
├── app.py                  # 메인 진입점
├── modules/
│   ├── mock_data.py        # 시연용 가짜 데이터
│   ├── api_clients.py      # (TODO) Meta·Naver API 클라이언트
│   ├── diagnosis.py        # (TODO) 진단 엔진
│   └── actions.py          # (TODO) 액션 실행
├── requirements.txt
└── README.md
```

## 다음 단계 (Phased)

| Phase | 내용 |
|---|---|
| ✅ 0. 시연 골격 (Mock) | 현재 |
| ⏭️ 1. Meta API 연결 (읽기) | 토큰 발급 후 |
| 2. Naver API 연결 (읽기) | API Key 발급 후 |
| 3. 진단 엔진 구현 | PDF 진단 트리 코드화 |
| 4. 액션 실행 (ON/OFF, 입찰) | API 쓰기 권한 |
| 5. SERP 크롤링 | BrightData/Firecrawl 통합 |
| 6. 자연어 질문 (Claude API) | 선택 |

## 사내 배포 (Phase 1 이후)

### 옵션 A — 회사 서버 + Docker
```bash
# Dockerfile 작성 후
docker build -t lululab-ads-dashboard .
docker run -p 8501:8501 lululab-ads-dashboard
```
사내망에서만 접근 가능. 가장 안전.

### 옵션 B — Streamlit Cloud Teams
- https://streamlit.io/cloud
- $20/user/월
- 비밀번호 보호 + GitHub 연동
- 가장 쉬움

### 옵션 C — Railway / Fly.io
- 빠른 클라우드 배포
- 도메인·HTTPS 자동
- 월 $5~20
