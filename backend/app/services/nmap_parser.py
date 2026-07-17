import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import re
import os


KNOWN_VULNERABLE_SERVICES = {
    "telnet": {"risk": "high", "reason": "Telnet transmits data in plaintext, including credentials."},
    "ftp": {"risk": "medium", "reason": "FTP transmits data including credentials in plaintext."},
    "rlogin": {"risk": "high", "reason": "Rlogin allows unauthenticated remote login with minimal encryption."},
    "rsh": {"risk": "high", "reason": "Remote shell uses unencrypted connections."},
    "finger": {"risk": "medium", "reason": "Finger service exposes user information."},
    "netstat": {"risk": "medium", "reason": "Network information service can reveal topology."},
    "smtp": {"risk": "low", "reason": "SMTP should be reviewed for open relay configuration."},
    "pop3": {"risk": "medium", "reason": "POP3 transmits credentials in plaintext unless using SSL."},
    "imap": {"risk": "medium", "reason": "IMAP transmits credentials in plaintext unless using SSL."},
    "snmp": {"risk": "medium", "reason": "SNMP with default community strings is a common attack vector."},
    "mysql": {"risk": "medium", "reason": "Database service exposed — ensure strong auth and firewall rules."},
    "ms-sql-s": {"risk": "high", "reason": "MSSQL exposed to network — high-value target for attackers."},
    "rdp": {"risk": "high", "reason": "RDP is frequently targeted by brute-force and exploit attacks."},
    "vnc": {"risk": "high", "reason": "VNC may lack encryption and is a common attack vector."},
    "x11": {"risk": "medium", "reason": "X11 forwarding can allow unauthorized display access."},
    "afp": {"risk": "medium", "reason": "Apple Filing Protocol may expose file shares."},
    "smb": {"risk": "high", "reason": "SMB shares can be exploited for lateral movement and data theft."},
    "netbios-ssn": {"risk": "high", "reason": "NetBIOS is commonly exploited for information disclosure."},
    "microsoft-ds": {"risk": "high", "reason": "Direct hosting over SMB can be exploited."},
    "kpasswd": {"risk": "medium", "reason": "Kerberos password change service exposed."},
    "exec": {"risk": "high", "reason": "Remote execution service — extremely dangerous if exposed."},
    "login": {"risk": "high", "reason": "Remote login service exposed."},
    "shell": {"risk": "high", "reason": "Remote shell service exposed."},
    "sunrpc": {"risk": "medium", "reason": "RPC services can expose system information."},
    "mountd": {"risk": "medium", "reason": "NFS mount daemon can reveal shared filesystems."},
    "nfs": {"risk": "medium", "reason": "NFS shares may be accessible to unauthorized users."},
}

SERVICE_VERSION_PATTERNS = [
    (r"Apache/(\d+\.\d+)", "Apache", 2.4, 4.6, "high"),
    (r"nginx/(\d+\.\d+)", "Nginx", 1.10, 1.25, "medium"),
    (r"OpenSSH/(\d+\.\d+)", "OpenSSH", 7.0, 9.6, "low"),
    (r"ProFTPD/(\d+\.\d+)", "ProFTPD", 1.3, 1.4, "medium"),
    (r"vsftpd/(\d+\.\d+)", "vsftpd", 2.3, 3.1, "low"),
    (r"MySQL/(\d+\.\d+)", "MySQL", 5.5, 8.0, "high"),
    (r"PostgreSQL/(\d+\.\d+)", "PostgreSQL", 9.0, 16.0, "medium"),
    (r"Microsoft-IIS/(\d+\.\d+)", "IIS", 8.0, 10.0, "high"),
    (r"Samba/(\d+\.\d+)", "Samba", 3.0, 4.19, "high"),
    (r"Sendmail/(\d+\.\d+)", "Sendmail", 8.0, 8.18, "medium"),
]


def parse_nmap_xml(file_path: str) -> Dict:
    """Parse nmap XML output and extract structured data."""
    tree = ET.parse(file_path)
    root = tree.getroot()

    result = {
        "scanner": root.get("scanner", "nmap"),
        "args": root.get("args", ""),
        "start_time": datetime.fromtimestamp(int(root.get("start", 0))).isoformat() if root.get("start") else None,
        "scan_info": {},
        "hosts": [],
        "stats": {
            "hosts_up": 0,
            "hosts_down": 0,
            "total_ports_scanned": 0,
        },
    }

    scan_info = root.find("scaninfo")
    if scan_info is not None:
        result["scan_info"] = {
            "protocol": scan_info.get("protocol"),
            "num_services": scan_info.get("numservices"),
        }

    all_ports = []

    for host in root.findall("host"):
        host_data = {
            "status": host.find("status").get("state") if host.find("status") is not None else "unknown",
            "addresses": [],
            "hostnames": [],
            "ports": [],
        }

        if host_data["status"] == "up":
            result["stats"]["hosts_up"] += 1
        else:
            result["stats"]["hosts_down"] += 1

        for addr in host.findall("address"):
            host_data["addresses"].append({
                "type": addr.get("addrtype"),
                "address": addr.get("addr"),
            })

        for hostname in host.findall(".//hostname"):
            host_data["hostnames"].append(hostname.get("name"))

        ports_elem = host.find("ports")
        if ports_elem is not None:
            for port in ports_elem.findall("port"):
                port_data = parse_port(port)
                host_data["ports"].append(port_data)
                all_ports.append(port_data)
                result["stats"]["total_ports_scanned"] += 1

        if host_data["ports"]:
            result["hosts"].append(host_data)

    result["stats"]["total_unique_ports"] = len(set(
        (p["port_number"], p["protocol"]) for p in all_ports
    ))

    result["ports"] = all_ports

    return result


def parse_port(port_elem) -> Dict:
    """Parse a single port element."""
    state_elem = port_elem.find("state")
    service_elem = port_elem.find("service")
    scripts = port_elem.findall("script")

    port_data = {
        "port_number": int(port_elem.get("portid")),
        "protocol": port_elem.get("protocol", "tcp"),
        "state": state_elem.get("state") if state_elem is not None else "unknown",
        "reason": state_elem.get("reason") if state_elem is not None else "",
        "service": service_elem.get("name") if service_elem is not None else None,
        "product": service_elem.get("product") if service_elem is not None else None,
        "version": service_elem.get("version") if service_elem is not None else None,
        "extra_info": service_elem.get("extrainfo") if service_elem is not None else None,
        "cpe": [cpe.text for cpe in service_elem.findall("cpe")] if service_elem is not None else [],
        "scripts": [],
        "is_outdated": False,
        "risk_level": "low",
    }

    for script in scripts:
        port_data["scripts"].append({
            "id": script.get("id"),
            "output": script.get("output"),
        })

    port_data["banner"] = port_data["product"]
    if port_data["version"]:
        port_data["banner"] = f"{port_data['product']} {port_data['version']}"

    if port_data["state"] == "open":
        svc = (port_data["service"] or "").lower()
        if svc in KNOWN_VULNERABLE_SERVICES:
            vinfo = KNOWN_VULNERABLE_SERVICES[svc]
            port_data["risk_level"] = vinfo["risk"]
        elif port_data["port_number"] in (21, 23, 25, 53, 110, 143, 445, 1433, 3306, 3389, 5432, 5900):
            port_data["risk_level"] = "medium"

        if port_data["product"] and port_data["version"]:
            port_data["is_outdated"] = check_version_outdated(
                port_data["product"], port_data["version"]
            )
            if port_data["is_outdated"]:
                port_data["risk_level"] = "high"

    return port_data


def check_version_outdated(product: str, version: str) -> bool:
    """Check if a software version is potentially outdated."""
    try:
        ver_parts = [int(x) for x in version.split(".")[:2]]
        if len(ver_parts) < 2:
            return False

        for pattern, name, min_ver, max_ver, _ in SERVICE_VERSION_PATTERNS:
            if product and name.lower() in product.lower():
                ver_num = ver_parts[0] + ver_parts[1] / 100
                return ver_num < min_ver or ver_num > max_ver + 1
    except (ValueError, TypeError):
        pass
    return False


def calculate_risk_score(ports: List[Dict]) -> int:
    """Calculate overall risk score 0-100."""
    if not ports:
        return 0

    open_ports = [p for p in ports if p["state"] == "open"]
    if not open_ports:
        return 0

    score = 0

    risk_weights = {"critical": 30, "high": 20, "medium": 10, "low": 3}
    for port in open_ports:
        level = port.get("risk_level", "low")
        score += risk_weights.get(level, 3)

    vulnerable_ports = [p for p in open_ports if p["is_outdated"]]
    score += len(vulnerable_ports) * 10

    high_risk_services = [p for p in open_ports if p.get("risk_level") in ("high", "critical")]
    if len(high_risk_services) >= 3:
        score += 15

    common_attack_ports = [21, 23, 445, 3389, 5900, 1433, 3306]
    exposed_attack_ports = [p for p in open_ports if p["port_number"] in common_attack_ports]
    score += len(exposed_attack_ports) * 8

    return min(score, 100)


def get_risk_label(score: int) -> str:
    """Return risk label for score."""
    if score >= 80:
        return "critical"
    elif score >= 60:
        return "high"
    elif score >= 40:
        return "medium"
    elif score >= 20:
        return "low"
    return "minimal"
