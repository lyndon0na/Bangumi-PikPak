"""通知模块测试"""

import pytest
from unittest.mock import Mock, patch
from notifier import Notifier
from config import Config


def test_notifier_disabled():
    """测试通知功能禁用"""
    config = Config(
        username="test@example.com",
        password="password",
        path="path",
        rss="http://test.com",
        enable_notifications=False,
    )
    notifier = Notifier(config)

    result = notifier.send("Test", "Message")
    assert result is True  # 禁用时返回 True


def test_notifier_no_url():
    """测试未配置通知 URL"""
    config = Config(
        username="test@example.com",
        password="password",
        path="path",
        rss="http://test.com",
        enable_notifications=True,
        ntfy_url="",
    )
    notifier = Notifier(config)

    result = notifier.send("Test", "Message")
    assert result is False


@patch("notifier.requests.post")
def test_notifier_send_success(mock_post):
    """测试通知发送成功"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    config = Config(
        username="test@example.com",
        password="password",
        path="path",
        rss="http://test.com",
        enable_notifications=True,
        ntfy_url="https://ntfy.sh/test",
    )
    notifier = Notifier(config)

    result = notifier.send("Test Title", "Test Message")
    assert result is True

    mock_post.assert_called_once()
    assert mock_post.call_args[1]["headers"]["Title"] == "Test Title"


@patch("notifier.requests.post")
def test_notifier_send_failure(mock_post):
    """测试通知发送失败"""
    mock_response = Mock()
    mock_response.status_code = 500
    mock_post.return_value = mock_response

    config = Config(
        username="test@example.com",
        password="password",
        path="path",
        rss="http://test.com",
        enable_notifications=True,
        ntfy_url="https://ntfy.sh/test",
    )
    notifier = Notifier(config)

    result = notifier.send("Test", "Message")
    assert result is False


def test_notifier_special_methods():
    """测试特殊通知方法"""
    config = Config(
        username="test@example.com",
        password="password",
        path="path",
        rss="http://test.com",
        enable_notifications=False,
    )
    notifier = Notifier(config)

    # 禁用通知时，所有特殊方法都应该返回 True
    assert notifier.send_bangumi_update("Test Anime") is True
    assert notifier.send_task_created("Test Task") is True
    assert notifier.send_error("Test Error") is True
