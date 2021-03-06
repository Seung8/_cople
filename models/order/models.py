from django.conf import settings
from django.contrib.postgres.fields import ArrayField, JSONField
from django.db import models

from models.order.tasks import observe_coin_price
from ..market.models import Coin


class OrderCondition(models.Model):
    """매수/매도 주문 조건"""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user', on_delete=models.CASCADE)
    coin = models.ForeignKey(Coin, related_name='coin', on_delete=models.CASCADE)
    ref_price = models.FloatField('기준가', default=0.0, help_text='최초 로직 실행 시 참고가 될 기준가. 생성 이후에 절대 수정 금지')

    # 시세 상승 조건
    rise_value = models.FloatField('상승 값', default=0.0, help_text='양수 혹은 음수')
    rise_ratio = models.BooleanField('상승값 %여부', default=True, help_text='% 단위로 상승(매도) 조건 지정 시 체크')

    # 시세 하락 조건
    fall_value = models.FloatField('하락 값', default=0.0, help_text='양수 혹은 음수')
    fall_ratio = models.BooleanField('하락 값 %여부', default=True, help_text='% 단위로 하락(매수) 조건 지정 시 체크')

    # 구매 예정 개수
    buy_amount = ArrayField(
        models.FloatField(), verbose_name='매수량', help_text='[1, 2.1, 3.5, 5...] 형태로 양수 혹은 음수를 입력'
    )

    # 비동기 로직 동작 여부
    is_active = models.BooleanField(
        '로직 실행', default=False, help_text='최초 주문 조건 생성 시 자동으로 활성되므로 체크 해제로 둘 것,'
                                          ' 최초 생성 후 도중에 중단하고 싶은 경우 체크 해제'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'order_condition'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.before_is_active = self.is_active

    def __str__(self):
        return '{} - {}'.format(self.user, self.coin)

    def save(self, *args, **kwargs):
        # 최초 생성 시
        if not self.pk:
            self.is_active = True

        super().save(*args, **kwargs)

        # 중복 감시를 피하기 위해 로직 실행여부(is_active)가 False => True 인 경우에만
        # 자동 감시 주문 로직 실행
        if not self.before_is_active and self.is_active:
            observe_coin_price.delay(condition_id=self.pk)


class Order(models.Model):
    """주문 조건의 개별 주문"""

    WAIT, DONE, FAIL, CANCEL = 0, 1, 2, 3
    STATUS_CHOICE = (
        (WAIT, '체결대기'),
        (DONE, '체결완료'),
        (FAIL, '주문실패'),
        (CANCEL, '주문취소'),
    )

    BUY, SELL = 0, 1
    TYPE_CHOICES = (
        (BUY, '매수'),
        (SELL, '매도'),
    )

    condition = models.ForeignKey(
        OrderCondition,
        related_name='orders',
        on_delete=models.CASCADE,
        verbose_name='주문 조건'
    )

    uuid = models.CharField('주문 고유번호', max_length=40, unique=True)
    status = models.IntegerField('주무 상태', choices=STATUS_CHOICE, default=0)
    type = models.IntegerField('주문 유형', choices=TYPE_CHOICES)
    valance = models.FloatField('주문 개수', default=0.0)
    price = models.FloatField('개당 주문가', default=0.0)
    sell_price = models.FloatField('목표 매도가', default=0.0, help_text='매수인 경우에만 적용')
    is_sold = models.BooleanField('판매 완료 처리 여부', default=False)

    extra = JSONField(default=dict, blank=True, verbose_name='부가정보')

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'order'

    def __str__(self):
        return '{}({})'.format(self.uuid[:5] + '...', self.get_status_display())
