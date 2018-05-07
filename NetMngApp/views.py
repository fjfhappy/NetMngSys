from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, FileResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import time
import queue
import threading
import json
from django.contrib.auth.decorators import login_required

import xlwt

from NetMngApp.IPAddress import IPAddress
from NetMngApp.pingTool import icmp_ping, icmp_ping_delay
from NetMngApp.SNMPTool import getHuaweiSWinfo, getRuijieSWinfo, getCiscoSWinfo, SNMPv2WALK, SNMPv2GET
from NetMngApp.models import DevInfoVerbose, Netsets, DevPingInfo, DevARPMACTableInfo, SysSettingInfo


# Create your views here.

def debug_printdic(dic):
    for key in dic:
        print(key + "=" + str(dic[key]))


@login_required
def base(request):
    return render(request, 'base.html')


@login_required
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


@login_required
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


# destFlag: 0 ping success SNMP fial, 1 ping success topology success, 2 ping success topology fail, 3 gate
def getdevinfothreadfun(ip, mask, gate, port, community, step, devsinfolist, crawlinfoqueue, timeout, pingcount):
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
        (connceted, info, delaytime) = icmp_ping_delay(ip.ip, timeout, pingcount)
        if (not connceted):
            # print(ip.ip + " " + info)
            crawlinfoqueue.put(ip.ip + " " + info)
            if (not ip.next()):
                break
            continue

        devinfodic['connected'] = connceted
        devinfodic['delaytime'] = delaytime
        (success, sysDescr) = SNMPv2GET(ip.ip, port, community, '.1.3.6.1.2.1.1.1.0')
        # print(ip.ip + ":\n" + sysDescr)
        crawlinfoqueue.put(ip.ip + ":\n" + sysDescr)
        devinfodic['updateTime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        if (not success):
            devinfodic['IP'] = ip.ip
            devinfodic['errorInfo'] = sysDescr
            devinfodic['sysDescr'] = ""
            for i in range(4, len(devinfodickeys)):
                devinfodic[devinfodickeys[i]] = ""
            devinfodic['destIP'] = gate
            devinfodic['destFlag'] = 0
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
                devinfodic[devinfodickeys[i]] = ""
            devsinfolist.append(devinfodic)
            if (not ip.next()):
                break
            continue

        devinfodic['destIP'] = ""
        devinfodic['destPort'] = ""
        devinfodic['destFlag'] = ""

        devsinfolist.append(devinfodic)
        if (not ip.next()):
            break


@login_required
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
    SNMPport = int(SysSettingInfo.objects.get(settingitem="SNMPport").settingvalue)
    pingtimeout = int(SysSettingInfo.objects.get(settingitem="pingtimeout").settingvalue)
    pingcount = int(SysSettingInfo.objects.get(settingitem="pingcount").settingvalue)
    resultslist = []
    threadslist = []

    for i in range(threadsnum):
        resultslist.append([])

        # print(ip.ip + " " + mask + " " + gateaddress + " " + str(step))
        threadslist.append(threading.Thread(target=getdevinfothreadfun, name="crawlthread %d" % i,
                                            args=(ip.ip, mask, gateaddress, SNMPport, community, step, resultslist[i],
                                                  devcrawlinfoqueue, pingtimeout, pingcount)))
        ip.walk(step)
        threadslist[i].start()

    for i in range(threadsnum):
        threadslist[i].join()

    allresultlist = []
    for i in range(threadsnum):
        allresultlist.extend(resultslist[i])
    del (resultslist)

    devcrawlinfoqueue.put("Sorting.")

    # inner sorting function
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
    for dev in allresultlist:
        dev['gateaddress'] = gateaddress

    devcrawlinfoqueue.put("Coputing topology.")
    MAC2IPDic = {}
    IP2MACTableDic = {}
    IP2destIPDic = {}
    IP2destPortDic = {}
    IP2destFlagDic = {}
    for i in range(len(allresultlist)):
        MAC2IPDic[allresultlist[i]['MAC']] = allresultlist[i]['IP']
        IP2MACTableDic[allresultlist[i]['IP']] = allresultlist[i]['MACTable']
        IP2destIPDic[allresultlist[i]['IP']] = allresultlist[i]['destIP']
        IP2destPortDic[allresultlist[i]['IP']] = allresultlist[i]['destPort']
        IP2destFlagDic[allresultlist[i]['IP']] = allresultlist[i]['destFlag']
    # print("############MAC2IPDic")
    # debug_printdic(MAC2IPDic)
    # print("##############IP2MACTableDic")
    # debug_printdic(IP2MACTableDic)
    # print("#############IP2destIPDic")
    # debug_printdic(IP2destIPDic)
    # print("################IP2destPortDic")
    # debug_printdic(IP2destPortDic)
    # print("#############IP2destFlagDic")
    # debug_printdic(IP2destFlagDic)
    # replace MAC with IP, delete unmatchable
    for IP in IP2MACTableDic:
        tempdic = {}
        for port in IP2MACTableDic[IP]:
            for MACAdd in IP2MACTableDic[IP][port]:
                if MAC2IPDic.__contains__(MACAdd):
                    if tempdic.__contains__(port):
                        tempdic[port].append(MAC2IPDic[MACAdd])
                    else:
                        tempdic[port] = [MAC2IPDic[MACAdd]]
        IP2MACTableDic[IP] = tempdic

    # print("##############IP2MACTableDic after replace")
    # debug_printdic(IP2MACTableDic)
    # inner function: get sons
    def getSons(infodic):
        sonlist = []
        for port in infodic:
            for ip in infodic[port]:
                sonlist.append(ip)
        return sonlist

    # remove grandsons
    IP2SonDic = {}
    for IP in IP2MACTableDic:
        IP2SonDic[IP] = IP2MACTableDic[IP].copy()
        for port in IP2MACTableDic[IP]:
            for sonip in IP2MACTableDic[IP][port]:
                grandsons = getSons(IP2MACTableDic[sonip])
                for cmpip in IP2MACTableDic[IP][port]:
                    if (cmpip != sonip and grandsons.__contains__(cmpip) and IP2SonDic[IP][port].__contains__(cmpip)):
                        IP2SonDic[IP][port].remove(cmpip)
            if (len(IP2SonDic[IP][port]) == 0):
                del (IP2SonDic[IP][port])
    del (IP2MACTableDic)
    # print("##############IP2SonDic")
    # debug_printdic(IP2SonDic)
    # add uplink informations
    for IP in IP2SonDic:
        for port in IP2SonDic[IP]:
            for sonip in IP2SonDic[IP][port]:
                IP2destIPDic[sonip] = IP
                IP2destPortDic[sonip] = port
                IP2destFlagDic[sonip] = 1
    for IP in IP2destFlagDic:
        if (IP2destFlagDic[IP] == ""):
            IP2destFlagDic[IP] = 2
            IP2destIPDic[IP] = gateaddress
    for dev in allresultlist:
        if (dev['destFlag'] == 0):
            # ping success SNMP fail, has processed in threadfunction
            if (dev['IP'] == gateaddress):
                dev['destFlag'] = 3
            else:
                pass
        else:
            dev['destIP'] = IP2destIPDic[dev['IP']]
            dev['destPort'] = IP2destPortDic[dev['IP']]
            dev['destFlag'] = IP2destFlagDic[dev['IP']]

    devcrawlinfoqueue.put("Storing.")
    Netsets.objects.update_or_create(netaddress=ip.networkaddress,
                                     defaults={'netaddress': ip.networkaddress, 'netmask': ip.mask,
                                               'gateaddress': gateaddress,
                                               "community": community, 'ipcounts': len(allresultlist)})

    for i in range(len(allresultlist)):
        pinginfodic = {}
        pinginfodic['connected'] = allresultlist[i]['connected']
        del (allresultlist[i]['connected'])

        pinginfodic['delaytime'] = allresultlist[i]['delaytime']
        del (allresultlist[i]['delaytime'])
        arpmactabledic = {}
        arpmactabledic['ARPTable'] = allresultlist[i]['ARPTable']
        del (allresultlist[i]['ARPTable'])
        arpmactabledic['MACTable'] = allresultlist[i]['MACTable']
        del (allresultlist[i]['MACTable'])

        (dev, flag) = DevInfoVerbose.objects.update_or_create(IP=allresultlist[i]['IP'], defaults=allresultlist[i])
        if (flag):
            pinginfodic['DEV'] = dev
            arpmactabledic['DEV'] = dev
            DevPingInfo.objects.update_or_create(DEV__IP=allresultlist[i]['IP'], defaults=pinginfodic)
            DevARPMACTableInfo.objects.update_or_create(DEV__IP=allresultlist[i]['IP'], defaults=arpmactabledic)

    devcrawlinfoqueue.put("CrawlOver")


@login_required
def crawlnet(request):
    global devcrawlinfoqueue
    netaddress = request.GET['netaddress']
    mask = request.GET['mask']
    gateaddress = request.GET['gateaddress']
    community = request.GET['communityname']
    # netinfo = IPAddress(netaddress, mask)
    # Netsets.objects.update_or_create(netaddress=netaddress,
    #                                  defaults={'netaddress': netaddress, 'netmask': mask, "community": community,
    #                                            'ipcounts': netinfo.ipaddresscount})
    threading.Thread(target=docrawl, args=(netaddress, mask, gateaddress, community, devcrawlinfoqueue)).start()
    return render(request, 'crawlnet.html', {'netaddress': netaddress})


@login_required
def datarefresh(request):
    global devcrawlinfoqueue
    devinfolist = []
    while not devcrawlinfoqueue.empty():
        devinfolist.append(devcrawlinfoqueue.get())
    return JsonResponse(devinfolist, safe=False)


def DFS(Edgeslist, current):
    for edge in Edgeslist:
        if (edge[2] == True or edge[1] != current[0][0]):
            continue
        else:
            edge[2] = True
            son = [edge[0]]
            current.append(son)
            DFS(Edgeslist, son)


def debug_printedgelist(edgeslist):
    print("######EDGELISTS#########")
    for edge in edgeslist:
        print(edge[0][0], end="")
        print("--------->" + edge[1] + "    " + str(edge[2]))


@login_required
def nettopology(request):
    netinfolist = list(Netsets.objects.values_list('netaddress', 'netmask', 'gateaddress'))
    topologyretdic = {}
    for netinfo in netinfolist:

        devinfolist = list(
            DevInfoVerbose.objects.values_list('IP', 'destIP', 'destFlag').filter(gateaddress__contains=netinfo[2]))
        edgeslist = []
        for devinfo in devinfolist:
            node = (devinfo[0], devinfo[2])
            edgeslist.append([node, devinfo[1], False])
        del (devinfolist)
        for edge in edgeslist:
            if (edge[0][0] == netinfo[2]):
                current = [edge[0]]
                edge[2] = True
                break
        DFS(edgeslist, current)
        topologyretdic[netinfo[0] + "(" + netinfo[1] + ")"] = current

    return render(request, 'nettopology.html', {'topologyretdic': topologyretdic})


@login_required
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
        pingtimeout = int(SysSettingInfo.objects.get(settingitem="pingtimeout").settingvalue)
        pingcount = int(SysSettingInfo.objects.get(settingitem="pingcount").settingvalue)
        (connceted, info, time) = icmp_ping_delay(IPaddress, pingtimeout, pingcount)
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


@login_required
def devdetail(request):
    ip = request.GET.get('ipaddress')
    devdetaildic = DevInfoVerbose.objects.get(IP=ip).valuedic()
    return render(request, 'devdetail.html', {"devdetaildic": devdetaildic})


@login_required
def devmonitor(request):
    alldevpinginfolist = list(DevPingInfo.objects.all())
    responselist = []
    for i in range(len(alldevpinginfolist)):
        if (i % 6 == 0):
            responselist.append([])
            j = int(i / 6)
        responselist[j].append(
            [alldevpinginfolist[i].DEV.IP, alldevpinginfolist[i].DEV.sysName, alldevpinginfolist[i].delaytime,
             alldevpinginfolist[i].connected])
    return render(request, 'devmonitor.html', {"responselist": responselist})


@login_required
def settings(request):
    if (len(request.GET) > 0):
        pingrefresh = request.GET.get('pingrefresh')
        pingtimeout = request.GET.get('pingtimeout')
        pingcount = request.GET.get('pingcount')
        SNMPport = request.GET.get('SNMPport')
        devinforefresh = request.GET.get('devinforefresh')

        SysSettingInfo.objects.update_or_create(settingitem="pingrefresh",
                                                defaults={"settingitem": "pingrefresh",
                                                          "settingvalue": pingrefresh})
        SysSettingInfo.objects.update_or_create(settingitem="pingtimeout",
                                                defaults={"settingitem": "pingtimeout",
                                                          "settingvalue": pingtimeout})
        SysSettingInfo.objects.update_or_create(settingitem="pingcount",
                                                defaults={"settingitem": "pingcount",
                                                          "settingvalue": pingcount})
        SysSettingInfo.objects.update_or_create(settingitem="SNMPport",
                                                defaults={"settingitem": "SNMPport",
                                                          "settingvalue": SNMPport})
        SysSettingInfo.objects.update_or_create(settingitem="devinforefresh",
                                                defaults={"settingitem": "devinforefresh",
                                                          "settingvalue": devinforefresh})

    netsummarylist = list(Netsets.objects.values_list('netaddress', 'netmask', 'gateaddress', 'community', 'ipcounts'))
    syssettinglist = list(SysSettingInfo.objects.values_list('settingitem', 'settingvalue'))
    return render(request, "settings.html", {'netsummary': netsummarylist, 'syssettinglist': syssettinglist,
                                             'syssettinglistJS': json.dumps(syssettinglist)})


@login_required
def deletnet(request):
    netaddress = request.GET.get("netaddress")
    mask = request.GET.get("mask")
    Netsets.objects.filter(netaddress__contains=netaddress).delete()
    NETAddress = IPAddress(netaddress, mask)

    deviplist = list(DevInfoVerbose.objects.values_list('IP'))
    for i in range(len(deviplist)):
        if (NETAddress.hasip(deviplist[i][0], mask)):
            DevInfoVerbose.objects.filter(IP__contains=deviplist[i][0]).delete()

    netsummarylist = list(Netsets.objects.values_list('netaddress', 'netmask', 'ipcounts'))
    return render(request, "settings.html", {'netsummary': netsummarylist})

@login_required
def generatereport(request):
    file = "report.xls"
    reportbook = xlwt.Workbook()
    reportsheet = reportbook.add_sheet('sheet 1')
    fields = DevInfoVerbose._meta.fields
    fieldslist = [f.name for f in fields]
    for i in range(len(fieldslist)):
        reportsheet.write(0, i, fieldslist[i])
    row = 1
    devinfolist = list(DevInfoVerbose.objects.all().values_list())
    for dev in devinfolist:
        for i in range(len(dev)):
            reportsheet.write(row, i, dev[i])
        row += 1
    reportbook.save(file)

    downloadfile = open(file, "rb")
    response = FileResponse(downloadfile)
    response['Content-Type'] = 'application/octect-stream'
    response['Content-Disposition'] = 'attachment;filename="report.xls"'

    return response


def refreshdevverboseinfo():
    global devcrawlinfoqueue
    netsinfo = list(Netsets.objects.values())
    for i in range(len(netsinfo)):
        netaddress = netsinfo[i]['netaddress']
        netmask = netsinfo[i]['netmask']
        gateaddress = netsinfo[i]['gateaddress']
        community = netsinfo[i]['community']
        docrawl(netaddress, netmask, gateaddress, community, devcrawlinfoqueue)
        devcrawlinfoqueue.queue.clear()


def test(request):
    return render(request, 'test.html')
