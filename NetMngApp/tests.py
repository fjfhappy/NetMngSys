from django.test import TestCase, Client
from NetMngApp.models import DevInfoVerbose, DevPingInfo
# Create your tests here.

class ModelTest(TestCase):
    def setUp(self):
        dev1 = DevInfoVerbose.objects.create(id = 1, IP="172.16.10.1", updateTime = "201804", destIP = "1.1.1.1")
        delay1 = DevPingInfo.objects.create(DEV=dev1, delaytime="11ms")

    def test_get(self):
        dev = DevPingInfo.objects.get(DEV__IP="172.16.10.1")
        print(dev.valuelist())


        # DevPingInfo.objects.filter(delaytime="11ms").update(delaytime="12ms")
        # dev = DevPingInfo.objects.get(delaytime="12ms")
        # print(dev.delaytime)

    # def test_filter(self):
    #     devlist = DevInfoVerbose.objects.values_list('destIP', 'IP', 'updateTime').filter(IP__contains="172.16")
    #     devlist2 = devlist.filter(updateTime__contains="2018")
    #     print(list(devlist2))

