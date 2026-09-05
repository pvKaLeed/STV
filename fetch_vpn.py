import os
import re
import urllib.request
import time
import socket
import json
import base64

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def fetch_webpage(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""

def get_vpngate_servers():
    """Fetch VPNGate public server list"""
    html = fetch_webpage("https://www.vpngate.net/api/iphone/")
    if not html:
        return []
    
    servers = []
    lines = html.strip().split('\n')
    
    for line in lines[1:]:
        parts = line.split(',')
        if len(parts) < 10:
            continue
            
        try:
            host = parts[1].strip()
            country = parts[6].strip()
            country_code = parts[7].strip()
            ping = float(parts[4].strip())
            speed = float(parts[5].strip())
            config_base64 = parts[9].strip()
            
            config_content = base64.b64decode(config_base64).decode('utf-8')
            
            servers.append({
                "host": host,
                "country": country,
                "country_code": country_code,
                "ping_ms": ping,
                "speed_mbps": speed,
                "config_content": config_content
            })
        except Exception as e:
            continue
    
    return servers

def main():
    print("Fetching VPNGate servers...")
    servers = get_vpngate_servers()
    
    if not servers:
        print("No servers found!")
        return
    
    print(f"Found {len(servers)} servers")
    
    # Sort by ping (lowest first)
    servers.sort(key=lambda x: x["ping_ms"])
    top_10 = servers[:10]
    
    output_data = {
        "updated_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "username": "vpn",
        "password": "vpn",
        "total_active_found": len(servers),
        "servers": [{
            "file_name": f"{s['host']}.ovpn",
            "host": s["host"],
            "port": 443,
            "proto": "tcp",
            "country": s["country"],
            "country_code": s["country_code"],
            "latency_ms": s["ping_ms"],
            "config_content": s["config_content"]
        } for s in top_10]
    }
    
    with open("servers.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)
    
    print(f"✅ Updated servers.json with {len(top_10)} servers!")

if __name__ == "__main__":
    main()
