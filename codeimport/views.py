from django.shortcuts import render, redirect
import re
from WLANCodesWebApp.models import Code


def codeimport(request):
    if request.method == 'GET':
        return render(request, 'codeimport.html', {})
    if request.method == 'POST':
        # get Codes
        text = request.POST.get('codes')
        codes = re.findall(r'\d\d\d\d\d-\d\d\d\d\d', text)
        # TODO Auf Duplikate prüfen
        for code in codes:
            Code.objects.create(
                code=code,
                type=request.POST.get('type'),
                duration=int(request.POST.get('duration'))
            )
        return redirect('codeimport')
