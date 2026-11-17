"""Settings read from the environment (SPEC section 8)."""

from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class Settings:
    db_path: str = "kurul.db"
    base_url: str = "http://localhost:8000"
    agent_token: str = ""
    session_secret: str = ""
    bootstrap_token: str = ""
    coordinator_email: str = "coordinator@invalid"
    smtp_url: str = ""
    mail_from: str = "Knotenlinie Board <board@invalid>"
    # Limits; overridable in tests.
    max_running: int = 3
    message_rate_per_min: int = 20
    login_rate_per_ip: int = 10        # per 15 minutes
    login_rate_per_email: int = 3      # per 15 minutes
    extra: dict = field(default_factory=dict)

    @property
    def secure_cookie(self) -> bool:
        u = self.base_url.lower()
        return not (u.startswith("http://localhost") or u.startswith("http://127.0.0.1"))

    @classmethod
    def from_env(cls) -> "Settings":
        e = os.environ.get
        return cls(
            db_path=e("KURUL_DB", "kurul.db"),
            base_url=(e("KURUL_BASE_URL", "http://localhost:8000") or "").rstrip("/"),
            agent_token=e("KURUL_AGENT_TOKEN", ""),
            session_secret=e("KURUL_SESSION_SECRET", ""),
            bootstrap_token=e("KURUL_BOOTSTRAP_TOKEN", ""),
            coordinator_email=e("KURUL_COORDINATOR_EMAIL", "coordinator@invalid"),
            smtp_url=e("KURUL_SMTP_URL", ""),
            mail_from=e("KURUL_MAIL_FROM", "") or "Knotenlinie Board <board@invalid>",
        )
