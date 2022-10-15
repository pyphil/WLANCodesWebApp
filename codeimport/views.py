from django.shortcuts import render, redirect
import re
from WLANCodesWebApp.models import Code, Config


def codeimport(request):
    if request.method == 'GET':
        try:
            lnk_controller = Config.objects.get(name='lnk_controller')
            lnk_controller = lnk_controller.setting
        except Config.DoesNotExist:
            lnk_controller = "#"
        return render(request, 'codeimport.html', {'lnk_controller': lnk_controller})
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
