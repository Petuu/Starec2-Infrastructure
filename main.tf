# 1. 구글 클라우드 설정
provider "google" {
  credentials = file("gcp-key.json")
  project     = "gcprecoder"       # <--- [확인] 본인 프로젝트 ID가 맞는지 꼭 다시 확인!
  region      = "us-central1"
  zone        = "us-central1-a"
}

# [추가됨] 2. VM을 위한 전용 서비스 계정 생성
# "기본 계정"이 없으니, 우리가 직접 하나 만들어주는 겁니다.
resource "google_service_account" "starec_sa" {
  account_id   = "starec-vm-account"
  display_name = "Service Account for Starec VM"
}

# 3. 방화벽 설정
resource "google_compute_firewall" "starec_custom_ports" {
  name    = "allow-starec-ports"
  network = "default"

  allow {
    protocol = "tcp"
    ports    = ["13901", "6969", "22"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["starec-server"]
}

# 4. VM 인스턴스
resource "google_compute_instance" "starec_replica" {
  name         = "starec2-terraform-vm"
  machine_type = "t2a-standard-1"  # ARM64
  zone         = "us-central1-a"

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2204-lts-arm64" # ARM64 이미지
      size  = 10
      type  = "pd-balanced"
    }
  }

  network_interface {
    network = "default"
    access_config {
      # 공인 IP 자동 할당
    }
  }

  # [수정됨] 서비스 계정 연결
  service_account {
    # 위에서 만든 'starec_sa'를 이 VM에 갖다 붙입니다.
    email  = google_service_account.starec_sa.email
    scopes = ["cloud-platform"]
  }

  tags = ["http-server", "https-server", "starec-server"]
}