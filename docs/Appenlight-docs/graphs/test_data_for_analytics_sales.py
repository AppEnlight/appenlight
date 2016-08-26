import requests
import json
import random

from datetime import datetime, timedelta

endpoint = 'https://api.appenlight.com/api/logs?protocol_version=0.5'
endpoint = 'http://127.0.0.1:6543/api/logs?protocol_version=0.5'


logs = []

date = datetime.utcnow()
for x in xrange(0, 500):
    price = random.randint(1, 10)
    quantity = random.randint(1, 15)
    date = date - timedelta(hours=random.randint(1, 8))
    logs.append(
        {"log_level": "INFO",
         "message": "shop operation",
         "timestamp": "",
         "date": (date - timedelta(days=x)).strftime('%Y-%m-%dT%H:%M:%S.0'),
         "namespace": "rc.shop.dummy_data",
         "server": "dummy.server.com",
         # "primary_key": x,
         "permanent": True,
         "tags": [["action", 'buy'],
                  ["product", 'product_name %s' % price],
                  ["price", price],
                  ["quantity", quantity],
                  ["total_payment", price * quantity],
         ]
        }
    )

resp = requests.post(endpoint, data=json.dumps(logs), headers={
    "Content-Type": "application/json",
    "X-appenlight-api-key": "Your.API.Key"
})

print resp.status_code, resp.text
