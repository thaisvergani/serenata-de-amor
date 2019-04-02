from django.urls import path
from django.conf.urls import url

from . import views

app_name = 'dataviz'

urlpatterns = [
    url(r'^$', views.dataviz_dashboard),
    url(r'^api/tweet_chart/', views.tweet_chart, name='tweet_chart'),

]
