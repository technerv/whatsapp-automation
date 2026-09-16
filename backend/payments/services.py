import base64
from datetime import datetime

import requests
from django.conf import settings
from requests.auth import HTTPBasicAuth


def _base_url():
    environment = getattr(settings, 'MPESA_ENVIRONMENT', 'sandbox')
    if environment == 'production':
        return 'https://api.safaricom.co.ke'
    return 'https://sandbox.safaricom.co.ke'


def initiate_stk_push(*, phone_number, amount, order_id):
    """Call Daraja STK Push and return its response, without marking payment paid."""
    required = [settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET,
                settings.MPESA_SHORTCODE, settings.MPESA_PASSKEY, settings.MPESA_CALLBACK_URL]
    if not all(required):
        raise RuntimeError('M-PESA credentials and callback URL are not configured.')

    token_response = requests.get(
        f'{_base_url()}/oauth/v1/generate?grant_type=client_credentials',
        auth=HTTPBasicAuth(settings.MPESA_CONSUMER_KEY, settings.MPESA_CONSUMER_SECRET),
        timeout=15,
    )
    token_response.raise_for_status()
    access_token = token_response.json()['access_token']
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode(
        f'{settings.MPESA_SHORTCODE}{settings.MPESA_PASSKEY}{timestamp}'.encode()
    ).decode()
    response = requests.post(
        f'{_base_url()}/mpesa/stkpush/v1/processrequest',
        json={
            'BusinessShortCode': settings.MPESA_SHORTCODE,
            'Password': password,
            'Timestamp': timestamp,
            'TransactionType': 'CustomerPayBillOnline',
            'Amount': int(amount),
            'PartyA': phone_number,
            'PartyB': settings.MPESA_SHORTCODE,
            'PhoneNumber': phone_number,
            'CallBackURL': settings.MPESA_CALLBACK_URL,
            'AccountReference': str(order_id),
            'TransactionDesc': f'Payment for Order {order_id}',
        },
        headers={'Authorization': f'Bearer {access_token}'},
        timeout=15,
    )
    response.raise_for_status()
    return response.json()