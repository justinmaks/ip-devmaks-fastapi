# ip-devmaks-fastapi

This is a FastAPI application that retrieves and returns the IP address information of the requester. The application logs request details and the time taken to handle each request.

https://ip.devmaks.biz/

## Features

- Extracts the client's IP address from HTTP headers or the request object.
- Identifies whether the IP address is IPv4 or IPv6.
- Logs request details and processing time.
- Provides a JSON response with the IP address and its type.


## Usage

```bash
python3-m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
uvicorn main:app --reload
```

### Docker

```bash
docker build -t fastapi-app .
docker run -d -p 9005:9005 fastapi-app
```

### GET /

Retrieve the IP address information of the requester.

#### Request Headers

- `ip_type` (optional): Specify "ipv4" or "ipv6" to get a specific type of IP address.

#### Response

- **200 OK**

  ```json
  {
      "ip": "192.168.1.1",
      "type": "IPV4"
  }

- **500 Internal Server Error**

  ```json
    {
        "detail": "Unable to determine IP address"
    }
