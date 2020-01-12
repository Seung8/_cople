import hashlib
import json
import time
import uuid
import jwt
from urllib.parse import urlencode

import requests
from django.utils import timezone
from django.apps import apps


class TransactionController:
    """
    주문 조건(OrderCondition)의 id를 받아 거래를 처리하는 컨트롤러

    특정 코인을 기준으로 매 초마다 시세를 조회하고
    기준에 따라 매수, 매도를 실행
    """

    def __init__(self, condition_id, user_id):
        self.condition_id = condition_id
        self.user_id = user_id

        self.__request_url = 'https://api.upbit.com'

    @property
    def request_url(self):
        return self.__request_url

    @request_url.setter
    def request_url(self, sub):
        self.__request_url = self.__request_url + sub

    def get_condition(self):
        """주문 조건 객체 반환 """
        model = apps.get_model('transaction', 'OrderCondition')

        return model.objects.filter(id=self.condition_id).first()

    def get_api_keys(self):
        """주문 요청자의 액세스 키와 시크릿 키를 튜플형으로 반환"""
        model = apps.get_model('account', 'UserAPIInfo')
        api_info = model.objects.filter(user_id=self.user_id, is_active=True).first()

        if not api_info:
            return None, None

        return api_info.access_key, api_info.secret_key

    def get_coin_price(self):
        """주문 조건에 등록된 코인의 시세 조회"""
        self.request_url = '/v1/ticker'

        condition = self.get_condition()
        params = {'markets': condition.coin.code}
        response = requests.get(self.request_url, params=params)

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

    def set_headers(self, query):
        """
        주문을 위한 payload 데이터 설정
        """
        api_keys = self.get_api_keys()

        query_string = urlencode(query).encode()
        hash_data = hashlib.sha512()
        hash_data.update(query_string)
        query_hash = hash_data.hexdigest()

        payload = {
            'access_key': api_keys[0],
            'nonce': str(uuid.uuid4()),
            'query_hash': query_hash,
            'query_hash_alg': 'SHA512'
        }

        jwt_token = jwt.encode(payload, api_keys[1]).decode('utf-8')
        authorization = 'Bearer {}'.format(jwt_token)

        return {'Authorization': authorization}

    def order(self, query):
        self.request_url = '/v1/orders'
        response = requests.post(self.request_url, params=query, headers=self.set_headers(query))

        if response.status_code > 201:
            # todo: 추후 로깅 대체
            print(json.loads(response.text))
            return False

        return True

    def run(self):
        """
        자동 감시 주문 실행

        * 만약 while loop 동작 중 조건이 비활성화 된 경우 즉시 while loop 를 탈출해야 하므로
        매 초마다 데이터베이스에서 주문 조건 조회

        주문 쿼리
        query = {
            'market': '<Coin code>',
            'side': '<bid(매수), ask(매도)>',
            'volume': '주문 수량, 소수점 문자열',
            'price': '개당 주문가',
            'ord_type': 'limit(지정가 주문)'
        }
        """
        while True:
            condition = self.get_condition()
            if not condition.is_active:
                break
            print('async function is working!')
            time.sleep(1)
