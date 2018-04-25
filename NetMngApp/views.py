from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import time
import queue
import threading
import json
from django.db.models import Q

from NetMngApp.IPAddress import IPAddress
from NetMngApp.pingTool import icmp_ping
from NetMngApp.SNMPTool import getHuaweiSWinfo, getRuijieSWinfo, getCiscoSWinfo, SNMPv2WALK, SNMPv2GET
from NetMngApp.models import DevInfoVerbose, Netsets

# Create your views here.

testdata = [['1.1.1.1', '1a2b:3c4d:5e6f', 'YanjiushengNanlouHJ', '1', '2.2.2.2', '23', '2009.12.12'],
            ['1.1.1.1', '1a2b:3c4d:5e6f', 'YanjiushengNanlouHJ', '2', '2.2.2.2', '23', '2009.12.12'],
            ['1.1.1.1', '1a2b:3c4d:5e6f', 'YanjiushengNanlouHJ', '3', '2.2.2.2', '23', '2009.12.12'],
            ['1.1.1.1', '1a2b:3c4d:5e6f', 'YanjiushengNanlouHJ', '4', '2.2.2.2', '23', '2009.12.12'],
            ['1.1.1.1', '1a2b:3c4d:5e6f', 'YanjiushengNanlouHJ', '5', '2.2.2.2', '23', '2009.12.12'],
            ['1.1.1.1', '1a2b:3c4d:5e6f', 'YanjiushengNanlouHJ', '6', '2.2.2.2', '23', '2009.12.12'],
            ['1.1.1.1', '1a2b:3c4d:5e6f', 'YanjiushengNanlouHJ', '7', '2.2.2.2', '23', '2009.12.12'],
            ['1.1.1.1', '1a2b:3c4d:5e6f', 'YanjiushengNanlouHJ', '8', '2.2.2.2', '23', '2009.12.12'],
            ['1.1.1.1', '1a2b:3c4d:5e6f', 'YanjiushengNanlouHJ', '9', '2.2.2.2', '23', '2009.12.12'],
            ['1.1.1.1', '1a2b:3c4d:5e6f', 'YanjiushengNanlouHJ', '10', '2.2.2.2', '23', '2009.12.12'],
            ['1.1.1.1', '1a2b:3c4d:5e6f', 'YanjiushengNanlouHJ', '11', '2.2.2.2', '23', '2009.12.12'],
            ['1.1.1.1', '1a2b:3c4d:5e6f', 'YanjiushengNanlouHJ', '12', '2.2.2.2', '23', '2009.12.12'],
            ['1.1.1.1', '1a2b:3c4d:5e6f', 'YanjiushengNanlouHJ', '13', '2.2.2.2', '23', '2009.12.12'],
            ['1.1.1.1', '1a2b:3c4d:5e6f', 'YanjiushengNanlouHJ', '14', '2.2.2.2', '23', '2009.12.12'],
            ['1.1.1.1', '1a2b:3c4d:5e6f', 'YanjiushengNanlouHJ', '15', '2.2.2.2', '23', '2009.12.12'],
            ['1.1.1.1', '1a2b:3c4d:5e6f', 'YanjiushengNanlouHJ', '16', '2.2.2.2', '23', '2009.12.12'],
            ['1.1.1.1', '1a2b:3c4d:5e6f', 'YanjiushengNanlouHJ', '17', '2.2.2.2', '23', '2009.12.12'],
            ['1.1.1.1', '1a2b:3c4d:5e6f', 'YanjiushengNanlouHJ', '18', '2.2.2.2', '23', '2009.12.12'],
            ['1.1.1.1', '1a2b:3c4d:5e6f', 'YanjiushengNanlouHJ', '19', '2.2.2.2', '23', '2009.12.12'],
            ['1.1.1.1', '1a2b:3c4d:5e6f', 'YanjiushengNanlouHJ', '20', '2.2.2.2', '23', '2009.12.12'],
            ['1.1.1.1', '1a2b:3c4d:5e6f', 'YanjiushengNanlouHJ', '21', '2.2.2.2', '23', '2009.12.12'],
            ['1.1.1.1', '1a2b:3c4d:5e6f', 'YanjiushengNanlouHJ', '22', '2.2.2.2', '23', '2009.12.12'],
            ['1.1.1.1', '1a2b:3c4d:5e6f', 'YanjiushengNanlouHJ', '23', '2.2.2.2', '23', '2009.12.12'],
            ['1.1.1.1', '1a2b:3c4d:5e6f', 'YanjiushengNanlouHJ', '24', '2.2.2.2', '23', '2009.12.12'],
            ['1.1.1.1', '1a2b:3c4d:5e6f', 'YanjiushengNanlouHJ', '25', '2.2.2.2', '23', '2009.12.12'],
            ['1.1.1.1', '1a2b:3c4d:5e6f', 'YanjiushengNanlouHJ', '26', '2.2.2.2', '23', '2009.12.12'],
            ['1.1.1.1', '1a2b:3c4d:5e6f', 'YanjiushengNanlouHJ', '27', '2.2.2.2', '23', '2009.12.12'],
            ['1.1.1.1', '1a2b:3c4d:5e6f', 'YanjiushengNanlouHJ', '28', '2.2.2.2', '23', '2009.12.12']]


def base(request):
    return render(request, 'base.html')


def devlist(request):
    alldevlist = list(DevInfoVerbose.objects.values_list('IP', 'MAC', 'sysName', 'UpLinkPort', 'destIP', 'CPUUsage', 'memoryUsage'))
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
    if(ipaddress):
        ipaddress = ipaddress.strip()
    macaddress = request.GET.get('macaddress')
    if(macaddress):
        macaddress = macaddress.strip()
    destip = request.GET.get('destip')
    if(destip):
        destip = destip.strip()
    devname = request.GET.get('devname')
    if(devname):
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
        if(ipaddress):
            searchdevQuery = DevInfoVerbose.objects.values_list('IP', 'MAC', 'sysName', 'UpLinkPort', 'destIP',
                                                                'CPUUsage', 'memoryUsage').filter(IP__contains=ipaddress)
        if(macaddress and searchdevQuery):
            searchdevQuery = searchdevQuery.filter(MAC__icontains=macaddress)
        elif(macaddress and not searchdevQuery):
            searchdevQuery = DevInfoVerbose.objects.values_list('IP', 'MAC', 'sysName', 'UpLinkPort', 'destIP',
                                                                'CPUUsage', 'memoryUsage').filter(MAC__icontains=macaddress)
        if(destip and searchdevQuery):
            searchdevQuery = searchdevQuery.filter(destIP__contains=destip)
        elif(destip and not searchdevQuery):
            searchdevQuery = DevInfoVerbose.objects.values_list('IP', 'MAC', 'sysName', 'UpLinkPort', 'destIP',
                                                                'CPUUsage', 'memoryUsage').filter(destIP__contains=destip)
        if(devname and searchdevQuery):
            searchdevQuery = searchdevQuery.filter(sysName__icontains=devname)
        elif(devname and not searchdevQuery):
            searchdevQuery = DevInfoVerbose.objects.values_list('IP', 'MAC', 'sysName', 'UpLinkPort', 'destIP',
                                                                'CPUUsage', 'memoryUsage').filter(sysName__icontains=devname)
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
        responsedic['result'] = 'GOOD BOY'
        return render(request, 'SNMPtool.html', {'responsedic': json.dumps(responsedic)})

def devdetail(request):
    ip = request.GET.get('ipaddress')
    print(ip)
    dev = DevInfoVerbose.objects.get(IP=ip)
    print(dev.getattr("IP"))
    print(type(dev))
    return render(request, 'devdetail.html')

def test(request):
    return render(request, 'test.html')
