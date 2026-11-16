from __future__ import annotations

import importlib

import sys

import pytest
from participium.core.exceptions import AuthorizationError, ValidationError
from participium.models.enums import Role
from participium.models.message import Message
from participium.models.report import Report
from participium.models.user import User
from participium.services.messaging_service import MessagingService
from unittest.mock import Mock



def _user(role, cat_id,user_id):
    return User(role=role, category_id=cat_id,id=user_id)

def _report(reporter_id,category_id):
    return Report(reporter_id=reporter_id,category_id=category_id)


@pytest.fixture
def service():
    message_repository = Mock()
    session = Mock()
    notification_service = Mock()

    return MessagingService(
        message_repository=message_repository,
        session=session,
        notification_service=notification_service
    )


def test_can_access_thread_none_case(service):
    service=service
    report=_report(1,2)
    assert service.can_access_thread(report,None)==False



def test_can_access_thread_admin(service):
    service=service
    report=_report(1,2)
    user_admin=_user(role=Role.ADMIN,cat_id=1,user_id=1)
    assert service.can_access_thread(report,user_admin)==True


def test_can_access_thread_operator_and_diff_cat_same_id(service):
    service=service
    report=_report(1,2)
    operator=_user(role=Role.OPERATOR,cat_id=3,user_id=1)
    assert service.can_access_thread(report,operator)==True

def test_can_access_thread_operator_same_cat(service):
    service=service
    report=_report(1,2)
    operator=_user(role=Role.OPERATOR,cat_id=2,user_id=2)
    assert service.can_access_thread(report,operator)==True

def test_can_access_thread_operator_and_diff_cat_diff_id(service):
    service=service
    report=_report(1,2)
    operator=_user(role=Role.OPERATOR,cat_id=3,user_id=4)
    assert service.can_access_thread(report,operator)==False


def test_send_message_body_empty(service,monkeypatch):
    monkeypatch.setattr(service,"_resolve_recipient",lambda *args: _user(role=Role.ADMIN,cat_id=1,user_id=200))
    monkeypatch.setattr(service,"can_access_thread",lambda *args: True)
    report=_report(1,2)
    user=_user(role=Role.ADMIN,cat_id=1,user_id=1)
    with pytest.raises(ValidationError):
        service.send_message(report,user,"")

def test_send_message_body_empty_and_no_recipient(service,monkeypatch):
    monkeypatch.setattr(service,"_resolve_recipient",lambda *args: None)
    monkeypatch.setattr(service,"can_access_thread",lambda *args: True)
    report=_report(1,2)
    user=_user(role=Role.ADMIN,cat_id=1,user_id=1)
    with pytest.raises(ValidationError, match="Message body cannot be empty."):
        service.send_message(report,user,"")


def test_send_message_cannot_access(service,monkeypatch):
    monkeypatch.setattr(service,"_resolve_recipient",lambda *args: _user(role=Role.ADMIN,cat_id=1,user_id=200))
    monkeypatch.setattr(service,"can_access_thread",lambda *args: False)
    report=_report(1,2)
    user=_user(role=Role.ADMIN,cat_id=1,user_id=1)
    with pytest.raises(AuthorizationError):
        service.send_message(report,user,"ciao")

def test_send_message_cannot_access_recipient_none(service,monkeypatch):
    monkeypatch.setattr(service,"_resolve_recipient",lambda *args: None)
    monkeypatch.setattr(service,"can_access_thread",lambda *args: True)
    report=_report(1,2)
    user=_user(role=Role.ADMIN,cat_id=1,user_id=1)
    with pytest.raises(ValidationError):
        service.send_message(report,user,"ciao")


def test_send_message_success(service,monkeypatch):
    monkeypatch.setattr(service,"_resolve_recipient",lambda *args: _user(role=Role.ADMIN,cat_id=1,user_id=200))
    monkeypatch.setattr(service,"can_access_thread",lambda *args: True)
    report=Report(id=3)
    user=_user(role=Role.ADMIN,cat_id=1,user_id=1)
    message = service.send_message(report,user,"ciao")
    assert message.recipient_id==200
    assert message.sender_id==1
    assert message.report_id==3