@echo off
chcp 65001 >nul
echo ====================================
echo GitHub 업로드 준비
echo ====================================
echo.

cd /d "%~dp0"

echo [1/4] Git 초기화...
git init

echo.
echo [2/4] 모든 파일 추가 (.gitignore 적용)...
git add .

echo.
echo [3/4] 첫 커밋 생성...
git commit -m "Initial commit: 오늘의 급등이슈 자동화"

echo.
echo ====================================
echo 준비 완료!
echo ====================================
echo.
echo 다음 단계:
echo 1. GitHub에 로그인 (https://github.com)
echo 2. 새 레포지토리 생성 (New Repository)
echo 3. 아래 명령어 실행:
echo.
echo    git remote add origin https://github.com/[사용자명]/[레포지토리명].git
echo    git branch -M main
echo    git push -u origin main
echo.
echo ⚠️  주의: service_account.json.json 파일이 업로드되지 않았는지 확인!
echo.
pause

