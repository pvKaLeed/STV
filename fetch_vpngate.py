import requests
import pandas as pd
import json

def fetch_and_save_vpngate():
    print("Fetching VPNGate data...")
    url = "https://www.vpngate.net/api/iphone/"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status() # HTTP Error ရှိရင် ဖမ်းမယ်
        
        # VPNGate API က CSV format နဲ့ ပြန်ပေးတာမို့ စာကြောင်းတွေကို ရှင်းမယ်
        raw_text = response.text
        lines = raw_text.split('\n')
        
        # '#' နဲ့ စတဲ့ မလိုအပ်တဲ့ စာကြောင်းတွေ နဲ့ အလွတ်စာကြောင်းတွေ ဖျက်မယ်
        clean_lines = [line for line in lines if not line.startswith('#') and line.strip()]
        csv_data = "\n".join(clean_lines)
        
        # CSV ကို Pandas နဲ့ ဖတ်မယ်
        df = pd.read_csv(pd.io.common.StringIO(csv_data))
        
        # --- အဓိက Error ဖြေရှင်းချက် ---
        # 'Speed' နဲ့ 'Ping' ကော်လံတွေကို နံပါတ် (float) အဖြစ် ပြောင်းမယ်။
        # မပြောင်းနိုင်တဲ့ စာသားတွေ (ဥပမာ - Japan, N/A, -) ပါလာရင်
        # errors='coerce' က အဲ့ဒါတွေကို NaN (Not a Number) အဖြစ် ပြောင်းပေးမယ်။
        if 'Speed' in df.columns:
            df['Speed'] = pd.to_numeric(df['Speed'], errors='coerce')
        if 'Ping' in df.columns:
            df['Ping'] = pd.to_numeric(df['Ping'], errors='coerce')
        
        # NaN ဖြစ်နေတဲ့ (တန်ဖိုးမရှိတဲ့) အတန်းတွေကို ဖျက်ပစ်မယ်
        df = df.dropna(subset=['Speed', 'Ping'])
        
        # '#' သင်္ကေတတွေ ဒါမှမဟုတ် မလိုအပ်တဲ့ အတန်းတွေ ကျန်နေရင် ထပ်ရှင်းမယ်
        df = df[df['Country'].apply(lambda x: isinstance(x, str) and not x.startswith('*'))]
        
        # နောက်ဆုံး Data ကို JSON ဖိုင်ထဲ သိမ်းမယ်
        final_data = df.to_dict(orient='records')
        
        with open('servers.json', 'w', encoding='utf-8') as f:
            json.dump(final_data, f, indent=4, ensure_ascii=False)
            
        print(f"✅ အောင်မြင်ပါပြီ! VPN ဆာဗာ {len(final_data)} ခုကို 'servers.json' ထဲ သိမ်းပြီးပါပြီ။")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ အင်တာနက် ချိတ်ဆက်မှု အမှား: {e}")
    except Exception as e:
        print(f"❌ အခြားအမှားတစ်ခု ဖြစ်ပွားသွားပါသည်: {e}")

if __name__ == "__main__":
    fetch_and_save_vpngate()
