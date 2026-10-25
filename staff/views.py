from django.shortcuts import render


# Shows the login page
def login_view(request):
    return render(request, 'staff/login.html')


# Shows the staff registration page
def staff(request):
    return render(request, 'staff/staff.html')
