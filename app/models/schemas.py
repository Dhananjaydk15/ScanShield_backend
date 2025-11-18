from pydantic import BaseModel, Field, constr
from typing import List, Optional, Dict, Any

class ScanRequest(BaseModel):
    target: constr(strip_whitespace=True, min_length=1, max_length=255)
    ports: Optional[str] = Field("80,443", example="80,443,8080")


class PortsScanRequest(BaseModel):
    target: constr(strip_whitespace=True, min_length=1, max_length=255)
    port_range: Optional[str] = Field("1-65535", example="80,443 or 1-1000")
    quick_scan: Optional[bool] = Field(False, description="If true, scan common ports only")

class PortScriptOutput(BaseModel):
    name: str
    output: Optional[str] = None

class PortEntry(BaseModel):
    port: int
    proto: str
    state: str
    service: Optional[str] = None
    product: Optional[str] = None
    version: Optional[str] = None
    extrainfo: Optional[str] = None
    risk_level: str
    risk_data: Dict[str, str]
    scripts: Optional[Dict[str, Any]] = None
    parsed_headers: Optional[Dict[str, str]] = None
    security_headers_present: Optional[List[Dict[str, str]]] = None
    security_headers_missing: Optional[List[Dict[str, str]]] = None
    security_score: Optional[float] = None

class ProtocolEntry(BaseModel):
    protocol: str
    ports: List[PortEntry]

class HostEntry(BaseModel):
    host: str
    hostname: Optional[str] = None
    state: Optional[str] = None
    protocols: List[ProtocolEntry]

class PortsScanResponse(BaseModel):
    target: str
    port_range: str
    total_open_ports: int
    hosts: List[HostEntry]