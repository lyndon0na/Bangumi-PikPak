"""工具函数模块测试"""

import pytest
from utils import mask_sensitive_data, sanitize_filename


def test_mask_sensitive_data():
    """测试敏感数据脱敏"""
    assert mask_sensitive_data("password123", show_length=3) == "pas********"
    # 度 <= show_length 时，全部脱敏
    assert mask_sensitive_data("abc", show_length=3) == "***"
    assert mask_sensitive_data("", show_length=3) == ""
    assert mask_sensitive_data("a", show_length=3) == "*"
    assert mask_sensitive_data("1234567890", show_length=2) == "12********"


def test_sanitize_filename():
    """测试文件名清理"""
    assert sanitize_filename("normal_file.txt") == "normal_file.txt"
    assert sanitize_filename("file<name>.txt") == "file_name_.txt"
    assert sanitize_filename("file:name.txt") == "file_name.txt"
    assert sanitize_filename('file"name.txt') == "file_name.txt"
    assert sanitize_filename("file|name.txt") == "file_name.txt"
    assert sanitize_filename("file?name.txt") == "file_name.txt"
    assert sanitize_filename("file*name.txt") == "file_name.txt"
    assert sanitize_filename("  file.txt  ") == "file.txt"
