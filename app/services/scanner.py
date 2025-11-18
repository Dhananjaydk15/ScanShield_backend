# services/scanner.py
from typing import Dict, Any, List
import nmap
import requests             
from requests.exceptions import RequestException

# Important HTTP Security Headers
SECURITY_HEADERS = [
    "strict-transport-security",
    "x-frame-options",
    "x-content-type-options",
    "content-security-policy",
    "referrer-policy",
    "permissions-policy",
    "x-xss-protection"
]


def _normalize_headers(headers: Dict[str, str]) -> Dict[str, str]:
    """Normalize headers (lowercase keys, trimmed values)."""
    return {k.lower(): v.strip() for k, v in headers.items()}


def _port_to_scheme(port: int) -> str:
    """Guess scheme from port."""
    if port == 443:
        return "https"
    return "http"


def _fetch_headers_via_requests(host: str, port: int, timeout: int = 6) -> Dict[str, Any]:
    """Fetch headers using HTTP request as fallback."""
    scheme = _port_to_scheme(port)
    url = f"{scheme}://{host}"
    if (scheme == "http" and port != 80) or (scheme == "https" and port != 443):
        url = f"{scheme}://{host}:{port}/"

    try:
        resp = requests.head(url, timeout=timeout, allow_redirects=True)
        if resp.status_code == 405:
            resp = requests.get(url, timeout=timeout, allow_redirects=True)
        return {
            "ok": True,
            "status": resp.status_code,
            "headers": _normalize_headers(dict(resp.headers)),
            "url": resp.url
        }
    except RequestException as e:
        return {"ok": False, "error": str(e)}


def _analyze_headers(headers: Dict[str, str]) -> Dict[str, Any]:
    """Compare existing headers to expected ones and compute vulnerability percentage."""
    present = []
    missing = []

    for h in SECURITY_HEADERS:
        if h in headers:
            present.append(h)
        else:
            missing.append(h)

    total = len(SECURITY_HEADERS)
    found = len(present)
    missing_count = len(missing)

    # Vulnerability percentage = (missing / total) * 100
    vulnerability_percentage = round((missing_count / total) * 100, 2)
    security_score = 100 - vulnerability_percentage

    return {
        "present_headers": present,
        "missing_headers": missing,
        "vulnerability_percentage": vulnerability_percentage,
        "security_score": security_score
    }


def scan_security_headers(target: str, ports: str = "80,443") -> Dict[str, Any]:
    """
    Scan target for HTTP security headers.
    Tries nmap first, falls back to direct HTTP requests.
    """
    nm = nmap.PortScanner()
    scan_args = "--script http-headers -sV"
    result = {"target": target, "ports": {}, "method": None}

    try:
        nm.scan(hosts=target, ports=ports, arguments=scan_args)
        result["method"] = "nmap"

        for host in nm.all_hosts():
            tcp_ports = nm[host].get("tcp", {})
            for port, data in tcp_ports.items():
                port = int(port)
                scripts = data.get("script", {})
                headers_found = {}

                # Try to extract headers from nmap script output
                if "http-headers" in scripts:
                    raw_output = scripts["http-headers"]
                    for line in raw_output.splitlines():
                        if ":" in line:
                            k, v = line.split(":", 1)
                            headers_found[k.strip().lower()] = v.strip()

                # Fallback to direct HTTP request
                if not headers_found:
                    response = _fetch_headers_via_requests(target, port)
                    if response.get("ok"):
                        headers_found = response["headers"]
                    else:
                        result["ports"][port] = {"error": response.get("error")}
                        continue

                analysis = _analyze_headers(headers_found)
                result["ports"][port] = {
                    "headers_found": headers_found,
                    "analysis": analysis
                }

        return result

    except nmap.PortScannerError:
        result["method"] = "requests_fallback"
        ports_list = [int(p.strip()) for p in ports.split(",") if p.strip().isdigit()]
        for port in ports_list:
            resp = _fetch_headers_via_requests(target, port)
            if resp.get("ok"):
                headers = resp["headers"]
                result["ports"][port] = {
                    "headers_found": headers,
                    "analysis": _analyze_headers(headers)
                }
            else:
                result["ports"][port] = {"error": resp.get("error")}
        return result
