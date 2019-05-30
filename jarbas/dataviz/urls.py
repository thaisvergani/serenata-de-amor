from django.urls import path
from django.conf.urls import url

from . import views

app_name = 'dataviz'

urlpatterns = [
    url(r'^$', views.dataviz_dashboard),
    url(r'^api/tweet_chart', views.tweet_chart, name='tweet_chart'),
    url(r'^api/congressperson_info', views.get_congress_person_data, name='congressperson_info'),

]
