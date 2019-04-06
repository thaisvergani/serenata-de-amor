from django.urls import path
from django.conf.urls import url

from . import views

app_name = 'dataviz'

urlpatterns = [
    url(r'^$', views.dataviz_dashboard),
    url(r'^api/tweet_chart/', views.tweet_chart, name='tweet_chart'),
    url(r'^meals_chart/', views.meals_chart, name='meals_chart'),
    url(r'^api/meals_chart/', views.meals_chart_data, name='meals_chart_data'),

]
