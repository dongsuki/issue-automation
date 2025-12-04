# 🚀 GitHub에서 자동 실행하는 방법

GitHub Actions를 사용하면 **설치 없이 깃허브에서 바로 실행**할 수 있습니다!

## 📋 목차
1. [초기 설정](#초기-설정)
2. [수동 실행](#수동-실행)
3. [자동 실행 (예약)](#자동-실행-예약)
4. [생성된 이미지 다운로드](#생성된-이미지-다운로드)

---

## 🔧 초기 설정

### 1단계: GitHub 레포지토리 생성

1. GitHub에 로그인 (https://github.com)
2. **New Repository** 클릭
3. 레포지토리 이름 입력 (예: `stock-issue-automation`)
4. **Private** 선택 (보안을 위해)
5. **Create repository** 클릭

### 2단계: 코드 업로드

**방법 A: 배치 파일 사용 (Windows)**
```bash
# 1. 깃허브_업로드.bat 더블클릭
# 2. 안내에 따라 명령어 입력:

git remote add origin https://github.com/[사용자명]/[레포지토리명].git
git branch -M main
git push -u origin main
```

**방법 B: 수동 업로드**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/[사용자명]/[레포지토리명].git
git branch -M main
git push -u origin main
```

### 3단계: 구글 API 키 설정 (중요! 🔐)

1. **구글 서비스 계정 JSON 파일** 내용 복사
   - `service_account.json.json` 파일 열기
   - 전체 내용 복사

2. **GitHub Secrets 등록**
   - GitHub 레포지토리 → **Settings** 탭
   - 왼쪽 메뉴에서 **Secrets and variables** → **Actions**
   - **New repository secret** 클릭
   - Name: `GOOGLE_CREDENTIALS`
   - Value: 복사한 JSON 내용 붙여넣기
   - **Add secret** 클릭

---

## ▶️ 수동 실행

### 급등이슈 생성

1. GitHub 레포지토리 → **Actions** 탭
2. 왼쪽에서 **"급등이슈 카드 자동 생성"** 선택
3. **Run workflow** 버튼 클릭
4. **Run workflow** 재확인
5. 완료될 때까지 대기 (약 1~2분)

### 등락률 상위 생성

1. GitHub 레포지토리 → **Actions** 탭
2. 왼쪽에서 **"등락률 상위 자동 생성"** 선택
3. **Run workflow** 버튼 클릭
4. **Run workflow** 재확인
5. 완료될 때까지 대기 (약 1~2분)

---

## ⏰ 자동 실행 (예약) - 현재 비활성화

**현재는 수동 실행만 가능합니다!**

원할 때만 `Run workflow` 버튼을 눌러서 실행하세요.

### 자동 실행 활성화하려면?

워크플로우 파일에 스케줄 추가:

`.github/workflows/급등이슈_생성.yml` 파일 수정:

```yaml
on:
  workflow_dispatch:  # 수동 실행
  schedule:           # 이 부분 추가
    - cron: '0 9 * * 1-5'  # 월~금 오전 9시 (UTC) = 한국시간 오후 6시
```

**예시:**
```yaml
# 매일 오전 8시 (한국시간 오후 5시)
- cron: '0 8 * * *'

# 월~금 오전 10시 (한국시간 오후 7시)
- cron: '0 10 * * 1-5'

# 매일 오전 6시와 오후 3시 (한국시간 오후 3시, 자정)
- cron: '0 6,15 * * *'
```

**Cron 표현식 도구:** https://crontab.guru/

---

## 📥 생성된 이미지 다운로드

👉 **[다운로드_방법.md](다운로드_방법.md)** - 상세 가이드 (화면 예시 포함)

### 간단 요약

**방법 1: Artifacts (추천! ⭐)**
1. **Actions** 탭 → 완료된 워크플로우 클릭
2. 하단 **Artifacts** 섹션에서 ZIP 다운로드
3. 압축 해제
- **보관 기간:** 30일

**방법 2: 레포지토리 (영구 보관 ⭐)**
1. 레포지토리 메인 페이지 → `output` 폴더
2. 생성된 이미지 파일 클릭
3. **Download** 버튼 클릭
- **보관 기간:** 영구

> 💡 **팁:** 두 방법 모두 자동으로 설정되어 있습니다!  
> Artifacts는 30일 후 삭제, output 폴더는 영구 보관됩니다.

---

## 🔍 문제 해결

### "Error: GOOGLE_CREDENTIALS not found"
- GitHub Secrets에 `GOOGLE_CREDENTIALS`가 제대로 등록되었는지 확인
- Secret 이름이 정확한지 확인 (대소문자 구분)

### "Error: No data found"
- 구글 시트에 데이터가 있는지 확인
- 서비스 계정에 시트 공유가 되어 있는지 확인

### 워크플로우가 실행되지 않음
- **Actions** 탭에서 워크플로우가 활성화되어 있는지 확인
- GitHub의 Actions 실행 권한 확인
  - Settings → Actions → General → **Allow all actions**

### 이미지가 생성되지 않음
- **Actions** 탭에서 실행 로그 확인
- 빨간색 에러 메시지 확인

---

## 💡 추가 팁

### 1. 알림 받기
- GitHub → Settings → Notifications
- Actions 실패 시 이메일 알림 설정 가능

### 2. 여러 시트 사용
워크플로우 파일을 복사해서 다른 스프레드시트용으로 사용 가능

### 3. 보안 강화
- 레포지토리를 **Private**으로 유지
- `service_account.json.json` 파일은 절대 업로드 금지
- `.gitignore`에 포함되어 있는지 확인

---

## 📞 도움말

문제가 있으면 GitHub Issues에 질문을 남겨주세요!

**유용한 링크:**
- [GitHub Actions 문서](https://docs.github.com/en/actions)
- [Cron 스케줄러](https://crontab.guru/)
- [Google Sheets API](https://developers.google.com/sheets/api)

