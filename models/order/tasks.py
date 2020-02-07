import time

from django.apps import apps
from django.db.models import Sum
from django.utils import timezone

from controllers.market import CoinController
from controllers.order import OrderController
from settings import celery_app


@celery_app.task
def observe_coin_price(condition_id: str):
    """자동 감시 주문"""
    cc = CoinController()
    oc = OrderController(condition_id=condition_id)
    loop_count = 0

    _order = apps.get_model('order', 'Order')
    _condition = apps.get_model('order', 'OrderCondition')
    _buy_amount = None

    while True:
        loop_count += 1

        condition = oc.get_condition()
        # 차감하면서 사용할 구매 개수 목록
        available_amount = condition.buy_amount.copy()

        # 최초 순회 시 새 조건(OrderCondition)에 사용할 구매 개수 목록 저장
        if loop_count == 1:
            _buy_amount = condition.buy_amount

        # 감시 중 주문 조건 비활성화 시 로직 중단
        if not condition.is_active:
            # todo: 주문조건 비활성 알림 전송
            print('[{}] 주문 조건 비활성화로 로직 중단'.format(timezone.now()))
            condition.is_active = False
            condition.save()
            break

        # 더이상 구매할 개수가 없는 경우 로직 중단
        if not len(available_amount) > 0:
            print('[{}] 매수 개수 소진으로 로직 중단'.format(timezone.now()))
            condition.is_active = False
            condition.save()
            break

        # 코인 시세 감시
        cur_price = cc.get_coin_price(condition.coin.code)

        # 기준가
        ref_price = condition.ref_price

        # 시세 하락 시 매수할 가격 설정
        if condition.fall_ratio:
            buy_price = ref_price - (ref_price * condition.fall_value / 100.0)
        else:
            buy_price = ref_price - condition.fall_value

        # 현재 코인 가격이 설정값 이상 하락한 경우
        if cur_price <= buy_price:
            volume = float(available_amount.pop(0))
            response = oc.request_order(action='bid', volume=volume)
            bought_price = response.get('price')

            # 구매 이력(Order) 생성
            _order.objects.create(
                uuid=response.get('uuid'),
                status=_order.DONE,
                type=_order.BUY,
                valance=volume,
                price=response.get('price'),
                extra=response
            )

            # 구매 예정 개수 목록에서 구매한 개수는 제거, 매수한 가격으로 기준가 업데이트
            condition.buy_amount = available_amount
            condition.ref_price = bought_price
            condition.save()

        # 주문 내역 쿼리
        orders = _order.objects.select_related('condition__coin').filter(
            condition__coin__code=condition.coin.code, price__lte=cur_price
        )

        # 주문 내역 중 현재가보다 낮은 가격에 매수한 코인이 있다면 모두 시장가 매수 진행
        # 매수가 완료되면 기존 로직은 중단시키고 매도 가격으로 새로운 로직 진행
        if orders:
            volume = orders.aggregate(volume=Sum('valance'))['volume']
            response = oc.request_order(action='ask', volume=float(volume))

            # 매도 주문 기록(Order) 생성
            _order.objects.create(
                uuid=response.get('uuid'),
                status=_order.DONE,
                type=_order.SELL,
                valance=float(volume),
                price=response.get('price'),
                extra=response
            )

            _condition.objects.create(
                user_id=condition.user.id,
                coin_id=condition.coin.id,
                ref_price=response.get('price'),
                rise_value=condition.raise_value,
                rise_ratio=condition.rise_ratio,
                fall_value=condition.fall_value,
                fall_ratio=condition.fall_ratio,
                buy_amount=_buy_amount,
                is_active=True
            )

            condition.is_active = False
            condition.save()
            break

        time.sleep(2.0)
