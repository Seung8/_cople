import requests
import json

from models.market.models import Coin


class CoinController:
    def __init__(self):
        self.base_url = 'https://api.upbit.com'
        self.coins = self.get_coins()

    def get_coins(self):
        url = self.base_url + '/v1/market/all'
        response = requests.get(url)

        if response.status_code == 200:
            data = json.loads(response.text)
            return data

        return None

    def update_coins(self):
        """
        업비트에 새로 추가된 코인이 있는 경우 새로 코인 등록
        """
        if self.coins:
            creatable_items = []

            for coin in self.coins:
                if not Coin.objects.filter(code=coin['market']).values_list('id').exists():
                    creatable_items.append(
                        Coin(name_ko=coin['korean_name'], name_en=coin['english_name'], code=coin['market'])
                    )

            Coin.objects.bulk_create(creatable_items)
            # todo: 추후 하기 내용은 로그로 대체하여 저장
            print('{}건의 코인 생성 완료'.format(creatable_items))
            return True
        return False
