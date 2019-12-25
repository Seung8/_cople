from django.db import models


class Coin(models.Model):
    """
    코인 테이블

    사용자로부터 입력을 받아 코인을 거래할 경우 사용자 입력 방식에 따라 예외가 발생할 수 있으므로
    미리 프로젝트에서 사용자가 코인을 선택하여 거래할 수 있도록 코인을 기록
    """
    name_ko = models.CharField('코인명(한글)', max_length=20)
    name_en = models.CharField('코인명(영어)', max_length=50)
    code = models.CharField('코인 코드', max_length=20)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'coin'
        ordering = ['-name_ko']

    def __str__(self):
        return '{}({})'.format(self.name_ko, self.name_en)
