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
         "message": "support ticket",
         "timestamp": "",
         "date": (date - timedelta(days=x)).strftime('%Y-%m-%dT%H:%M:%S.0'),
         "namespace": "rc.support_tickets",
         "server": "dummy2.server.com",
         "permanent": True,
         # "primary_key": x,
         "tags": [
             ["product", 'product_name %s' % price],
             ["status",
              random.choice(['open', 'closed', 'pending', 'invalid'])],
             ['owner',
              random.choice(['brian', 'lisa', 'martin', 'karen', 'sarah'])]
         ]
        }
    )

resp = requests.post(endpoint, data=json.dumps(logs), headers={
    "Content-Type": "application/json",
    "X-appenlight-api-key": "Your.API.Key"
})

print resp.status_code, resp.text
