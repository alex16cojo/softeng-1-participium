from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from participium.services.email_service import (
    BaseEmailGateway,
    ConsoleEmailGateway,
    SmtpEmailGateway,
    build_email_gateway,
)


# -------------------------
# Tests: BaseEmailGateway
# -------------------------

def test_base_email_gateway_send(capsys):
    gateway = BaseEmailGateway()

    gateway.send(
        recipient="test@example.com",
        subject="Hello",
        body="World",
    )

    captured = capsys.readouterr()

    assert "Simulating email send operation." in captured.out


# -------------------------
# Tests: ConsoleEmailGateway
# -------------------------

def test_console_email_gateway_creates_outbox(tmp_path):
    outbox_dir = tmp_path / "outbox"

    ConsoleEmailGateway(
        outbox_dir=outbox_dir,
        sender="noreply@example.com",
    )

    assert outbox_dir.exists()
    assert outbox_dir.is_dir()


@patch("participium.services.email_service.uuid4")
def test_console_email_gateway_send(mock_uuid, tmp_path):
    mock_uuid.return_value.hex = "abc123"

    outbox_dir = tmp_path / "outbox"

    gateway = ConsoleEmailGateway(
        outbox_dir=outbox_dir,
        sender="noreply@example.com",
    )

    gateway.send(
        recipient="mario@example.com",
        subject="Welcome",
        body="Hello Mario",
    )

    output_file = outbox_dir / "abc123.txt"

    assert output_file.exists()

    content = output_file.read_text(encoding="utf-8")

    assert "FROM: noreply@example.com" in content
    assert "TO: mario@example.com" in content
    assert "SUBJECT: Welcome" in content
    assert "Hello Mario" in content


# -------------------------
# Tests: SmtpEmailGateway
# -------------------------

@patch("participium.services.email_service.smtplib.SMTP")
def test_smtp_email_gateway_send_without_auth(mock_smtp):
    smtp_instance = MagicMock()

    mock_smtp.return_value.__enter__.return_value = smtp_instance

    gateway = SmtpEmailGateway(
        host="smtp.example.com",
        port=587,
        username=None,
        password=None,
        sender="noreply@example.com",
        use_tls=True,
    )

    gateway.send(
        recipient="user@example.com",
        subject="Test Subject",
        body="Test Body",
    )

    mock_smtp.assert_called_once_with(
        "smtp.example.com",
        587,
        timeout=10,
    )

    smtp_instance.starttls.assert_called_once()
    smtp_instance.login.assert_not_called()
    smtp_instance.send_message.assert_called_once()


@patch("participium.services.email_service.smtplib.SMTP")
def test_smtp_email_gateway_send_with_auth(mock_smtp):
    smtp_instance = MagicMock()

    mock_smtp.return_value.__enter__.return_value = smtp_instance

    gateway = SmtpEmailGateway(
        host="smtp.example.com",
        port=587,
        username="admin",
        password="secret",
        sender="noreply@example.com",
        use_tls=True,
    )

    gateway.send(
        recipient="user@example.com",
        subject="Subject",
        body="Body",
    )

    smtp_instance.starttls.assert_called_once()

    smtp_instance.login.assert_called_once_with(
        "admin",
        "secret",
    )

    smtp_instance.send_message.assert_called_once()


@patch("participium.services.email_service.smtplib.SMTP")
def test_smtp_email_gateway_send_without_tls(mock_smtp):
    smtp_instance = MagicMock()

    mock_smtp.return_value.__enter__.return_value = smtp_instance

    gateway = SmtpEmailGateway(
        host="smtp.example.com",
        port=25,
        username=None,
        password=None,
        sender="noreply@example.com",
        use_tls=False,
    )

    gateway.send(
        recipient="user@example.com",
        subject="Subject",
        body="Body",
    )

    smtp_instance.starttls.assert_not_called()
    smtp_instance.send_message.assert_called_once()


# -------------------------
# Tests: build_email_gateway
# -------------------------

class DummySettings:
    def __init__(
        self,
        mail_backend="console",
        smtp_host=None,
        smtp_port=587,
        smtp_username=None,
        smtp_password=None,
        smtp_use_tls=True,
        mail_from="noreply@example.com",
        mail_outbox_dir=Path("/tmp/outbox"),
    ):
        self.mail_backend = mail_backend
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.smtp_use_tls = smtp_use_tls
        self.mail_from = mail_from
        self.mail_outbox_dir = mail_outbox_dir


def test_build_email_gateway_smtp():
    settings = DummySettings(
        mail_backend="smtp",
        smtp_host="smtp.example.com",
    )

    gateway = build_email_gateway(settings)

    assert isinstance(gateway, SmtpEmailGateway)

    assert gateway.host == "smtp.example.com"
    assert gateway.port == 587
    assert gateway.sender == "noreply@example.com"


def test_build_email_gateway_console(tmp_path):
    settings = DummySettings(
        mail_backend="console",
        smtp_host=None,
        mail_outbox_dir=tmp_path / "outbox",
    )

    gateway = build_email_gateway(settings)

    assert isinstance(gateway, ConsoleEmailGateway)

    assert gateway.outbox_dir == settings.mail_outbox_dir
    assert gateway.sender == "noreply@example.com"