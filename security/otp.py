# Owner: Helen Mezgebe
# Feature: User Registration and Secure Access

import hashlib
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import UUID

from config import OTP_EXPIRE_MINUTES, OTP_MAX_ATTEMPTS


@dataclass
class OtpRecord:
    code_hash: str
    expires_at: datetime
    attempts: int = 0


class OtpStore:
    def __init__(self):
        self.records: dict[str, OtpRecord] = {}

    def issue(self, user_id: UUID) -> str:
        code = f"{secrets.randbelow(1_000_000):06d}"
        self.records[str(user_id)] = OtpRecord(
            code_hash=self._hash(code),
            expires_at=datetime.now(timezone.utc)
            + timedelta(minutes=OTP_EXPIRE_MINUTES),
        )
        return code

    def verify(self, user_id: UUID, code: str) -> bool:
        key = str(user_id)
        record = self.records.get(key)

        if record is None:
            return False

        if datetime.now(timezone.utc) > record.expires_at:
            self.records.pop(key, None)
            return False

        record.attempts += 1
        if record.attempts > OTP_MAX_ATTEMPTS:
            self.records.pop(key, None)
            return False

        if not secrets.compare_digest(record.code_hash, self._hash(code)):
            return False

        self.records.pop(key, None)
        return True

    def invalidate(self, user_id: UUID) -> None:
        self.records.pop(str(user_id), None)

    @staticmethod
    def _hash(code: str) -> str:
        return hashlib.sha256(code.encode("utf-8")).hexdigest()


otp_store = OtpStore()
