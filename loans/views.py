from django.shortcuts import render


# Shows the loan application page
def loan(request):
    return render(request, 'loans/loan.html')


# Shows the loan payment page
def loan_payment(request):
    return render(request, 'loans/loan_payment.html')
