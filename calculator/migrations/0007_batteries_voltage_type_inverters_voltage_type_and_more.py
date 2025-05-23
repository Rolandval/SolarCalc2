# Generated by Django 5.1.7 on 2025-04-11 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calculator', '0006_panels_panel_height'),
    ]

    operations = [
        migrations.AddField(
            model_name='batteries',
            name='voltage_type',
            field=models.CharField(default='zzz', max_length=20, verbose_name='Тип напруги'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='inverters',
            name='voltage_type',
            field=models.CharField(default='zzz', max_length=20, verbose_name='Тип напруги'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='batteries',
            name='datasheet',
            field=models.FileField(help_text='Файл датащиту', upload_to='datasheets/batteries/', verbose_name='Дашбоард'),
        ),
        migrations.AlterField(
            model_name='inverters',
            name='datasheet',
            field=models.FileField(help_text='Файл датащиту', upload_to='datasheets/inverters/', verbose_name='Дашбоард'),
        ),
        migrations.AlterField(
            model_name='panels',
            name='datasheet',
            field=models.FileField(help_text='Файл датащиту', upload_to='datasheets/panels/', verbose_name='Дашбоард'),
        ),
        migrations.AlterField(
            model_name='panels',
            name='panel_height',
            field=models.DecimalField(decimal_places=3, max_digits=10, verbose_name='Висота'),
        ),
        migrations.AlterField(
            model_name='panels',
            name='panel_length',
            field=models.DecimalField(decimal_places=3, max_digits=10, verbose_name='Довжина'),
        ),
        migrations.AlterField(
            model_name='panels',
            name='panel_width',
            field=models.DecimalField(decimal_places=3, max_digits=10, verbose_name='Ширина'),
        ),
    ]
