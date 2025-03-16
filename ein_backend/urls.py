
from django.contrib import admin
from django.urls import path, include



urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include([
        path('messaging/', include('messaging.urls')),
       
        path('stores/', include('stores.urls')),
        path('reviews/', include('reviews.urls')),
        path('users/', include('users.urls')),


    ])),

]




