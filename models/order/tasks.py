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

    # 조건별 감시 루프 실행
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
            msg = '[{}] 주문 조건 비활성화로 로직 중단'.format(timezone.now())
            print(msg)
            condition.is_active = False
            condition.save()
            break

        # 더이상 구매할 개수가 없는 경우 로직 중단
        if not len(available_amount) > 0:
            msg = '[{}] 매수 개수 소진으로 로직 중단'.format(timezone.now())
            print(msg)
            condition.is_active = False
            condition.save()
            break

        # 코인 시세 감시
        cur_price = cc.get_coin_price(condition.coin.code)

        # 기준가
        ref_price = condition.ref_price

        # 목표 판매가
        if condition.rise_ratio:
            sell_price = ref_price + (ref_price * condition.rise_value / 100.0)
        else:
            sell_price = ref_price + condition.rise_value

        # 시세 하락 시 매수할 가격 설정 및 목표 매수가 설정
        # 목표 판매가(sell_price)는 구매가(buy_price) + 해당 주문 조건의 상승 값(_rise_value)
        if condition.fall_ratio:
            buy_price = ref_price - (ref_price * condition.fall_value / 100.0)
        else:
            buy_price = ref_price - condition.fall_value

        print('\n### {}코인 기준가: {}, 현재가: {}, 목표 매수(하락)가: {}, 목표 매수(상승)가: {}'.format(
            condition.coin.name_ko, ref_price, cur_price, buy_price, sell_price
        ))

        # 현재 코인 가격이 설정값 이상 하락한 경우 매수 주문 실행
        if cur_price <= buy_price:
            volume = float(available_amount.pop(0))
            response = oc.request_order(action='bid', volume=volume, price=float(cur_price))
            bought_price = float(response.get('price'))

            print('\n### 현재가({})가 목표 매수(하락)가({}) 보다 낮으므로 매수 주문 실행'.format(
                cur_price, buy_price
            ))

            # 구매 이력(Order) 생성
            _order.objects.create(
                condition_id=condition.id,
                uuid=response.get('uuid'),
                status=_order.DONE,
                type=_order.BUY,
                valance=volume,
                price=response.get('price'),
                sell_price=sell_price,
                extra=response
            )

            # 구매 예정 개수 목록에서 구매한 개수는 제거, 매수한 가격으로 기준가 업데이트
            condition.buy_amount = available_amount
            condition.ref_price = bought_price
            condition.save()

        # 매수 후 인터벌
        time.sleep(1.0)

        # 목표 상승가 이상 상승한 주문 목록 쿼리
        orders = _order.objects.select_related('condition__coin').filter(
            condition__coin__code=condition.coin.code, sell_price__gte=cur_price, is_sold=False
        )

        # 목표 상승가 이상 상승한 주문이 있다면 매도 주문 실행
        if orders.count() > 0:
            print('\n### 현재가({})보다 목표 매도가({})가 큰 매수 건 {}건에 대한 매도 주문 실행'.format(
                cur_price, sell_price, orders.count()
            ))

            sell_volume = orders.aggregate(volume=Sum('valance'))['volume']
            response = oc.request_order(action='ask', volume=float(sell_volume), price=float(cur_price))
            print('\n### 매도 주문 결과: {}'.format(response))

            # 매도 주문 기록(Order) 생성
            _order.objects.create(
                condition_id=condition.id,
                uuid=response.get('uuid'),
                status=_order.DONE,
                type=_order.SELL,
                valance=float(sell_volume),
                price=response.get('price'),
                extra=response
            )

            # 매도 완료 처리
            orders.update(is_sold=True)

            # 새 주문 생성
            _condition.objects.create(
                user_id=condition.user.id,
                coin_id=condition.coin.id,
                ref_price=response.get('price'),
                rise_value=condition.rise_value,
                rise_ratio=condition.rise_ratio,
                fall_value=condition.fall_value,
                fall_ratio=condition.fall_ratio,
                buy_amount=_buy_amount,
            )

        # 매도 후 인터벌
        time.sleep(1.0)