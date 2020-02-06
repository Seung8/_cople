# Generated by Django 2.2.9 on 2020-02-06 09:29

from django.conf import settings
import django.contrib.postgres.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('market', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderCondition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('buy_price', models.IntegerField(default=0, verbose_name='최초 구매 설정가')),
                ('rise_value', models.IntegerField(default=0, verbose_name='상승 값')),
                ('rise_ratio', models.BooleanField(default=True, verbose_name='상승값 %여부')),
                ('fall_value', models.IntegerField(default=0, verbose_name='하락 값')),
                ('fall_ratio', models.BooleanField(default=True, verbose_name='하락 값 %여부')),
                ('buy_amount', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), size=None, verbose_name='매수량(1,2,3... 형태로 입력)')),
                ('coin_amount', models.IntegerField(default=0, verbose_name='총 코인 보유량')),
                ('is_active', models.BooleanField(default=False, verbose_name='로직 실행')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('coin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='coin', to='market.Coin')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'order_condition',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.CharField(max_length=40, unique=True, verbose_name='주문 고유번호')),
                ('status', models.IntegerField(choices=[(0, '체결대기'), (1, '체결완료'), (2, '주문실패'), (3, '주문취소')], default=0, verbose_name='주무 상태')),
                ('type', models.IntegerField(choices=[(0, '매수'), (1, '매도')], verbose_name='주문 유형')),
                ('valance', models.FloatField(default=0.0, verbose_name='주문 개수')),
                ('price', models.FloatField(default=0.0, verbose_name='개당 주문가')),
                ('extra', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, verbose_name='부가정보')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('condition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='order.OrderCondition', verbose_name='주문 조건')),
            ],
            options={
                'db_table': 'order',
            },
        ),
    ]