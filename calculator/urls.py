from django.urls import path

from . import views

app_name = 'calculator'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/calculate/', views.calculate, name='calculate'),
    path('generate-pdf/', views.generate_pdf, name='generate_pdf'),
    path('send-pdf-telegram/', views.send_pdf_telegram, name='send_pdf_telegram'),
    path('send_pdf_to_telegram/', views.send_pdf_telegram, name='send_pdf_to_telegram'),
    path('send-pdf-email/', views.send_pdf_email, name='send_pdf_email'),
    path('panels/create/', views.create_panel, name='create_panel'),
    path('panels/datasheet/<int:panel_id>/', views.download_datasheet, name='download_datasheet'),
    path('inverters/create/', views.create_inverter, name='create_inverter'),
    path('batteries/create/', views.create_battery, name='create_battery'),
    path('inverters/datasheet/<int:inverter_id>/', views.download_inverter_datasheet, name='download_inverter_datasheet'),
    path('batteries/datasheet/<int:battery_id>/', views.download_battery_datasheet, name='download_battery_datasheet'),
]