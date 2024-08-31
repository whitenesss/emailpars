from django.shortcuts import render


# Create your views here.
def email_massage(request):
    return render(request, 'parsers/email_massage.html')
