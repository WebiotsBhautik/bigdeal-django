from django.urls import path
from .import views

urlpatterns = [
    path('',views.index,name='index'),
    path('layout2',views.layout2,name='layout2'),
    path('layout3',views.layout3,name='layout3'),
]
