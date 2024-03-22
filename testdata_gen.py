import gzip
from pathlib import Path
import time
import os
import pandas as pd
import csv



class GenBinl:
    
    def __init__(self,csvpath):
    #########################################新建时间戳文件夹###########################################################
        self.pins = []
        self.csvpath=csvpath
        self.testpointmap={}
        self.binlname='sidd_pangu_B0_PS2_FullChip_sidd_final_062623_pDPS'
        self.smsize=0
        self.wft=''
        self.sqpgcount=0
        self.tpsecount={}
        self.dftdcount={}
    def mkdir(self):
        time_now=time.strftime("%Y%m%d-%H%M",time.localtime())
        root=os.getcwd()
        print(root)
        path = root+'\\'+time_now
        if not os.path.exists(path):
            os.makedirs(path)
            print('done'+path)

    #################################################################################################################
    def ungz (self):
        gz_path='D:\workspace\python\dpsbinl'
        try:
            for f in os.listdir(gz_path):
                if ".gz" in f:

                    g=gzip.GzipFile(mode="rb",fileobj=open(gz_path+"\\"+f,'rb'))
                    open(gz_path+"\\"+f.replace(".gz",""),"wb").write(g.read())
        except Exception as e:
            print(e)
        else:
            print("sucese")

    # #########################################写binl文件###########################################################
    def writeline(self,temp,line):
        if temp==0:
            outbinlfilepath='D:/workspace/python/20230706-1439'
            outbinlfilename='temp_file.txt'
            filename=Path(outbinlfilepath+'\\'+outbinlfilename)
            f=open(filename,'ab+')
            f.write(line.encode())
        elif temp ==1:
            outbinlfilepath='D:/workspace/python/20230706-1439'
            outbinlfilename='iddq_pangu_B0_PS2_FullChip_PANGU_B0_IDDQ_BODY_GDDR0_V02_PR002876_051623_pDPS.binl'
            filename=Path(outbinlfilepath+'\\'+outbinlfilename)
            f=open(filename,'ab+')
            f.write(line.encode())
            #write pattern name
            # line='SQLB "'+self.binlname+'",MAIN,0,135,"WFT_GDDR_PLL",(pDPS)'
            # f.write(line.encode())
        elif temp ==2:
            outbinlfilepath='D:/workspace/python/20230706-1439'
            outbinlfilename='iddq_pangu_B0_PS2_FullChip_PANGU_B0_IDDQ_BODY_GDDR0_V02_PR002876_051623_pDPS.lev'
            filename=Path(outbinlfilepath+'\\'+outbinlfilename)
            f=open(filename,'ab+')
            f.write(line.encode())

    #########################################读binl.gz文件###########################################################
    # binlfilepath='D:\workspace\python\sidd_pangu_B0_PS2_FullChip_sidd_final_062623_pDPS.binl.gz'
    # filepath = pathlib.Path(binlfilepath)
    # with gzip.open(filepath,'rb')as f:
    #     content=f.read()
    #     # start=content.find("<?xml version=\"1.0\"?>")
    #     # end=content.find("</sequence>")
    #     # print(start)
    #     print("end")
    #     for linedata in f:
    #         # writebinlfile(linedata)
    #         print(str(linedata,'utf-8'))


    ########################################读testedata xlsx文件###########################################################
    # testdata='D:\production\B0\debuglog\testdata.xlsx'
    # filepath = pathlib.Path(binlfilepath)
    def readcsv(self):
        # self.csvpath = 'D:\workspace\python\dpsbinl\\testpoints.csv'
        with open(self.csvpath, encoding='utf-8-sig') as csvfile:
            reader = csv.reader(csvfile)
            rows = [row for row in reader]
        # print(rows)
        for row in rows:
            match row[0]:
                case 'binlname':
                    self.binlname=row[1]
                case 'smsize':
                    self.smsize=int(row[1])
                case 'wft':
                    self.wft=row[1]
                case 'period':
                    period=row[1]
                    # print(period)
                case 'testpin':
                    pinlist=row[1:]
                    # print(pinlist)
                case 'testtimestart':
                    timestartlist=row[1:]
                    # print(timestartlist)
                case 'testtimeend':
                    timeendlist=row[1:]
                    # print(timeendlist)
                case 'testpoint':
                    pointlist=row[1:]
                    # print(pointlist)
                case 'testpointname':
                    pointnamelist=row[1:]
                    # print(pointnamelist)
                case _:
                    testinfo=row[1:]
        self.pins=[Testpin(period,dps,timestartlist[index],timeendlist[index],pointlist[index],pointnamelist[index]) for index,dps in enumerate(pinlist)]
        # print(self.pins[0].period,self.pins[0].pin,self.pins[0].timestart,self.pins[0].timeend,self.pins[0].pointname)
################################################初始化测试信息#############################################################
    def porcesstestpoint(self,pointlist):
        timeendlist=pointlist.timeend
        timestartlist=pointlist.timestart
        testpointslist=pointlist.point
        pinname=pointlist.pin
        pointname=pointlist.pointname
        res=[]
        plist=[]
        for index,value in enumerate(timestartlist):
            res.append((timeendlist[index]-timestartlist[index])/testpointslist[index])
            plist.append(timestartlist[index]+res[index]/2)
            for p in range (testpointslist[index]-1):
                plist.append(plist[-1]+res[index])
        self.testpointmap.update({pinname:plist})
        # print('testpointmap is:',self.testpointmap)
    def writetempfile(self):
        maxrptv=16777215
        pointsetup=64
        restrptv=0
        sqpgcount=3
        tpse={}
        dftd={}
        # print(self.pins)
        testpointlist={}
        sumpointlist=[]
        pointmap = {}
        pointname_timemap={}
        anchor=0
        for pin in self.pins:
            GenBinl.porcesstestpoint(self,pin)
            for index,pn in enumerate(pin.pointname):
                for key,val in self.testpointmap.items():
                    if key in pn:
                        pointname_timemap[pn]=val[index]
                        # print(pn,val[index])
        # print('pointname_timemap is :',pointname_timemap)

        for value in self.testpointmap.values():
            sumpointlist=sumpointlist+value
        # print('sumpointlist un sort is :',sumpointlist)
        sumpointlistsort=sorted(list(set(sumpointlist)))
        # print('sumpointlist is :',sumpointlist)
        for index,pointtime in enumerate(sumpointlistsort):
            if index==0:
                maxrptvlooptimes=(sumpointlistsort[index]/self.pins[0].period-pointsetup)/maxrptv
                restrptv=(sumpointlistsort[index]/self.pins[0].period-pointsetup)%maxrptv
                for sqpg in range(int(maxrptvlooptimes)):
                    line='SQPG '+str(sqpgcount)+',RPTV,1,'+str(int(maxrptv))+',,(pDPS)\n'
                    # print(line)
                    GenBinl.writeline(self,0,line)
                    sqpgcount=sqpgcount+1
                    anchor=anchor+1
                    # print(testpointlist)
                else:
                    line='SQPG '+str(sqpgcount)+',RPTV,1,'+str(int(restrptv))+',,(pDPS)\n'
                    # print(line)
                    GenBinl.writeline(self,0,line)
                    sqpgcount = sqpgcount + 1
                    anchor=anchor+1
                    line = 'SQPG '+str(sqpgcount)+',GENV,'+str(pointsetup)+',,,(pDPS)\n'
                    # print(line)
                    GenBinl.writeline(self,0,line)
                    sqpgcount=sqpgcount+1
                    anchor=anchor+pointsetup
                    testpointlist[anchor]=sumpointlistsort[index]
                    # print(testpointlist)
            else:
                maxrptvlooptimes=((sumpointlistsort[index]-sumpointlistsort[index-1])/self.pins[0].period-pointsetup)/maxrptv
                restrptv=((sumpointlistsort[index]-sumpointlistsort[index-1])/self.pins[0].period-pointsetup)%maxrptv
                for sqpg in range(int(maxrptvlooptimes)):
                    line='SQPG '+str(sqpgcount)+',RPTV,1,'+str(int(maxrptv))+',,(pDPS)\n'
                    # print(line)
                    GenBinl.writeline(self,0,line)
                    sqpgcount=sqpgcount+1
                    anchor=anchor+1
                    # print(testpointlist)
                else:
                    line='SQPG '+str(sqpgcount)+',RPTV,1,'+str(int(restrptv))+',,(pDPS)\n'
                    # print(line)
                    GenBinl.writeline(self,0,line)
                    sqpgcount = sqpgcount + 1
                    anchor=anchor+1
                    line = 'SQPG '+str(sqpgcount)+',GENV,'+str(pointsetup)+',,,(pDPS)\n'
                    # print(line)
                    GenBinl.writeline(self, 0,line)
                    sqpgcount=sqpgcount+1
                    anchor=anchor+pointsetup
                    testpointlist[anchor]=sumpointlistsort[index]
        # sqpgcount=sqpgcount+1
        GenBinl.writeline(self,0,'SQPG '+str(sqpgcount)+',STOP,,,,(pDPS)\nWSDM 1,2')
        self.sqpgcount=sqpgcount

        for pointname,testtime in pointname_timemap.items():
            for an1,testtime1 in testpointlist.items():
                for pin in self.pins:
                    if testtime==testtime1:
                        if pin.pin in pointname:
                            try:
                                if pin.pin == currentpin:
                                    GenBinl.writeline(self,0,'<tp anchor="'+str(an1)+'" td="'+str(pointname)+'"/>\n')
                                    try:
                                        tpse[str(pin.pin)]=tpse.get(str(pin.pin))+len(str('<tp anchor="'+str(an1)+'" td="'+str(pointname)+'"/>\n').encode())
                                    except:
                                        tpse[str(pin.pin)]=len(str('<tp anchor="'+str(an1)+'" td="'+str(pointname)+'"/>\n').encode())
                                else:
                                    GenBinl.writeline(self,0,'</sequence>\n')
                                        #如何在一个pin的tpse之后结束？
                                currentpin=pin.pin
                            except:
                                currentpin = pin.pin
        GenBinl.writeline(self,0,'</sequence>\n')
        print('tpse is:',tpse.values())
        self.tpsecount=tpse

        # print('pointmap is :',pointmap)
        for tp,an in pointname_timemap.items():
            for pin in self.pins:
                if pin.pin in tp:
                    GenBinl.writeline(self,0,'  <td id="'+str(tp)+'" type="'+'dcset'+'"><measure type="'+'current'+'" samples="'+'32'+'"/></td>\n')
                    try:
                        dftd[str(pin.pin)]=dftd.get(str(pin.pin))+len(str('  <td id="'+str(tp)+'" type="'+'dcset'+'"><measure type="'+'current'+'" samples="'+'32'+'"/></td>\n').encode())
                    except:
                        dftd[str(pin.pin)]=len(str('  <td id="'+str(tp)+'" type="'+'dcset'+'"><measure type="'+'current'+'" samples="'+'32'+'"/></td>\n').encode())
        print('dftdcount is:',dftd.values())
        self.dftdcount=dftd
    def genpattern(self):
        sqpgstart=0
        tpsestart=0
        levstart=0
        sqpgsize=0
        binlpins={}
        binlpinsize=0
        levelpins={}
        levelpinsize=0
        f=open('D:/workspace/python/20230706-1439/temp_file.txt','r')
        rd=f.readlines()
        # print(self.pins[0].pin)
        for dl in rd:
            if 'SQPG' in dl:
                if sqpgstart==0:
                    GenBinl.writeline(self,1,'hp93000,vector,0.1\n')
                    GenBinl.writeline(self,1,'DMAS PARA,SM,'+str(self.smsize)+',(pDPS)\n')
                    GenBinl.writeline(self,1,'DMAS SQPG,SM,'+str(self.sqpgcount+3)+',(pDPS)\n')
                    GenBinl.writeline(self,1,'SQLB "'+self.binlname+'",MAIN,0,'+str(self.sqpgcount+2)+',"'+str(self.wft)+'",(pDPS)\n')
                    GenBinl.writeline(self,1,'SQLA LBL,"'+self.binlname+'","PARA_MEM=SM,PARA_MCTX=DEFAULT",(pDPS)\n')
                    GenBinl.writeline(self,1,'SQPG 0,STVA,0,,,(pDPS)\nSQPG 1,STSA,,,,(pDPS)\n')
                    GenBinl.writeline(self,1,dl)
                    sqpgstart=1
                else:
                    GenBinl.writeline(self,1,dl)

            elif 'anchor' in dl:
                for tp in self.pins:
                    if tp.pin in dl:
                        if tpsestart==0:
                            GenBinl.writeline(self,1,'TPSE "'+self.binlname+'",MAIN,"'+self.binlname+'",REPLACE,('+tp.pin+'),#9'+str(self.tpsecount.get(tp.pin)+32).rjust(8,'0')+'<?xml version="1.0"?>\n<sequence>\n')
                            tpsestart=1
                        else:
                            GenBinl.writeline(self,1,dl)
                        # try:
                        #     pinvalue=binlpins.get(tp.pin)
                        #     # print('update',pinvalue)
                        #     pinvalue=pinvalue+len(str(dl).encode())
                        #     binlpins.update({tp.pin:pinvalue})
                        #
                        # except:
                        #     binlpins[tp.pin]=len(str(dl).encode())
                        #     print('1st init')
            elif '</sequence>' in dl:
                GenBinl.writeline(self,1,dl)
                tpsestart=0
            elif 'type=' in dl:
                for tp in self.pins:
                    if tp.pin in dl:
                        try:
                            pinvalue=levelpins.get(tp.pin)
                            pinvalue=pinvalue+len(str(dl).encode())
                            levelpins.update({tp.pin:pinvalue})
                        except:
                            levelpins[tp.pin]=len(str(dl).encode())
        print(binlpins,levelpins)

class Testpin:
    def __init__(self,testperiod,testpin,testtimestrat,testtimeend,testpoint,testpointname):

        testtimestrat=testtimestrat.split(",")
        testtimeend=testtimeend.split(",")
        self.period=int(testperiod[:-2])
        self.pin=testpin
        self.timestart=[self.convertunit(time) for time in testtimestrat]
        self.timeend=[self.convertunit(time) for time in testtimeend]
        self.point=[int(x) for x in testpoint.split(',')]
        self.pointname=[testpointname+'_'+str(countnum) for countnum in range(sum(self.point))]
    def convertunit(self,time):
        if 'ps' in time:
            return int(time.replace('ps', ''))*1e-3
        elif 'ns' in time:
            return int(time.replace('ns', ''))
        elif 'us' in time:
            return int(time.replace('us', '')) * 1e3
        elif 'ms' in time:
            return int(time.replace('ms', '')) * 1e6
        elif 's' in time:
            return int(time.replace('s', '')) * 1e9


#################################################解压.gz文件####################################################

if __name__ == '__main__':
    csvpath='D:\workspace\python\dpsbinl\\testpoints.csv'
    gen=GenBinl(csvpath)
    gen.readcsv()
    # gen.writeline()
    gen.writetempfile()
    gen.genpattern()
