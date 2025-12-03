# 🔧 상세 설정 가이드

## 1. 구글 API 서비스 계정 생성

### 1단계: Google Cloud Console 접속
1. https://console.cloud.google.com/ 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택

### 2단계: Google Sheets API 활성화
1. 좌측 메뉴 → "API 및 서비스" → "라이브러리"
2. "Google Sheets API" 검색
3. "사용 설정" 클릭

### 3단계: 서비스 계정 생성
1. 좌측 메뉴 → "API 및 서비스" → "사용자 인증 정보"
2. "사용자 인증 정보 만들기" → "서비스 계정"
3. 서비스 계정 이름 입력 (예: "issue-automation")
4. "만들기 및 계속하기" 클릭
5. 역할 선택 (기본값으로 둬도 됨)
6. "완료" 클릭

### 4단계: JSON 키 다운로드
1. 생성된 서비스 계정 클릭
2. "키" 탭 이동
3. "키 추가" → "새 키 만들기"
4. JSON 선택 → "만들기"
5. 다운로드된 JSON 파일을 `service_account.json.json` 이름으로 변경
6. 프로젝트 폴더에 저장

### 5단계: 구글 시트 공유
1. 구글 시트 열기
2. 우측 상단 "공유" 클릭
3. 서비스 계정 이메일 입력 (JSON 파일의 `client_email` 값)
   - 예: `issue-automation@your-project.iam.gserviceaccount.com`
4. "편집자" 권한으로 공유

## 2. 구글 시트 설정

### 시트 ID 확인
구글 시트 URL에서 ID 추출:
```
https://docs.google.com/spreadsheets/d/[이 부분이 SHEET_ID]/edit
```

### main.py에 시트 ID 입력
`main.py` 파일 열기 → 31번째 줄 수정:
```python
SPREADSHEET_ID = "여기에_시트_ID_입력"
```

## 3. GitHub 업로드

### 방법 1: 배치 파일 사용 (Windows)
```bash
깃허브_업로드.bat 더블클릭
```

### 방법 2: 수동 업로드

#### 3-1. Git 초기화
```bash
cd "C:\Users\USER\Desktop\issue automation"
git init
git add .
git commit -m "Initial commit: 오늘의 급등이슈 자동화"
```

#### 3-2. GitHub 레포지토리 생성
1. https://github.com 접속
2. 우측 상단 "+" → "New repository"
3. Repository name: `issue-automation` (원하는 이름)
4. Public 또는 Private 선택
5. "Create repository" 클릭

#### 3-3. 레포지토리 연결 및 업로드
GitHub에 표시된 명령어 실행:
```bash
git remote add origin https://github.com/[사용자명]/[레포지토리명].git
git branch -M main
git push -u origin main
```

## 4. 다른 컴퓨터에서 사용

### 클론 및 설정
```bash
# 레포지토리 클론
git clone https://github.com/[사용자명]/[레포지토리명].git
cd [레포지토리명]

# 라이브러리 설치
pip install -r requirements.txt
python -m playwright install chromium

# 서비스 계정 키 추가
# service_account.json.json 파일을 수동으로 복사
```

## 5. 보안 주의사항

### ⚠️ 절대 업로드하면 안되는 파일
- `service_account.json.json` (구글 API 인증키)
- `output/*.png` (개인 데이터가 담긴 이미지)

### ✅ 업로드 전 확인
```bash
git status
```
위 명령어 실행 시 `service_account.json.json`이 보이면 안됨!

### 🔒 이미 업로드한 경우
1. GitHub 레포지토리에서 파일 삭제
2. 구글 API 콘솔에서 해당 서비스 계정 삭제
3. 새 서비스 계정 생성 및 키 재발급

## 6. 자주 묻는 질문

### Q: Private 레포지토리로 해야 하나요?
A: `service_account.json.json`만 업로드 안하면 Public도 괜찮습니다. 하지만 시트 ID는 노출되므로 Private 권장.

### Q: 협업하려면?
A: GitHub 레포지토리에 Collaborator 추가 후, 각자 `service_account.json.json` 파일 공유 (암호화된 채널 사용)

### Q: 코드 수정 후 재업로드?
```bash
git add .
git commit -m "수정 내용 설명"
git push
```

