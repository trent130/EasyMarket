from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_add_fk_relationships'),
        ('products', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Order: status default lowercase, reference allow blank
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('pending', 'Pending'), ('processing', 'Processing'),
                    ('shipped', 'Shipped'), ('delivered', 'Delivered'),
                    ('canceled', 'Canceled'), ('refunded', 'Refunded'),
                    ('returned', 'Returned'),
                ],
                default='pending',
            ),
        ),
        migrations.AlterField(
            model_name='order',
            name='reference',
            field=models.CharField(max_length=20, unique=True, blank=True),
        ),
        # Tighten FK fields that were nullable only for migration purposes (tables are empty)
        migrations.AlterField(
            model_name='orderitem',
            name='order',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='items',
                to='orders.order',
            ),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='product',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to='products.product',
            ),
        ),
        migrations.AlterField(
            model_name='refund',
            name='order',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='orders.order',
            ),
        ),
        migrations.AlterField(
            model_name='refund',
            name='status',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected'),
                ],
                default='pending',
            ),
        ),
        migrations.AlterField(
            model_name='shippingaddress',
            name='user',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
