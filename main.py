from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import logging
from typing import Union
import ipaddress
import time

app = FastAPI()

logging.basicConfig(filename='app.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

class IPResponse:
    def __init__(self, ip: str, ip_type: str):
        self.ip = ip
        self.type = ip_type

def get_ip(request: Request) -> str:
    xff = request.headers.get("X-Forwarded-For")
    if xff:
        return xff.split(",")[0].strip()

    xri = request.headers.get("X-Real-IP")
    if xri:
        return xri

    client_host = request.client.host
    return client_host

def get_specific_ip(request: Request, ip_type: str) -> Union[str, None]:
    xff = request.headers.get("X-Forwarded-For")
    if xff:
        for ip in xff.split(","):
            trimmed_ip = ip.strip()
            parsed_ip = ipaddress.ip_address(trimmed_ip)
            if (ip_type == "ipv4" and parsed_ip.version == 4) or (ip_type == "ipv6" and parsed_ip.version == 6):
                return trimmed_ip

    xri = request.headers.get("X-Real-IP")
    if xri:
        parsed_ip = ipaddress.ip_address(xri)
        if (ip_type == "ipv4" and parsed_ip.version == 4) or (ip_type == "ipv6" and parsed_ip.version == 6):
            return xri

    client_host = request.client.host
    parsed_ip = ipaddress.ip_address(client_host)
    if (ip_type == "ipv4" and parsed_ip.version == 4) or (ip_type == "ipv6" and parsed_ip.version == 6):
        return client_host

    return None

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logging.info(f"Handled request in {process_time} seconds")
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9005)
