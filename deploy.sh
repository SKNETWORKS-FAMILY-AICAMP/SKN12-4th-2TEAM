#!/bin/bash

echo "🚀 ESG Chatbot 배포 시작..."

# 환경변수 파일 확인
if [ ! -f .env ]; then
    echo "❌ .env 파일이 없습니다. env.example을 복사하여 설정하세요."
    exit 1
fi

# Docker 이미지 빌드
echo "📦 Docker 이미지 빌드 중..."
docker-compose -f docker-compose.prod.yml build

# 기존 컨테이너 중지 및 제거
echo "🛑 기존 컨테이너 중지 중..."
docker-compose -f docker-compose.prod.yml down

# 새 컨테이너 시작
echo "▶️  새 컨테이너 시작 중..."
docker-compose -f docker-compose.prod.yml up -d

# 상태 확인
echo "✅ 배포 완료!"
echo "🌐 웹사이트: http://localhost"
echo "📚 API 문서: http://localhost/docs"
echo "💚 헬스체크: http://localhost/health"

# 컨테이너 상태 확인
docker-compose -f docker-compose.prod.yml ps 