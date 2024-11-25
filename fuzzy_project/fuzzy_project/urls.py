from django.contrib import admin
from django.urls import path, include
from fuzzy_system import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('one/', views.index, name='index'),
    path('many/', include('fuzzylogic.urls')),
]


