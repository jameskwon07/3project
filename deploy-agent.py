#!/usr/bin/env python3
"""
Agent 배포 스크립트
C# Agent를 Windows와 Mac용으로 빌드합니다.
"""

import argparse
import sys
import subprocess
import platform
from pathlib import Path
from version import VersionManager


def check_dotnet():
    """.NET SDK 설치 확인"""
    try:
        result = subprocess.run(
            ["dotnet", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✓ .NET SDK 설치됨: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ .NET SDK가 설치되어 있지 않습니다.")
        print("   설치: https://dotnet.microsoft.com/download")
        return False


def build_agent_windows():
    """Windows용 Agent 빌드"""
    print("📦 Windows x64 Agent 빌드 중...")
    agent_dir = Path("agent")
    
    subprocess.run(
        [
            "dotnet", "publish",
            "-c", "Release",
            "-r", "win-x64",
            "-p:PublishSingleFile=true",
            "-p:IncludeNativeLibrariesForSelfExtract=true",
            "--self-contained", "true",
            "-o", "../dist/agent-windows"
        ],
        cwd=agent_dir,
        check=True
    )
    print("✓ Windows Agent 빌드 완료: dist/agent-windows/Agent.exe")


def build_agent_macos_x64():
    """macOS x64용 Agent 빌드"""
    print("📦 macOS x64 Agent 빌드 중...")
    agent_dir = Path("agent")
    
    subprocess.run(
        [
            "dotnet", "publish",
            "-c", "Release",
            "-r", "osx-x64",
            "-p:PublishSingleFile=true",
            "-p:IncludeNativeLibrariesForSelfExtract=true",
            "--self-contained", "true",
            "-o", "../dist/agent-macos-x64"
        ],
        cwd=agent_dir,
        check=True
    )
    print("✓ macOS x64 Agent 빌드 완료: dist/agent-macos-x64/Agent")


def build_agent_macos_arm64():
    """macOS ARM64용 Agent 빌드 (Apple Silicon)"""
    print("📦 macOS ARM64 Agent 빌드 중...")
    agent_dir = Path("agent")
    
    subprocess.run(
        [
            "dotnet", "publish",
            "-c", "Release",
            "-r", "osx-arm64",
            "-p:PublishSingleFile=true",
            "-p:IncludeNativeLibrariesForSelfExtract=true",
            "--self-contained", "true",
            "-o", "../dist/agent-macos-arm64"
        ],
        cwd=agent_dir,
        check=True
    )
    print("✓ macOS ARM64 Agent 빌드 완료: dist/agent-macos-arm64/Agent")


def build_all_platforms():
    """모든 플랫폼용 Agent 빌드"""
    build_agent_windows()
    build_agent_macos_x64()
    build_agent_macos_arm64()


def main():
    parser = argparse.ArgumentParser(description="Agent 배포 스크립트")
    parser.add_argument(
        "--version",
        type=str,
        help="배포할 버전 (예: 1.0.0)",
        required=True
    )
    parser.add_argument(
        "--platform",
        type=str,
        choices=["windows", "macos-x64", "macos-arm64", "all"],
        default="all",
        help="빌드할 플랫폼 (기본: all)"
    )

    args = parser.parse_args()

    try:
        # .NET SDK 확인
        if not check_dotnet():
            sys.exit(1)

        # 버전 관리
        version_manager = VersionManager()
        version_manager.update_version(args.version)

        # dist 디렉토리 생성
        Path("dist").mkdir(exist_ok=True)

        # 플랫폼별 빌드
        if args.platform == "windows":
            build_agent_windows()
        elif args.platform == "macos-x64":
            build_agent_macos_x64()
        elif args.platform == "macos-arm64":
            build_agent_macos_arm64()
        else:  # all
            build_all_platforms()

        # Git 태그
        version_manager.create_tag(args.version)

        print(f"\n✅ Agent 배포 완료! 버전 {args.version}")
        print("\n빌드 결과:")
        if args.platform in ["windows", "all"]:
            print("  Windows: dist/agent-windows/Agent.exe")
        if args.platform in ["macos-x64", "all"]:
            print("  macOS x64: dist/agent-macos-x64/Agent")
        if args.platform in ["macos-arm64", "all"]:
            print("  macOS ARM64: dist/agent-macos-arm64/Agent")

    except subprocess.CalledProcessError as e:
        print(f"❌ 오류 발생: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

