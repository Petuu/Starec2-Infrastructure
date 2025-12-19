import os
import logging
import asyncio
import zipfile
import io
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
import docker

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 1. 토큰 및 설정
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")
TARGET_CONTAINER = "starec2_main"  # 조종할 Starec2 컨테이너 이름
LOG_DIR = "/app/logs"             # 로그 파일이 위치한 경로 (볼륨 마운트 필요)

# 2. 앱 초기화
app = AsyncApp(token=SLACK_BOT_TOKEN)
docker_client = docker.from_env()

# --- [기능 1] 서버 재시작 (/restart) ---
@app.command("/restart")
async def handle_restart_command(ack, say, command):
    await ack()
    user_id = command['user_id']
    await say(f"<@{user_id}> 님, Starec2 컨테이너 재시작을 시도합니다... 🔄")
    
    try:
        loop = asyncio.get_running_loop()
        def restart_container():
            container = docker_client.containers.get(TARGET_CONTAINER)
            container.restart()
            return container.name

        container_name = await loop.run_in_executor(None, restart_container)
        logging.info(f"Container {container_name} restarted by ChatOps")
        await say(f"✅ 재시작 명령 전달 완료! `{container_name}` 컨테이너가 다시 시작되었습니다.")
    except Exception as e:
        await say(f"❌ 재시작 실패: {str(e)}")
        logging.error(f"Restart failed: {e}")

# --- [기능 2] 디스크 및 컨테이너 상태 확인 (/disk) ---
@app.command("/disk")
async def handle_disk_command(ack, say):
    await ack()
    try:
        loop = asyncio.get_running_loop()
        def get_status():
            container = docker_client.containers.get(TARGET_CONTAINER)
            # 컨테이너 내부에서 디스크 용량 확인 명령어 실행
            exit_code, output = container.exec_run("df -h /app/output")
            return container.status, output.decode('utf-8')

        status, disk_info = await loop.run_in_executor(None, get_status)
        msg = f"📊 *Starec2 상태 보고*\n• 컨테이너: `{status}`\n• 디스크 사용량:\n```{disk_info}```"
        await say(msg)
    except Exception as e:
        await say(f"❌ 상태 확인 실패: {str(e)}")

# --- [기능 3] 최근 로그 20줄 보기 (/logs) ---
@app.command("/logs")
async def handle_logs_command(ack, say):
    await ack()
    try:
        loop = asyncio.get_running_loop()
        def get_logs():
            container = docker_client.containers.get(TARGET_CONTAINER)
            return container.logs(tail=20).decode('utf-8')

        logs = await loop.run_in_executor(None, get_logs)
        await say(f"📜 *최근 로그 (Last 20 lines)*\n```{logs}```")
    except Exception as e:
        await say(f"❌ 로그 조회 실패: {str(e)}")

# --- [기능 4] 전체 로그 압축 파일 다운로드 (/ziplogs) ---
@app.command("/ziplogs")
async def handle_ziplogs_command(ack, say, client, command):
    await ack()
    channel_id = command['channel_id']
    target_files = ["drive.log", "launcher.txt", "master.txt", "slave_default_0.txt"]
    
    await say("📦 로그 파일을 수집하여 압축하는 중입니다. 잠시만 기다려주세요...")

    try:
        zip_buffer = io.BytesIO()
        files_found = 0
        
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for filename in target_files:
                file_path = os.path.join(LOG_DIR, filename)
                if os.path.exists(file_path):
                    zf.write(file_path, filename)
                    files_found += 1
        
        zip_buffer.seek(0)

        if files_found == 0:
            await say("⚠️ 전송할 로그 파일이 없습니다.")
            return

        await client.files_upload_v2(
            channel=channel_id,
            file=zip_buffer,
            filename="starec_logs.zip",
            title="Starec2 Log Bundle",
            initial_comment=f"✅ {files_found}개의 로그 파일을 압축했습니다."
        )
    except Exception as e:
        await say(f"❌ 로그 파일 전송 실패: {str(e)}")

# 3. 메인 실행
async def main():
    handler = AsyncSocketModeHandler(app, SLACK_APP_TOKEN)
    await handler.start_async()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass