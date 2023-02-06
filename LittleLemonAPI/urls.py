from django.urls import path
from . import views

urlpatterns = [
    path("menu-items", views.MenuItemsAPIView.as_view()),
    path("menu-items/<int:pk>", views.SingleMenuItemAPIView.as_view())
]
