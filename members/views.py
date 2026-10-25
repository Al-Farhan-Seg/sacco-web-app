from django.shortcuts import render


# Shows the member registration page
def member(request):
    return render(request, 'members/member.html')
