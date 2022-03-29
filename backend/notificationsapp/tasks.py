import json
import os

import requests

from settings.celery import app


@app.task
def send_message(message_id, phone, text):
    payload = json.dumps({
        "id": int(message_id),
        "phone": int(phone),
        "text": text
    })
    headers = {
        "accept": 'application/json',
        "Authorization": f'Bearer {os.environ.get("API_TOKEN")}'
    }
    resp = requests.post(f'https://probe.fbrq.cloud/v1/send/{message_id}',
                         data=payload, headers=headers)
    return {
        "code": resp.status_code,
        "body": resp.text
    }
