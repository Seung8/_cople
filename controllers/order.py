import json

import requests
from django.apps import apps
from django.utils import timezone

from controllers._base import RequestController


class OrderController(RequestController):
    """주문 컨트롤러"""

    def __init__(self, condition_id):
        super().__init__()
        self.condition_id = condition_id

    def get_condition(self):
        model = apps.get_model('order.OrderCondition')
        condition = model.objects.select_related('coin', 'user').prefetch_related('user__api_info').filter(
            id=self.condition_id, is_active=True
        ).first()

        if not condition:
            raise Exception('존재하지 않는 주문 조건({})입니다.'.format(self.condition_id))
        return condition

    def request_order(self, action: str, volume: float, price: float):
        """매수(bid)/매도(ask) 주문 요청"""
        allowed_actions = ['bid', 'ask']

        if action not in allowed_actions:
            raise Exception('허용하지 않는 주문 유형({})입니다.'.format(action))

        if not isinstance(volume, float):
            raise TypeError('주문 개수(volume)는 반드시 float()형이어야 합니다.')

        condition = self.get_condition()
        api_info = condition.user.api_info.first()

        if not api_info:
            raise Exception('인증 정보가 올바르지 않습니다.')

        query = {
            'market': condition.coin.code,
            'side': action,
            'volume': str(volume),
            'ord_type': 'limit',
            'price': str(price)
        }

        access_key = api_info.access_key
        secret_key = api_info.secret_key

        request_url = self.request_url + '/v1/orders'
        headers = self.set_headers(access_key, secret_key, params=query)

        response = requests.post(request_url, params=query, headers=headers)
        data = json.loads(response.text)

        # 매수인 경우 주문 타입(ord_type)을 지정가 매수(price)로 설정
        msg_action = '매수' if action == 'bid' else '매도'

        print('\n### [{}] {}주문 요청쿼리: {}'.format(
            timezone.now(), msg_action, query
        ))

        if response.status_code != 201:
            raise Exception(data)

        print('\n### [{}] {}주문 실행 성공 : {}'.format(timezone.now(), msg_action, data))
        return data
