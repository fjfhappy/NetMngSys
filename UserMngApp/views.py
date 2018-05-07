from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout

from NetMngApp.models import DevPingInfo, SysSettingInfo
from NetMngApp.views import refreshdevverboseinfo
import time, datetime
import threading
from NetMngApp.pingTool import icmp_ping_delay
# Create your views here.

democreated = False


def dorecycleping():
    while(True):
        refreshtime = int(SysSettingInfo.objects.get(settingitem="pingrefresh").settingvalue)
        pingtimeout = int(SysSettingInfo.objects.get(settingitem="pingtimeout").settingvalue)
        pingcount = int(SysSettingInfo.objects.get(settingitem="pingcount").settingvalue)
        devs = DevPingInfo.objects.all()
        for dev in devs:
            ip = dev.DEV.IP
            (connceted, info, delaytime) = icmp_ping_delay(ip, pingtimeout, pingcount)
            DevPingInfo.objects.update_or_create(DEV=dev.DEV, defaults={'DEV':dev.DEV, 'connected':connceted, 'delaytime':delaytime})
        time.sleep(refreshtime)

def dorefreshdevverbose():
    while(True):
        refreshhour = int(SysSettingInfo.objects.get(settingitem="devinforefresh").settingvalue)
        dnow = datetime.datetime.now()
        nowstruct = time.localtime(time.time())
        year = nowstruct[0]
        month = nowstruct[1]
        day = nowstruct[2]
        hour = nowstruct[3]
        if (hour < refreshhour):
            drefresh = datetime.datetime(year, month, day, refreshhour, 0, 0)
        else:
            tommrow = datetime.date.today() + datetime.timedelta(days=1)
            year = tommrow.year
            month = tommrow.month
            day = tommrow.day
            drefresh = datetime.datetime(year, month, day, refreshhour, 0, 0)
        sleepsecs = (drefresh - dnow).seconds
        time.sleep(sleepsecs)
        refreshdevverboseinfo()


def startDemothreads(request):
    global democreated

    if(not democreated):
        recyclepingthread = threading.Thread(target=dorecycleping)
        recyclepingthread.setDaemon(True)
        recyclepingthread.start()
        refreshdevverboseinfothread = threading.Thread(target=dorefreshdevverbose)
        refreshdevverboseinfothread.setDaemon(True)
        refreshdevverboseinfothread.start()
        democreated = True
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