
import pytest
import importlib.util, sys, pathlib
import  os
from flask import Flask

from unittest.mock import Mock
from participium.core.exceptions import AuthenticationError, AuthorizationError
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
AUTH_PATH = os.path.join(BASE_DIR, "backend", "participium", "core", "auth.py")

if not os.path.exists(AUTH_PATH):
    raise FileNotFoundError(f"Non trovo auth.py in: {AUTH_PATH}")





#sys.modules["participium.core.exceptions"] = exceptions_mock

spec = importlib.util.spec_from_file_location("participium.core.auth", AUTH_PATH)
auth = importlib.util.module_from_spec(spec)
sys.modules["auth"] = auth
spec.loader.exec_module(auth)


def stub_current_user_none():
    return None

def stub_current_user_is_admin():
    user=Mock()
    user.role="ADMIN"
    return user

def stub_current_user_is_citizen():
    user=Mock()
    user.role="CITIZEN"
    return user


def test_login_required_successfull(monkeypatch):
    app = Flask(__name__)
    monkeypatch.setattr(auth, "current_user", stub_current_user_is_admin)
    with app.test_request_context(path="/"):
        login_required=auth.login_required
        def my_view():
            return "OK"
        wrapped_view=login_required(my_view)
        assert wrapped_view() == "OK"


def test_login_required_authentication_error(monkeypatch):
    app = Flask(__name__)
    monkeypatch.setattr(auth, "current_user", stub_current_user_none)
    with app.test_request_context(path="/api/.c."):
        login_required = auth.login_required
        def my_view():
            return "OK"
        wrapped_view=login_required(my_view)
        with pytest.raises(AuthenticationError):
            wrapped_view()



def test_login_required_redirect(monkeypatch):
    app = Flask(__name__)
    monkeypatch.setattr(auth, "current_user", stub_current_user_none)
    app.add_url_rule("/login", endpoint="web.login")
    with app.test_request_context(path="/ciao"):
        login_required = auth.login_required

        def my_view():
            return "OK"

        wrapped_view = login_required(my_view)
        response = wrapped_view()

        assert response.status_code == 302
        assert "/login" in response.location
        assert "next=" in response.location
        assert "/ciao" in response.location




def test_roles_required_success(monkeypatch):
    app = Flask(__name__)
    monkeypatch.setattr(auth, "current_user", stub_current_user_is_admin)
    roles_required = auth.roles_required
    def my_view():
        return "SUCCESS"
    wrapped_view = roles_required("ADMIN","OPERATOR")(my_view)
    assert wrapped_view() == "SUCCESS"


def test_roles_required_authentication_error(monkeypatch):
    app = Flask(__name__)
    monkeypatch.setattr(auth, "current_user", stub_current_user_none)
    roles_required = auth.roles_required
    def my_view():
        return "SUCCESS"
    wrapped_view = roles_required("ADMIN","OPERATOR")(my_view)
    with pytest.raises(AuthenticationError):
        wrapped_view()



def test_roles_required_authorization_error(monkeypatch):
    app = Flask(__name__)
    monkeypatch.setattr(auth, "current_user", stub_current_user_is_citizen)
    roles_required = auth.roles_required
    def my_view():
        return "SUCCESS"
    wrapped_view = roles_required("ADMIN","OPERATOR")(my_view)
    with pytest.raises(AuthorizationError):
        wrapped_view()