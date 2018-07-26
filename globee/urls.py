from django.urls import path

from globee import views

urlpatterns = [
    path('globee-ipn/', views.globee_ipn_view, name='globee-ipn'),
]
