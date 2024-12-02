from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('queries/', views.query_demonstration, name='query_demonstration'),

    path('locations/', views.location_list, name='location_list'),
    path('locations/<int:pk>/', views.location_detail, name='location_detail'),
    path('locations/create/', views.location_create, name='location_create'),
    path('locations/<int:pk>/update/', views.location_update, name='location_update'),
    path('locations/<int:pk>/delete/', views.location_delete, name='location_delete'),

    path('metrics/', views.metric_list, name='metric_list'),
    path('metrics/<int:pk>/', views.metric_detail, name='metric_detail'),
    path('metrics/create/', views.metric_create, name='metric_create'),
    path('metrics/<int:pk>/update/', views.metric_update, name='metric_update'),
    path('metrics/<int:pk>/delete/', views.metric_delete, name='metric_delete'),

    path('alerts/', views.alert_list, name='alert_list'),
    path('alerts/<int:pk>/', views.alert_detail, name='alert_detail'),
    path('alerts/create/', views.alert_create, name='alert_create'),
    path('alerts/<int:pk>/update/', views.alert_update, name='alert_update'),
    path('alerts/<int:pk>/delete/', views.alert_delete, name='alert_delete'),

    path('aqi/', views.aqi_list, name='aqi_list'),
    path('aqi/<int:pk>/', views.aqi_detail, name='aqi_detail'),
    path('aqi/create/', views.aqi_create, name='aqi_create'),
    path('aqi/<int:pk>/update/', views.aqi_update, name='aqi_update'),
    path('aqi/<int:pk>/delete/', views.aqi_delete, name='aqi_delete'),
]