import nmap
from typing import Dict, List
from ..models import schemas
import re

# High & Medium risk maps (copied/adapted from your script)
HIGH_RISK_PORTS = {
    21: {'service': 'FTP', 'risk': 'Plaintext credentials, old FTP servers have many vulnerabilities'},
    22: {'service': 'SSH', 'risk': 'Brute-force and credential reuse; outdated OpenSSH bugs'},
    23: {'service': 'Telnet', 'risk': 'Cleartext auth — never use in production'},
    25: {'service': 'SMTP', 'risk': 'Open relays or vulnerable mail servers can be abused'},
    53: {'service': 'DNS', 'risk': 'DNS cache poisoning, amplification DDoS, misconfigured resolvers'},
    69: {'service': 'TFTP', 'risk': 'No auth, used to move firmware — often abused'},
    80: {'service': 'HTTP', 'risk': 'Web app vulnerabilities (XSS, SQLi, RCE); exposed admin panels'},
    110: {'service': 'POP3', 'risk': 'Mail servers with weak auth, plaintext variants are risky'},
    143: {'service': 'IMAP', 'risk': 'Mail servers with weak auth, plaintext variants are risky'},
    443: {'service': 'HTTPS', 'risk': 'Web app vulnerabilities; check for security headers'},
    445: {'service': 'SMB', 'risk': 'Ransomware, worm exploits'},
    3306: {'service': 'MySQL', 'risk': 'Unprotected DB access leaks data'},
    3389: {'service': 'RDP', 'risk': 'Brute force; targeted by attackers'},
    5432: {'service': 'PostgreSQL', 'risk': 'Exposed DB risk'},
    5900: {'service': 'VNC', 'risk': 'Often unencrypted auth; default passwords'},
    6379: {'service': 'Redis', 'risk': 'No auth by default in many setups'},
    8080: {'service': 'HTTP-Proxy', 'risk': 'Alternative HTTP port, same web vulnerabilities'},
    9200: {'service': 'Elasticsearch', 'risk': 'Exposed indices / RCE / data leak'},
    27017: {'service': 'MongoDB', 'risk': 'Open MongoDBs have been wiped/held ransom'},
    2375: {'service': 'Docker API', 'risk': 'Unauthenticated Docker API allows container control'},
}

MEDIUM_RISK_PORTS = {
    161: {'service': 'SNMP', 'risk': 'Misconfigured community strings leak network info'},
    162: {'service': 'SNMP Trap', 'risk': 'SNMP trap service, check for default communities'},
    123: {'service': 'NTP', 'risk': 'Can be abused for amplification DDoS if misconfigured'},
    389: {'service': 'LDAP', 'risk': 'LDAP injection or misconfig can leak auth info'},
    636: {'service': 'LDAPS', 'risk': 'Secure LDAP but check for weak ciphers'},
    11211: {'service': 'Memcached', 'risk': 'DDoS amplification & data exposure'},
}

# Security headers set (same as earlier)
SECURITY_HEADERS = {
    'Content-Security-Policy': {'purpose': 'Prevents XSS', 'example': "default-src 'self'"},
    'Strict-Transport-Security': {'purpose': 'Forces HTTPS', 'example': 'max-age=63072000; includeSubDomains'},
    'X-Content-Type-Options': {'purpose': 'Stops MIME sniffing', 'example': 'nosniff'},
    'X-Frame-Options': {'purpose': 'Prevents clickjacking', 'example': 'DENY'},
    'X-XSS-Protection': {'purpose': 'Legacy XSS protection header', 'example': '1; mode=block'},
    'Referrer-Policy': {'purpose': 'Controls referrer', 'example': 'no-referrer-when-downgrade'},
    'Permissions-Policy': {'purpose': 'Controls features', 'example': 'camera=()'},
    'Cross-Origin-Opener-Policy': {'purpose': 'Isolates browsing context', 'example': 'same-origin'},
    'Cross-Origin-Resource-Policy': {'purpose': 'Blocks other origins', 'example': 'same-origin'},
    'Cross-Origin-Embedder-Policy': {'purpose': 'Requires corp or same-origin', 'example': 'require-corp'},
}

COMMON_PORTS_QUICK = "21-23,25,53,69,80,110,143,443,445,3306,3389,5432,5900,6379,8080,9200,27017"

def get_port_risk_level(port: int):
    if port in HIGH_RISK_PORTS:
        return "HIGH", HIGH_RISK_PORTS[port]
    if port in MEDIUM_RISK_PORTS:
        return "MEDIUM", MEDIUM_RISK_PORTS[port]
    return "LOW", {"service": "Unknown", "risk": "Unknown service"}

def parse_headers_from_script(script_output: str) -> Dict[str, str]:
    headers = {}
    if not script_output:
        return headers
    for line in script_output.strip().split("\n"):
        if ":" in line:
            k, v = line.split(":", 1)
            headers[k.strip()] = v.strip()
    return headers

def check_security_headers(headers: Dict[str, str]):
    present = []
    missing = []
    lower = {k.lower(): v for k, v in headers.items()}
    for h, meta in SECURITY_HEADERS.items():
        if h.lower() in lower:
            present.append({"header": h, "value": headers.get(h, lower.get(h.lower())), "purpose": meta["purpose"]})
        else:
            missing.append({"header": h, "purpose": meta["purpose"], "recommended": meta["example"]})
    return present, missing

def run_ports_scan(target: str, port_range: str = "1-65535", quick_scan: bool = False) -> dict:
    nm = nmap.PortScanner()
    ports = COMMON_PORTS_QUICK if quick_scan else port_range

    # run nmap with service detection and scripts for banner + http-headers
    nm.scan(hosts=target, ports=ports, arguments='-sV -sC --script=banner,http-headers')

    result_hosts = []

    total_open = 0
    for host in nm.all_hosts():
        host_entry = {
            "host": host,
            "hostname": nm[host].hostname(),
            "state": nm[host].state(),
            "protocols": []
        }

        for proto in nm[host].all_protocols():
            proto_ports = []
            for port in sorted(nm[host][proto].keys()):
                port_info = nm[host][proto][port]
                if port_info.get("state") != "open":
                    continue

                total_open += 1
                risk_level, risk_data = get_port_risk_level(port)

                port_entry = {
                    "port": port,
                    "proto": proto,
                    "state": port_info.get("state"),
                    "service": port_info.get("name"),
                    "product": port_info.get("product"),
                    "version": port_info.get("version"),
                    "extrainfo": port_info.get("extrainfo"),
                    "risk_level": risk_level,
                    "risk_data": risk_data,
                    "scripts": port_info.get("script", {}),
                    "parsed_headers": None,
                    "security_headers_present": None,
                    "security_headers_missing": None,
                    "security_score": None
                }

                # If http-headers script returned output, parse and check headers
                scripts = port_info.get("script", {})
                if "http-headers" in scripts:
                    headers = parse_headers_from_script(scripts["http-headers"])
                    present, missing = check_security_headers(headers)
                    port_entry["parsed_headers"] = headers
                    port_entry["security_headers_present"] = present
                    port_entry["security_headers_missing"] = missing
                    port_entry["security_score"] = round((len(present) / len(SECURITY_HEADERS)) * 100, 2)

                proto_ports.append(port_entry)

            host_entry["protocols"].append({"protocol": proto, "ports": proto_ports})
        result_hosts.append(host_entry)

    return {
        "target": target,
        "port_range": ports,
        "total_open_ports": total_open,
        "hosts": result_hosts
    }
