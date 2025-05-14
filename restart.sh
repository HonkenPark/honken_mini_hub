#!/bin/bash

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 현재 실행 중인 컨테이너 확인
echo -e "${YELLOW}현재 실행 중인 컨테이너를 확인합니다...${NC}"
CONTAINER_ID=$(docker ps -a -q -f name=honken_mini_hub)

if [ ! -z "$CONTAINER_ID" ]; then
    echo -e "${YELLOW}기존 컨테이너를 중지하고 삭제합니다...${NC}"
    docker stop $CONTAINER_ID 2>/dev/null || true
    docker rm $CONTAINER_ID 2>/dev/null || true
    echo -e "${GREEN}기존 컨테이너가 제거되었습니다.${NC}"
else
    echo -e "${GREEN}실행 중인 컨테이너가 없습니다.${NC}"
fi

# 이미지 삭제
echo -e "${YELLOW}기존 이미지를 삭제합니다...${NC}"
docker rmi honken_mini_hub:latest 2>/dev/null || true
echo -e "${GREEN}기존 이미지가 제거되었습니다.${NC}"

# 새 이미지 빌드
echo -e "${YELLOW}새로운 이미지를 빌드합니다...${NC}"
docker build -t honken_mini_hub:latest .
echo -e "${GREEN}이미지 빌드가 완료되었습니다.${NC}"

# 새 컨테이너 실행
echo -e "${YELLOW}새로운 컨테이너를 실행합니다...${NC}"
docker run -d \
    --name honken_mini_hub \
    -p 8000:8000 \
    -v $(pwd)/data:/app/data \
    -v $(pwd)/app/core/config:/app/app/core/config \
    --restart unless-stopped \
    honken_mini_hub:latest

# 컨테이너 실행 확인
if [ $? -eq 0 ]; then
    echo -e "${GREEN}컨테이너가 성공적으로 실행되었습니다!${NC}"
    echo -e "${YELLOW}컨테이너 로그를 확인합니다...${NC}"
    docker logs -f honken_mini_hub
else
    echo -e "${RED}컨테이너 실행 중 오류가 발생했습니다.${NC}"
    exit 1
fi 