import json
import os
from pathlib import Path
import tempfile

from .serializers import from_data, to_data


class SaveError(Exception):
    """화면에 표시할 수 있는 저장·복원 실패."""


class SaveManager:
    DEFAULT_PATH = Path(__file__).resolve().parents[2] / "data" / "saves" / "continue.json"

    def __init__(self, path=None):
        self.path = Path(path) if path is not None else self.DEFAULT_PATH
        self.backup_path = self.path.with_suffix(".bak")
        self._last_text = None

    def exists(self):
        return self.path.is_file()

    @staticmethod
    def _atomic_write(path, text):
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                             prefix=path.name + ".", suffix=".tmp", delete=False) as stream:
                temporary = Path(stream.name)
                stream.write(text)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, path)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

    def save(self, session):
        try:
            text = json.dumps(to_data(session), ensure_ascii=False, allow_nan=False, indent=2)
            if text == self._last_text and self.exists():
                return
            # 쓰기 전에 같은 복원 경로로 검증한다. 잘못된 현재 상태로 정상 파일을 덮지 않는다.
            from_data(json.loads(text))
            if self.exists():
                previous = self.path.read_text(encoding="utf-8")
                try:
                    from_data(json.loads(previous))
                except (ValueError, KeyError, TypeError, AttributeError, IndexError, OverflowError):
                    pass
                else:
                    self._atomic_write(self.backup_path, previous)
            self._atomic_write(self.path, text)
            self._last_text = text
        except (OSError, ValueError, KeyError, TypeError, AttributeError, IndexError, OverflowError) as error:
            raise SaveError(f"게임을 저장하지 못했습니다: {error}") from error

    def load(self):
        try:
            text = self.path.read_text(encoding="utf-8")
            session = from_data(json.loads(text))
            self._last_text = None
            return session
        except (OSError, ValueError, KeyError, TypeError, AttributeError, IndexError, OverflowError) as error:
            raise SaveError("저장 파일을 읽을 수 없거나 지원하지 않는 데이터입니다. 기존 파일은 유지됩니다.") from error

    def delete(self):
        try:
            # 백업 제거 실패 시 본 저장은 유지한다.
            self.backup_path.unlink(missing_ok=True)
            self.path.unlink(missing_ok=True)
            self._last_text = None
        except OSError as error:
            raise SaveError("기존 저장 파일을 삭제하지 못했습니다.") from error
