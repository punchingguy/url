from django.urls import path
from . import views
from .views import VerificationView
urlpatterns =[
    path("register",views.register, name="register"),
    path("login",views.login, name="login"),
    path("logout",views.logout, name="logout"),
    path("base",views.base,name="base"),
    path('activate/<uidb64>/<token>', VerificationView.as_view(), name="activate")
]