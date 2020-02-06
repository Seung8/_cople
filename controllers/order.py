import json

import requests

from controllers._base import RequestController
from models.order.models import OrderCondition


class OrderController(RequestController):
    """주문 컨트롤러"""

    def __init__(self, condition_id):
        super().__init__()
        self.condition_id = condition_id

    @property
    def condition(self):
        condition = OrderCondition.objects.select_related('coin').filter(id=self.condition_id).first()

        if not condition:
            raise Exception('존재하지 않는 주문 조건({})입니다.'.format(self.condition_id))
        return condition

    def get_orders(self):
        """주문 목록 조회"""
        pass

    def cancel_order(self, uuid: list):
        """주문 취소 접수"""
        # 주문 uuid 를 list 형태로 받아서 순차 처리
        pass

    def request_order(self, action: str, volume: float, price: float):
        """매수(bid)/매도(ask) 주문 요청"""
        allowed_actions = ['bid', 'ask']

        if action not in allowed_actions:
            raise Exception('허용하지 않는 주문 유형({})입니다.'.format(action))

        if not isinstance(volume, float):
            raise TypeError('주문 개수(volume)는 반드시 float()형이어야 합니다.')

        if not isinstance(price, float):
            raise TypeError('주문 가격(price)는 반드시 float()형이어야 합니다.')

        condition = self.condition
        api_keys = condition.user.api_keys

        if not api_keys:
            raise Exception('인증 정보가 올바르지 않습니다.')

        query = {
            'market': self.condition.coin.code,
            'side': action,
            'volume': str(volume),
            'price': str(100.0),
            'ord_type': 'limit'
        }

        access_key = api_keys['access_key']
        secret_key = api_keys['secret_key']

        request_url = self.request_url + '/v1/orders'
        headers = self.set_headers(access_key, secret_key, params=query)

        response = requests.post(request_url, params=query, headers=headers)
        data = json.loads(response.text)

        if response.status_code != 201:
            raise Exception(data)

        return data
