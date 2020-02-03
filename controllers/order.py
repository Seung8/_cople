from controllers._base import RequestController
from models.order.models import OrderCondition


class OrderController(RequestController):
    """주문 컨트롤러"""
    ALLOWED_ACTIONS = ['ask', 'bid']

    def __init__(self, condition_id):
        super().__init__()
        self.condition_id = condition_id

    def get_condition(self):
        return OrderCondition.objects.filter(id=self.condition_id).first()

    def get_orders(self):
        """주문 목록 조회"""
        pass

    def cancel_order(self, uuid: list):
        """주문 취소 접수"""
        # 주문 uuid 를 list 형태로 받아서 순차 처리
        pass

    def request_order(self, action: str):
        """코인 매수(bid), 매도(ask) 주문 요청"""
        # 주문 유형(action) 인자는 반드시 문자열이어야 함
        if not isinstance(action, str):
            raise TypeError('주문 유형(action)은 문자열(str)이어야 합니다.')

        # 매수(bid), 매도(ask) 외의 요청은 허용하지 않음
        if action.lower() not in self.ALLOWED_ACTIONS:
            raise ValueError('허용하지 않는 주문 유형({})입니다.'.format(action))

        pass
