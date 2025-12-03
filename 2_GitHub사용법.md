# 🚀 GitHub Actions 사용법

## 📤 업로드 방법

### 1단계: GitHub에 업로드
```
"1_깃허브_업로드.bat" 파일을 더블클릭
```

처음 업로드 시 GitHub 로그인 요청이 나올 수 있습니다.

---

## 🔐 2단계: 보안키 등록 (최초 1회만)

GitHub Actions에서 구글 시트에 접근하려면 서비스 계정 키를 등록해야 합니다.

### 2-1. service_account.json.json 파일 열기
- 메모장으로 `service_account.json.json` 파일 열기
- 내용 전체 복사 (Ctrl+A → Ctrl+C)

### 2-2. GitHub Secrets 등록
1. https://github.com/dongsuki/issue-automation 접속
2. 상단 메뉴 `Settings` 클릭
3. 좌측 `Secrets and variables` → `Actions` 클릭
4. `New repository secret` 클릭
5. **Name**: `SERVICE_ACCOUNT_KEY`
6. **Secret**: 복사한 JSON 내용 붙여넣기
7. `Add secret` 클릭

---

## ▶️ 3단계: 수동 실행

### GitHub에서 실행하기
1. https://github.com/dongsuki/issue-automation 접속
2. 상단 메뉴 `Actions` 클릭
3. 좌측 `급등이슈 이미지 생성` 클릭
4. 우측 `Run workflow` 버튼 클릭
5. `Run workflow` 확인

### 실행 확인
- 실행 중: 🟡 노란색 점
- 성공: ✅ 초록색 체크
- 실패: ❌ 빨간색 X

### 생성된 이미지 다운로드
1. 완료된 워크플로우 클릭
2. 하단 `Artifacts` 섹션
3. `급등이슈-이미지-XXX` 클릭하여 다운로드

---

## 📱 스마트폰에서도 실행 가능!

1. GitHub 앱 설치 (iOS/Android)
2. https://github.com/dongsuki/issue-automation 접속
3. Actions 탭 → Run workflow

언제 어디서든 구글 시트만 수정하고 GitHub에서 버튼만 누르면 이미지 생성! 🎉

---

## 🔄 코드 수정 후 재업로드

```bash
git add .
git commit -m "수정 내용"
git push
```

또는 `1_깃허브_업로드.bat` 다시 실행

---

## ❓ 문제 해결

### "remote origin already exists" 오류
```bash
git remote remove origin
git remote add origin https://github.com/dongsuki/issue-automation.git
```

### Actions 실행 실패
1. `SERVICE_ACCOUNT_KEY`가 제대로 등록되었는지 확인
2. 구글 시트가 서비스 계정과 공유되어 있는지 확인
3. Actions 탭에서 실패 로그 확인

### "playwright 오류"
GitHub Actions에서는 자동으로 Playwright 설치됨 (로컬과 다름)

