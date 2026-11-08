from django.contrib.auth.decorators import login_required
from django.shortcuts import render


# Shows the home page
@login_required
def index(request):
    return render(request, 'dashboard/index.html')
