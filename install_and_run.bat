@echo off
REM Lululab 광고 운영 대시보드 - Windows 원클릭 설치 및 실행
REM 사용법: 이 파일을 더블클릭

cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python이 설치되어 있지 않습니다.
    echo.
    echo 1. https://www.python.org/downloads/ 접속
    echo 2. "Download Python 3.x" 클릭
    echo 3. 설치 시 "Add Python to PATH" 반드시 체크
    echo 4. 설치 후 이 파일 다시 더블클릭
    echo.
    pause
    exit /b 1
)

if not exist venv (
    echo [1/3] 가상환경 생성 중...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] 가상환경 생성 실패
        pause
        exit /b 1
    )
)

echo [2/3] 의존성 설치 중 (처음 1~2분 소요)...
call venv\Scripts\pip.exe install --quiet --upgrade pip
call venv\Scripts\pip.exe install --quiet -r requirements.txt
if errorlevel 1 (
    echo [ERROR] 패키지 설치 실패
    pause
    exit /b 1
)

echo [3/3] 대시보드 실행 - 브라우저가 자동으로 열립니다
echo 종료하려면 이 창을 닫으세요
echo.
call venv\Scripts\streamlit.exe run app.py

pause
