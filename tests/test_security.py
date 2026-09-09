import pytest
from app.security import validate_platform_url


def test_kuaishou_dynamic_share_subdomain():
    url = 'https://kph8gvfz.m.chenzhongtech.com/fw/photo/example'
    assert validate_platform_url(url) == url
    with pytest.raises(ValueError):
        validate_platform_url('https://m.chenzhongtech.com.example.org/fw/photo/example')
