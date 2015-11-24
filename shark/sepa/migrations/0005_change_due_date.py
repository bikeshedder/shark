# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sepa', '0004_optional_reference_and_executed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='directdebitbatch',
            name='due_date',
            field=models.DateField(help_text='Must be min. 5 TARGET dates in the future for the first transaction and 2 target days in the future for recurring transactions.', verbose_name='due date'),
        ),
    ]
