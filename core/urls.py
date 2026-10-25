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
from django.urls import path

from accounts import views as accounts_views
from dashboard import views as dashboard_views
from loans import views as loans_views
from members import views as members_views
from savings import views as savings_views
from staff import views as staff_views
from withdrawals import views as withdrawals_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Home page, also reachable as index.html to match the nav links
    path('', dashboard_views.index),
    path('index.html', dashboard_views.index),

    # Login and staff registration pages
    path('login.html', staff_views.login_view),
    path('staff.html', staff_views.staff),

    # Member registration page
    path('member.html', members_views.member),

    # Account application page
    path('account.html', accounts_views.account),

    # Saving registration page
    path('saving.html', savings_views.saving),

    # Loan application and loan payment pages
    path('loan.html', loans_views.loan),
    path('loan-payment.html', loans_views.loan_payment),

    # Withdrawal page
    path('withdrawal.html', withdrawals_views.withdrawal),
]
