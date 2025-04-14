from django.db import models
import os
from django.conf import settings
import boto3
from django.utils import timezone

class Users(models.Model):
    phone = models.CharField(max_length=20, verbose_name="Телефон", null=True)
    email: str = models.EmailField(verbose_name="Email", null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")

    def __str__(self):
        return self.email
    

class Panels(models.Model):
    brand = models.CharField(max_length=20, verbose_name="Бренд")
    model = models.CharField(max_length=20, verbose_name="Модель")
    panel_length = models.DecimalField(max_digits=10, decimal_places=3, verbose_name="Довжина")
    panel_width = models.DecimalField(max_digits=10, decimal_places=3, verbose_name="Ширина")
    panel_height = models.DecimalField(max_digits=10, decimal_places=3, verbose_name="Висота")
    datasheet_url = models.URLField(verbose_name="URL датащиту", blank=True, null=True)
    datasheet_name = models.CharField(max_length=255, verbose_name="Назва файлу", blank=True, null=True)
    datasheet_last_updated = models.DateTimeField(verbose_name="Останнє оновлення", blank=True, null=True)

    def __str__(self):
        return f"{self.brand} {self.model}"
    
    def upload_datasheet(self, file):
        """Завантажує даташит в S3 та оновлює URL"""
        if not file:
            return
            
        try:
            # Створюємо клієнта S3
            s3 = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )
            
            # Генеруємо унікальну назву файлу
            file_extension = os.path.splitext(file.name)[1]
            filename = f"panels/{timezone.now().strftime('%Y%m%d_%H%M%S')}_{file.name}"
            
            # Завантажуємо файл в S3
            s3.upload_fileobj(
                file,
                settings.AWS_STORAGE_BUCKET_NAME,
                filename,
            )
            
            # Оновлюємо URL та інформацію про файл
            self.datasheet_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{filename}"
            self.datasheet_name = file.name
            self.datasheet_last_updated = timezone.now()
            self.save()
            
            return self.datasheet_url
            
        except Exception as e:
            print(f"Помилка при завантаженні файлу: {str(e)}")
            raise
    
    def get_datasheet_url(self):
        return self.datasheet_url


class Inverters(models.Model):
    brand = models.CharField(max_length=20, verbose_name="Бренд")
    model = models.CharField(max_length=20, verbose_name="Модель")
    power = models.DecimalField(max_digits=10, decimal_places=3, verbose_name="Максимальна потужність")
    phases_count = models.IntegerField(verbose_name="Кількість фаз")
    voltage_type = models.CharField(max_length=20, verbose_name="Тип напруги")
    datasheet_url = models.URLField(verbose_name="URL датащиту", blank=True, null=True)
    datasheet_name = models.CharField(max_length=255, verbose_name="Назва файлу", blank=True, null=True)
    datasheet_last_updated = models.DateTimeField(verbose_name="Останнє оновлення", blank=True, null=True)

    def __str__(self):
        return f"{self.brand} {self.model}"

    def upload_datasheet(self, file):
        """Завантажує даташит в S3 та оновлює URL"""
        if not file:
            return
            
        try:
            # Створюємо клієнта S3
            s3 = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )
            
            # Генеруємо унікальну назву файлу
            file_extension = os.path.splitext(file.name)[1]
            filename = f"inverters/{timezone.now().strftime('%Y%m%d_%H%M%S')}_{file.name}"
            
            # Завантажуємо файл в S3
            s3.upload_fileobj(
                file,
                settings.AWS_STORAGE_BUCKET_NAME,
                filename,
            )
            
            # Оновлюємо URL та інформацію про файл
            self.datasheet_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{filename}"
            self.datasheet_name = file.name
            self.datasheet_last_updated = timezone.now()
            self.save()
            
            return self.datasheet_url
            
        except Exception as e:
            print(f"Помилка при завантаженні файлу: {str(e)}")
            raise
    
    def get_datasheet_url(self):
        return self.datasheet_url


class Batteries(models.Model):
    brand = models.CharField(max_length=20, verbose_name="Бренд")
    model = models.CharField(max_length=20, verbose_name="Модель")
    capacity = models.DecimalField(max_digits=10, decimal_places=3, verbose_name="Ємність")
    is_head = models.BooleanField(default=False, verbose_name="Head")
    is_stand = models.BooleanField(default=False, verbose_name="Стенд")
    voltage_type = models.CharField(max_length=20, verbose_name="Тип напруги")
    datasheet_url = models.URLField(verbose_name="URL датащиту", blank=True, null=True)
    datasheet_name = models.CharField(max_length=255, verbose_name="Назва файлу", blank=True, null=True)
    datasheet_last_updated = models.DateTimeField(verbose_name="Останнє оновлення", blank=True, null=True)

    def __str__(self):
        return f"{self.brand} {self.model}"
    
    def upload_datasheet(self, file):
        """Завантажує даташит в S3 та оновлює URL"""
        if not file:
            return
            
        try:
            # Створюємо клієнта S3
            s3 = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )
            
            # Генеруємо унікальну назву файлу
            file_extension = os.path.splitext(file.name)[1]
            filename = f"batteries/{timezone.now().strftime('%Y%m%d_%H%M%S')}_{file.name}"
            
            # Завантажуємо файл в S3
            s3.upload_fileobj(
                file,
                settings.AWS_STORAGE_BUCKET_NAME,
                filename,
            )
            
            # Оновлюємо URL та інформацію про файл
            self.datasheet_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{filename}"
            self.datasheet_name = file.name
            self.datasheet_last_updated = timezone.now()
            self.save()
            
            return self.datasheet_url
            
        except Exception as e:
            print(f"Помилка при завантаженні файлу: {str(e)}")
            raise
    
    def get_datasheet_url(self):
        return self.datasheet_url