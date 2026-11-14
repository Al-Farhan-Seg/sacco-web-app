from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render

from .forms import SignUpForm


# Lets a logged-out visitor create an account, then signs them straight in
def sign_up(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f"Welcome, {user.first_name}. Your account is ready.")
        return redirect("dashboard")

    return render(request, "registration/sign_up.html", {"form": form})
