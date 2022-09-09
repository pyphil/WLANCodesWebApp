from django.shortcuts import render


def codes(request):
    return render(request, 'codes.html', {'text': "12345-67891"})
