from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('ar/', views.index, {'lang': 'ar'}, name='index_ar'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('sitemap.xml', views.sitemap_xml, name='sitemap_xml'),
]
