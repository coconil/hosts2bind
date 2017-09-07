#! /usr/bin/python3


import requests
import os
class Record:
    def __init__(self, name, address):
        self.name = name
        self.address = address


class Zone:
    'a name zone'

    def __init__(self, name):
        self.name = name
        self.recordList = []

    def insertRecord(self, record):
        self.recordList.append(record)

    def __contains__(self, record):
        return record in self.recordList


def parseZoneName(name):
    index = name.rfind('.com')
    if index < 0:
        return None
    index = name.rfind('.', 0, index)
    # print('zone name:', name[index + 1:])
    return name[index + 1:]


def getZoneFromName(list, name):
    for zone in list:
        if zone.name == name:
            return zone
    return None

r = requests.get('https://raw.githubusercontent.com/racaljk/hosts/master/hosts')
file=open("hosts", 'w+')
file.write(r.text.replace('\t', ' '))
file.seek(0)
zoneList = []

while True:
    line = file.readline()
    if not line:
        break
    if line.find('#') == 0:
        continue
    index = line.find(' ')
    if index < 0:
        continue
    address = line[0:index]
    while line[index] == ' ':
        index += 1
    name = line[index:len(line) - 1]
    tempZoneName = parseZoneName(name)
    if not tempZoneName:
        continue
    tempZone = getZoneFromName(zoneList, tempZoneName)
    if tempZone:
        tempRecordName = name[:name.find(tempZoneName) - 1]
        if not (name in tempZone):
            tempZone.insertRecord(Record(name[:name.find(tempZoneName) - 1], address))
    else:
        tempZone = Zone(tempZoneName)
        tempZone.insertRecord(Record(name[:name.find(tempZoneName) - 1], address))
        zoneList.append(tempZone)
file.close()
outputDirName='bind'
if os.path.exists("output"):
    if not os.path.isdir(outputDirName):
        print('error,there is a regular file named output')
        raise Exception("File Exit")
else:
    os.mkdir(outputDirName)

zoneFile = open(outputDirName+'/myzone.conf', 'w+')
for zone in zoneList:

    print('\n' + zone.name + ': ')
    zoneFile.write(' zone '+'"'+zone.name+'" '+'''{
type master;
file "/etc/bind/db.'''+zone.name+'''";
};
''')
    outfile = open(outputDirName+'/db.' + zone.name, 'w+')
    outfile.write('''
$TTL 7200
; domain.tld
@       IN      SOA     ns.lab.cn. ns2.lab.cn. (
                                        2017071401 ; Serial
                                        28800      ; Refresh
                                        1800       ; Retry
                                        604800     ; Expire - 1 week
                                        86400 )    ; Minimum
@       IN      NS      ns.lab.cn.
''')
    for record in zone.recordList:
        outfile.write(record.name + '     IN      A       ' + record.address + '\n')
        print(record.name, record.address)
    outfile.close()
zoneFile.close()
    # print('address:', address, ' name:', name)
