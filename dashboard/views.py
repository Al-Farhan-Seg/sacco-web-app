from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .stats import summary


# Shows the home page with the SACCO's live numbers
@login_required
def index(request):
    return render(request, 'dashboard/index.html', summary())
