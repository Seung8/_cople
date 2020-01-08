import json
import time
import requests
from django.utils import timezone
from django.apps import apps


class TransactionController:
    """
    주문 조건(OrderCondition)의 id를 받아 거래를 처리하는 컨트롤러

    특정 코인을 기준으로 매 초마다 시세를 조회하고
    기준에 따라 매수, 매도를 실행
    """

    def __init__(self, condition_id):
        self.base_url = 'https://api.upbit.com'
        self.condition_id = condition_id

        self.__condition = None

    @property
    def condition(self):
        """주문 조건 객체 반환 """
        print('set condition')
        model = apps.get_model('transaction', 'OrderCondition')
        self.__condition = model.objects.filter(id=self.condition_id).first()

        return self.__condition

    @property
    def coin_price(self):
        """주문 조건에 등록된 코인의 시세 조회"""
        condition = self.condition

        if not condition:
            return None

        url = self.base_url + '/v1/ticker'
        params = {'markets': self.condition.coin.code}
        response = requests.get(url, params=params)

        # 가격 조회에 실패하면 해당 예외를 출력(로깅)하고 즉시 while 루프 탈출
        if response.status_code != 200:
            condition.is_active = False
            condition.modified_at = timezone.localtime()
            condition.save(update_fields=['is_active', 'modified_at'])

            # todo: 추후 로깅으로 대체
            print(response.text)

            return None

        result = json.loads(response.text)
        price = result[0]['trade_price']

        return float(price)

    def buy(self):
        """매수"""
        pass

    def sell(self):
        """매도"""
        pass

    def run(self):
        """
        자동 감시 주문 실행

        만약 while loop 동작 중 조건이 비활성화 된 경우 즉시 while loop 를 탈출해야 하므로
        매 초마다 주문 조건(self.condition)을 조회
        """
        while True:
            condition = self.condition
            if not condition.is_active:
                break
            print('async function is working!')
            time.sleep(1)
