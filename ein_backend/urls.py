
from django.contrib import admin
from django.urls import path, include
from messaging import routing


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include([
        path('messaging/', include('messaging.urls')),
        path('messaging/ws/', include(routing.websocket_urlpatterns)),
        path('stores/', include('stores.urls')),
        path('reviews/', include('reviews.urls')),
        path('users/', include('users.urls')),


    ])),

]




