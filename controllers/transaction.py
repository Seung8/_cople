import json
import threading

import requests
from django.utils import timezone


class TransactionController:
    """
    주문 조건(OrderCondition)을 받아 거래를 처리하는 컨트롤러

    특정 코인을 기준으로 매 초마다 시세를 조회하고
    기준에 따라 매수, 매도를 실행
    """

    def __init__(self, condition):
        self.__is_active = threading.Event()
        self.condition = condition
        self.base_url = 'https://api.upbit.com'
        self.current_price = None

    @property
    def is_active(self):
        return self.__is_active

    @is_active.setter
    def is_active(self):
        """
        전달 받은 주문 조건의 실행 상태(is_active)가 False 인 경우
        loop 중단을 위해 threading.Event() 객체를 False 로  전환
        """
        if not self.condition.is_active:
            self.__is_active = self.__is_active.set()

    # 코인 시세 조회
    def get_coin_price(self):
        url = self.base_url + '/v1/ticker'
        params = {'markets': self.condition.coin.code}
        response = requests.get(url, params=params)

        # 시세 조회에 성공한 경우에만 코인 가격 리턴
        if response.status_code == 200:
            result = json.loads(response.text)
            price = result[0].get('trade_price')
            self.current_price = price
        else:
            # todo: 추후 로깅으로 대체
            print(response.text)

        return self.current_price
