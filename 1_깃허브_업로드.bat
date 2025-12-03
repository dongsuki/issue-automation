@echo off
chcp 65001 >nul
echo ====================================
echo GitHub 업로드 - dongsuki/issue-automation
echo ====================================
echo.

cd /d "%~dp0"

echo [1/6] Git 초기화...
git init

echo.
echo [2/6] 원격 저장소 연결...
git remote add origin https://github.com/dongsuki/issue-automation.git

echo.
echo [3/6] 파일 추가...
git add .

echo.
echo [4/6] 커밋 생성...
git commit -m "Initial commit: 오늘의 급등이슈 자동화"

echo.
echo [5/6] 브랜치 이름 변경...
git branch -M main

echo.
echo [6/6] GitHub에 업로드...
git push -u origin main

echo.
echo ====================================
echo 업로드 완료!
echo ====================================
echo.
echo GitHub에서 확인: https://github.com/dongsuki/issue-automation
echo.
echo ⚠️  다음 단계:
echo 1. GitHub 사이트 접속
echo 2. Settings ^> Secrets and variables ^> Actions
echo 3. New repository secret 클릭
echo 4. Name: SERVICE_ACCOUNT_KEY
echo 5. Value: service_account.json.json 파일 내용 전체 복사/붙여넣기
echo 6. Add secret 클릭
echo.
pause

