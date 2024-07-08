from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import logging
from typing import Union, Optional
import ipaddress
import time

app = FastAPI()

logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class IPResponse:
    def __init__(self, ip: str, ip_type: str):
        self.ip = ip
        self.type = ip_type

def get_ip_from_headers(request: Request, header_name: str) -> Optional[str]:
    header_value = request.headers.get(header_name)
    if header_value:
        return header_value.split(",")[0].strip()
    return None

def get_ip(request: Request) -> str:
    ip = get_ip_from_headers(request, "X-Forwarded-For")
    if ip:
        return ip

    ip = get_ip_from_headers(request, "X-Real-IP")
    if ip:
        return ip

    return request.client.host

def get_specific_ip(request: Request, ip_type: str) -> Optional[str]:
    xff = request.headers.get("X-Forwarded-For")
    if xff:
        for ip in xff.split(","):
            parsed_ip = ipaddress.ip_address(ip.strip())
            if (ip_type == "ipv4" and parsed_ip.version == 4) or (ip_type == "ipv6" and parsed_ip.version == 6):
                return str(parsed_ip)

    xri = request.headers.get("X-Real-IP")
    if xri:
        parsed_ip = ipaddress.ip_address(xri)
        if (ip_type == "ipv4" and parsed_ip.version == 4) or (ip_type == "ipv6" and parsed_ip.version == 6):
            return str(parsed_ip)

    client_host = request.client.host
    parsed_ip = ipaddress.ip_address(client_host)
    if (ip_type == "ipv4" and parsed_ip.version == 4) or (ip_type == "ipv6" and parsed_ip.version == 6):
        return str(parsed_ip)

    return None

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logging.info(f"Handled request in {process_time:.4f} seconds")
    return response

@app.get("/")
async def read_root(request: Request):
    ip_type_header = request.headers.get("ip_type")
    ip = get_specific_ip(request, ip_type_header) if ip_type_header in ["ipv4", "ipv6"] else get_ip(request)

    if not ip:
        logging.error(f"Unable to determine IP address from request: {request}")
        raise HTTPException(status_code=500, detail="Unable to determine IP address")

    ip_type = "IPV6" if ipaddress.ip_address(ip).version == 6 else "IPV4"
    response = IPResponse(ip=ip, ip_type=ip_type)

    logging.info(f"Request from IP: {ip} ({ip_type})")

    return JSONResponse(content=response.__dict__)

@app.head("/")
async def read_root_head(request: Request):
    return JSONResponse(content=None, status_code=200)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9005)
