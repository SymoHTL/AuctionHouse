from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('create_listing', views.create_listing, name='create_listing'),
    path("<int:listing_id>", views.active_listing, name="active_listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("close_bid", views.close_bid, name="close_bid"),
    path('comment', views.comment, name='comment'),
    path('category/<str:category>', views.category, name='category'),
    ]
