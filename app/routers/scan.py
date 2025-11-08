from fastapi import APIRouter, HTTPException
from ..models.schemas import ScanRequest
from ..services.scanner import scan_security_headers
import nmap

router = APIRouter(prefix="/scan", tags=["Nmap Scanner"])

@router.get("/", summary="Usage info")
def get_usage_info():
    return {
        "info": "POST /scan to perform an Nmap security header scan.",
        "example": {
            "target": "example.com",
            "ports": "80,443"
        }
    }


@router.post("/", summary="Scan target for HTTP Security Headers")
def run_scan(request: ScanRequest):
    try:
        result = scan_security_headers(request.target, request.ports)
        return result
    except nmap.PortScannerError as e:
        raise HTTPException(status_code=500, detail=f"Nmap error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



