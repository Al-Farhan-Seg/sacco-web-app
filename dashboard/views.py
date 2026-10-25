from django.shortcuts import render


# Shows the home page
def index(request):
    return render(request, 'dashboard/index.html')
