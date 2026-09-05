import requests
import pandas as pd
import json

# 1. Data ကို ယူမယ် (Fetch Data)
url = "https://www.vpngate.net/api/iphone/"
response = requests.get(url)
data = response.text

# 2. Data ကို ရှင်းလင်းမယ် (Parse Data)
# VPNGate API က OpenVPN ရဲ့ ပုံစံနဲ့ လာတာမို့ ပထမဆုံး မလိုအပ်တဲ့ စာကြောင်းတွေကို ဖြတ်ထုတ်ရပါမယ်
lines = data.split('\n')
filtered_lines = [line for line in lines if not line.startswith('#') and line.strip()]
csv_data = "\n".join(filtered_lines)

# 3. CSV အနေနဲ့ ဖတ်မယ် (Read as CSV)
try:
    # header=0 ဆိုတာက ပထမဆုံး row ကို header အနေနဲ့ ယူမယ်လို့ ဆိုလိုတာပါ
    df = pd.read_csv(pd.io.common.StringIO(csv_data))
except Exception as e:
    print(f"Error reading CSV: {e}")
    df = pd.DataFrame()

# 4. မလိုအပ်တဲ့ အမှားတွေကို ပြင်မယ် (Fixing the error - အဓိကအချက်)
if not df.empty:
    # 'Speed' နဲ့ 'Ping' column တွေကို float ပြောင်းတဲ့အခါ အက္ခရာ (ဥပမာ 'Japan') ပါလာရင် 
    # error တက်တာမို့ 'coerce' ကို သုံးပြီး အမှားဖြစ်တဲ့ data တွေကို NaN (Not a Number) ဖြစ်အောင်လုပ်မယ်
    df['Speed'] = pd.to_numeric(df['Speed'], errors='coerce')
    df['Ping'] = pd.to_numeric(df['Ping'], errors='coerce')

    # NaN ဖြစ်နေတဲ့ row တွေကို ဖျက်ပစ်မယ် (ဒါမှ နောက်ပိုင်း float ပြောင်းတဲ့အခါ အမှားမတက်တော့ဘူး)
    df = df.dropna(subset=['Speed', 'Ping'])

    # (Optional) နောက်ထပ် မလိုအပ်တဲ့ အမှားမျိုး မဖြစ်အောင် အခြား Columns တွေကိုလည်း ရှင်းလင်းနိုင်ပါတယ်
    # ဥပမာ - df = df.dropna() ဆိုပြီး NaN ရှိသမျှ row အားလုံး ဖျက်လို့ရပါတယ်။

# 5. servers.json ဖိုင်ထဲ သိမ်းမယ် (Save to servers.json)
output_data = df.to_dict(orient='records')
with open('servers.json', 'w', encoding='utf-8') as f:
    json.dump(output_data, f, indent=4)

print(f"Successfully saved {len(output_data)} servers to servers.json")
