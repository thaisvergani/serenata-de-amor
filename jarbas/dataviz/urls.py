from django.urls import path

from . import views

app_name = 'dataviz'

urlpatterns = [
    path('', views.dataviz_dashboard),

]
