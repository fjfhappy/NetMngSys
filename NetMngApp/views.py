from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import time
import queue
import threading
import json
from django.db.models import Q

from NetMngApp.IPAddress import IPAddress
from NetMngApp.pingTool import icmp_ping, icmp_ping_delay
from NetMngApp.SNMPTool import getHuaweiSWinfo, getRuijieSWinfo, getCiscoSWinfo, SNMPv2WALK, SNMPv2GET
from NetMngApp.models import DevInfoVerbose, Netsets


# Create your views here.

def base(request):
    return render(request, 'base.html')


def devlist(request):
    alldevlist = list(
        DevInfoVerbose.objects.values_list('IP', 'MAC', 'sysName', 'UpLinkPort', 'destIP', 'CPUUsage', 'memoryUsage'))
    paginator = Paginator(alldevlist, 15, 3)
    page = request.GET.get('page')
    if (page):
        try:
            dev_page = paginator.page(page)
        except PageNotAnInteger:
            dev_page = paginator.page(1)
        except EmptyPage:
            dev_page = paginator.page(paginator.num_pages)
    else:
        dev_page = paginator.page(1)
    dev_list = dev_page.object_list
    return render(request, 'devlist.html', {"title": "设备列表", "dev_page": dev_page, "dev_list": dev_list})


searchdevlist = []
searchtitle = "查询结果："


def devsearch(request):
    global searchdevlist
    global searchtitle
    ipaddress = request.GET.get('ipaddress')
    if (ipaddress):
        ipaddress = ipaddress.strip()
    macaddress = request.GET.get('macaddress')
    if (macaddress):
        macaddress = macaddress.strip()
    destip = request.GET.get('destip')
    if (destip):
        destip = destip.strip()
    devname = request.GET.get('devname')
    if (devname):
        devname = devname.strip()
    searchflag = 0
    if ipaddress or macaddress or devname or destip:
        searchtitle = "查询结果："
        searchflag = 1
    if ipaddress:
        searchtitle = searchtitle + "IP地址" + ipaddress
    if macaddress:
        searchtitle = searchtitle + "MAC地址" + macaddress
    if destip:
        searchtitle = searchtitle + "上联IP" + destip
    if devname:
        searchtitle = searchtitle + "设备名" + devname

    if (searchflag == 1):
        searchdevQuery = None
        if (ipaddress):
            searchdevQuery = DevInfoVerbose.objects.values_list('IP', 'MAC', 'sysName', 'UpLinkPort', 'destIP',
                                                                'CPUUsage', 'memoryUsage').filter(
                IP__contains=ipaddress)
        if (macaddress and searchdevQuery):
            searchdevQuery = searchdevQuery.filter(MAC__icontains=macaddress)
        elif (macaddress and not searchdevQuery):
            searchdevQuery = DevInfoVerbose.objects.values_list('IP', 'MAC', 'sysName', 'UpLinkPort', 'destIP',
                                                                'CPUUsage', 'memoryUsage').filter(
                MAC__icontains=macaddress)
        if (destip and searchdevQuery):
            searchdevQuery = searchdevQuery.filter(destIP__contains=destip)
        elif (destip and not searchdevQuery):
            searchdevQuery = DevInfoVerbose.objects.values_list('IP', 'MAC', 'sysName', 'UpLinkPort', 'destIP',
                                                                'CPUUsage', 'memoryUsage').filter(
                destIP__contains=destip)
        if (devname and searchdevQuery):
            searchdevQuery = searchdevQuery.filter(sysName__icontains=devname)
        elif (devname and not searchdevQuery):
            searchdevQuery = DevInfoVerbose.objects.values_list('IP', 'MAC', 'sysName', 'UpLinkPort', 'destIP',
                                                                'CPUUsage', 'memoryUsage').filter(
                sysName__icontains=devname)
        searchdevlist = list(searchdevQuery)
    paginator = Paginator(searchdevlist, 4, 3)
    page = request.GET.get('page')
    if (page):
        try:
            dev_page = paginator.page(page)
        except PageNotAnInteger:
            dev_page = paginator.page(1)
        except EmptyPage:
            dev_page = paginator.page(paginator.num_pages)
    else:
        dev_page = paginator.page(1)
    dev_list = dev_page.object_list
    return render(request, 'devlist.html', {"title": searchtitle, "dev_page": dev_page, "dev_list": dev_list})


devcrawlinfoqueue = queue.Queue()


def getdevinfothreadfun(ip, mask, gate, port, community, step, devsinfolist, crawlinfoqueue, timeout=2, pingcount=4):
    devinfodickeys = ['updateTime', 'sysDescr', 'errorInfo', 'IP', 'sysUptime', 'sysContact', 'sysName', 'sysLocation',
                      'hardwareVersion', 'softwareVersion', 'serialNumber', 'CPUUsage', 'CPUUsageUpper', 'memoryUsage',
                      'memoryUsageUpper', 'memorySize', 'CPUTemprature', 'CPUTempratureUpper', 'CPUTempratureLower',
                      'ARPTable', 'MAC', 'MACTable', 'UpLinkPort', 'destIP', 'destPort', 'destFlag']
    ip = IPAddress(ip, mask, gate)
    # devsinfolist = []
    # print(threading.current_thread().getName() + str(step))
    for i in range(step):
        if (ip.isoutrange()):
            break

        devinfodic = {}
        (connceted, info) = icmp_ping(ip.ip, timeout, pingcount)
        if (not connceted):
            # print(ip.ip + " " + info)
            crawlinfoqueue.put(ip.ip + " " + info)
            if (not ip.next()):
                break
            continue

        (success, sysDescr) = SNMPv2GET(ip.ip, port, community, '.1.3.6.1.2.1.1.1.0')
        # print(ip.ip + ":\n" + sysDescr)
        crawlinfoqueue.put(ip.ip + ":\n" + sysDescr)
        devinfodic['updateTime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        if (not success):
            devinfodic['IP'] = ip.ip
            devinfodic['errorInfo'] = sysDescr
            devinfodic['sysDescr'] = ""
            for i in range(4, len(devinfodickeys)):
                devinfodic[i] = ""
            devsinfolist.append(devinfodic)
            if (not ip.next()):
                break
            continue

        devinfodic['sysDescr'] = sysDescr[sysDescr.find('=') + 1:].strip()
        sysDescr = sysDescr.lower()
        if (sysDescr.find('huawei') > -1):
            devinfodic.update(getHuaweiSWinfo(ip.ip, ip.gate, port, community))
        elif (sysDescr.find('ruijie') > -1):
            devinfodic.update(getRuijieSWinfo(ip.ip, ip.gate, port, community))
        elif (sysDescr.find('cisco') > -1):
            devinfodic.update(getCiscoSWinfo(ip.ip, ip.gate, port, community))
        else:
            devinfodic['IP'] = ip.ip
            devinfodic['errorInfo'] = ""
            for i in range(4, len(devinfodickeys)):
                devinfodic[i] = ""
            devsinfolist.append(devinfodic)
            if (not ip.next()):
                break
            continue
        devinfodic['destIP'] = "2.2.2.2"
        devinfodic['destPort'] = ""
        devinfodic['destFlag'] = ""

        devsinfolist.append(devinfodic)
        if (not ip.next()):
            break


def crawlinput(request):
    return render(request, 'crawlinput.html')


def docrawl(netaddress, mask, gateaddress, community, devcrawlinfoqueue):
    ip = IPAddress(netaddress, mask, gateaddress)
    if (ip.ipaddresscount < 64):
        threadsnum = 1
        step = ip.ipaddresscount
    else:
        threadsnum = 4
        step = int(ip.ipaddresscount / 4)

    devcrawlinfoqueue.put("Start crawling with %d threads" % threadsnum)
    resultslist = []
    threadslist = []

    for i in range(threadsnum):
        resultslist.append([])
        threadslist.append(threading.Thread(target=getdevinfothreadfun, name="crawlthread %d" % i,
                                            args=(ip.ip, mask, gateaddress, 161, community, step, resultslist[i],
                                                  devcrawlinfoqueue)))
        ip.walk(step)
        threadslist[i].start()

    for i in range(threadsnum):
        threadslist[i].join()

    allresultlist = []
    for i in range(threadsnum):
        allresultlist.extend(resultslist[i])
    del (resultslist)

    devcrawlinfoqueue.put("Sorting.")

    def cmp_fun(infodic):
        ipstrlist = infodic['IP'].split(".")
        ipintlist = []
        for i in range(len(ipstrlist)):
            ipintlist.append(int(ipstrlist[i]))
        ipintnum = 0
        for i in range(3, -1, -1):
            ipintnum += ipintlist[i] * (256 ** (3 - i))
        return ipintnum

    allresultlist.sort(key=cmp_fun)

    devcrawlinfoqueue.put("Coputing topology.")

    devcrawlinfoqueue.put("Storing.")
    for i in range(len(allresultlist)):
        # p = DevInfoVerbose()
        # for key in devinfodickeys:
        #     setattr(p, key, allresultlist[i][key])
        DevInfoVerbose.objects.update_or_create(IP=allresultlist[i]['IP'], defaults=allresultlist[i])
        # p.save()

    devcrawlinfoqueue.put("CrawlOver")


def crawlnet(request):
    global devcrawlinfoqueue
    netaddress = request.GET['netaddress']
    mask = request.GET['mask']
    gateaddress = request.GET['gateaddress']
    community = request.GET['communityname']
    netinfo = IPAddress(netaddress, mask)
    Netsets.objects.update_or_create(netaddress=netaddress,
                                     defaults={'netaddress': netaddress, 'netmask': mask,
                                               'ipcounts': netinfo.ipaddresscount})
    threading.Thread(target=docrawl, args=(netaddress, mask, gateaddress, community, devcrawlinfoqueue)).start()
    return render(request, 'crawlnet.html', {'netaddress': netaddress})


def datarefresh(request):
    global devcrawlinfoqueue
    devinfolist = []
    while not devcrawlinfoqueue.empty():
        devinfolist.append(devcrawlinfoqueue.get())
    return JsonResponse(devinfolist, safe=False)


def nettopology(request):
    return render(request, 'nettopology.html')


def SNMPtool(request):
    responsedic = {}
    if (len(request.GET) == 0):
        return render(request, 'SNMPtool.html', {'responsedic': json.dumps(responsedic)})
    else:
        responsedic = request.GET.copy()
        IPaddress = request.GET.get("IPaddress")
        port = int(request.GET.get("port"))
        community = request.GET.get("community")
        OID = request.GET.get("OID")
        getway = request.GET.get("getway")
        (connceted, info) = icmp_ping(IPaddress, 2, 2)
        if (not connceted):
            responsedic['success'] = False
            responsedic['result'] = info
            return render(request, 'SNMPtool.html', {'responsedic': json.dumps(responsedic)})
        elif (getway == "getself"):
            (success, result) = SNMPv2GET(IPaddress, port, community, OID)
            responsedic['success'] = success
            responsedic['result'] = result
            return render(request, 'SNMPtool.html', {'responsedic': json.dumps(responsedic)})
        else:
            (success, result) = SNMPv2WALK(IPaddress, port, community, OID)
            responsedic['success'] = success
            responsedic['result'] = result
        return render(request, 'SNMPtool.html', {'responsedic': json.dumps(responsedic)})


def devdetail(request):
    ip = request.GET.get('ipaddress')
    devdetaildic = DevInfoVerbose.objects.get(IP=ip).valuedic()
    return render(request, 'devdetail.html', {"devdetaildic": devdetaildic})


def devmonitor(request):
    alldevlist = list(DevInfoVerbose.objects.values_list('IP', 'sysName'))
    responselist = []
    for i in range(len(alldevlist)):
        if(i % 6 == 0):
            responselist.append([])
            j = int(i / 6)
        (success, time) = icmp_ping_delay(alldevlist[i][0], 2, 2)
        alldevlist[i] = list(alldevlist[i])
        alldevlist[i].append(time)
        alldevlist[i].append(success)
        responselist[j].append(alldevlist[i])
    return render(request, 'devmonitor.html', {"responselist": responselist})

def settings(request):
    netsummarylist = list(Netsets.objects.values_list('netaddress', 'netmask', 'ipcounts'))
    return render(request, "settings.html", {'netsummary': netsummarylist})

def deletnet(request):
    netaddress = request.GET.get("netaddress")
    mask = request.GET.get("mask")
    Netsets.objects.filter(netaddress__contains=netaddress).delete()
    Startnetaddress = IPAddress(netaddress, mask)
    endnetaddress = Startnetaddress.broadcast
    deviplist = list(DevInfoVerbose.objects.values_list('IP'))
    for i in range(len(deviplist)):
        if(Startnetaddress.lessthan(deviplist[i][0]) and IPAddress(deviplist[i][0], mask).lessthan(endnetaddress)):
            DevInfoVerbose.objects.filter(IP__contains=deviplist[i][0]).delete()

    netsummarylist = list(Netsets.objects.values_list('netaddress', 'netmask', 'ipcounts'))
    return render(request, "settings.html", {'netsummary': netsummarylist})

def test(request):
    return render(request, 'test.html')
