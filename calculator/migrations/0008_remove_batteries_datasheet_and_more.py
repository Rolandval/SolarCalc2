# Generated by Django 5.1.7 on 2025-04-14 07:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calculator', '0007_batteries_voltage_type_inverters_voltage_type_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='batteries',
            name='datasheet',
        ),
        migrations.RemoveField(
            model_name='inverters',
            name='datasheet',
        ),
        migrations.RemoveField(
            model_name='panels',
            name='datasheet',
        ),
        migrations.AddField(
            model_name='batteries',
            name='datasheet_last_updated',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Останнє оновлення'),
        ),
        migrations.AddField(
            model_name='batteries',
            name='datasheet_name',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Назва файлу'),
        ),
        migrations.AddField(
            model_name='batteries',
            name='datasheet_url',
            field=models.URLField(blank=True, null=True, verbose_name='URL датащиту'),
        ),
        migrations.AddField(
            model_name='inverters',
            name='datasheet_last_updated',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Останнє оновлення'),
        ),
        migrations.AddField(
            model_name='inverters',
            name='datasheet_name',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Назва файлу'),
        ),
        migrations.AddField(
            model_name='inverters',
            name='datasheet_url',
            field=models.URLField(blank=True, null=True, verbose_name='URL датащиту'),
        ),
        migrations.AddField(
            model_name='panels',
            name='datasheet_last_updated',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Останнє оновлення'),
        ),
        migrations.AddField(
            model_name='panels',
            name='datasheet_name',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Назва файлу'),
        ),
        migrations.AddField(
            model_name='panels',
            name='datasheet_url',
            field=models.URLField(blank=True, null=True, verbose_name='URL датащиту'),
        ),
        migrations.AlterField(
            model_name='batteries',
            name='capacity',
            field=models.DecimalField(decimal_places=3, max_digits=10, verbose_name='Ємність'),
        ),
    ]
