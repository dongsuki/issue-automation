# 📈 오늘의 급등이슈 자동화

구글 시트에 주식 데이터를 입력하면 자동으로 예쁜 이미지를 생성하는 프로그램입니다.

<img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/Google_Sheets-34A853?style=flat-square&logo=google-sheets&logoColor=white"/>
<img src="https://img.shields.io/badge/Playwright-2D3748?style=flat-square&logo=playwright&logoColor=white"/>

## ✨ 주요 기능

- ✅ **구글 시트 연동**: 시트에 데이터 입력 → 자동 이미지 생성
- ✅ **자동 그룹화**: 테마별 5개씩, 개별이슈 3개씩 자동 분리
- ✅ **반응형 디자인**: 종목 개수에 관계없이 일정한 카드 높이 유지
- ✅ **날짜 자동 인식**: 시트의 최신 날짜 자동 감지
- ✅ **멀티 페이지**: 카드가 많으면 자동으로 여러 페이지 생성

## 🚀 빠른 시작

### 방법 1: GitHub Actions로 실행 (추천! 🌟)

**설치 없이 GitHub에서 바로 실행 가능!**

1. 구글 시트에 데이터 입력
2. GitHub Actions 탭 → `Run workflow` 클릭
3. 생성된 이미지 다운로드

👉 **[GitHub 사용법 보기 (필독!)](GitHub_사용법.md)**

---

### 방법 2: 로컬 설치

#### 1. 설치

```bash
# 레포지토리 클론
git clone https://github.com/[YOUR_USERNAME]/issue-automation.git
cd issue-automation

# 필요한 라이브러리 설치
pip install -r requirements.txt

# Playwright 브라우저 설치
python -m playwright install chromium
```

#### 2. 구글 API 설정

1. [Google Cloud Console](https://console.cloud.google.com/)에서 프로젝트 생성
2. Google Sheets API 활성화
3. 서비스 계정 생성 및 JSON 키 다운로드
4. 다운로드한 JSON 키를 `service_account.json.json` 이름으로 프로젝트 폴더에 저장
5. 구글 시트를 서비스 계정 이메일과 공유

#### 3. 구글 시트 준비

시트에 아래 형식으로 데이터 입력:

| A열(날짜) | B열(타입) | C열(그룹명) | D열(종목명) | E열(등락률) | F열(이슈내용) |
|-----------|-----------|-------------|-------------|-------------|---------------|
| 12.04 | 테마 | 반도체 | 삼성전자 | 3.50% | 반도체 훈풍에 상승 |
| 12.04 | 테마 | 반도체 | SK하이닉스 | 3.50% | |
| 12.04 | 개별 | 개별이슈 | 코칩 | 29.98% | 美 엔비디아에 공급 |

**참고:**
- **테마**: 같은 그룹명으로 묶이며, 5개 초과 시 자동 분리
- **개별**: 3개씩 자동 분리
- **이슈내용**: 테마는 첫 행에만, 개별은 모든 행에 입력

#### 4. 실행

**Windows:**
```bash
# 더블클릭으로 실행
실행.bat

# 또는 명령 프롬프트에서
python main.py
```

**Mac/Linux:**
```bash
python main.py
```

**옵션:**
```bash
python main.py                    # 시트의 최신 날짜 자동 사용
python main.py --date 2025.12.04  # 특정 날짜 지정
python main.py --test             # 테스트 데이터로 실행
```

#### 5. 결과 확인

생성된 이미지는 `output` 폴더에 저장됩니다:
```
output/
├── 급등이슈_251204_1.png
├── 급등이슈_251204_2.png
└── ...
```

## 📁 프로젝트 구조

```
issue-automation/
├── main.py                       # 메인 실행 파일
├── sheet_reader.py               # 구글 시트 연동
├── html_renderer.py              # HTML → 이미지 생성
├── template.html                 # 디자인 템플릿
├── requirements.txt              # 필요한 라이브러리
├── service_account.json.json     # 구글 API 키 (업로드 금지)
├── 실행.bat                      # Windows 실행 스크립트
├── output/                       # 생성된 이미지 저장
└── README.md
```

## 🎨 디자인 커스터마이징

`template.html` 파일을 수정하여 디자인 변경 가능:
- 색상, 폰트, 레이아웃 등 자유롭게 수정
- Tailwind CSS 사용
- Google Fonts (Noto Sans KR) 적용

## 🔧 문제 해결

### "python을 찾을 수 없습니다"
Python이 설치되어 있는지 확인하고 환경변수 PATH에 추가

### "No module named ..."
```bash
pip install -r requirements.txt
```

### "구글 시트 연결 실패"
- `service_account.json.json` 파일 위치 확인
- 구글 시트 공유 설정 확인
- Google Sheets API 활성화 확인

### "Playwright 브라우저 없음"
```bash
python -m playwright install chromium
```

## 📝 라이선스

MIT License

## 🤝 기여

이슈와 PR은 언제나 환영합니다!

## 📧 문의

문제가 있으시면 이슈를 등록해주세요.

