import ipaddress
from typing import List

def is_valid_ip(ip: str) -> bool:
    try:
        ipaddress.ip_address(ip)
        return True
    except Exception:
        return False

def is_valid_cidr(cidr: str) -> bool:
    try:
        ipaddress.ip_network(cidr, strict=False)
        return True
    except Exception:
        return False

def is_ip_in_allowlist(ip: str, allowlist: List[str]) -> bool:
    """allowlist: list of CIDR strings or single IPs"""
    try:
        addr = ipaddress.ip_address(ip)
        for entry in allowlist:
            entry = entry.strip()
            if not entry:
                continue
            if '/' in entry:
                net = ipaddress.ip_network(entry, strict=False)
                if addr in net:
                    return True
            else:
                if addr == ipaddress.ip_address(entry):
                    return True
        return False
    except Exception:
        return False
