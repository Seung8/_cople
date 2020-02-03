from controllers._base import RequestController


class AccountController(RequestController):
    """계좌 관련 컨트롤러"""

    def retrieve_orders(self):
        """주문 목록 조회"""
        pass

    def retrieve_order(self, order_uuid):
        """개별 주문 조회"""
        pass
