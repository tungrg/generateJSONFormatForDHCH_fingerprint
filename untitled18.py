
import json
import re

file1 = open('dhcp_fingerprints.conf', 'r')
text = file1.readlines()

#class for OS
class OS:
  def __init__(self, name, range):
    self.name = name
    self.range = range

#get range of os for example: "members=100-199" -> (100,199)
def parseListRange(rangeListToParse):
  rangeListTemp = rangeListToParse.rsplit(",")
  rangeList = []
  for i in rangeListTemp:
    rangeList.append((int(i.rsplit("-")[0]),int(i.rsplit("-")[-1])))
  return rangeList

#parse to get each line in the file
def parseOS(Lines):
  index = 0
  listOS = []
  while(index < len(Lines)):
    if("[class" in Lines[index]):
      index+=1
      name = Lines[index].strip().rsplit("=")[1]
      index+=1
      range = Lines[index].rsplit("=")[1]
      rangeList = parseListRange(range)
      operatingSystem = OS(name, rangeList);
      listOS.append(operatingSystem)
    index+=1
    if ("[os" in Lines[index]):
      break
  return index, listOS

indexing, OSlist = parseOS(text)

#fingerprint from decimal to heximal
def parseDecimalToHex(decimalList):
  result = ""
  for i in decimalList.rsplit(","):
    result+= format(int(i), '02x')
  return result

#class for child os
class ChildOS(OS):
  def __init__(self, name, id, vendorList, fingerprint):
    self.name = name
    self.id = id
    self.vendorList = vendorList
    self.fingerprint = fingerprint

#parse child os
def ParseChildOS(Lines, index):
  OSChildList = []
  while(index < len(Lines)):
    if("[os" in Lines[index]):
      id = int(re.findall(r'\d+', Lines[index])[0])
      index +=1
    if ('description' in Lines[index]):
      name = Lines[index].strip().rsplit("=")[1]
      index +=1
    vendorIDList = []
    if ("vendor_id" in Lines[index]):
      index+=1
      while("EOT" not in Lines[index]):
        vendorIDList.append(Lines[index].strip())
        index+=1
      index+=1
    fingerprintsList = []
    if("fingerprints" in Lines[index]):
      index+=1
      fingerprint = ""
      while("EOT" not in Lines[index]):
        fingerprint = parseDecimalToHex(Lines[index])
        fingerprintsList.append(fingerprint)
        index+=1
      index +=1
      OSChildList.append(ChildOS(name,id, vendorIDList, fingerprintsList))
    index+=1
  return OSChildList

#get the list of all child os from the text file
OSChildList = ParseChildOS(text,indexing)

#get class of child os from its id
def getClassOS(id, OSlistAug):
  classOS = []
  for i in OSlistAug:
    for j in i.range:
      if id >= j[0] and id <= j[1]:
        classOS.append(i.name)
  return classOS

OSChildList[0].name

#save the result into a dictionary
result = {}
for i in OSChildList:
  if not i.vendorList:
    tempDictResult = {"description": i.name, "fingerprint": i.fingerprint}
  else:
    tempDictResult = {"description": i.name, "vendor_id": i.vendorList, "fingerprint": i.fingerprint}
  idResult = getClassOS(i.id, OSlist)
  for j in idResult:
    if j in result:
      result[j].append(tempDictResult)
    else:
      result[j] = [tempDictResult]

result

#adjust the result so it fit more with the task
listDictResult = []
for i in result.keys():
  tempDict = {"description": i, "os" : result[i]}
  listDictResult.append(tempDict)

#save to json file
with open("sample.json", "w") as outfile:
    json.dump({"class": listDictResult}, outfile, indent = 3)