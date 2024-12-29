from django.urls import path
from . import views
urlpatterns = [
    path('playground/', views.say_hello)
]
 
