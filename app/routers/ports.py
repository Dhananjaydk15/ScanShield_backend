from fastapi import APIRouter, HTTPException
# from mod.schemas import PortsScanRequest, PortsScanResponse
from ..models.schemas import *
from ..services.ports_scanner import run_ports_scan
import nmap

router = APIRouter(tags=["Ports Scanner"])

@router.post("/scan_ports", response_model=PortsScanResponse, summary="Scan target ports with risk assessment")
def scan_ports_endpoint(body: PortsScanRequest):
    """
    body:
      - target: hostname or IPv4
      - port_range: e.g. "1-65535" or "80,443,8080"
      - quick_scan: boolean: scan common ports if true
    """
    try:
        result = run_ports_scan(body.target, port_range=body.port_range, quick_scan=body.quick_scan)
        return result
    except nmap.PortScannerError as e:
        raise HTTPException(status_code=500, detail=f"Nmap error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
