"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from dashboard import views as dashboard_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', dashboard_views.index, name='dashboard'),
    path('analytics/', dashboard_views.analytics, name='analytics'),

    # Each app's urls.py lists its own list/add/edit/delete routes.
    path("", include("members.urls")),
    path("", include("staff.urls")),
    path("", include("accounts.urls")),
    path("", include("savings.urls")),
    path("", include("withdrawals.urls")),
    path("", include("loans.urls")),
]
