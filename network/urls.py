
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("following", views.following, name="following"),
    path("<str:username>", views.profile, name="profile"),
    path("edit/<int:postID>", views.edit, name="edit"),
    path("like_status/<int:postID>", views.like_status, name="like_status"),
    path("like/<int:postID>", views.like, name="like")
]
