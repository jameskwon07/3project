#!/usr/bin/env python3
"""
Master 배포 스크립트
Python 웹 서버 및 프론트엔드를 배포합니다.
"""

import argparse
import sys
import subprocess
import os
from pathlib import Path
from version import VersionManager


def install_backend_dependencies():
    """Backend 의존성 설치"""
    print("📦 Backend 의존성 설치 중...")
    backend_dir = Path("master/backend")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
        cwd=backend_dir,
        check=True
    )
    print("✓ Backend 의존성 설치 완료")


def install_frontend_dependencies():
    """Frontend 의존성 설치"""
    print("📦 Frontend 의존성 설치 중...")
    frontend_dir = Path("master/frontend")
    
    # npm이 있는지 확인
    try:
        subprocess.run(["npm", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ npm이 설치되어 있지 않습니다.")
        print("   Node.js와 npm을 설치해주세요: https://nodejs.org/")
        sys.exit(1)
    
    subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)
    print("✓ Frontend 의존성 설치 완료")


def build_frontend():
    """Frontend 빌드"""
    print("🏗️  Frontend 빌드 중...")
    frontend_dir = Path("master/frontend")
    subprocess.run(["npm", "run", "build"], cwd=frontend_dir, check=True)
    print("✓ Frontend 빌드 완료")


def deploy_master(version: str, production: bool = False):
    """Master 배포"""
    print(f"🚀 Master 배포 중... (버전: {version})")
    
    if production:
        print("   프로덕션 모드로 실행")
        # TODO: 프로덕션 배포 로직
        # 예: systemd 서비스 설정, nginx 설정 등
    else:
        print("   개발 모드로 실행")
        print("   실행: cd master/backend && python main.py")
    
    print("✓ Master 배포 준비 완료")


def main():
    parser = argparse.ArgumentParser(description="Master 배포 스크립트")
    parser.add_argument(
        "--version",
        type=str,
        help="배포할 버전 (예: 1.0.0)",
        required=True
    )
    parser.add_argument(
        "--skip-install",
        action="store_true",
        help="의존성 설치 건너뛰기"
    )
    parser.add_argument(
        "--production",
        action="store_true",
        help="프로덕션 모드로 배포"
    )

    args = parser.parse_args()

    try:
        # 버전 관리
        version_manager = VersionManager()
        version_manager.update_version(args.version)

        # 의존성 설치
        if not args.skip_install:
            install_backend_dependencies()
            install_frontend_dependencies()

        # Frontend 빌드
        build_frontend()

        # 배포
        deploy_master(args.version, args.production)

        # Git 태그
        version_manager.create_tag(args.version)

        print(f"\n✅ Master 배포 완료! 버전 {args.version}")
        print("\n실행 방법:")
        print("  cd master/backend")
        print("  python main.py")

    except subprocess.CalledProcessError as e:
        print(f"❌ 오류 발생: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

