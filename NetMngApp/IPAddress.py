# encoding:utf-8

class IPAddress:
    def __init__(self, ip, mask, gate=""):
        self.ip = ip
        self.mask = mask
        self.gate = gate
        maskstrlist = self.mask.split(".")
        maskintlist = []
        for i in range(len(maskstrlist)):
            maskintlist.append(int(maskstrlist[i]))
        ipstrlist = self.ip.split(".")
        ipintlist = []
        for i in range(len(ipstrlist)):
            ipintlist.append(int(ipstrlist[i]))
        networkaddressintlist = []
        for i in range(len(ipintlist)):
            networkaddressintlist.append(maskintlist[i] & ipintlist[i])
        self.networkaddress = ".".join(str(x) for x in networkaddressintlist)
        self.ipaddresscount = 0
        for i in range(3, -1, -1):
            self.ipaddresscount += (255 ^ maskintlist[i]) * (256 ** (3 - i))
        self.ipaddresscount += 1
        networkaddressintlist[3] += self.ipaddresscount - 1
        for i in range(3, -1, -1):
            if (i > 0):
                networkaddressintlist[i - 1] += int(networkaddressintlist[i] / 256)
            networkaddressintlist[i] %= 256
        self.broadcast = ".".join(str(x) for x in networkaddressintlist)

    def __str__(self):
        return "IP:" + self.ip + "\nMASK:" + self.mask + "\nGATE:" + self.gate + "\nNETWORK:" + self.networkaddress + "\nIPCOUNT:" + str(
            self.ipaddresscount) + "\nbroadcast:" + self.broadcast

    def walk(self, step=1):
        ipstrlist = self.ip.split(".")
        ipintlist = []
        for i in range(len(ipstrlist)):
            ipintlist.append(int(ipstrlist[i]))
        ipintlist[3] += step
        for i in range(3, -1, -1):
            if (i > 0):
                ipintlist[i - 1] += int(ipintlist[i] / 256)
            ipintlist[i] %= 256
        self.ip = ".".join(str(x) for x in ipintlist)
        return self.ip

    def lessthan(self, ip):
        selfintlist = [int(x) for x in self.ip.split(".")]
        otheripintlist = [int(x) for x in ip.split(".")]
        for i in range(4):
            if (selfintlist[i] == otheripintlist[i]):
                i += 1
            else:
                break
        if (i > 3):
            return False
        return selfintlist[i] < otheripintlist[i]

    def next(self):
        self.walk()

        if (not self.lessthan(self.broadcast)):
            return None
        return self.ip

    def isoutrange(self):
        if(self.lessthan(self.broadcast)):
            return False
        else:
            return True

    def hasip(self, ip, mask):
        if(IPAddress(self.networkaddress, self.mask).lessthan(ip) and IPAddress(ip, mask).lessthan(self.broadcast)):
            return True
        else:
            return False


if __name__ == "__main__":
    ip = IPAddress('172.16.70.12', "255.255.254.0")
    print(ip.next())
    print(ip)
    print(ip.isoutrange())
    print(ip.walk(10))
    print(ip.isoutrange())
    print(ip.ipaddresscount)
    None
