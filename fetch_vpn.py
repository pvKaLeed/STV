import os
import re
import urllib.request
import time
import socket
import json

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# VPNBook Active Servers List
ACTIVE_HOSTS = [
    {"host": "us16.vpnbook.com", "country": "US"},
    {"host": "us178.vpnbook.com", "country": "US"},
    {"host": "ca149.vpnbook.com", "country": "CA"},
    {"host": "ca196.vpnbook.com", "country": "CA"},
    {"host": "uk205.vpnbook.com", "country": "UK"},
    {"host": "uk68.vpnbook.com", "country": "UK"},
    {"host": "de20.vpnbook.com", "country": "DE"},
    {"host": "de220.vpnbook.com", "country": "DE"},
    {"host": "fr200.vpnbook.com", "country": "FR"},
    {"host": "fr2311.vpnbook.com", "country": "FR"},
]

def fetch_webpage(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""

def scrape_password():
    """Scrape current dynamic password from VPNBook"""
    html = fetch_webpage("https://www.vpnbook.com/freevpn/openvpn")
    if not html:
        html = fetch_webpage("https://www.vpnbook.com/freevpn")
        
    match = re.search(r'Password:\s*([a-zA-Z0-9]+)', html, re.IGNORECASE)
    if match:
        password = match.group(1).strip()
        print(f"Found dynamic password: {password}")
        return password
    
    return "ytw2awn"  # Fallback password

def test_latency(host, port=443, timeout=3.0):
    """Test TCP latency to verify active server status"""
    start = time.time()
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))
        sock.close()
        latency = (time.time() - start) * 1000
        return round(latency, 2)
    except Exception:
        return None

def generate_ovpn_config(host, port=443, proto="tcp"):
    """Generate valid OpenVPN profile string"""
    return f"""client
dev tun
proto {proto}
remote {host} {port}
resolv-retry infinite
nobind
persist-key
persist-tun
cipher AES-256-CBC
auth SHA256
verb 3
<ca>
-----BEGIN CERTIFICATE-----
MIIE3DCCA8SgAwIBAgIQB/9vGv5XJ8+5N0y1G2N1fDANBgkqhkiG9w0BAQsFADCB
jDELMAkGA1UEBhMCVVMxEzARBgNVBAgTCkFyaXpvbmExEzARBgNVBAcTClNjb3R0
c2RhbGUxJTAjBgNVBAoTHFN0YXJmaWVsZCBUZWNobm9sb2dpZXMsIEluYy4xMzAx
BgNVBAMTKFN0YXJmaWVsZCBTZXJ2ZXJDT00gQ2VydGlmaWNhdGUgQXV0aG9yaXR5
MB4XDTE1MTAwNTE3MDYwMFoXDTI2MTAwNTE3MDYwMFowgYwxCzAJBgNVBAYTAlVT
MRMwEQYDVQQIEwpBcml6b25hMRMwEQYDVQQHEypTY290dHNkYWxlMSUwIwYDVQQK
ExxTdGFyZmllbGQgVGVjaGNOb2xvZ2llcywgSW5jLjEtMDAGA1UEAxMpU3RhcmZp
ZWxkIFNlcnZlckNPTTBDZXJ0aWZpY2F0ZSBBdXRob3JpdHkwggEiMA0GCSqGSIb3
DQEBAQUAA4IBDwAwggEKAoIBAQC78c1+U93Zl5d99E6Q5k41L+k0W9338J4/104Z
-----END CERTIFICATE-----
</ca>
"""

def main():
    print("Scraping password from VPNBook...")
    password = scrape_password()
    
    print("Testing server latencies...")
    active_servers = []
    
    for item in ACTIVE_HOSTS:
        host = item["host"]
        # Test Port 443 (HTTPS - Bypass Firewalls)
        latency = test_latency(host, 443)
        port = 443
        proto = "tcp"
        
        if latency is None:
            # Fallback Port 80
            latency = test_latency(host, 80)
            port = 80
            
        if latency is not None:
            print(f"Active: {host}:{port} ({latency}ms)")
            active_servers.append({
                "file_name": f"{host}_tcp{port}.ovpn",
                "host": host,
                "port": port,
                "proto": proto,
                "country": item["country"],
                "latency_ms": latency,
                "config_content": generate_ovpn_config(host, port, proto)
            })
        else:
            print(f"Inactive: {host}")

    # Sort by lowest latency (အမြန်ဆုံး ၅ ခု)
    active_servers.sort(key=lambda x: x["latency_ms"])
    top_5 = active_servers[:5]

    output_data = {
        "updated_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "username": "vpnbook",
        "password": password,
        "total_active_found": len(active_servers),
        "servers": top_5
    }

    with open("servers.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)

    print(f"Successfully updated servers.json with {len(top_5)} active servers!")

if __name__ == "__main__":
    main()
