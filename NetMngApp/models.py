from django.db import models


# Create your models here.

class DevInfoVerbose(models.Model):
    sysDescr = models.CharField(max_length=1024)
    errorInfo = models.CharField(max_length=1024)
    IP = models.CharField(max_length=16)
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


if __name__ == "__main__":
    dev = DevInfoVerbose()
    print(dev._meta.get_fields())
    pass
