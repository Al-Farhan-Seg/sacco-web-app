from django.shortcuts import render


# Shows the account application page
def account(request):
    return render(request, 'accounts/account.html')
