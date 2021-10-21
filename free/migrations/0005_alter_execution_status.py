# Generated by Django 3.2.6 on 2021-09-30 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('free', '0004_alter_result_execution'),
    ]

    operations = [
        migrations.AlterField(
            model_name='execution',
            name='status',
            field=models.CharField(choices=[('C', 'Configured'), ('E', 'Error'), ('R', 'Running'), ('F', 'Finished'), ('A', 'Aborted'), ('T', 'Timeout')], max_length=1, verbose_name='Status'),
        ),
    ]