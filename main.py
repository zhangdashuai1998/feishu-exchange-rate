import os
import requests
from datetime import datetime

APP_ID = os.environ["APP_ID"]
APP_SECRET = os.environ["APP_SECRET"]
BASE_TOKEN = os.environ["BASE_TOKEN"]
TABLE_ID = os.environ["TABLE_ID"]

currencies = [
    "USD","EUR","GBP","PLN","NZD",
    "AUD","CAD","RON","CHF","SEK",
    "NOK","DKK","CZK","MXN","BRL"
]

# 获取 tenant_access_token
token_url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"

token_resp = requests.post(
    token_url,
    json={
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    }
).json()

tenant_token = token_resp["tenant_access_token"]

headers = {
    "Authorization": f"Bearer {tenant_token}",
    "Content-Type": "application/json"
}

# 获取汇率
rate_resp = requests.get(
    "https://open.er-api.com/v6/latest/CNY"
).json()

rates = rate_resp["rates"]

update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 查询记录
records_url = (
    f"https://open.feishu.cn/open-apis/bitable/v1/apps/"
    f"{BASE_TOKEN}/tables/{TABLE_ID}/records"
)

records_resp = requests.get(
    records_url,
    headers=headers
).json()

print("FEISHU RESPONSE:")
print(records_resp)

records = records_resp.get("data", {}).get("items", [])

print("records count =", len(records))

for record in records:

    fields = record["fields"]

    if "币种" not in fields:
        continue

    pair = fields["币种"]

    code = pair.split("/")[0]

    if code not in rates:
        continue

    value = round(1 / rates[code], 4)

update_url = (
    f"https://open.feishu.cn/open-apis/bitable/v1/apps/"
    f"{BASE_TOKEN}/tables/{TABLE_ID}/records/{record['record_id']}"
)

payload = {
    "fields": {
        "汇率": value,
        "更新时间": update_time
    }
}

update_resp = requests.put(
    update_url,
    headers=headers,
    json=payload
)

print(update_resp.status_code)
print(update_resp.text)

print("Update completed.")
