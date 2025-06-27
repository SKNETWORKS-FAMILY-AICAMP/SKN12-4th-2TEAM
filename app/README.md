# ESG Chatbot Backend (app)

이 디렉토리는 ESG Chatbot의 **백엔드(Backend)** 코드입니다. FastAPI, SQLAlchemy, PostgreSQL을 기반으로 하며, 사용자 인증, 멀티룸 챗봇, 피드백, 이메일 인증 등 주요 기능을 제공합니다.

---

## 1. 폴더 구조

- `main.py` : FastAPI 앱 진입점, 라우터 등록, CORS 등 설정
- `routers/` : API 엔드포인트(회원, 챗봇, 피드백, 이메일, 채팅방 등)
- `models/` : SQLAlchemy ORM 모델(테이블 정의)
- `schemas/` : Pydantic 스키마(요청/응답 검증)
- `services/` : 비즈니스 로직(예: RAG 파이프라인, 이메일 발송)
- `utils/` : 보안, 유틸 함수 등
- `database.py` : DB 연결/세션 관리
- `dependencies.py` : 공통 의존성(인증 등)
- `data/` : 예시 데이터, ChromaDB 등

---

## 2. 데이터베이스 명세서 (주요 테이블)

### user
| 필드명        | 타입      | 설명           |
|--------------|----------|----------------|
| id           | int      | PK             |
| email        | string   | 이메일(고유)   |
| password_hash| string   | 비밀번호 해시  |
| name         | string   | 이름           |
| company      | string   | 회사명         |
| is_verified  | bool     | 이메일 인증여부|
| is_admin     | bool     | 관리자 여부    |
| created_at   | datetime | 가입일         |

### chat_room
| 필드명    | 타입    | 설명         |
|----------|--------|--------------|
| id       | int    | PK           |
| user_id  | int    | FK(user)     |
| title    | string | 방 제목      |
| created_at|datetime| 생성일       |

### chat
| 필드명      | 타입    | 설명           |
|------------|--------|----------------|
| id         | int    | PK             |
| user_id    | int    | FK(user)       |
| chatroom_id| int    | FK(chat_room)  |
| question   | text   | 질문           |
| response   | text   | 답변           |
| created_at |datetime| 생성일         |

### feedback
| 필드명    | 타입    | 설명           |
|----------|--------|----------------|
| id       | int    | PK             |
| chat_id  | int    | FK(chat)       |
| user_id  | int    | FK(user)       |
| score    | int    | 1(좋아요)/-1(싫어요) |
| created_at|datetime| 생성일         |

### email_token
| 필드명    | 타입    | 설명           |
|----------|--------|----------------|
| id       | int    | PK             |
| user_id  | int    | FK(user)       |
| token    | string | 인증 토큰      |
| is_used  | bool   | 사용 여부      |
| expires_at|datetime| 만료일         |

---

## 3. 주요 API 설계서

### 인증/회원
- `POST /auth/login` : 로그인(쿠키)
- `POST /auth/logout` : 로그아웃(쿠키 삭제)
- `GET /auth/me` : 내 정보 조회(로그인 필요)
- `POST /auth/change-password` : 비밀번호 변경
- `POST /auth/request-password-reset` : 비밀번호 재설정 인증번호 전송
- `POST /auth/verify-password-reset-code` : 인증번호 확인
- `POST /auth/reset-password` : 비밀번호 재설정
- `POST /auth/find-email` : 이름+회사명으로 이메일 찾기

### 채팅/챗봇
- `POST /chat/chat` : 챗봇 질문(방 ID 필요)
- `GET /chat/chat/{user_id}` : 내 전체 대화 이력

### 채팅방(멀티룸)
- `POST /chatroom/` : 채팅방 생성(첫 질문이 제목)
- `GET /chatroom/list` : 내 채팅방 목록
- `GET /chatroom/{room_id}` : 채팅방 상세
- `GET /chatroom/{room_id}/messages` : 해당 방의 메시지 목록 (각 메시지에 feedback_given 포함)

### 피드백
- `POST /feedback/feedback` : 답변 피드백(좋아요/싫어요)
- `GET /feedback/feedback/all` : 전체 피드백(관리자)

### 이메일 인증
- `POST /email/send-code` : 이메일 인증번호 전송
- `POST /email/verify-code` : 인증번호 확인
- `POST /email/register-after-verification` : 이메일 인증 후 회원가입

---

## 4. 예시: 채팅방 메시지 목록 응답
```json
[
  {
    "id": 1,
    "chatroom_id": 2,
    "user_id": 3,
    "question": "ESG란?",
    "response": "ESG는 ...",
    "created_at": "2024-06-24T12:34:56",
    "feedback_given": false
  },
  ...
]
```

---

## 5. 기타
- 모든 API는 인증(쿠키 기반) 필요, 일부(회원가입/로그인/이메일 인증 등)는 예외
- 관리자 전용 API는 is_admin 체크
- DB는 PostgreSQL, ORM은 SQLAlchemy 사용

---

자세한 사용법/설치법은 프로젝트 루트의 README를 참고하세요.