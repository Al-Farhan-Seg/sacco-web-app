from django.shortcuts import render


# Shows the saving registration page
def saving(request):
    return render(request, 'savings/saving.html')
