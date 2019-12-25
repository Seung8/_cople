# Generated by Django 3.0.1 on 2019-12-25 14:31

from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('market', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderCondition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reference_price', models.IntegerField(default=0, verbose_name='기준가')),
                ('gain_value', models.IntegerField(default=0, verbose_name='상승 값')),
                ('gain_ratio', models.BooleanField(default=True, verbose_name='상승값 %여부')),
                ('sank_value', models.IntegerField(default=0, verbose_name='하락 값')),
                ('sank_ratio', models.BooleanField(default=True, verbose_name='하락 값 %여부')),
                ('buy_amount', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), size=None, verbose_name='매수량(1,2,3... 형태로 입력)')),
                ('bought_amount', models.IntegerField(default=0, verbose_name='총 매수량')),
                ('is_active', models.BooleanField(default=True, verbose_name='로직 실행')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('stopped_at', models.DateTimeField(blank=True, null=True)),
                ('coin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='market.Coin')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'order_condition',
            },
        ),
    ]