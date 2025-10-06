from backend import validators
def test_ip_valid():
    assert validators.is_valid_ip('127.0.0.1')
    assert not validators.is_valid_ip('999.999.999.999')
def test_allowlist():
    al = ['192.168.0.0/16','10.0.0.5']
    assert validators.is_ip_in_allowlist('10.0.0.5', al)
    assert validators.is_ip_in_allowlist('192.168.1.1', al)
    assert not validators.is_ip_in_allowlist('8.8.8.8', al)
