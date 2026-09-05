import urllib.request
import json
import base64
import time

def fetch_vpngate_data():
    url = "https://www.vpngate.net/api/iphone/"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            data = response.read().decode('utf-8')
            return data
    except Exception as e:
        print(f"Error: {e}")
        return None

def parse_vpngate_csv(data):
    servers = []
    lines = data.strip().split('\n')
    
    for line in lines[1:]:  # Skip header
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
            
            if not config_base64:
                continue
                
            config = base64.b64decode(config_base64).decode('utf-8')
            
            servers.append({
                "host": host,
                "country": country,
                "country_code": country_code,
                "ping_ms": ping,
                "speed_mbps": speed,
                "config_content": config
            })
        except Exception as e:
            print(f"Parse error: {e}")
            continue
    
    return servers

def main():
    print("Fetching VPNGate data...")
    data = fetch_vpngate_data()
    
    if not data:
        print("Failed to fetch data")
        return
    
    servers = parse_vpngate_csv(data)
    print(f"Found {len(servers)} servers")
    
    # Filter and sort
    filtered = [s for s in servers if s["ping_ms"] < 200 and s["speed_mbps"] > 1]
    filtered.sort(key=lambda x: x["ping_ms"])
    top_10 = filtered[:10]
    
    output = {
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
    
    with open("servers.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"Updated servers.json with {len(top_10)} servers")

if __name__ == "__main__":
    main()
