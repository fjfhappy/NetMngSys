from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout

from NetMngApp.models import DevPingInfo, SysSettingInfo
import time
import threading
from NetMngApp.pingTool import icmp_ping_delay
# Create your views here.

democrated = False

def dorecycleping():
    refreshtime = int(SysSettingInfo.objects.get(settingitem="pingrefresh").settingvalue)
    pingtimeout = int(SysSettingInfo.objects.get(settingitem="pingtimeout").settingvalue)
    pingcount = int(SysSettingInfo.objects.get(settingitem="pingcount").settingvalue)
    while(True):
        devs = DevPingInfo.objects.all()
        for dev in devs:
            ip = dev.DEV.IP
            (connceted, info, delaytime) = icmp_ping_delay(ip, pingtimeout, pingcount)
            DevPingInfo.objects.update_or_create(DEV=dev.DEV, defaults={'DEV':dev.DEV, 'connected':connceted, 'delaytime':delaytime})
        print(refreshtime)
        time.sleep(refreshtime)

def startDemothreads(request):
    global democrated
    if(not democrated):
        recyclepingthread = threading.Thread(target=dorecycleping())
        recyclepingthread.setDaemon(True)
        recyclepingthread.start()
        democrated = True
    return HttpResponse()


def dologin(request):
    if(request.method == "POST"):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username = username, password = password)
        if user:
            login(request, user)
            return redirect('/devlist/')
        else:
            return render(request, 'login.html')
    else:
        return render(request, 'login.html')

def dologout(request):
    logout(request)
    return redirect('/login/')