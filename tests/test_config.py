"""配置模块测试"""

import pytest
from config import Config


def test_config_validation_missing_fields():
    """测试缺少必填字段"""
    config = Config()
    errors = config.validate()

    assert len(errors) > 0
    assert any("username" in err for err in errors)
    assert any("password" in err for err in errors)
    assert any("path" in err for err in errors)
    assert any("rss" in err for err in errors)


def test_config_validation_invalid_email():
    """测试无效邮箱格式"""
    config = Config(
        username="invalid_email",
        password="password",
        path="path",
        rss="http://test.com",
    )
    errors = config.validate()

    assert any("username" in err for err in errors)


def test_config_validation_valid():
    """测试有效配置"""
    config = Config(
        username="test@example.com",
        password="password123",
        path="folder_id",
        rss="https://mikanani.me/RSS/MyBangumi?token=test",
    )
    errors = config.validate()

    assert len(errors) == 0


def test_config_validation_proxy_enabled_no_proxy():
    """测试启用代理但未配置代理地址"""
    config = Config(
        username="test@example.com",
        password="password123",
        path="folder_id",
        rss="https://mikanani.me/RSS/MyBangumi?token=test",
        enable_proxy=True,
        http_proxy="",
        https_proxy="",
        socks_proxy="",
    )
    errors = config.validate()

    # 启用代理但没有代理地址应该不报错（可能使用环境变量）
    assert len(errors) == 0


def test_config_validation_invalid_proxy():
    """测试无效代理格式"""
    config = Config(
        username="test@example.com",
        password="password123",
        path="folder_id",
        rss="https://mikanani.me/RSS/MyBangumi?token=test",
        enable_proxy=True,
        http_proxy="invalid_proxy",
    )
    errors = config.validate()

    assert any("http_proxy" in err for err in errors)


def test_config_validation_invalid_rss_interval():
    """测试无效的 RSS 检查间隔"""
    config = Config(
        username="test@example.com",
        password="password123",
        path="folder_id",
        rss="https://mikanani.me/RSS/MyBangumi?token=test",
        rss_check_interval=30,  # 太小
    )
    errors = config.validate()

    assert any("rss_check_interval" in err for err in errors)


def test_config_validation_invalid_log_level():
    """测试无效的日志级别"""
    config = Config(
        username="test@example.com",
        password="password123",
        path="folder_id",
        rss="https://mikanani.me/RSS/MyBangumi?token=test",
        log_level="INVALID",
    )
    errors = config.validate()

    assert any("log_level" in err for err in errors)


def test_config_email_validation():
    """测试邮箱格式验证"""
    assert Config._is_valid_email("test@example.com") is True
    assert Config._is_valid_email("invalid_email") is False
    assert Config._is_valid_email("test@") is False
    assert Config._is_valid_email("@example.com") is False


def test_config_url_validation():
    """测试 URL 格式验证"""
    assert Config._is_valid_url("https://example.com") is True
    assert Config._is_valid_url("http://example.com/path") is True
    assert Config._is_valid_url("invalid_url") is False
    assert Config._is_valid_url("example.com") is False


def test_config_proxy_url_validation():
    """测试代理 URL 格式验证"""
    assert Config._is_valid_proxy_url("http://127.0.0.1:7890", "http") is True
    assert Config._is_valid_proxy_url("https://127.0.0.1:7890", "http") is True
    assert Config._is_valid_proxy_url("socks5://127.0.0.1:7890", "socks") is True
    assert Config._is_valid_proxy_url("invalid_proxy", "http") is False
