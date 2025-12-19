# ==========================================
# 🏗️ Stage 1: 빌드 전용 이미지
# ==========================================
FROM python:3.12-slim-bookworm AS builder

ENV DEBIAN_FRONTEND=noninteractive

# 빌드 도구 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    libgd-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libavutil-dev \
    libavfilter-dev

# mtn 소스 빌드 및 설치 (make install 까지 실행!)
WORKDIR /tmp
RUN git clone https://gitlab.com/movie_thumbnailer/mtn.git && \
    cd mtn/src && \
    sed -i 's/-DMTN_WITH_AVIF//g' Makefile && \
    make && \
    make install 
# make install을 하면 /usr/local/bin/mtn 에 생성됩니다.

# ==========================================
# 🏠 Stage 2: 실제 실행 이미지
# ==========================================
FROM python:3.12-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Seoul

# 1. 런타임 필수 패키지 설치
# (libgd3는 mtn 실행에 필요해서 추가됨)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    unzip \
    fontconfig \
    fonts-noto-cjk \
    fonts-nanum \
    fonts-liberation \
    libgl1 \
    libegl1-mesa \
    fuse3 \
    ffmpeg \
    libgd3 \
    && rm -rf /var/lib/apt/lists/*

# 2. Stage 1에서 설치된 실행 파일 복사
# /tmp/... 가 아니라 /usr/local/bin/mtn 에서 가져옵니다.
COPY --from=builder /usr/local/bin/mtn /usr/local/bin/mtn

# 3. Rclone 설치
RUN curl https://rclone.org/install.sh | bash

# 4. 작업 디렉토리 설정
WORKDIR /app

# 5. 파이썬 라이브러리 설치
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 6. 소스 코드 복사
COPY . .

# 7. 포트 개방
EXPOSE 13901 6969