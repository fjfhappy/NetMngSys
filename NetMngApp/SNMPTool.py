# encoding=utf-8

from pysnmp.hlapi import *

def SNMPv2GET(ip, port, community, oid):
    iterator = getCmd(SnmpEngine(),
                      CommunityData(community),
                      UdpTransportTarget((ip, port)),
                      ContextData(),
                      ObjectType(ObjectIdentity(oid)))

    errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

    result = ""
    if errorIndication:
        return (False, str(errorIndication))
        # print(errorIndication)
    else:
        if errorStatus:
            return (False, '%s at %s' % (errorStatus.prettyPrint(), varBinds[int(errorIndex) - 1] if errorIndex else '?'))
            # print('%s at %s' % (errorStatus.prettyPrint(), varBinds[int(errorIndex) - 1] if errorIndex else '?'))
        else:
            for varBind in varBinds:
                result += ' = '.join([x.prettyPrint() for x in varBind]) + "\n"
                # print(' = '.join([x.prettyPrint() for x in varBind]))
    return (True, result)


def SNMPv2WALK(ip, port, community, oid):
    result = ""
    for (errorIndication,
         errorStatus,
         errorIndex,
         varBinds) in nextCmd(SnmpEngine(),
                              CommunityData(community),
                              UdpTransportTarget((ip, port)),
                              ContextData(),
                              ObjectType(ObjectIdentity(oid)),
                              lexicographicMode=False):

        if errorIndication:
            return (False, str(errorIndication))
            # print(errorIndication)
        else:
            if errorStatus:
                return (False, '%s at %s' % (errorStatus.prettyPrint(), varBinds[int(errorIndex) - 1] if errorIndex else '?'))
                # print('%s at %s' % (errorStatus.prettyPrint(), varBinds[int(errorIndex) - 1] if errorIndex else '?'))
            else:
                for varBind in varBinds:
                    result += ' = '.join([x.prettyPrint() for x in varBind]) + "\n"
                    # print(' = '.join([x.prettyPrint() for x in varBind]))
    return (True, result)


def getHuaweiSWinfo(ip, gateip, port=161, community='public'):
    snmpEngine = SnmpEngine()
    communityData = CommunityData(community)
    udpTransportTarget = UdpTransportTarget((ip, port))
    contextData = ContextData()
    HuaweiInfodic = {}
    HuaweiInfodic['errorInfo'] = ""
    HuaweiInfodic['IP'] = ip

    queue = [
        # cpuTemperatureLower
        [ObjectType(ObjectIdentity('.1.3.6.1.4.1.2011.5.25.31.1.1.1.1.16.67108873'))],
        # cpuTemperatureUpper
        [ObjectType(ObjectIdentity('.1.3.6.1.4.1.2011.5.25.31.1.1.1.1.12.67108873'))],
        # cpuTemperature
        [ObjectType(ObjectIdentity('.1.3.6.1.4.1.2011.5.25.31.1.1.1.1.11.67108873'))],
        # memorySize
        [ObjectType(ObjectIdentity('.1.3.6.1.4.1.2011.5.25.31.1.1.1.1.9.67108873'))],
        # memoryUsageUpper
        [ObjectType(ObjectIdentity('.1.3.6.1.4.1.2011.5.25.31.1.1.1.1.8.67108873'))],
        # memoryUsage
        [ObjectType(ObjectIdentity('.1.3.6.1.4.1.2011.5.25.31.1.1.1.1.7.67108873'))],
        # cpuUsageUpper
        [ObjectType(ObjectIdentity('.1.3.6.1.4.1.2011.5.25.31.1.1.1.1.6.67108873'))],
        # cpuUsage
        [ObjectType(ObjectIdentity('.1.3.6.1.4.1.2011.5.25.31.1.1.1.1.5.67108873'))],
        # serialNumber
        [ObjectType(ObjectIdentity('.1.3.6.1.2.1.47.1.1.1.1.11.67108873'))],
        # softwareVersion
        [ObjectType(ObjectIdentity('.1.3.6.1.2.1.47.1.1.1.1.10.67108873'))],
        # hardwareVersion
        [ObjectType(ObjectIdentity('.1.3.6.1.2.1.47.1.1.1.1.8.67108873'))],
        # sysLocation
        [ObjectType(ObjectIdentity('.1.3.6.1.2.1.1.6.0'))],
        # sysName
        [ObjectType(ObjectIdentity('.1.3.6.1.2.1.1.5.0'))],
        # sysContact
        [ObjectType(ObjectIdentity('.1.3.6.1.2.1.1.4.0'))],
        # sysUptime
        [ObjectType(ObjectIdentity('.1.3.6.1.2.1.1.3.0'))],
        # sysDescr
        # [ObjectType(ObjectIdentity('.1.3.6.1.2.1.1.1.0'))]
    ]

    iter = getCmd(snmpEngine,
                  communityData,
                  udpTransportTarget,
                  contextData)
    next(iter)
    while queue:
        errorIndication, errorStatus, errorIndex, varBinds = iter.send(queue.pop())

        if errorIndication:
            HuaweiInfodic['errorInfo'] = HuaweiInfodic['errorInfo'] + errorIndication + '\n'
            # print(errorIndication)
        elif errorStatus:
            HuaweiInfodic['errorInfo'] = HuaweiInfodic['errorInfo'] + errorStatus.prettyPrint() + '\n'
            # print('%s at %s' % (errorStatus.prettyPrint(), varBinds[int(errorIndex) - 1] if errorIndex else '?'))
        else:
            for varBind in varBinds:
                if (str(varBind[0]).find('1.3.6.1.2.1.1.3.0') > -1):
                    sysuptime = int(varBind[1] / 100)
                    sysupseconds = sysuptime % 60
                    sysuptime = int(sysuptime / 60)
                    sysupminute = sysuptime % 60
                    sysuptime = int(sysuptime / 60)
                    sysuphour = sysuptime % 24
                    sysupday = int(sysuptime / 24)
                    HuaweiInfodic['sysUptime'] = str(sysupday) + "天" + str(sysuphour) + "小时" + str(
                        sysupminute) + "分" + str(sysupseconds) + "秒"
                elif (str(varBind[0]).find('1.3.6.1.2.1.1.4.0') > -1):
                    HuaweiInfodic['sysContact'] = str(varBind[1])
                elif (str(varBind[0]).find('1.3.6.1.2.1.1.5.0') > -1):
                    HuaweiInfodic['sysName'] = str(varBind[1])
                elif (str(varBind[0]).find('1.3.6.1.2.1.1.6.0') > -1):
                    HuaweiInfodic['sysLocation'] = str(varBind[1])
                elif (str(varBind[0]).find('1.3.6.1.2.1.47.1.1.1.1.8.67108873') > -1):
                    HuaweiInfodic['hardwareVersion'] = str(varBind[1])
                elif (str(varBind[0]).find('1.3.6.1.2.1.47.1.1.1.1.10.67108873') > -1):
                    HuaweiInfodic['softwareVersion'] = str(varBind[1])
                elif (str(varBind[0]).find('1.3.6.1.2.1.47.1.1.1.1.11.67108873') > -1):
                    HuaweiInfodic['serialNumber'] = str(varBind[1])
                elif (str(varBind[0]).find('2011.5.25.31.1.1.1.1.5.67108873') > -1):
                    HuaweiInfodic['CPUUsage'] = str(varBind[1]) + "%"
                elif (str(varBind[0]).find('2011.5.25.31.1.1.1.1.6.67108873') > -1):
                    HuaweiInfodic['CPUUsageUpper'] = str(varBind[1]) + "%"
                elif (str(varBind[0]).find('2011.5.25.31.1.1.1.1.7.67108873') > -1):
                    HuaweiInfodic['memoryUsage'] = str(varBind[1]) + "%"
                elif (str(varBind[0]).find('2011.5.25.31.1.1.1.1.8.67108873') > -1):
                    HuaweiInfodic['memoryUsageUpper'] = str(varBind[1]) + "%"
                elif (str(varBind[0]).find('2011.5.25.31.1.1.1.1.9.67108873') > -1):
                    HuaweiInfodic['memorySize'] = str(varBind[1]) + "B"
                elif (str(varBind[0]).find('2011.5.25.31.1.1.1.1.11.67108873') > -1):
                    HuaweiInfodic['CPUTemprature'] = str(varBind[1]) + "C"
                elif (str(varBind[0]).find('2011.5.25.31.1.1.1.1.12.67108873') > -1):
                    HuaweiInfodic['CPUTempratureUpper'] = str(varBind[1]) + "C"
                elif (str(varBind[0]).find('2011.5.25.31.1.1.1.1.16.67108873') > -1):
                    HuaweiInfodic['CPUTempratureLower'] = str(varBind[1]) + "C"

    # getARPtable
    HuaweiInfodic['ARPTable'] = {}
    for (errorIndication,
         errorStatus,
         errorIndex,
         varBinds) in nextCmd(snmpEngine,
                              communityData,
                              udpTransportTarget,
                              ContextData(),
                              ObjectType(ObjectIdentity('.1.3.6.1.2.1.3.1.1.2')),
                              ObjectType(ObjectIdentity('.1.3.6.1.2.1.3.1.1.3')),
                              lexicographicMode=False):
        if errorIndication:
            HuaweiInfodic['errorInfo'] = HuaweiInfodic['errorInfo'] + errorIndication + '\n'
            # print(errorIndication)
            break
        elif errorStatus:
            HuaweiInfodic['errorInfo'] = HuaweiInfodic['errorInfo'] + errorStatus.prettyPrint() + '\n'
            # print('%s at %s' % (errorStatus.prettyPrint(), errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
            break
        else:
            macentry = varBinds[0][1].prettyPrint()
            macaddress = macentry[-12:-8] + ":" + macentry[-8:-4] + ":" + macentry[-4:]
            ipaddress = varBinds[1][1].prettyPrint()
            HuaweiInfodic['ARPTable'][macaddress] = ipaddress
            if (ipaddress == ip):
                HuaweiInfodic['MAC'] = macaddress
            elif (ipaddress == gateip):
                gateMAC = macaddress

    # getMACtable
    # get port-serial-number to mac-address map
    HuaweiInfodic['MACTable'] = {}
    for (errorIndication,
         errorStatus,
         errorIndex,
         varBinds) in nextCmd(snmpEngine,
                              communityData,
                              udpTransportTarget,
                              ContextData(),
                              ObjectType(ObjectIdentity('.1.3.6.1.2.1.17.4.3.1.1')),
                              ObjectType(ObjectIdentity('.1.3.6.1.2.1.17.4.3.1.2')),
                              lexicographicMode=False):
        if errorIndication:
            HuaweiInfodic['errorInfo'] = HuaweiInfodic['errorInfo'] + errorIndication + '\n'
            # print(errorIndication)
            break
        elif errorStatus:
            HuaweiInfodic['errorInfo'] = HuaweiInfodic['errorInfo'] + errorStatus.prettyPrint() + '\n'
            # print('%s at %s' % (errorStatus.prettyPrint(), errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
            break
        else:
            macentry = varBinds[0][1].prettyPrint()
            macaddress = macentry[-12:-8] + ":" + macentry[-8:-4] + ":" + macentry[-4:]
            interentry = varBinds[1][1].prettyPrint()
            if (macaddress == gateMAC):
                HuaweiInfodic['UpLinkPort'] = interentry
            if (HuaweiInfodic['MACTable'].__contains__(interentry)):
                HuaweiInfodic['MACTable'][interentry].append(macaddress)
            else:
                HuaweiInfodic['MACTable'][interentry] = [macaddress]
    del (HuaweiInfodic['MACTable'][HuaweiInfodic['UpLinkPort']])

    # get port-serial-number to port-index map
    portserialtoindexdic = {}
    for (errorIndication,
         errorStatus,
         errorIndex,
         varBinds) in nextCmd(snmpEngine,
                              communityData,
                              udpTransportTarget,
                              ContextData(),
                              ObjectType(ObjectIdentity('.1.3.6.1.2.1.17.1.4.1.2')),
                              lexicographicMode=False):
        if errorIndication:
            HuaweiInfodic['errorInfo'] = HuaweiInfodic['errorInfo'] + errorIndication + '\n'
            # print(errorIndication)
            break
        elif errorStatus:
            HuaweiInfodic['errorInfo'] = HuaweiInfodic['errorInfo'] + errorStatus.prettyPrint() + '\n'
            # print('%s at %s' % (errorStatus.prettyPrint(), errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
            break
        else:
            for varBind in varBinds:
                tempstr = str(varBind[0])
                portserialnumber = tempstr[tempstr.rfind('.') + 1:]
                portindex = str(varBind[1])
                if (not portserialtoindexdic.__contains__(portserialnumber)):
                    portserialtoindexdic[portserialnumber] = portindex

    # replace port serial number to port index in Huaweiinfodic[mactable]
    tempdic = {}
    for key in HuaweiInfodic['MACTable']:
        if portserialtoindexdic.__contains__(key):
            tempdic[portserialtoindexdic[key]] = HuaweiInfodic['MACTable'][key]
        else:
            tempdic[key] = HuaweiInfodic['MACTable'][key]
    HuaweiInfodic['MACTable'].clear()
    HuaweiInfodic['MACTable'] = tempdic.copy()
    if portserialtoindexdic.__contains__(HuaweiInfodic['UpLinkPort']):
        HuaweiInfodic['UpLinkPort'] = portserialtoindexdic[HuaweiInfodic['UpLinkPort']]

    # get port-index to port-name map, use .1.3.6.1.2.1.31.1.1.1.1
    portindextonamedic = {}
    for (errorIndication,
         errorStatus,
         errorIndex,
         varBinds) in nextCmd(snmpEngine,
                              communityData,
                              udpTransportTarget,
                              contextData,
                              ObjectType(ObjectIdentity('.1.3.6.1.2.1.31.1.1.1.1')),
                              lexicographicMode=False):

        if errorIndication:
            HuaweiInfodic['errorInfo'] = HuaweiInfodic['errorInfo'] + errorIndication + '\n'
            # print(errorIndication)
            break
        elif errorStatus:
            HuaweiInfodic['errorInfo'] = HuaweiInfodic['errorInfo'] + errorStatus.prettyPrint() + '\n'
            # print('%s at %s' % (errorStatus.prettyPrint(), errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
        else:
            for varBind in varBinds:
                tempstr = str(varBind[0])
                portindex = tempstr[tempstr.rfind(".") + 1:]
                portname = str(varBind[1])
                portindextonamedic[portindex] = portname

    # replace port index to port name in Huaweiinfodic[mactable]
    tempdic = {}
    for key in HuaweiInfodic['MACTable']:
        if portindextonamedic.__contains__(key):
            tempdic[portindextonamedic[key]] = HuaweiInfodic['MACTable'][key]
        else:
            tempdic[key] = HuaweiInfodic['MACTable'][key]
    HuaweiInfodic['MACTable'].clear()
    HuaweiInfodic['MACTable'] = tempdic.copy()
    if portindextonamedic.__contains__(HuaweiInfodic['UpLinkPort']):
        HuaweiInfodic['UpLinkPort'] = portindextonamedic[HuaweiInfodic['UpLinkPort']]

    return HuaweiInfodic


def getRuijieSWinfo(ip, gateip, port=161, community='public'):
    snmpEngine = SnmpEngine()
    communityData = CommunityData(community)
    udpTransportTarget = UdpTransportTarget((ip, port))
    contextData = ContextData()
    RuijieInfodic = {}
    RuijieInfodic['errorInfo'] = ""
    RuijieInfodic['IP'] = ip

    queue = [
        #     # cpuTemperatureLower
        #     [ObjectType(ObjectIdentity('.1.3.6.1.4.1.2011.5.25.31.1.1.1.1.16.67108873'))],
        #     # cpuTemperatureUpper
        #     [ObjectType(ObjectIdentity('.1.3.6.1.4.1.2011.5.25.31.1.1.1.1.12.67108873'))],
        #     # cpuTemperature
        #     [ObjectType(ObjectIdentity('.1.3.6.1.4.1.2011.5.25.31.1.1.1.1.11.67108873'))],
        # memorySize
        [ObjectType(ObjectIdentity('.1.3.6.1.4.1.4881.1.1.10.2.35.1.1.1.6.1'))],
        #     # memoryUsageUpper
        #     [ObjectType(ObjectIdentity('.1.3.6.1.4.1.2011.5.25.31.1.1.1.1.8.67108873'))],
        # memoryUsage
        [ObjectType(ObjectIdentity('.1.3.6.1.4.1.4881.1.1.10.2.35.1.1.1.3.1'))],
        #     # cpuUsageUpper
        #     [ObjectType(ObjectIdentity('.1.3.6.1.4.1.2011.5.25.31.1.1.1.1.6.67108873'))],
        #     # cpuUsage
        [ObjectType(ObjectIdentity('.1.3.6.1.4.1.4881.1.1.10.2.36.1.1.1.0'))],
        # serialNumber
        [ObjectType(ObjectIdentity('.1.3.6.1.4.1.4881.1.1.10.2.1.1.24.0'))],
        # softwareVersion
        [ObjectType(ObjectIdentity('.1.3.6.1.4.1.4881.1.1.10.2.1.1.2.0'))],
        # hardwareVersion
        [ObjectType(ObjectIdentity('.1.3.6.1.4.1.4881.1.1.10.2.1.1.25.1.6.1'))],
        #     # sysLocation
        [ObjectType(ObjectIdentity('.1.3.6.1.2.1.1.6.0'))],
        #     # sysName
        [ObjectType(ObjectIdentity('.1.3.6.1.2.1.1.5.0'))],
        # sysContact
        [ObjectType(ObjectIdentity('.1.3.6.1.2.1.1.4.0'))],
        # sysUptime
        [ObjectType(ObjectIdentity('.1.3.6.1.2.1.1.3.0'))],
        # sysDescr
        # [ObjectType(ObjectIdentity('.1.3.6.1.2.1.1.1.0'))]
    ]

    iter = getCmd(snmpEngine,
                  communityData,
                  udpTransportTarget,
                  contextData)
    next(iter)
    while queue:
        errorIndication, errorStatus, errorIndex, varBinds = iter.send(queue.pop())

        if errorIndication:
            RuijieInfodic['errorInfo'] = RuijieInfodic['errorInfo'] + errorIndication + '\n'
            # print(errorIndication)
        elif errorStatus:
            RuijieInfodic['errorInfo'] = RuijieInfodic['errorInfo'] + errorStatus.prettyPrint() + '\n'
            # print('%s at %s' % (errorStatus.prettyPrint(), varBinds[int(errorIndex) - 1] if errorIndex else '?'))
        else:
            for varBind in varBinds:
                if (str(varBind[0]).find('1.3.6.1.2.1.1.3.0') > -1):
                    sysuptime = int(varBind[1] / 100)
                    sysupseconds = sysuptime % 60
                    sysuptime = int(sysuptime / 60)
                    sysupminute = sysuptime % 60
                    sysuptime = int(sysuptime / 60)
                    sysuphour = sysuptime % 24
                    sysupday = int(sysuptime / 24)
                    RuijieInfodic['sysUptime'] = str(sysupday) + "天" + str(sysuphour) + "小时" + str(
                        sysupminute) + "分" + str(sysupseconds) + "秒"
                elif (str(varBind[0]).find('1.3.6.1.2.1.1.4.0') > -1):
                    RuijieInfodic['sysContact'] = str(varBind[1])
                elif (str(varBind[0]).find('1.3.6.1.2.1.1.5.0') > -1):
                    RuijieInfodic['sysName'] = str(varBind[1])
                elif (str(varBind[0]).find('1.3.6.1.2.1.1.6.0') > -1):
                    RuijieInfodic['sysLocation'] = str(varBind[1])
                elif (str(varBind[0]).find('1.3.6.1.4.1.4881.1.1.10.2.1.1.25.1.6.1') > -1):
                    RuijieInfodic['hardwareVersion'] = str(varBind[1])
                elif (str(varBind[0]).find('1.3.6.1.4.1.4881.1.1.10.2.1.1.2.0') > -1):
                    RuijieInfodic['softwareVersion'] = str(varBind[1])
                elif (str(varBind[0]).find('1.3.6.1.4.1.4881.1.1.10.2.1.1.24.0') > -1):
                    RuijieInfodic['serialNumber'] = str(varBind[1])
                elif (str(varBind[0]).find('1.3.6.1.4.1.4881.1.1.10.2.36.1.1.1') > -1):
                    RuijieInfodic['CPUUsage'] = str(varBind[1]) + "%"
                    #             elif (str(varBind[0]).find('2011.5.25.31.1.1.1.1.6.67108873') > -1):
                    #                 RuijieInfodic['CPUUsageUpper'] = str(varBind[1]) + "%"
                elif (str(varBind[0]).find('1.3.6.1.4.1.4881.1.1.10.2.35.1.1.1.3.1') > -1):
                    RuijieInfodic['memoryUsage'] = str(varBind[1]) + "%"
                    #             elif (str(varBind[0]).find('2011.5.25.31.1.1.1.1.8.67108873') > -1):
                    #                 RuijieInfodic['memoryUsageUpper'] = str(varBind[1]) + "%"
                elif (str(varBind[0]).find('1.3.6.1.4.1.4881.1.1.10.2.35.1.1.1.6.1') > -1):
                    RuijieInfodic['memorySize'] = str(varBind[1]) + "B"
    # elif (str(varBind[0]).find('2011.5.25.31.1.1.1.1.11.67108873') > -1):
    #                 RuijieInfodic['CPUTemprature'] = str(varBind[1]) + "?"
    #             elif (str(varBind[0]).find('2011.5.25.31.1.1.1.1.12.67108873') > -1):
    #                 RuijieInfodic['CPUTempratureUpper'] = str(varBind[1]) + "C"
    #             elif (str(varBind[0]).find('2011.5.25.31.1.1.1.1.16.67108873') > -1):
    #                 RuijieInfodic['CPUTempratureLower'] = str(varBind[1]) + "C"
    #
    # getARPtable
    RuijieInfodic['ARPTable'] = {}
    for (errorIndication,
         errorStatus,
         errorIndex,
         varBinds) in nextCmd(snmpEngine,
                              communityData,
                              udpTransportTarget,
                              ContextData(),
                              ObjectType(ObjectIdentity('.1.3.6.1.2.1.3.1.1.2')),
                              ObjectType(ObjectIdentity('.1.3.6.1.2.1.3.1.1.3')),
                              lexicographicMode=False):
        if errorIndication:
            RuijieInfodic['errorInfo'] = RuijieInfodic['errorInfo'] + errorIndication + '\n'
            # print(errorIndication)
            break
        elif errorStatus:
            RuijieInfodic['errorInfo'] = RuijieInfodic['errorInfo'] + errorStatus.prettyPrint() + '\n'
            # print('%s at %s' % (errorStatus.prettyPrint(), errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
            break
        else:
            macentry = varBinds[0][1].prettyPrint()
            macaddress = macentry[-12:-8] + ":" + macentry[-8:-4] + ":" + macentry[-4:]
            ipaddress = varBinds[1][1].prettyPrint()
            RuijieInfodic['ARPTable'][macaddress] = ipaddress
            if (ipaddress == ip):
                RuijieInfodic['MAC'] = macaddress
            elif (ipaddress == gateip):
                gateMAC = macaddress

    # getMACtable
    # get port-serial-number to mac-address map
    RuijieInfodic['MACTable'] = {}
    for (errorIndication,
         errorStatus,
         errorIndex,
         varBinds) in nextCmd(snmpEngine,
                              communityData,
                              udpTransportTarget,
                              ContextData(),
                              ObjectType(ObjectIdentity('.1.3.6.1.2.1.17.4.3.1.1')),
                              ObjectType(ObjectIdentity('.1.3.6.1.2.1.17.4.3.1.2')),
                              lexicographicMode=False):
        if errorIndication:
            RuijieInfodic['errorInfo'] = RuijieInfodic['errorInfo'] + errorIndication + '\n'
            # print(errorIndication)
            break
        elif errorStatus:
            RuijieInfodic['errorInfo'] = RuijieInfodic['errorInfo'] + errorStatus.prettyPrint() + '\n'
            # print('%s at %s' % (errorStatus.prettyPrint(), errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
            break
        else:
            macentry = varBinds[0][1].prettyPrint()
            macaddress = macentry[-12:-8] + ":" + macentry[-8:-4] + ":" + macentry[-4:]
            interentry = varBinds[1][1].prettyPrint()
            if (macaddress == gateMAC):
                RuijieInfodic['UpLinkPort'] = interentry
            if (RuijieInfodic['MACTable'].__contains__(interentry)):
                RuijieInfodic['MACTable'][interentry].append(macaddress)
            else:
                RuijieInfodic['MACTable'][interentry] = [macaddress]
    del (RuijieInfodic['MACTable'][RuijieInfodic['UpLinkPort']])

    # get port-serial-number to port-index map
    portserialtoindexdic = {}
    for (errorIndication,
         errorStatus,
         errorIndex,
         varBinds) in nextCmd(snmpEngine,
                              communityData,
                              udpTransportTarget,
                              ContextData(),
                              ObjectType(ObjectIdentity('.1.3.6.1.2.1.17.1.4.1.2')),
                              lexicographicMode=False):
        if errorIndication:
            RuijieInfodic['errorInfo'] = RuijieInfodic['errorInfo'] + errorIndication + '\n'
            # print(errorIndication)
            break
        elif errorStatus:
            RuijieInfodic['errorInfo'] = RuijieInfodic['errorInfo'] + errorStatus.prettyPrint() + '\n'
            # print('%s at %s' % (errorStatus.prettyPrint(), errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
            break
        else:
            for varBind in varBinds:
                tempstr = str(varBind[0])
                portserialnumber = tempstr[tempstr.rfind('.') + 1:]
                portindex = str(varBind[1])
                if (not portserialtoindexdic.__contains__(portserialnumber)):
                    portserialtoindexdic[portserialnumber] = portindex

    # replace port serial number to port index in Ruijieinfodic[mactable]
    tempdic = {}
    for key in RuijieInfodic['MACTable']:
        if portserialtoindexdic.__contains__(key):
            tempdic[portserialtoindexdic[key]] = RuijieInfodic['MACTable'][key]
        else:
            tempdic[key] = RuijieInfodic['MACTable'][key]
    RuijieInfodic['MACTable'].clear()
    RuijieInfodic['MACTable'] = tempdic.copy()
    if portserialtoindexdic.__contains__(RuijieInfodic['UpLinkPort']):
        RuijieInfodic['UpLinkPort'] = portserialtoindexdic[RuijieInfodic['UpLinkPort']]

    # get port-index to port-name map, use .1.3.6.1.2.1.31.1.1.1.1
    portindextonamedic = {}
    for (errorIndication,
         errorStatus,
         errorIndex,
         varBinds) in nextCmd(snmpEngine,
                              communityData,
                              udpTransportTarget,
                              contextData,
                              ObjectType(ObjectIdentity('.1.3.6.1.2.1.31.1.1.1.1')),
                              lexicographicMode=False):

        if errorIndication:
            RuijieInfodic['errorInfo'] = RuijieInfodic['errorInfo'] + errorIndication + '\n'
            # print(errorIndication)
            break
        elif errorStatus:
            RuijieInfodic['errorInfo'] = RuijieInfodic['errorInfo'] + errorStatus.prettyPrint() + '\n'
            # print('%s at %s' % (errorStatus.prettyPrint(), errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
        else:
            for varBind in varBinds:
                tempstr = str(varBind[0])
                portindex = tempstr[tempstr.rfind(".") + 1:]
                portname = str(varBind[1])
                portindextonamedic[portindex] = portname

    # replace port index to port name in Ruijieinfodic[mactable]
    tempdic = {}
    for key in RuijieInfodic['MACTable']:
        if portindextonamedic.__contains__(key):
            tempdic[portindextonamedic[key]] = RuijieInfodic['MACTable'][key]
        else:
            tempdic[key] = RuijieInfodic['MACTable'][key]
    RuijieInfodic['MACTable'].clear()
    RuijieInfodic['MACTable'] = tempdic.copy()
    if portindextonamedic.__contains__(RuijieInfodic['UpLinkPort']):
        RuijieInfodic['UpLinkPort'] = portindextonamedic[RuijieInfodic['UpLinkPort']]

    return RuijieInfodic


def getCiscoSWinfo(ip, gateip, port=161, community='public'):
    snmpEngine = SnmpEngine()
    communityData = CommunityData(community)
    udpTransportTarget = UdpTransportTarget((ip, port))
    contextData = ContextData()
    CiscoInfodic = {}
    CiscoInfodic['errorInfo'] = ""
    CiscoInfodic['IP'] = ip

    queue = [
        #     # cpuTemperatureLower
        #     [ObjectType(ObjectIdentity('.1.3.6.1.4.1.2011.5.25.31.1.1.1.1.16.67108873'))],
        #     # cpuTemperatureUpper
        #     [ObjectType(ObjectIdentity('.1.3.6.1.4.1.2011.5.25.31.1.1.1.1.12.67108873'))],
        #     # cpuTemperature
        #     [ObjectType(ObjectIdentity('.1.3.6.1.4.1.2011.5.25.31.1.1.1.1.11.67108873'))],
        # memorySize count by memory free
        [ObjectType(ObjectIdentity('.1.3.6.1.4.1.9.9.48.1.1.1.6.1'))],
        #     # memoryUsageUpper
        #     [ObjectType(ObjectIdentity('.1.3.6.1.4.1.2011.5.25.31.1.1.1.1.8.67108873'))],
        # memoryUsage count by usage B and free B
        [ObjectType(ObjectIdentity('.1.3.6.1.4.1.9.9.48.1.1.1.5.1'))],
        #     # cpuUsageUpper
        #     [ObjectType(ObjectIdentity('.1.3.6.1.4.1.2011.5.25.31.1.1.1.1.6.67108873'))],
        # cpuUsage
        [ObjectType(ObjectIdentity('.1.3.6.1.4.1.9.9.109.1.1.1.1.6.1'))],
        #     # serialNumber
        #     [ObjectType(ObjectIdentity('.1.3.6.1.2.1.47.1.1.1.1.11.67108873'))],
        #     # softwareVersion
        #     [ObjectType(ObjectIdentity('.1.3.6.1.2.1.47.1.1.1.1.10.67108873'))],
        #     # hardwareVersion
        #     [ObjectType(ObjectIdentity('.1.3.6.1.2.1.47.1.1.1.1.8.67108873'))],
        # sysLocation
        [ObjectType(ObjectIdentity('.1.3.6.1.2.1.1.6.0'))],
        # sysName
        [ObjectType(ObjectIdentity('.1.3.6.1.2.1.1.5.0'))],
        # sysContact
        [ObjectType(ObjectIdentity('.1.3.6.1.2.1.1.4.0'))],
        # sysUptime
        [ObjectType(ObjectIdentity('.1.3.6.1.2.1.1.3.0'))],
        #     # sysDescr
        #     # [ObjectType(ObjectIdentity('.1.3.6.1.2.1.1.1.0'))]
    ]

    iter = getCmd(snmpEngine,
                  communityData,
                  udpTransportTarget,
                  contextData)
    next(iter)
    while queue:
        errorIndication, errorStatus, errorIndex, varBinds = iter.send(queue.pop())

        if errorIndication:
            CiscoInfodic['errorInfo'] = CiscoInfodic['errorInfo'] + errorIndication + '\n'
            # print(errorIndication)
        elif errorStatus:
            CiscoInfodic['errorInfo'] = CiscoInfodic['errorInfo'] + errorStatus.prettyPrint() + '\n'
            # print('%s at %s' % (errorStatus.prettyPrint(), varBinds[int(errorIndex) - 1] if errorIndex else '?'))
        else:
            for varBind in varBinds:
                if (str(varBind[0]).find('1.3.6.1.2.1.1.3.0') > -1):
                    sysuptime = int(varBind[1] / 100)
                    sysupseconds = sysuptime % 60
                    sysuptime = int(sysuptime / 60)
                    sysupminute = sysuptime % 60
                    sysuptime = int(sysuptime / 60)
                    sysuphour = sysuptime % 24
                    sysupday = int(sysuptime / 24)
                    CiscoInfodic['sysUptime'] = str(sysupday) + "天" + str(sysuphour) + "小时" + str(
                        sysupminute) + "分" + str(sysupseconds) + "秒"
                elif (str(varBind[0]).find('1.3.6.1.2.1.1.4.0') > -1):
                    CiscoInfodic['sysContact'] = str(varBind[1])
                elif (str(varBind[0]).find('1.3.6.1.2.1.1.5.0') > -1):
                    CiscoInfodic['sysName'] = str(varBind[1])
                elif (str(varBind[0]).find('1.3.6.1.2.1.1.6.0') > -1):
                    CiscoInfodic['sysLocation'] = str(varBind[1])
                    #             elif (str(varBind[0]).find('1.3.6.1.2.1.47.1.1.1.1.8.67108873') > -1):
                    #                 CiscoInfodic['hardwareVersion'] = str(varBind[1])
                    #             elif (str(varBind[0]).find('1.3.6.1.2.1.47.1.1.1.1.10.67108873') > -1):
                    #                 CiscoInfodic['softwareVersion'] = str(varBind[1])
                    #             elif (str(varBind[0]).find('1.3.6.1.2.1.47.1.1.1.1.11.67108873') > -1):
                    #                 CiscoInfodic['serialNumber'] = str(varBind[1])
                elif (str(varBind[0]).find('1.3.6.1.4.1.9.9.109.1.1.1.1.6.1') > -1):
                    CiscoInfodic['CPUUsage'] = varBind[1].prettyPrint() + "%"
                    #             elif (str(varBind[0]).find('2011.5.25.31.1.1.1.1.6.67108873') > -1):
                    #                 CiscoInfodic['CPUUsageUpper'] = str(varBind[1]) + "%"
                elif (str(varBind[0]).find('1.3.6.1.4.1.9.9.48.1.1.1.5.1') > -1):
                    memoryused = int(varBind[1].prettyPrint())
                    #             elif (str(varBind[0]).find('2011.5.25.31.1.1.1.1.8.67108873') > -1):
                    #                 CiscoInfodic['memoryUsageUpper'] = str(varBind[1]) + "%"
                elif (str(varBind[0]).find('1.3.6.1.4.1.9.9.48.1.1.1.6.1') > -1):
                    memorysize = int(varBind[1].prettyPrint()) + memoryused
                    CiscoInfodic['memorySize'] = str(memorysize) + "B"
                    CiscoInfodic['memoryUsage'] = "%.0f" % (memoryused * 100 / memorysize) + "%"
    # elif (str(varBind[0]).find('2011.5.25.31.1.1.1.1.11.67108873') > -1):
    #                 CiscoInfodic['CPUTemprature'] = str(varBind[1]) + "?"
    #             elif (str(varBind[0]).find('2011.5.25.31.1.1.1.1.12.67108873') > -1):
    #                 CiscoInfodic['CPUTempratureUpper'] = str(varBind[1]) + "C"
    #             elif (str(varBind[0]).find('2011.5.25.31.1.1.1.1.16.67108873') > -1):
    #                 CiscoInfodic['CPUTempratureLower'] = str(varBind[1]) + "C"


    # getARPtable
    CiscoInfodic['ARPTable'] = {}
    for (errorIndication,
         errorStatus,
         errorIndex,
         varBinds) in nextCmd(snmpEngine,
                              communityData,
                              udpTransportTarget,
                              ContextData(),
                              ObjectType(ObjectIdentity('.1.3.6.1.2.1.3.1.1.2')),
                              ObjectType(ObjectIdentity('.1.3.6.1.2.1.3.1.1.3')),
                              lexicographicMode=False):
        if errorIndication:
            CiscoInfodic['errorInfo'] = CiscoInfodic['errorInfo'] + errorIndication + '\n'
            # print(errorIndication)
            break
        elif errorStatus:
            CiscoInfodic['errorInfo'] = CiscoInfodic['errorInfo'] + errorStatus.prettyPrint() + '\n'
            # print('%s at %s' % (errorStatus.prettyPrint(), errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
            break
        else:
            macentry = varBinds[0][1].prettyPrint()
            macaddress = macentry[-12:-8] + ":" + macentry[-8:-4] + ":" + macentry[-4:]
            ipaddress = varBinds[1][1].prettyPrint()
            CiscoInfodic['ARPTable'][macaddress] = ipaddress
            if (ipaddress == ip):
                CiscoInfodic['MAC'] = macaddress
            elif (ipaddress == gateip):
                gateMAC = macaddress

    # getMACtable
    CiscoInfodic['MACTable'] = {}
    # get vlan list, use .1.3.6.1.4.1.9.9.46.1.3.1.1.18 to find all vlans, the last number in OID is vlan
    vlanlist = []
    for (errorIndication,
         errorStatus,
         errorIndex,
         varBinds) in nextCmd(snmpEngine,
                              communityData,
                              udpTransportTarget,
                              contextData,
                              ObjectType(ObjectIdentity('.1.3.6.1.4.1.9.9.46.1.3.1.1.18')),
                              lexicographicMode=False):

        if errorIndication:
            CiscoInfodic['errorInfo'] = CiscoInfodic['errorInfo'] + errorIndication + '\n'
            # print(errorIndication)
            break
        elif errorStatus:
            CiscoInfodic['errorInfo'] = CiscoInfodic['errorInfo'] + errorStatus.prettyPrint() + '\n'
            # print('%s at %s' % (errorStatus.prettyPrint(), errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
            break
        else:
            for varBind in varBinds:
                vlanstr = str(varBind[0])
                vlanlist.append(vlanstr[vlanstr.rfind('.') + 1:])

    # get port-serial-number to mac-address map, loop vlan list for community
    for vlanitem in vlanlist:
        communityData = CommunityData(community + '@' + vlanitem)
        for (errorIndication,
             errorStatus,
             errorIndex,
             varBinds) in nextCmd(snmpEngine,
                                  communityData,
                                  udpTransportTarget,
                                  ContextData(),
                                  ObjectType(ObjectIdentity('.1.3.6.1.2.1.17.4.3.1.1')),
                                  ObjectType(ObjectIdentity('.1.3.6.1.2.1.17.4.3.1.2')),
                                  lexicographicMode=False):
            if errorIndication:
                CiscoInfodic['errorInfo'] = CiscoInfodic['errorInfo'] + errorIndication + '\n'
                # print(errorIndication)
                break
            elif errorStatus:
                CiscoInfodic['errorInfo'] = CiscoInfodic['errorInfo'] + errorStatus.prettyPrint() + '\n'
                # print('%s at %s' % (errorStatus.prettyPrint(), errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
                break
            else:
                macentry = varBinds[0][1].prettyPrint()
                macaddress = macentry[-12:-8] + ":" + macentry[-8:-4] + ":" + macentry[-4:]
                interentry = varBinds[1][1].prettyPrint()
                if (macaddress == gateMAC):
                    CiscoInfodic['UpLinkPort'] = interentry
                if (CiscoInfodic['MACTable'].__contains__(interentry)):
                    CiscoInfodic['MACTable'][interentry].append(macaddress)
                else:
                    CiscoInfodic['MACTable'][interentry] = [macaddress]
    del (CiscoInfodic['MACTable'][CiscoInfodic['UpLinkPort']])

    # get port-serial-number to port-index map, loop vlan list for community
    portserialtoindexdic = {}
    for vlanitem in vlanlist:
        communityData = CommunityData(community + '@' + vlanitem)
        for (errorIndication,
             errorStatus,
             errorIndex,
             varBinds) in nextCmd(snmpEngine,
                                  communityData,
                                  udpTransportTarget,
                                  ContextData(),
                                  ObjectType(ObjectIdentity('.1.3.6.1.2.1.17.1.4.1.2')),
                                  lexicographicMode=False):
            if errorIndication:
                CiscoInfodic['errorInfo'] = CiscoInfodic['errorInfo'] + errorIndication + '\n'
                # print(errorIndication)
                break
            elif errorStatus:
                CiscoInfodic['errorInfo'] = CiscoInfodic['errorInfo'] + errorStatus.prettyPrint() + '\n'
                # print('%s at %s' % (errorStatus.prettyPrint(), errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
                break
            else:
                for varBind in varBinds:
                    tempstr = str(varBind[0])
                    portserialnumber = tempstr[tempstr.rfind('.') + 1:]
                    portindex = str(varBind[1])
                    if (not portserialtoindexdic.__contains__(portserialnumber)):
                        portserialtoindexdic[portserialnumber] = portindex

    # replace port serial number to port index in ciscoinfodic[mactable]
    tempdic = {}
    for key in CiscoInfodic['MACTable']:
        if portserialtoindexdic.__contains__(key):
            tempdic[portserialtoindexdic[key]] = CiscoInfodic['MACTable'][key]
        else:
            tempdic[key] = CiscoInfodic['MACTable'][key]
    CiscoInfodic['MACTable'].clear()
    CiscoInfodic['MACTable'] = tempdic.copy()
    if portserialtoindexdic.__contains__(CiscoInfodic['UpLinkPort']):
        CiscoInfodic['UpLinkPort'] = portserialtoindexdic[CiscoInfodic['UpLinkPort']]

    # get port-index to port-name map, use .1.3.6.1.2.1.31.1.1.1.1
    communityData = CommunityData(community)
    portindextonamedic = {}
    for (errorIndication,
         errorStatus,
         errorIndex,
         varBinds) in nextCmd(snmpEngine,
                              communityData,
                              udpTransportTarget,
                              contextData,
                              ObjectType(ObjectIdentity('.1.3.6.1.2.1.31.1.1.1.1')),
                              lexicographicMode=False):

        if errorIndication:
            CiscoInfodic['errorInfo'] = CiscoInfodic['errorInfo'] + errorIndication + '\n'
            # print(errorIndication)
            break
        elif errorStatus:
            CiscoInfodic['errorInfo'] = CiscoInfodic['errorInfo'] + errorStatus.prettyPrint() + '\n'
            # print('%s at %s' % (errorStatus.prettyPrint(), errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
        else:
            for varBind in varBinds:
                tempstr = str(varBind[0])
                portindex = tempstr[tempstr.rfind(".") + 1:]
                portname = str(varBind[1])
                portindextonamedic[portindex] = portname

    # replace port index to port name in ciscoinfodic[mactable]
    tempdic = {}
    for key in CiscoInfodic['MACTable']:
        if portindextonamedic.__contains__(key):
            tempdic[portindextonamedic[key]] = CiscoInfodic['MACTable'][key]
        else:
            tempdic[key] = CiscoInfodic['MACTable'][key]
    CiscoInfodic['MACTable'].clear()
    CiscoInfodic['MACTable'] = tempdic.copy()
    if portindextonamedic.__contains__(CiscoInfodic['UpLinkPort']):
        CiscoInfodic['UpLinkPort'] = portindextonamedic[CiscoInfodic['UpLinkPort']]

    return CiscoInfodic

if __name__ == "__main__":
    # infodic = getHuaweiSWinfo(ip="172.16.10.12", gateip="172.16.10.254", community="FmmuAccount")
    # for key in infodic:
    #     print("'"+key+"', ", end="")

    print(SNMPv2WALK('172.16.10.3', 161, "FmmuAccount", '.1.3.6.1.2.1.1'))
    pass
