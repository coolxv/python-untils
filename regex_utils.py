# -*- coding:utf-8 -*-
"""
Created on Wed Jul 15 13:10:11 2014

@author coolxv

Class:
    InfoTable

Function:
    readTextFromFile(fileName)
    def SplitGatherText(text)
 
    GetPreWord(patternString, text)
    GetPreCountWords(patternString, text, count)
    GetPreToken(patternString, text)
    GetPreCountTokens(patternString, text, count)
    GetPreString(patternString, text)
    GetNextWord(patternString, text)
    GetNextCountWords(patternString, text, count)
    GetNextToken(patternString, text)
    GetNextCountTokens(patternString, text,count)
    GetNextString(patternString, text)
    
    GetCurLine(patternString, text)
    GetPreLine(patternString, text)
    GetPreCountLines(patternString, text, count)
    GetPreOverLines(patternString, text, count)
    GetNextLine(patternString, text)
    GetNextCountLines(patternString, text, count)
    GetNextOverLines(patternString, text, count)
    GetMiddleLines(patternFistLine, patternLastLine, text)
    
    GetInterfaceName(text)
    GetIpv4Addr(text)
    GetAddrAndMaskFromCidr(text)
    GetIpv4AddrWithPort(text)
    GetAddrAndPortFromIpv4AddrWithPort(text)
    GetIpv6Addr(text)
    GetMacAddr(text)
    
    GetSheetByFeature(text, *featureArgv)
    
    Ipv4Addr2Num(ipv4Addr):
    Num2Ipv4Addr(Num):
    MaskAddrv4ToMaskNum(netMaskAddr)
    CidrNum2CidrAddrv4(cidrNum)
    GetIpv4NetAddrByCidrNum(ipv4Addr, cidrNum)
    GetIpv4NetAddrByCidrAddr(cidrAddrv4)
    IsSrcInDstNetwork(srcCidrAddrv4,dstCidrAddrv4)
    ReverseMaskToMask(ip)
    intTo2BinStr(x,K)
    
    IsSomeWordsExist(text, *wordArgv)
    ThrowExceptionForInvalidField(fieldName)
    GetInterfaceFullName(shortName)
    GetInterfaceShortName(fullName)
"""
import os
import sys
import re
import xml.etree.ElementTree as ET
import xml.dom.minidom as MD


##################################################
#                internal class
##################################################
class Converter(object):
    ##
    def __init__(self):
        pass
    ##
    def __CreateRoot(self,rootTag):
        root = ET.Element(rootTag)
        return root
    ##
    def __HeadToRow(self,listMember,rootTag='tableHead',ele='column'):
        if len(listMember) > 0:#属性存在
            root = self.__CreateRoot(rootTag)
            for member in listMember:
                #属性节点
                colm = ET.Element(ele)
                colm.text = member
                #加入节点列表
                root.append(colm)
            return root
    ##
    def __SetAttrByMember(self,colm,member):
        colm.text = member['text']
        attrList = member['attribute']
        if isinstance(attrList, list):
            for item in attrList:
                colm.set(item['attrName'], item['attrValue'])        
    ##        
    def __OneDataToRow(self,listMember,HeadNumber,rootTag='row',ele='column'):
        if len(listMember) > 0 and len(listMember) <= HeadNumber :
            root = self.__CreateRoot(rootTag)
            for member in listMember:
                #属性节点
                colm = ET.Element(ele)
                if isinstance(member, dict):
                    self.__SetAttrByMember(colm,member)
                else:
                    colm.text = member
                #加入节点列表
                root.append(colm)
            return root
    ##        
    def __DataToRow(self,MultiData,HeadNumber,rootTag='tableData'):
        if len(MultiData) > 0:
            root = self.__CreateRoot(rootTag)
            for oneData in MultiData:
                row = self.__OneDataToRow(oneData,HeadNumber)
                root.append(row)
            return root
    ##
    def __OneClassToXMLTree(self,classObj,rootTag='table'):
        if isinstance(classObj, InfoTable):
            #one table
            root = self.__CreateRoot(rootTag)
            root.set('name', classObj.tableName)
            root.set('type', classObj.tableType)
            root.set('result', classObj.tableResult)
            #table head
            ele = self.__HeadToRow(classObj.tableHead)
            if( ele is not None):
                root.append(ele)
            #table data
            ele = self.__DataToRow(classObj.tableData, len(classObj.tableHead))
            if( ele is not None):
                root.append(ele)
            return root
    ##
    def ClassToXMLTree(self,listObj,rootTag='tables'):
        root = None
        if isinstance(listObj, list) or isinstance(listObj, tuple):#列表或元组
            if len(listObj) > 0:
                root = self.__CreateRoot(rootTag)
                for obj in listObj:
                    itemE = self.__OneClassToXMLTree(obj)
                    if( itemE is not None):
                        root.append(itemE)
        elif isinstance(listObj, dict):#字典
            if len(listObj) > 0:
                root = self.__CreateRoot(rootTag)
                for key in listObj:
                    obj = listObj[key]
                    itemE = self.__OneClassToXMLTree(obj)
                    if( itemE is not None):
                        root.append(itemE)
        else:#对象
            if (listObj is not None):
                root = self.__CreateRoot(rootTag)
                obj = listObj
                itemE = self.__OneClassToXMLTree(obj)
                    
                if(itemE is not None):
                    root.append(itemE)
        #
        return root
    ##
    def XMLTreeToRoughXmlText(self,root,defaultEncoding='utf-8'): 
        xmlHead = '<?xml version="1.0" encoding="utf-8"?>'
        roughString = ET.tostring(root, defaultEncoding)
        roughXmlText = xmlHead + roughString
        return roughXmlText
    ##
    def XMLTreeToTidyXmlText(self,root,defaultEncoding='utf-8'): 
        roughXmlText = ET.tostring(root, encoding = defaultEncoding)
        reParsed = MD.parseString(roughXmlText)
        return reParsed.toprettyxml(indent="    ", encoding = defaultEncoding)

##################################################
#               table to xml class
##################################################
class InfoTable(object):
    #construct
    def __init__(self, name, type, result='successful'):
        self.tableName = name
        if type == 'vertical' or type == 'horizontal':
            self.tableType = type
        else:
            self.tableType = 'horizontal'
        
        if result == 'successful' or result == 'failed':
            self.tableResult = result
        else:
            self.tableResult = 'successful'
       
        self.tableHead =[]
        self.tableData = []
        self.defaultReason = u'生成xml时出错'
        self.DefaultTable = ('<?xml version="1.0" encoding="utf-8"?>'
                             '<tables>'
                             '<table name="error" type="vertical" result="failed">'
                             u'<tableHead><column>结论</column></tableHead>'
                             u'<tableData><row><column>表组装错误，具体原因:{0}。</column></row></tableData>'
                             '</table>'
                             '</tables>')
    ##   
    def CreateTableHead(self,headList):
        if (isinstance(headList, tuple) or isinstance(headList, list))and len(headList) > 0:
            self.tableHead = list(headList)
                
    ##        
    def AddTableData(self,itemList):
        if (isinstance(itemList, tuple) or isinstance(itemList, list)) and (len(self.tableHead) >= len(itemList) and 0 < len(itemList)):
            self.tableData.append(list(itemList))
    ##        
    def TableInfo2TidyXml(self):
        try:
            conventer = Converter()
            root = conventer.ClassToXMLTree(self)
            if(root is not None):
                xmlText = conventer.XMLTreeToTidyXmlText(root)
                return xmlText.decode('utf-8').decode('utf-8')
            else:
                return self.DefaultTable.format(self.defaultReason)
        except Exception, reason:
            return self.DefaultTable.format(reason)

    ##        
    def TableInfo2RoughXml(self):
        try:
            conventer = Converter()
            root = conventer.ClassToXMLTree(self)
            if(root is not None):
                xmlText = conventer.XMLTreeToRoughXmlText(root)
                return xmlText.decode('utf-8')
            else:
                return self.DefaultTable.format(self.defaultReason)
        except Exception, reason:
            return self.DefaultTable.format(reason)

##
def CreateItem(text):
    itemDict = dict()
    itemDict['text'] = text
    itemDict['attribute'] = []
    return itemDict
##
def AddAttrToItem(itemDict,name,value):
    attrList = itemDict['attribute']
    attr = dict()
    attr['attrName'] = name
    attr['attrValue'] = value
    attrList.append(attr)

##格式化输出内容，加粗、标红  
##调用时：FormatText(text, AU.attrRed | AU.attrBold)
attrRed = 1  #标红
attrBold = 2  #加粗
def FormatText(text, attr):
    itemDict = CreateItem(text)
    if attr & attrBold:
        AddAttrToItem(itemDict,'format','bold')
    if attr & attrRed:
        AddAttrToItem(itemDict,'color','red')
    return itemDict

##################################################
#               global function
##################################################
def readTextFromFile(fileName):
    try:
        with open(fileName, 'r') as f:
            text = f.read()
            return text
    except:
        return ''   
#################################################
#################################################
def OutputDebug(info):
    try:
        with open("debug_info.txt", 'a') as f:
            if isinstance(info, list) or isinstance(info, tuple):            
                for one in info:
                    f.write(one)
                    f.write("\r\n")
            else:
                f.write(info)
                f.write("\r\n")            
            return
    except:
        return 
#################################################
#################################################
def SplitGatherText(text):
    m1 = re.search('(?:/\*\*)(?P<preText>.*?)(?:\*\*/)', text, re.S)
    if m1:
        preText = m1.group('preText')
    else:
        preText = ''
    
    m2 = re.search('(?:\*\*/)(?P<postText>.*)', text, re.S)
    if m2:
        postText = m2.group('postText')
    else:
        postText = ''
    return preText,postText
#################################################
#################################################
def GetPreWord(patternString, text):
    m = re.search('(?P<preWord>\w+)(?:\s*)' + patternString, text)
    if m:
        return m.group('preWord')
    else:
        return ''
#################################################
#################################################
def GetPreCountWords(patternString, text, count):
    m = re.search('(?:\s*)(?P<preCountWords>((?:\s*)(?:\w+)(?:\s*)){%d})(?:\s*)'%count + patternString, text)
    if m:
        return m.group('preCountWords')
    else:
        return ''
#################################################
#################################################
def GetPreToken(patternString, text):
    m = re.search('(?P<preWord>\S+)(?:\s*)' + patternString, text)
    if m:
        return m.group('preWord')
    else:
        return ''
#################################################
#################################################
def GetPreCountTokens(patternString, text, count):
    m = re.search('(?P<preWord>((?:\S+)(?:\s*)){%d})'%count + patternString, text)
    if m:
        return m.group('preWord')
    else:
        return ''              
#################################################
#################################################
def GetPreString(patternString, text):
    m = re.search('(?:\s*)(?P<preString>.*?)(?:\s*)' + patternString, text)
    if m:
        return m.group('preString')
    else:
        return ''        
#################################################
#################################################
def GetNextWord(patternString, text):
    m = re.search(patternString + '(?:\s*)(?P<nextWord>\w+)', text)
    if m:
        return m.group('nextWord')
    else:
        return ''
#################################################
#################################################
def GetNextCountWords(patternString, text, count):
    m = re.search(patternString + '(?:\s*(?P<nextCountWords>(?:(?:\s*)(?:\w+)){%d}))'%count, text)
    if m:
        return m.group('nextCountWords')
    else:
        return ''
#################################################
#################################################
def GetNextToken(patternString, text):
    m = re.search(patternString + '(?:\s*)(?P<nextToken>\S+)', text)
    if m:
        return m.group('nextToken')
    else:
        return ''
#################################################
#################################################
def GetNextCountTokens(patternString, text,count):
    m = re.search(patternString + '(?:\s*(?P<nextCountToken>((?:\s*)(?:\S+)){%d}))'%count, text)
    if m:
        return m.group('nextCountToken')
    else:
        return ''
#################################################
#################################################
def GetNextString(patternString, text):
    m = re.search(patternString + '(?:\s*)(?P<nextString>.*)(?:\s*)', text)
    if m:
        return m.group('nextString')
    else:
        return ''
#################################################
#################################################
def GetCurLine(patternString, text):
    m = re.search('(?:\r\n|\n|\r)?(?P<curLine>(?:.*)%s(?:.*))(?:\r\n|\n|\r)?'%patternString, text)
    if m:
        return m.group('curLine').lstrip().rstrip()
    else:
        return ''
#################################################
#################################################
def GetPreLine(patternString, text):
    m = re.search('(?:\r\n|\n|\r)?(?P<preLine>.*)(?:\r\n|\n|\r)(?:.*)' + patternString, text)
    if m:
        return m.group('preLine').lstrip().rstrip()
    else:
        return ''
#################################################
#################################################
def GetPreCountLines(patternString, text, count):
    if count < 1:
        return ''
    m = re.search('(?:\r\n|\n|\r)?(?P<preCountLines>(.*(\r\n|\n|\r)){%d})(?:.*)'%count + patternString, text)
    if m:
        return m.group('preCountLines')
    else:
        return ''
#################################################
#################################################
def GetPreOverLines(patternString, text, count):
    if count < 1:
        return ''
    invalidCount = count - 1
    m = re.search('(?:\r\n|\n|\r)?(?:(?P<preCountLines>.*)(?:\r\n|\n|\r))(?:.*(?:\r\n|\n|\r)){%d}(?:.*)'%invalidCount + patternString, text)
    if m:
        return m.group('preCountLines').lstrip().rstrip()
    else:
        return ''
#################################################
#################################################
def GetNextLine(patternString, text):
    m = re.search(patternString + '(?:.*)(?:\r\n|\n|\r)(?P<nextLine>.*)(?:\r\n|\n|\r)?', text)
    if m:
        return m.group('nextLine').lstrip().rstrip()
    else:
        return ''
#################################################
#################################################
def GetNextOverLines(patternString, text, count):
    if count < 1:
        return ''
    invalidCount = count - 1
    m = re.search(patternString + '(?:.*)(?:\r\n|\n|\r)((?:.*)(?:\r\n|\n|\r)){%d}((?P<nextOverLines>.*)(?:\r\n|\n|\r)?)'%invalidCount, text)
    if m:
        return m.group('nextOverLines').lstrip().rstrip()
    else:
        return ''
#################################################
#################################################
def GetNextCountLines(patternString, text, count):
    if count < 1:
        return ''
    validCount = count - 1
    m = re.search(patternString + '(?:.*)(?:\r\n|\n|\r)(?P<nextCountLines>(.*(\r\n|\n|\r)){%d}(.*(\r\n|\n|\r)?))'%validCount, text)
    if m:
        return m.group('nextCountLines')
    else:
        return ''
#################################################
#################################################
def GetMiddleLines(patternFistLine, patternLastLine, text):
    if (patternFistLine and not patternLastLine):
        firstLine = GetCurLine(patternFistLine,text)
        firstLineRStr = re.escape(firstLine)
        patternString = '(?P<cond>%s)(?P<middleLines>.*)'%firstLineRStr
        m = re.search(patternString, text, re.S)
        if m and m.group('cond'):
            return m.group('middleLines')
    elif (not patternFistLine and patternLastLine):
        lastLine = GetCurLine(patternLastLine,text)
        lastLineRStr = re.escape(lastLine)
        patternString = '(?P<middleLines>.*?)(?P<cond>%s)'%lastLineRStr
        m = re.search(patternString, text, re.S)
        if m and m.group('cond'):
            return m.group('middleLines')
    elif (patternFistLine and patternLastLine):
        firstLine = GetCurLine(patternFistLine,text)
        middleText = GetMiddleLines(patternFistLine,'',text)
        lastLine = GetCurLine(patternLastLine,middleText)
        firstLineRStr = re.escape(firstLine)
        lastLineRStr = re.escape(lastLine)
        patternString = '(?P<cond1>%s)(?P<middleLines>.*?)(?P<cond2>%s)'%(firstLineRStr,lastLineRStr)
        m = re.search(patternString, text, re.S)
        if m and m.group('cond1') and m.group('cond2'):
            return m.group('middleLines')
    else:
        patternString = '(?P<middleLines>.*)'
        m = re.search(patternString, text, re.S)
        if m:
            return m.group('middleLines')

    return ''
#################################################
#################################################
def GetInterfaceName(text):
    m = re.search('(\S+)(?:\s*)((?:\d+)(?:/\d+)*)((?:\.\d+)?)', text)
    if m:
        return m.group(1) + m.group(2) + m.group(3)
    m = re.search('((?:\S+)(?::d+)?)',text)
    if m:
        return m.group(0)
    else:
        return ''
#################################################
#################################################
def GetIpv4Addr(text):
    m = re.search('(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[0-9]{1,2})(\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[0-9]{1,2})){3}(/\d{1,2})?', text)
    if m:
        return m.group(0)
    else:
        return ''
#################################################
#################################################
def GetAddrAndMaskFromCidr(text):
    m = re.search('(?P<ipv4>(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[0-9]{1,2})(?:\.(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[0-9]{1,2})){3})(:?/)(?P<mask>\d{1,2})?', text)
    if m:
        return m.group('ipv4'),m.group('mask')
    else:
        return '',''
#################################################
#################################################
def GetIpv4AddrWithPort(text):
    m = re.search('(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[0-9]{1,2})(\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[0-9]{1,2})){3}(:\d{1,5})?', text)
    if m:
        return m.group(0)
    else:
        return '',''
#################################################
#################################################
def GetAddrAndPortFromIpv4AddrWithPort(text):
    m = re.search('(?P<ipv4>(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[0-9]{1,2})(\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[0-9]{1,2})){3})(:)(?P<port>\d{1,5})?', text)
    if m:
        return m.group('ipv4'),m.group('port')
    else:
        return '',''
#################################################
#################################################
def GetIpv6Addr(text):
    ipv4 = '(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[0-9]{1,2})(\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[0-9]{1,2})){3}'
    m = re.search('''
                    (
                    (([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|
                    (([0-9A-Fa-f]{1,4}:){6}((%s)|:[0-9A-Fa-f]{1,4}|:))|
                    (([0-9A-Fa-f]{1,4}:){5}(:(%s)|((:[0-9A-Fa-f]{1,4}){1,2})|:))|
                    (([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4})?:(%s))|((:[0-9A-Fa-f]{1,4}){1,3})|:))|
                    (([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){0,2}:(%s))|((:[0-9A-Fa-f]{1,4}){1,4})|:))|
                    (([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){0,3}:(%s))|((:[0-9A-Fa-f]{1,4}){1,5})|:))|
                    (([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){0,4}:(%s))|((:[0-9A-Fa-f]{1,4}){1,6})|:))|
                    (:(((:[0-9A-Fa-f]{1,4}){0,5}:(%s))|(((:[0-9A-Fa-f]{1,4}){1,7}))))|
                    (::)
                    )
                    (/\d{1,3})?
                    '''%(ipv4,ipv4,ipv4,ipv4,ipv4,ipv4,ipv4), text, re.X)
    if m:
        return m.group(0)
    else:
        return ''
        

#################################################
#################################################
def GetMacAddr(text):
    m = re.search('((([0-9a-fA-F]{2}-){5}[0-9a-fA-F]{2})|(([0-9a-fA-F]{4}-){2}[0-9a-fA-F]{4}))', text)
    if m:
        return m.group(0)
    else:
        return ''    
#################################################
#################################################
anyFeature = '(.*?)'
numFeature = '(\d+)'
numSlashNumFeature = r'(\d+/\d+)'
wordFeature = '(\w+)'
tokenFeature = '(\S+)'
ipv4Feature = r'((?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[0-9]{1,2})(?:\.(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[0-9]{1,2})){3}(?:/\d{1,2})?)'
ipv4WithPortFeature = r'((?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[0-9]{1,2})(?:\.(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[0-9]{1,2})){3}(?::\d{1,5})?)'
macFeature = '((?:(?:[0-9a-fA-F]{2}-){5}[0-9a-fA-F]{2})|(?:(?:[0-9a-fA-F]{4}-){2}[0-9a-fA-F]{4}))'
timeFeature = '(\d{2}:\d{2}:\d{2})'
interfaceNameFeature = '((?:\S+(?:\s*)(?:(?:\d+/)+\d+)(?:\.\d+)?)|((?:\S+)(?::d+)?)|((?:\S+)))'

dateAndTimeFeature = '(\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2})'

def GetSheetByFeature(text, *featureArgv):
    if featureArgv:
        spaceFeature = '(?:\s*)'
        featurePattern = spaceFeature    
        for oneArg in featureArgv:
            featurePattern = featurePattern + oneArg + spaceFeature
        line = text.split('\n')
        sheet = []
        for oneLine in line:
            tempSheet = re.findall(featurePattern, oneLine)
            if len(tempSheet) == 1:
                sheet.append(tempSheet[0])
        if len(sheet) > 0:
            return sheet
    return []

#################################################
#################################################
def Ipv4Addr2Num(ipv4Addr):
    if not isinstance(ipv4Addr, str):
        return 0
    li=ipv4Addr.split('.')        
    if len(li)!=4:
        return 0
    li=[int(k) for k in li]
    for i in li:
        if (i<0) or (i>255):
            return 0
    ipNum=(li[0]<<24)|(li[1]<<16)|(li[2]<<8)|li[3]    
    return ipNum
#################################################
#################################################
def Num2Ipv4Addr(Num):
    if (not (isinstance(Num, int) or isinstance(Num, long))) or (Num > 0xFFFFFFFF):
        return '0.0.0.0'
    li=[str(Num>>24),str((Num>>16)&255),str((Num>>8)&255),str(Num&255)]
    return '.'.join(li)
#################################################
#################################################
def MaskAddrv4ToMaskNum(netMaskAddr):
    '''子网掩码有0.0.0.0、255.0.0.0、255.255.0.0、255.255.255.0和 255.255.255.255共五种。'''
    if not isinstance(netMaskAddr, str):
        return -1

    netMaskNum = Ipv4Addr2Num(netMaskAddr)
    if netMaskNum == 0:
        return 0
    i=32
    k=(255<<24)|(255<<16)|(255<<8)|255
    j=k
    while netMaskNum!=(j&k) and i>=8:
        k=k<<1
        i-=1
    if i<8:return -1
    return i
#################################################
#################################################
def CidrNum2CidrAddrv4(cidrNum):
    maskNum = int(cidrNum) if isinstance(cidrNum, str) else cidrNum
    if maskNum >= 0 and maskNum <= 32:
        hostNum = 32 -maskNum
        netIpv4Num = (0xFFFFFFFF << hostNum) & 0xFFFFFFFF
        return Num2Ipv4Addr(netIpv4Num)
    return '0.0.0.0' 
#################################################
#################################################
def GetIpv4NetAddrByCidrNum(ipv4Addr, cidrNum):
    if (not isinstance(ipv4Addr, str)) or (not isinstance(cidrNum, str)):
        return '0.0.0.0'
    cidrAddr = CidrNum2CidrAddrv4(cidrNum)
    cidrAddrNum = Ipv4Addr2Num(cidrAddr)
    v4AddrNum = Ipv4Addr2Num(ipv4Addr)
    netIpv4Addr = cidrAddrNum & v4AddrNum
    return Num2Ipv4Addr(netIpv4Addr)
#################################################
#################################################
def GetIpv4NetAddrByCidrAddr(cidrAddrv4):
    if not isinstance(cidrAddrv4, str):
        return '0.0.0.0'
    ipv4Addr,cidrNum = GetAddrAndMaskFromCidr(cidrAddrv4)
    return GetIpv4NetAddrByCidrNum(ipv4Addr, cidrNum)
#################################################
#################################################
def ReverseMaskToMask(ip):
    """ 
        反掩码取反求出掩码
    """
    item = ip.split('.')
    ipData = []
    for num in item:
        result = intTo2BinStr(num,8)
        ipData.append(result)
    dataStr = ''.join(ipData)
    
    num = int(dataStr,2)
    i = ~num
    data = intTo2BinStr(i,32)
    b = int(data,2)
    return b
#################################################
#################################################
def intTo2BinStr(x,K):
    """ 
        将整数x转化为 K 位二进制字符串
    """
    try:
        x = long(x)
    except:
        x = 0
    try:
        K = int(K)
    except:
        K = 1
    if K<1:
        k = 1
    if x<0:
        FH = 1
        x = -x
    else:
        FH=0
    A = [0 for J in xrange(0,K)]
    J = K-1
    while J>=0 and x>0:
        Y = x%2
        x = x/2
        A[J] = Y
        J = J-1
    if FH ==1:
        #求反
        for J in xrange(0,K):
            if A[J] == 1:
                A[J] =0
            else:
                A[J]=1
        #末尾加1
        J = K-1
        while J>=0:
            A[J] =A[J] +1
            if A[J] <= 1:
                break;
            A[J] = 0
            J=J-1        
    result = ''.join([chr(J+48) for J in A])
    return result


    
#################################################
#################################################
def IsSrcInDstNetwork(srcCidrAddrv4,dstCidrAddrv4):
    '''
    CIDR技术用子网掩码中连续的1部份表示网络ID，连续的0部份表示主机ID。
    CIDR表示方法：IP地址/网络ID的位数，比如192.168.23.35/21，其中用21位表示网络ID。
    '''
    if (not isinstance(srcCidrAddrv4, str)) or (not isinstance(dstCidrAddrv4, str)):
        return False
    srcIpv4Addr,srcCidrNum = GetAddrAndMaskFromCidr(srcCidrAddrv4)
    dstIpv4Addr,dstCidrNum = GetAddrAndMaskFromCidr(dstCidrAddrv4)
    if srcCidrNum == dstCidrNum:
        src = GetIpv4NetAddrByCidrAddr(srcCidrAddrv4)
        dst = GetIpv4NetAddrByCidrAddr(dstCidrAddrv4)
        if src == dst:
            return True
        return False
    elif int(srcCidrNum) > int(dstCidrNum):
        src = GetIpv4NetAddrByCidrNum(srcIpv4Addr,dstCidrNum)
        dst = GetIpv4NetAddrByCidrNum(dstIpv4Addr,dstCidrNum)
        if src == dst:
            return True
        return False
    else:
        return False

#################################################
#################################################
def IsSomeWordsExist(text, *wordArgv):
    if wordArgv:
        for oneArg in wordArgv:
            m = re.search('\s*%s\s*'%oneArg, text)
            if not m:
                return False
        return True
    return False

#################################################
#################################################
def ThrowExceptionForInvalidField(fieldName):
    raise ValueError, u'字段"%s"无效，信息采集结果不符合要求'%fieldName

#################################################
#################################################
def GetInterfaceFullName(shortName):
    m = re.search(r"\d+", shortName)
    temp = ''
    num = ''
    if m:
        temp = shortName[:m.start()].replace(" ","")
        num  = shortName[m.start():]
    else:
        temp = shortName
        num = ''
    interfaceName = {r'Atm':r'Atm',
                     r'XGE':r'Ten-GigabitEthernet',
                     r'FGE':r'FortyGigE',
                     r'Pos':r'Pos',
                     r'Cpos':r'Cpos',
                     r'RAGG':r'Route-Aggregation',
                     r'Tun':r'Tunnel',
                     r'VT':r'Virtual-Template',
                     r'Ana':r'Analogmodem',
                     r'Loop':r'LoopBack',
                     r'GE':r'GigabitEthernet',
                     r'Eth':r'Ethernet',
                     r'En':r'Encrypt',
                     r'S':r'Serial',
                     r'Cellular':r'Cellular',
                     r'Vlan':r'Vlan-interface'}
    if interfaceName.setdefault(temp) == None:
        return shortName
    else:
        return interfaceName.setdefault(temp)+num

def GetInterfaceShortName(fullName):
    m = re.search(r"\d+", fullName)
    temp = ''
    num = ''
    if m:
        temp = fullName[:m.start()].replace(" ","")
        num  = fullName[m.start():]
    else:
        temp = fullName
        num = ''
    interfaceName = {r'Atm':r'Atm',
                     r'Ten-GigabitEthernet':r'XGE',
                     r'FortyGigE':r'FGE',
                     r'Pos':r'Pos',
                     r'Cpos':r'Cpos',
                     r'Route-Aggregation':r'RAGG',
                     r'Tunnel':r'Tun',
                     r'Virtual-Template':r'VT',
                     r'Analogmodem':r'Ana',
                     r'LoopBack':r'Loop',
                     r'GigabitEthernet':r'GE',
                     r'Ethernet':r'Eth',
                     r'Encrypt':r'En',
                     r'Serial':r'S',
                     r'Cellular':r'Cellular',
                     r'Vlan-interface':r'Vlan'}
    if interfaceName.setdefault(temp) == None:
        return fullName
    else:
        return interfaceName.setdefault(temp)+num
