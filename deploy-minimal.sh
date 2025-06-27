#!/bin/bash

# ESG Chatbot 최소 배포 스크립트
echo "🚀 ESG Chatbot 최소 배포 시작..."

# 1. 필요한 디렉토리 생성
mkdir -p esg-chatbot-deploy
cd esg-chatbot-deploy

# 2. docker-compose.prod.yml 다운로드
cat > docker-compose.prod.yml << 'EOF'
version: "3.9"

services:
  db:
    image: postgres:14
    container_name: esg-postgres-prod
    environment:
      POSTGRES_USER: esgadmin
      POSTGRES_PASSWORD: mysecretpassword
      POSTGRES_DB: esg_chatbot
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  api:
    image: wonwookims/esg-chatbot:latest
    container_name: esg-api-prod
    env_file:
      - .env
    depends_on:
      - db
    environment:
      DATABASE_URL: postgresql://esgadmin:mysecretpassword@db:5432/esg_chatbot
    ports:
      - "8000:8000"
    restart: unless-stopped
    command: ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

  frontend:
    image: nginx:alpine
    container_name: esg-frontend-prod
    ports:
      - "80:80"
    volumes:
      - ./frontend:/usr/share/nginx/html
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - api
    restart: unless-stopped

volumes:
  postgres_data:
EOF

# 3. nginx.conf 다운로드
cat > nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    server {
        listen 80;
        server_name localhost;

        # 프론트엔드 (정적 파일)
        location / {
            root /usr/share/nginx/html;
            index index.html;
            try_files $uri $uri/ /index.html;
        }

        # API 프록시 - 모든 API 경로
        location /auth/ {
            proxy_pass http://api:8000/auth/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /chat/ {
            proxy_pass http://api:8000/chat/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /feedback/ {
            proxy_pass http://api:8000/feedback/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /email/ {
            proxy_pass http://api:8000/email/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /chatroom/ {
            proxy_pass http://api:8000/chatroom/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # 루트 API 엔드포인트들
        location /health {
            proxy_pass http://api:8000/health;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /docs {
            proxy_pass http://api:8000/docs;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /redoc {
            proxy_pass http://api:8000/redoc;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /openapi.json {
            proxy_pass http://api:8000/openapi.json;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # 정적 파일 캐싱
        location /assets/ {
            alias /usr/share/nginx/html/assets/;
            access_log off;
            expires 30d;
        }

        location /common/ {
            alias /usr/share/nginx/html/common/;
            access_log off;
            expires 30d;
        }
    }
}
EOF

# 4. .env 파일 템플릿 생성
cat > .env.template << 'EOF'
# 데이터베이스 (기본값 사용)
DATABASE_URL=postgresql://esgadmin:mysecretpassword@db:5432/esg_chatbot

# JWT 시크릿 (필수)
SECRET_KEY=your-secret-key-here-change-this-in-production

# 이메일 설정 (선택사항)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EOF

# 5. README 생성
cat > README.md << 'EOF'
# ESG Chatbot 최소 배포

## 🚀 빠른 시작

1. **환경 변수 설정**
   ```bash
   cp .env.template .env
   # .env 파일을 편집하여 필요한 설정을 변경하세요
   ```

2. **프론트엔드 파일 다운로드**
   ```bash
   # GitHub에서 frontend 폴더를 다운로드하거나
   # 프로젝트 전체를 클론한 후 frontend 폴더만 복사
   git clone https://github.com/your-username/esg_chatbot.git temp
   cp -r temp/frontend ./
   rm -rf temp
   ```

3. **Docker 실행**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

4. **접속**
   - 프론트엔드: http://localhost:80
   - API 문서: http://localhost/docs
   - 헬스체크: http://localhost/health

## 📁 필요한 파일 구조
```
esg-chatbot-deploy/
├── docker-compose.prod.yml  # 서비스 구성
├── nginx.conf              # Nginx 설정
├── .env                    # 환경 변수 (생성 필요)
├── frontend/               # 프론트엔드 파일 (다운로드 필요)
└── README.md              # 이 파일
```

## 🔧 환경 변수 설정
- `SECRET_KEY`: JWT 토큰 암호화 키 (필수)
- `EMAIL_*`: 이메일 기능 사용시 설정 (선택)
EOF

echo "✅ 최소 배포 파일 생성 완료!"
echo "📁 다음 단계:"
echo "1. cp .env.template .env"
echo "2. frontend 폴더를 다운로드"
echo "3. docker-compose -f docker-compose.prod.yml up -d" 