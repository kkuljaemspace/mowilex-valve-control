from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.menu, name="menu"),
    path('scan/', views.scan, name="scan"),
    path('po-detail/<int:ponum>/', views.po_detail, name='po_detail'),
    path('inquiry/', views.inquiry, name="inquiry"),
    path('open-valve/', views.open_valve, name='open_valve'),
    path('po-list/', views.list_po, name='po_list'),
    path('alarm/', views.alarm, name='alarm'),
    path('po/<int:ponum>/<str:valve>/done/', views.mark_po_done, name='mark_po_done'),
    path('po/<int:ponum>/<str:valve>/pause/', views.mark_po_pause, name='mark_po_pause'),
    
    # Modbus Service Management
    path('modbus/settings/', views.modbus_settings, name='modbus_settings'),
    path('modbus/start/', views.modbus_start, name='modbus_start'),
    path('modbus/stop/', views.modbus_stop, name='modbus_stop'),
    path('modbus/restart/', views.modbus_restart, name='modbus_restart'),
    path('modbus/status/', views.modbus_status_api, name='modbus_status_api'),
]


