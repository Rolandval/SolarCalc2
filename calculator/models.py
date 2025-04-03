from django.db import models
import os


class Users(models.Model):
    phone = models.CharField(max_length=20, verbose_name="Телефон", null=True)
    email: str = models.EmailField(verbose_name="Email", null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")

    def __str__(self):
        return self.email
    

class Panels(models.Model):
    brand = models.CharField(max_length=20, verbose_name="Бренд")
    model = models.CharField(max_length=20, verbose_name="Модель")
    panel_length = models.DecimalField(max_digits=10, decimal_places=3, verbose_name="Довжина панелі")
    panel_width = models.DecimalField(max_digits=10, decimal_places=3, verbose_name="Ширина панелі")
    panel_height = models.DecimalField(max_digits=10, decimal_places=3, verbose_name="Висота панелі")
    datasheet = models.CharField(max_length=255, verbose_name="Дашбоард", help_text="Шлях до файлу в директорії datasheets")

    def __str__(self):
        return f"{self.brand} {self.model}"
    
    def get_datasheet_url(self):
        return os.path.join('/media/datasheets/', os.path.basename(self.datasheet))


class Inverters(models.Model):
    brand = models.CharField(max_length=20, verbose_name="Бренд")
    model = models.CharField(max_length=20, verbose_name="Модель")
    power = models.DecimalField(max_digits=10, decimal_places=3, verbose_name="Максимальна потужність")
    phases_count = models.IntegerField(verbose_name="Кількість фаз")
    datasheet = models.CharField(max_length=255, verbose_name="Дашбоард",
                                 help_text="Шлях до файлу в директорії datasheets")

    def __str__(self):
        return f"{self.brand} {self.model}"

    def get_datasheet_url(self):
        return os.path.join('/media/datasheets/', os.path.basename(self.datasheet))


class Batteries(models.Model):
    brand = models.CharField(max_length=20, verbose_name="Бренд")
    model = models.CharField(max_length=20, verbose_name="Модель")
    capacity = models.DecimalField(max_digits=10, decimal_places=3, verbose_name="Максимальна потужність")
    is_head = models.BooleanField(default=False, verbose_name="Head")
    is_stand = models.BooleanField(default=False, verbose_name="Стенд")
    datasheet = models.CharField(max_length=255, verbose_name="Дашбоард",
                                 help_text="Шлях до файлу в директорії datasheets")

    def __str__(self):
        return f"{self.brand} {self.model}"

    def get_datasheet_url(self):
        return os.path.join('/media/datasheets/', os.path.basename(self.datasheet))
