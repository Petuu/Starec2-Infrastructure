\# 🎥 Starec2 Infrastructure \& Automation





> 개인 클라우드 녹화 서버(Starec2)를 운영하기 위한 인프라 구축(IaC), 컨테이너 최적화, 운영 자동화(ChatOps) 코드를 담은 리포지토리입니다.



\## 📝 About This Repository

이 프로젝트의 핵심 녹화 로직은 커뮤니티 배포형 소스 코드를 기반으로 하고 있습니다.

원작자의 저작권을 존중하기 위해 애플리케이션 코어 로직은 Private으로 관리하고 있으며, 본 리포지토리에는 제가 직접 설계하고 구현한 인프라 및 운영 자동화 코드만 공개합니다.



\## 🚀 Key Achievements

이 인프라 구성의 핵심 성과는 다음과 같습니다.



\### 1. Docker Optimization (Multi-stage Build)

\- Problem: 초기 빌드 시 gcc, make 등 빌드 도구로 인해 이미지 크기가 비대해짐 (약 600MB).

\- Solution: Multi-stage Build를 적용하여 빌드 단계와 런타임 단계를 분리.

\- Result: 불필요한 레이어를 제거하여 이미지 용량을 약 22% 절감 (595MB → 463MB)

\- 📂 관련 파일: Dockerfile



\### 2. ChatOps Automation (Slack Bot)

\- Problem: 장애 발생 시마다 SSH로 접속해야 하는 비효율과 물리적 제약.

\- Solution: Python과 Docker Socket을 연동한 Slack ChatOps 구축.

\- Features:

&nbsp;   - Monitoring: 모바일에서 실시간 디스크 용량 및 로그 확인.

&nbsp;   - Self-Healing: /restart 명령어로 문제 컨테이너 즉시 복구.

\- Result: 장애 대응 시간(MTTR)을 수 분 → 수 초 단위로 단축.

\- 📂 관련 파일: ops\_bot.py



\### 3. Infrastructure as Code (Terraform)

\- Problem: 수동 구축으로 인한 관리의 어려움 및 휴먼 에러 가능성.

\- Solution: Terraform을 도입하여 인프라 프로비저닝을 코드화.

\- 📂 관련 파일: main.tf



---



\## 📂 File Structure



📦 Starec2-Infrastructure

&nbsp;┣ 📜 Dockerfile          # Multi-stage Build 적용, ffmpeg 및 필수 의존성 최적화

&nbsp;┣ 📜 docker-compose.yml  # 컨테이너 오케스트레이션 및 볼륨/네트워크 정의

&nbsp;┣ 📜 main.tf             # GCP 인스턴스 및 리소스 프로비저닝 코드 (Terraform)

&nbsp;┗ 📜 ops\_bot.py          # Slack API 기반 운영 자동화 봇 (ChatOps)



\## 🛠️ Tech Stack

\* Infrastructure: GCP (Google Cloud Platform), Terraform

\* Container: Docker, Docker Compose

\* Language: Python 3.12 (Slim)

\* Automation: Slack API (Bolt)



---

