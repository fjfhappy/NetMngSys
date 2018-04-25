from django.db import models


# Create your models here.

class DevInfoVerbose(models.Model):
    updateTime = models.CharField(max_length=64)
    sysDescr = models.CharField(max_length=1024)
    errorInfo = models.CharField(max_length=1024)
    IP = models.CharField(max_length=32)
    sysUptime = models.CharField(max_length=128)
    sysContact = models.CharField(max_length=512)
    sysName = models.CharField(max_length=128)
    sysLocation = models.CharField(max_length=512)
    hardwareVersion = models.CharField(max_length=512)
    softwareVersion = models.CharField(max_length=512)
    serialNumber = models.CharField(max_length=128)
    CPUUsage = models.CharField(max_length=32)
    CPUUsageUpper = models.CharField(max_length=32)
    memoryUsage = models.CharField(max_length=32)
    memoryUsageUpper = models.CharField(max_length=32)
    memorySize = models.CharField(max_length=128)
    CPUTemprature = models.CharField(max_length=32)
    CPUTempratureUpper = models.CharField(max_length=32)
    CPUTempratureLower = models.CharField(max_length=32)
    ARPTable = models.CharField(max_length=2048)
    MAC = models.CharField(max_length=32)
    MACTable = models.CharField(max_length=2048)
    UpLinkPort = models.CharField(max_length=32)
    destIP = models.CharField(max_length=32)
    destPort = models.CharField(max_length=32)
    destFlag = models.CharField(max_length=32, default="0")

    def valuedic(self):
        return {"updateTime": self.updateTime, "sysDescr": self.sysDescr, "errorInfo": self.errorInfo, "IP": self.IP,
                "sysUptime": self.sysUptime, "sysContact": self.sysContact, "sysName": self.sysName,
                "sysLocation": self.sysLocation, "hardwareVersion": self.hardwareVersion,
                "softwareVersion": self.softwareVersion, "serialNumber": self.serialNumber, "CPUUsage": self.CPUUsage,
                "CPUUsageUpper": self.CPUUsageUpper, "memoryUsage": self.memoryUsage,
                "memoryUsageUpper": self.memoryUsageUpper, "memorySize": self.memorySize,
                "CPUTemprature": self.CPUTemprature, "CPUTempratureUpper": self.CPUTempratureUpper,
                "CPUTempratureLower": self.CPUTempratureLower, "ARPTable": self.ARPTable, "MAC": self.MAC,
                "MACTable": self.MACTable, "UpLinkPort": self.UpLinkPort, "destIP": self.destIP,
                "destPort": self.destPort, "destFlag": self.destFlag}

class Netsets(models.Model):
    netaddress = models.CharField(max_length=16)
    netmask = models.CharField(max_length=16)
    ipcounts = models.IntegerField()


if __name__ == "__main__":
    # dev = DevInfoVerbose()
    # print(dev._meta.get_fields())
    pass
