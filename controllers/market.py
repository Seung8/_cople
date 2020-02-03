import json

import requests

from controllers._base import RequestController
from models.market.models import Coin


class CoinController(RequestController):
    """코인 컨트롤러"""

    def get_coin_price(self, code: str = ''):
        """특정 코인 시세 조회"""
        coin = Coin.objects.filter(code=code).first()

        if not code or not coin:
            raise ValueError('존재하지 않는 코인({})입니다.'.format(code))

        self.request_url = '/v1/ticker'
        query_string = {'markets': code}
        response = requests.get(self.request_url, params=query_string)
        data = json.loads(response.text)

        if response.status_code != 200:
            raise Exception(data)

        return float(data[0]['trade_price'])

    def get_coins(self):
        """거래 가능한 코인 목록 조회"""
        self.request_url = '/v1/market/all'
        response = requests.get(self.request_url)

        if response.status_code == 200:
            data = json.loads(response.text)
            return data
        return None

    def update_coins(self):
        """업비트에 새로 추가된 코인이 있는 경우 새로 코인 등록"""
        coins = self.get_coins()

        if coins:
            creatable_items = []

            for coin in coins:
                if not Coin.objects.filter(code=coin['market']).values_list('id').exists():
                    creatable_items.append(
                        Coin(name_ko=coin['korean_name'], name_en=coin['english_name'], code=coin['market'])
                    )

            Coin.objects.bulk_create(creatable_items)
            # todo: 추후 로깅으로 대체
            print('{}건의 코인 생성 완료'.format(creatable_items))
            return True
        return False
