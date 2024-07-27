from django.contrib import admin
from django.urls import path

from paperwork import views as pw_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', pw_views.index_page),
]
