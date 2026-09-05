import os
import re
import zipfile
import urllib.request
import time
import socket
import json

# VPNBook Zip URLs
ZIP_URLS = [
    "https://www.vpnbook.com/freeovpn/VPNBook.com-OpenVPN-Euro1.zip",
    "https://www.vpnbook.com/freeovpn/VPNBook.com-OpenVPN-Euro2.zip",
    "https://www.vpnbook.com/freeovpn/VPNBook.com-OpenVPN-US1.zip",
    "https://www.vpnbook.com/freeovpn/VPNBook.com-OpenVPN-US2.zip",
    "https://www.vpnbook.com/freeovpn/VPNBook.com-OpenVPN-CA222.zip",
    "https://www.vpnbook.com/freeovpn/VPNBook.com-OpenVPN-DE233.zip",
]

def download_and_extract():
    os.makedirs("ovpn_files", exist_ok=True)
    extracted_files = []
    
    for url in ZIP_URLS:
        zip_path = "temp.zip"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response, open(zip_path, 'wb') as out_file:
                out_file.write(response.read())
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for file_info in zip_ref.infolist():
                    if file_info.filename.endswith('.ovpn'):
                        extracted_path = zip_ref.extract(file_info, "ovpn_files")
                        extracted_files.append(extracted_path)
            os.remove(zip_path)
        except Exception as e:
            print(f"Error downloading {url}: {e}")
            
    return extracted_files

def parse_ovpn(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Extract Remote Host and Port
    remote_match = re.search(r'^remote\s+([\w\.\-]+)\s+(\d+)', content, re.MULTILINE)
    proto_match = re.search(r'^proto\s+(\w+)', content, re.MULTILINE)

    if not remote_match:
        return None

    host = remote_match.group(1)
    port = int(remote_match.group(2))
    proto = proto_match.group(1) if proto_match else "udp"

    return {
        "file_name": os.path.basename(file_path),
        "host": host,
        "port": port,
        "proto": proto,
        "config_content": content
    }

def test_latency(host, port, timeout=2.0):
    """Socket ဖြင့် Latency / Active ဖြစ်မဖြစ် တိုင်းတာခြင်း"""
    start_time = time.time()
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))
        sock.close()
        latency = (time.time() - start_time) * 1000  # in ms
        return round(latency, 2)
    except Exception:
        return None  # Unreachable / Inactive

def get_vpnbook_credentials():
    """VPNBook Credential များ"""
    return {
        "username": "vpnbook",
        "password_note": "Get dynamic password or set fallback"
    }

def main():
    print("Downloading VPNBook config files...")
    files = download_and_extract()
    parsed_servers = []

    print(f"Parsing {len(files)} config files...")
    for f in files:
        data = parse_ovpn(f)
        if data:
            parsed_servers.append(data)

    print("Testing server latencies...")
    active_servers = []
    for server in parsed_servers:
        latency = test_latency(server["host"], server["port"])
        if latency is not None:
            server["latency_ms"] = latency
            active_servers.append(server)
            print(f"Active: {server['host']}:{server['port']} - Latency: {latency}ms")

    # Latency အနည်းဆုံး (အမြန်ဆုံး) ၅ ခုကို ရွေးထုတ်မည်
    active_servers.sort(key=lambda x: x["latency_ms"])
    top_5 = active_servers[:5]

    output_data = {
        "updated_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "username": "vpnbook",
        "total_active_found": len(active_servers),
        "servers": top_5
    }

    with open("servers.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)

    print("Done! Saved top 5 servers to servers.json")

if __name__ == "__main__":
    main()
