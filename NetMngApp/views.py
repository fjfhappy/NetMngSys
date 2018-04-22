from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import time
import queue
import threading
import json

# Create your views here.
devinfoqueue = queue.Queue()
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
    alldevlist = testdata
    paginator = Paginator(alldevlist, 3, 2)
    page = request.GET.get('page')
    if(page):
        try:
            dev_page = paginator.page(page)
        except PageNotAnInteger:
            dev_page = paginator.page(1)
        except EmptyPage:
            dev_page = paginator.page(paginator.num_pages)
    else:
        dev_page = paginator.page(1)
    dev_list = dev_page.object_list
    return render(request, 'devlist.html', {"title": "设备列表", "dev_page": dev_page, "dev_list":dev_list})

searchdevlist = []
searchtitle = "查询结果："
def devsearch(request):
    global searchdevlist
    global searchtitle
    ipaddress = request.GET.get('ipaddress')
    macaddress = request.GET.get('macaddress')
    devname = request.GET.get('devname')
    searchflag = 0
    if ipaddress or macaddress or devname:
        searchtitle = "查询结果："
        searchflag = 1
    if ipaddress:
        searchtitle = searchtitle + " " + ipaddress
    if macaddress:
        searchtitle = searchtitle + " " + macaddress
    if devname:
        searchtitle = searchtitle + " " + devname
    if(searchflag == 1):
        searchdevlist = testdata
    paginator = Paginator(searchdevlist, 3, 2)
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

def crawldev():
    i = 0
    for i in range(10):
        devinfoqueue.put(str(i))
        if (i == 9):
            devinfoqueue.put("CrawlOver")
        time.sleep(1)


def crawlinput(request):
    return render(request, 'crawlinput.html')


def crawlnet(request):
    netaddress = request.GET['netaddress']
    mask = request.GET['mask']
    gateaddress = request.GET['gateaddress']
    community = request.GET['communityname']
    threading.Thread(target=crawldev).start()
    return render(request, 'crawlnet.html', {'netaddress': netaddress})


def datarefresh(request):
    devinfolist = []
    while not devinfoqueue.empty():
        devinfolist.append(devinfoqueue.get())
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


def test(request):
    return render(request, 'test.html')
