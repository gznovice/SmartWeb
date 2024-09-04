import socket
import requests
import json

def __dns_lookup_0(domain):
    try:
        return socket.gethostbyname(domain)
    except socket.gaierror as e:
        print(f"exception found {e}")


DNS_LOOKUP_ADDR = "https://dns.google.com/resolve"
DOMAIN_REQUEST_PARAM = '{{"name":"{}", "type":"A"}}'

def __dns_lookup_1(domain):
    try:
        print(DOMAIN_REQUEST_PARAM.format(domain))
        request_param = json.loads(DOMAIN_REQUEST_PARAM.format(domain))
        print(request_param)
        response = requests.request("GET", DNS_LOOKUP_ADDR, params=request_param)
        if response.status_code == 200:
            dns_data = response.json()
            if "Answer" in dns_data:
                for answer in dns_data['Answer']:
                    return answer['data']
    except Exception as e:
        print(f"error:{e}")
        return(f"error:{e}")


def dns_lookup(domain, method):
    print(f'method:{method}')
    if method == '0':
        return __dns_lookup_0(domain)
    elif method == '1':
        return __dns_lookup_1(domain)
    else:
        return "not provided yet"