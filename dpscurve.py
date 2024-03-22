import pathlib
import sys

import matplotlib.pyplot as plt
import numpy as np
import re


class dpscurve():

    def __init__(self,filepath,curvetype):
        self.dpsname = ''
        self.group = ''
        self.vout = ''
        self.vout_rise_t_ms_per_volt = ''
        self.vout_rise_settling_t_ms = ''
        self.vout_fall_t_ms_per_volt = ''
        self.vout_fall_settling_t_ms = ''
        self.power = {}
        self.filepath=filepath
        self.curvetype=curvetype

    def plot(self):
        leftshfit=5
        rightshift=10
        dpsdata=readlevelfile(self.filepath,self.curvetype)
        dpsmap=dpsdata.readlevfile()
        del dpsmap['']#??????????????
        # print(dpsmap)
        max_risetime=0
        min_risetime=float(list(dpsmap.values())[0][2])
        max_falltime=0
        min_falltime=float(list(dpsmap.values())[0][4])

        for dps in dpsmap:
            if dpsmap[dps][2] + dpsmap[dps][4]!='':
               if float(dpsmap[dps][2]).__abs__() >max_risetime:
                   max_risetime=float(dpsmap[dps][2])
               if float(dpsmap[dps][2]).__abs__() <min_risetime:
                   min_risetime=float(dpsmap[dps][2])
               if float(dpsmap[dps][4]).__abs__() >max_falltime:
                    max_falltime=float(dpsmap[dps][4]).__abs__()
               if float(dpsmap[dps][4]).__abs__() < min_falltime:
                    min_falltime = float(dpsmap[dps][4]).__abs__()
        # print(max_risetime,max_falltime,min_risetime,min_falltime)
        for dps in dpsmap:
            # xa=list(map(lambda x:x,np.arange(-max_risetime,-min_falltime+20,0.1)))
            xa_rise=list(map(lambda x:x,np.arange(-max_risetime,-min_risetime+rightshift,0.1)))
            xa_fall=list(map(lambda x:x,np.arange(-max_falltime-leftshfit,-min_falltime+rightshift,0.1)))
            xa=xa_rise+xa_fall
            dpsformat=format(dpsmap[dps][0],dpsmap[dps][1],dpsmap[dps][2],dpsmap[dps][3],dpsmap[dps][4])
            dpsarrayrise=list(map(lambda x:dpsformat.dpsriseformat(x),np.arange(-max_risetime,-min_risetime+rightshift,0.1)))
            dpsarrayfall=list(map(lambda x:dpsformat.dpsfallformat(x),np.arange(-max_falltime-leftshfit,-min_falltime+rightshift,0.1)))
            dpsarray=dpsarrayrise+dpsarrayfall
            if self.curvetype.__contains__("rise"):
                plt.title('rise_curve')
                plt.plot(xa_rise, dpsarrayrise, label=dps.__str__())
                plt.rcParams.update(({'font.size': 10}))
            elif self.curvetype.__contains__("fall"):
                plt.title('fall_curve')
                plt.plot(xa_fall, dpsarrayfall, label=dps.__str__())
                plt.rcParams.update(({'font.size': 10}))
            elif self.curvetype.__contains__("curve"):
                plt.title('dps_curve')
                plt.plot(xa,dpsarray,label=dps.__str__())
                plt.rcParams.update(({'font.size':10}))
                # plt.text(x=10,y=10,s='You\'d better draw the rise and fall curves in two parts!!!!!!',va='top')
        plt.legend(bbox_to_anchor=(0.95, 1.0), loc='upper left')
        plt.show()



class format(dpscurve):
        #self.coortime
    def __init__(self,vout,vout_rise_t_ms_per_volt,vout_rise_settling_t_ms,vout_fall_t_ms_per_volt,vout_fall_settling_t_ms):
        # super.__init__()
        self._rise_settling_t_ms=float(vout_rise_settling_t_ms)
        self._rise_t_ms_per_volt=float(vout_rise_t_ms_per_volt)
        self._fall_settling_t_ms=float(vout_fall_settling_t_ms)
        self._fall_t_ms_per_volt=float(vout_fall_t_ms_per_volt)
        self.voltage=float(vout)

    def dpsriseformat(self,time):
        if time < -self._rise_settling_t_ms:
            currentvolt=0
        else:
           currentvolt = (time+self._rise_settling_t_ms) / self._rise_t_ms_per_volt
        return currentvolt if currentvolt<self.voltage else self.voltage

    def dpsfallformat(self,time):
        if time < -self._fall_settling_t_ms:
            currentvlot=self.voltage
        else:
            currentvlot= self.voltage - (time+self._fall_settling_t_ms) / self._fall_t_ms_per_volt
        return currentvlot if currentvlot > 0 else 0

class readlevelfile(dpscurve):

    def readlevfile(self):
        filepath = pathlib.Path(self.filepath)
        with open(filepath, "r") as fp:
            for linedata in fp:
                if linedata.__contains__("#"):
                    for index, char in enumerate(linedata):
                        if char == '#':
                            linedata = linedata[:index]
                if linedata.__contains__("DPSPINS"):
                    print(linedata)
                    self.dpsname = re.sub('\s|\t', '', linedata)[7:]
                    self.vout = re.sub('P', '.', self.dpsname.split("_")[-1])
                elif linedata.__contains__("vout_rise_t_ms_per_volt"):
                    self.vout_rise_t_ms_per_volt = linedata.strip().split("=")[1]
                elif linedata.__contains__("vout_rise_settling_t_ms"):
                    self.vout_rise_settling_t_ms = linedata.strip().split("=")[1]
                elif linedata.__contains__("vout_fall_t_ms_per_volt"):
                    self.vout_fall_t_ms_per_volt = linedata.strip().split("=")[1]
                elif linedata.__contains__("vout_fall_settling_t_ms"):
                    self.vout_fall_settling_t_ms = linedata.strip().split("=")[1]
                self.power[self.dpsname] = [self.vout, self.vout_rise_t_ms_per_volt, self.vout_rise_settling_t_ms,
                                            self.vout_fall_t_ms_per_volt, self.vout_fall_settling_t_ms]
        return self.power

# if __name__ == '__main__':
#     path = 'D:\workspace\python\shell_dfps_dps64.pin'
#     curvetype="rise"
#     dps=dpscurve(path,curvetype)
#     dps.plot()
    import argparse

if __name__ == '__main__':
    if len(sys.argv)==3:
       filepath=sys.argv[1]
       curveytpe=sys.argv[2]
    elif len(sys.argv)==2:
        print("You'd better draw the rise and fall curves in two parts!!!!!!")
        filepath = sys.argv[1]
        curveytpe='curve'
    else:
        print("pls check args!")
    dps=dpscurve(filepath,curveytpe)
    dps.plot()
