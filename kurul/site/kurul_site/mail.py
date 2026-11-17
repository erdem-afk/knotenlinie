"""Email: login links and the three notification kinds.

Without KURUL_SMTP_URL nothing is sent; the message (with its link) goes to the
server log, so the coordinator can still hand out links by hand.

KURUL_SMTP_URL forms:
  smtp://user:pass@host:587   (STARTTLS)
  smtps://user:pass@host:465  (implicit TLS)
  smtp://host:25              (plain, local relay)
"""

from __future__ import annotations

import logging
import smtplib
import ssl
import threading
from email.message import EmailMessage
from urllib.parse import unquote, urlsplit

log = logging.getLogger("kurul.mail")


class Mailer:
    def __init__(self, smtp_url: str, mail_from: str):
        self.smtp_url = smtp_url
        self.mail_from = mail_from
        self.sent: list[dict] = []  # kept for tests and inspection (bounded)

    @property
    def enabled(self) -> bool:
        return bool(self.smtp_url)

    def send(self, to: str, subject: str, text: str, background: bool = True) -> None:
        record = {"to": to, "subject": subject, "text": text}
        self.sent.append(record)
        del self.sent[:-200]
        if not self.enabled:
            log.warning("mail (SMTP not configured) to=%s subject=%s\n%s", to, subject, text)
            return
        if background:
            threading.Thread(target=self._deliver, args=(to, subject, text), daemon=True).start()
        else:
            self._deliver(to, subject, text)

    def _deliver(self, to: str, subject: str, text: str) -> None:
        try:
            u = urlsplit(self.smtp_url)
            msg = EmailMessage()
            msg["From"] = self.mail_from
            msg["To"] = to
            msg["Subject"] = subject
            msg.set_content(text)
            ctx = ssl.create_default_context()
            if u.scheme == "smtps":
                server = smtplib.SMTP_SSL(u.hostname, u.port or 465, context=ctx, timeout=20)
            else:
                server = smtplib.SMTP(u.hostname, u.port or 25, timeout=20)
                if (u.port or 25) != 25:
                    server.starttls(context=ctx)
            with server:
                if u.username:
                    server.login(unquote(u.username), unquote(u.password or ""))
                server.send_message(msg)
            log.info("mail sent to=%s subject=%s", to, subject)
        except Exception:
            log.exception("mail delivery failed to=%s subject=%s", to, subject)


# Notifications about runs, costs and feasibility: coordinators only, and only by real email.
COORDINATOR_KINDS = frozenset({"feasibility", "plan_approved"})


def notify(mailer: Mailer, user: dict, kind: str, subject: str, line: str, link: str) -> None:
    """The single entry point for notification emails.

    kind: 'plan_waiting' | 'answer' | 'mention' | 'feasibility' | 'plan_approved'.
    Member kinds without SMTP only log. Coordinator kinds (COORDINATOR_KINDS) never reach a member
    and do nothing at all while SMTP is not configured.
    """
    if not user or not user.get("email") or user.get("role") == "agent":
        return
    if kind in COORDINATOR_KINDS and (user.get("role") != "coordinator" or not mailer.enabled):
        return
    if user["email"].endswith("@invalid"):
        log.info("notify[%s] to user %s (no real address): %s %s", kind, user.get("id"), subject, link)
        return
    text = f"{line}\n\n{link}\n\nKnotenlinie Board\n"
    log.info("notify[%s] to user %s", kind, user.get("id"))
    mailer.send(user["email"], subject, text)
