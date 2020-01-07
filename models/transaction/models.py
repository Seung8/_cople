from django.conf import settings
from django.contrib.postgres.fields import ArrayField, JSONField
from django.db import models

from models.transaction.tasks import observe_condition
from ..market.models import Coin


class OrderCondition(models.Model):
    """
    매수/매도 주문 조건

    생성 시 시세 매 초마다 조회 후 로직 실행
    시세 상승으로 인하여 매도(총 구매 개수 -1개)가 일어난 경우
    해당 조건은 비활성화하고 새로운 조건을 생성하여 새로 루프를 실행
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user', on_delete=models.CASCADE)
    coin = models.ForeignKey(Coin, related_name='coin', on_delete=models.CASCADE)
    reference_price = models.IntegerField('기준가', default=0)

    # 시세 상승 조건
    rise_value = models.IntegerField('상승 값', default=0)
    rise_ratio = models.BooleanField('상승값 %여부', default=True)

    # 시세 하락 조건
    fall_value = models.IntegerField('하락 값', default=0)
    fall_ratio = models.BooleanField('하락 값 %여부', default=True)
    buy_amount = ArrayField(models.IntegerField(), verbose_name='매수량(1,2,3... 형태로 입력)')
    bought_amount = models.IntegerField('총 매수량', default=0)

    is_active = models.BooleanField('로직 실행', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'order_condition'

    def __str__(self):
        return '{} - {}'.format(self.user, self.coin)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        try:
            observe_condition.delay(self.pk)
        except Exception as e:
            print('예외 발생: ', e)


class Order(models.Model):
    class StatusChoices(models.IntegerChoices):
        DONE = (0, '완료')
        FAIL = (1, '실패')
        CANCEL = (2, '취소')

    condition = models.ForeignKey(OrderCondition, related_name='condition', on_delete=models.CASCADE)
    uuid = models.CharField('주문 고유번호', max_length=40, unique=True)
    status = models.IntegerField('주무 상태', choices=StatusChoices.choices, default=0)
    info = JSONField(default=dict, blank=True, verbose_name='주문 정보')

    class Meta:
        db_table = 'order'

    def __str__(self):
        return '{}({})'.format(self.uuid[:5] + '...', self.get_status_display())
