from django.test import TestCase, Client
from NetMngApp.models import DevInfoVerbose
# Create your tests here.

class ModelTest(TestCase):
    def setUp(self):
        DevInfoVerbose.objects.create(id = 1, IP="172.16.10.1", updateTime = "201804", destIP = "1.1.1.1")

    def test_get(self):
        dev = DevInfoVerbose.objects.get(IP="172.16.10.1")
        print("haha")
        print(dev.saysomething())


    # def test_filter(self):
    #     devlist = DevInfoVerbose.objects.values_list('destIP', 'IP', 'updateTime').filter(IP__contains="172.16")
    #     devlist2 = devlist.filter(updateTime__contains="2018")
    #     print(list(devlist2))

