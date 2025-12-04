@echo off
chcp 65001 >nul
echo ====================================
echo GitHub 업데이트 및 업로드
echo ====================================
echo.

cd /d "%~dp0"

echo [1/5] 현재 상태 확인...
git status

echo.
echo [2/5] 모든 변경사항 추가...
git add .

echo.
echo [3/5] 커밋 생성...
git commit -m "feat: 등락률 상위 시스템 추가 및 GitHub Actions 설정"

echo.
echo [4/5] 원격 저장소 확인...
git remote -v

echo.
echo [5/5] GitHub에 푸시...
git push origin main

echo.
echo ====================================
echo 업로드 완료!
echo ====================================
echo.
echo 다음 단계:
echo 1. GitHub에서 확인: https://github.com/dongsuki/issue-automation
echo 2. Settings → Secrets → Actions에서 GOOGLE_CREDENTIALS 설정
echo 3. Actions 탭에서 워크플로우 실행
echo.
pause

