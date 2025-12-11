"""
버전 관리 유틸리티
프로젝트 버전을 자동으로 관리하고 Git 태그를 생성합니다.
"""

import re
import subprocess
from pathlib import Path
from typing import Optional


class VersionManager:
    """버전 관리 클래스"""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
        self.version_file = self.project_root / "VERSION"

    def get_current_version(self) -> Optional[str]:
        """현재 버전 읽기"""
        if self.version_file.exists():
            return self.version_file.read_text().strip()
        return None

    def validate_version(self, version: str) -> bool:
        """버전 형식 검증 (semver: x.y.z)"""
        pattern = r'^\d+\.\d+\.\d+$'
        return bool(re.match(pattern, version))

    def update_version(self, version: str):
        """버전 파일 업데이트"""
        if not self.validate_version(version):
            raise ValueError(f"유효하지 않은 버전 형식: {version}. 형식: x.y.z")

        print(f"📝 버전 업데이트: {self.get_current_version()} -> {version}")
        self.version_file.write_text(version + "\n")

        # Git에 변경사항 커밋 (선택적)
        try:
            subprocess.run(
                ["git", "add", str(self.version_file)],
                check=True,
                capture_output=True
            )
            subprocess.run(
                ["git", "commit", "-m", f"Bump version to {version}"],
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError:
            # Git이 없거나 커밋이 실패해도 계속 진행
            pass

    def create_tag(self, version: str):
        """Git 태그 생성"""
        tag_name = f"v{version}"
        print(f"🏷️  Git 태그 생성: {tag_name}")

        try:
            # 태그가 이미 존재하는지 확인
            result = subprocess.run(
                ["git", "tag", "-l", tag_name],
                capture_output=True,
                text=True
            )
            if tag_name in result.stdout:
                print(f"⚠️  태그 {tag_name}가 이미 존재합니다.")
                return

            # 태그 생성
            subprocess.run(
                ["git", "tag", "-a", tag_name, "-m", f"Release {version}"],
                check=True
            )
            print(f"✓ 태그 {tag_name} 생성 완료")
        except subprocess.CalledProcessError as e:
            print(f"⚠️  Git 태그 생성 실패 (계속 진행): {e}")
        except FileNotFoundError:
            print("⚠️  Git이 설치되어 있지 않습니다. 태그를 생성할 수 없습니다.")

    def increment_version(self, part: str = "patch") -> str:
        """
        버전 자동 증가
        part: 'major', 'minor', 'patch'
        """
        current = self.get_current_version()
        if not current:
            return "1.0.0"

        major, minor, patch = map(int, current.split("."))

        if part == "major":
            major += 1
            minor = 0
            patch = 0
        elif part == "minor":
            minor += 1
            patch = 0
        elif part == "patch":
            patch += 1
        else:
            raise ValueError(f"유효하지 않은 버전 부분: {part}")

        new_version = f"{major}.{minor}.{patch}"
        self.update_version(new_version)
        return new_version

