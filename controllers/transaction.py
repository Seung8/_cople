import json
import time
import requests
from django.utils import timezone


class TransactionController:
    """
    주문 조건(OrderCondition)을 받아 거래를 처리하는 컨트롤러

    특정 코인을 기준으로 매 초마다 시세를 조회하고
    기준에 따라 매수, 매도를 실행
    """

    def __init__(self, condition):
        self.condition = condition
        self.base_url = 'https://api.upbit.com'

    # 코인 시세 조회
    def get_coin_price(self):
        url = self.base_url + '/v1/ticker'
        params = {'markets': self.condition.coin.code}
        response = requests.get(url, params=params)

        if response.status_code != 200:
            self.condition.is_active = False
            self.condition.modified_at = timezone.localtime()
            self.condition.save(update_fields=['is_active', 'modified_at'])

            # todo: 추후 로깅으로 대체
            print(response.text)

        result = json.loads(response.text)
        price = result[0]['trade_price']

        return price

    # 매수
    def buy(self):
        pass

    # 매도
    def sell(self):
        pass

    # 자동 감시 주문 로직 실행
    def run(self):
        while True:
            time.sleep(1)

            if not self.condition.is_active:
                break
