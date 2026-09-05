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
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""

def get_vpngate_servers():
    """Fetch VPNGate public server list"""
    print("🌐 Fetching VPNGate servers...")
    html = fetch_webpage("https://www.vpngate.net/api/iphone/")
    if not html:
        print("❌ Failed to fetch server list")
        return []
    
    servers = []
    lines = html.strip().split('\n')
    print(f"📊 Total lines: {len(lines)}")
    
    # Skip header line
    for idx, line in enumerate(lines[1:]):
        parts = line.split(',')
        if len(parts) < 10:
            continue
            
        try:
            # Format: 
            # 0: #, 1: HostName, 2: IP, 3: Score, 4: Ping, 5: Speed, 
            # 6: CountryLong, 7: CountryShort, 8: NumVpnSessions, 
            # 9: OpenVPN_ConfigData_Base64, 10: ...
            
            host = parts[1].strip()
            country = parts[6].strip()
            country_code = parts[7].strip()
            ping = float(parts[4].strip())  # in ms
            speed = float(parts[5].strip())  # in Mbps
            config_base64 = parts[9].strip()
            
            # Decode OpenVPN config
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
            print(f"⚠️ Error parsing line {idx}: {e}")
            continue
    
    print(f"✅ Found {len(servers)} servers")
    return servers

def main():
    print("🚀 Starting VPNGate server update...")
    servers = get_vpngate_servers()
    
    if not servers:
        print("❌ No servers found!")
        # Try fallback URL
        print("🔄 Trying fallback URL...")
        html = fetch_webpage("https://www.vpngate.net/api/iphone/")
        if html:
            servers = get_vpngate_servers()
    
    if not servers:
        print("❌ Still no servers, using cached data")
        return
    
    # Filter: only servers with good ping (< 200ms) and good speed (> 1 Mbps)
    filtered = [s for s in servers if s["ping_ms"] < 200 and s["speed_mbps"] > 1]
    print(f"📊 Filtered: {len(filtered)} servers (ping < 200ms, speed > 1 Mbps)")
    
    # Sort by ping (lowest first) then speed (highest first)
    filtered.sort(key=lambda x: (x["ping_ms"], -x["speed_mbps"]))
    top_10 = filtered[:10]
    
    print(f"📝 Selected top {len(top_10)} servers")
    
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
            "latency_ms": round(s["ping_ms"], 2),
            "config_content": s["config_content"]
        } for s in top_10]
    }
    
    with open("servers.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)
    
    print(f"✅ Successfully updated servers.json with {len(top_10)} VPNGate servers!")

if __name__ == "__main__":
    main()
