from django.urls import path

from . import views

app_name = "catalogue"
urlpatterns = [
    path("products/", views.catalogue, name="all"),
    path("products/new/", views.catalogue, {"preset": "new"}, name="new"),
    path("products/<slug:category>/", views.catalogue, name="category"),
    path("products/<slug:category>/<slug:slug>/", views.product, name="product"),
    path("spaces/<slug:space>/", views.catalogue, name="space"),
    path("outdoor/", views.catalogue, {"preset": "outdoor"}, name="outdoor"),
    path("search/", views.search, name="search"),
    path("search/suggest/", views.suggest, name="suggest"),
]
