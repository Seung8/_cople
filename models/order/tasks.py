import time

from django.apps import apps
from django.utils import timezone

from controllers.market import CoinController
from settings import celery_app


@celery_app.task
def observe_coin_price(condition_id: str):
    """자동 감시 주문"""
    print('### 자동 감시 주문 실행!')
    cc = CoinController()
    model = apps.get_model('order', 'OrderCondition')

    while True:
        condition = model.objects.select_related('coin', 'user').filter(id=condition_id).first()

        # 주문 조건이 없다면 순회 로직 중단
        if not condition:
            raise ValueError('존재하지 않는 주문 조건입니다.')

        # 감시 중 주문 조건 비활성화 시 로직 중단
        if not condition.is_active:
            # todo: 주문조건 비활성 알림 전송
            print('[{}] 주문 조건 비활성화로 로직 중단'.format(timezone.now()))
            break

        # 코인 시세 감시
        price = cc.get_coin_price(condition.coin.code)
        print('{}({}): {}'.format(condition.coin.name_ko, condition.coin.code, price))

        # 매수 주문

        # 만약 현재 가격에 판매해야 하는 코인이 있는 경우 판매 주문


        # 매도 주문

        time.sleep(2.0)
