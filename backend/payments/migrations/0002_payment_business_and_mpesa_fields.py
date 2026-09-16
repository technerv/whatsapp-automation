import django.db.models.deletion
from django.db import migrations, models


def backfill_business(apps, schema_editor):
    Payment = apps.get_model('payments', 'Payment')
    for payment in Payment.objects.select_related('invoice__order').all():
        payment.business_id = payment.invoice.order.business_id
        payment.save(update_fields=['business'])


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0001_initial'),
        ('payments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='business',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='payments',
                to='accounts.business',
            ),
        ),
        migrations.AddField(
            model_name='payment',
            name='callback_payload',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='checkout_request_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='merchant_request_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.RunPython(backfill_business, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='payment',
            name='business',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='payments',
                to='accounts.business',
            ),
        ),
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(fields=['business', 'status'], name='payments_pa_busines_4f4b5e_idx'),
        ),
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(fields=['business', 'created_at'], name='payments_pa_busines_8f4fb1_idx'),
        ),
        migrations.AddConstraint(
            model_name='payment',
            constraint=models.UniqueConstraint(
                condition=models.Q(checkout_request_id__isnull=False),
                fields=('business', 'checkout_request_id'),
                name='unique_payment_checkout_request_per_business',
            ),
        ),
    ]