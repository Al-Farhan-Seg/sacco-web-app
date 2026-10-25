from django.shortcuts import render


# Shows the withdrawal page
def withdrawal(request):
    return render(request, 'withdrawals/withdrawal.html')
