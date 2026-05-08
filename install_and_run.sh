#!/bin/bash
# Lululab 광고 운영 대시보드 — 원클릭 설치 + 실행
# 사용법: 터미널에서 ./install_and_run.sh

set -e
cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
  echo "▶ 가상환경 생성 중..."
  python3 -m venv venv
fi

echo "▶ 의존성 설치 중 (처음 1~2분 소요)..."
./venv/bin/pip install --quiet --upgrade pip
./venv/bin/pip install --quiet -r requirements.txt

echo "▶ 대시보드 실행 — 브라우저가 자동으로 열립니다"
echo "▶ 종료하려면 Ctrl+C"
./venv/bin/streamlit run app.py
