import math
import random
import warnings
import plotly.graph_objects as go
from scipy import optimize
import numpy as np
from pyXSteam.XSteam import XSteam
steamTable = XSteam(XSteam.UNIT_SYSTEM_MKS)
solve = optimize.fsolve

class RachfordRice:

    chemicals = ['Methane','Ethylene','Ethane','Propylene',
    'Propane', 'Isobutane' , 'n-Butane', 'Isopentane', 'n-Pentane',
    'n-Hexane', 'n-Heptane', 'n-Octane','n-Nonane', 'n-Decane' ]

    #Philip Wankat Table 2-3
    McWilliam_Coeff = {
        'Methane': [-292860, 0, 8.2445, -0.8951, 59.8465, 0, 1.66],
        'Ethylene': [-600076.875, 0, 7.90595, -0.84677, 42.94594, 0, 2.65],
        'Ethane': [-687248.25, 0, 7.90694, -0.88600, 49.02654, 0, 1.95],
        'Propylene': [-923484.6875, 0, 7.71725, -0.87871, 47.67624, 0, 1.90],
        'Propane':  [-970688.5625, 0, 7.15059, -0.76984, 0, 6.90224, 2.35],
        'Isobutane': [-1166846, 0, 7.72668, -0.92213, 0, 0, 2.52],
        'n-Butane': [-1280557, 0, 7.94986, -0.96455, 0, 0, 3.61],
        'Isopentane': [-1481.583, 0, 7.58071, -0.93159, 0, 0, 4.56],
        'n-Pentane': [-1524891, 0, 7.33129, -0.89143, 0, 0, 4.30],
        'n-Hexane': [-1778901, 0, 6.96783, -0.84634, 0, 0, 4.90],
        'n-Heptane': [-2018803, 0, 6.52914, -0.79543, 0, 0, 6.34],
        'n-Octane': [0, -7646.81641, 12.48457, -0.73152, 0, 0, 7.58],
        'n-Nonane': [-2551040, 0, 5.69313, -0.67818, 0, 0, 9.40],
        'n-Decane': [0, -9760.45703, 13.80354, -0.71470, 0, 0, 5.69]
    }

    CriticalT_P = {
        'Methane': [-82.6, 4595],
        'Ethylene': [9.2, 5040.8],
        'Ethane': [32.18, 4872],
        'Propylene': [92.42, 4664.6],
        'Propane':  [96.75, 4301],
        'Isobutane': [135, 3648.7],
        'n-Butane': [152.01, 3796],
        'Isopentane': [187.2, 3378],
        'n-Pentane': [196.55, 3367.5],
        'n-Hexane': [234.67, 3044.1],
        'n-Heptane': [266.98, 2736],
        'n-Octane': [295.59, 2483.6],
        'n-Nonane': [321.4, 2281],
        'n-Decane': [344.55, 2103]
    }
    

    params = {'Pmin': 101, 'Pmax': 6000, 'Tmin':-70, 'Tmax': 200, }
    #Just to learn about class methods. Can update new chemicals using this method
    @classmethod
    def add_chemical(cls, chemical_coeff):
        #Takes in dictionary chemical_coeff
        for k in chemical_coeff:
            if k not in cls.chemicals:
                cls.chemicals.append(k)
                cls.McWilliam_Coeff[k] = chemical_coeff[k]
            else:
                cls.McWilliam_Coeff[k] = chemical_coeff[k]

    def __init__(self, n, T, P, components, z):
        #Takes in n, T, P, components (array), z (array) and initialises it to self
        self.n = n
        self.T = T
        self.P = P
        self.components = components
        self.z = z
        self.calculate()
        if self.checkState() == "Vapor":
            self.v = 1
            self.x = [0, 0]
        elif self.checkState() == "Liquid":
            self.v = 0
            self.y = [0, 0]
        self.exceedT = False
        self.exceedP = False
        if self.T >= RachfordRice.CriticalT_P[self.components[0]][0] or self.T >= RachfordRice.CriticalT_P[self.components[1]][0]:
            self.exceedT = True
        if self.P >= RachfordRice.CriticalT_P[self.components[0]][1] or self.P >= RachfordRice.CriticalT_P[self.components[1]][1]:
            self.exceedP = True

    def calculate(self):
        self.T_degR = self.T * 9/5 + 491.67
        self.P_psia = self.P *0.145
        self.K = self.calcK()
        self.v = self.newtonMethod()
        self.x = self.calcX()
        self.y = self.calcY(self.x)
        
    #Update different values individually
    def setT(self,T):
        self.T = T
        self.calculate()
    
    def setP(self,P):
        self.P = P
        self.calculate()
    
    def setCompA(self,compA):
        self.components[0] = compA
        self.calculate()
    
    def setCompB(self,compB):
        self.components[1] = compB
        self.calculate()
    
    def setComponents(self,components):
        self.components = components
        self.calculate()
    
    def setZ(self,Z):
        self.Z = Z
        self.calculate()

    #Show current details
    def get_dets(self):
        #Method to print out the details stored
        print("n: " + str(self.n), end=", ")
        print("T: " + str(self.T), end="C, ")
        print("P: " + str(self.P), end="kPa, ")
        print("components: " + str(self.components), end=", ")
        print("z: " + str(self.z))

    def calcK(self):
        K = []
        for i in range(self.n):
            coeff = RachfordRice.McWilliam_Coeff[self.components[i]]
            aT1 = coeff[0]
            aT2 = coeff[1]
            aT3 = coeff[2]
            ap1 = coeff[3]
            ap2 = coeff[4]
            ap3 = coeff[5]
            lnK = aT1/(self.T_degR**2) + aT2/self.T_degR + aT3 + ap1*math.log(self.P_psia) + ap2/(self.P_psia**2) + ap3/self.P_psia
            K.append(math.exp(lnK))
        return K
    
    def RR(self,v,K,z):
        # Rachford Rice Eqn
        # v = V/F
        result = 0
        for i in range(0, len(K)):
            result += (K[i]-1)*z[i]/(1+(K[i]-1)*v)
        return result
    
    def RRprime(self,v,K,z):
        # Derivative of RR eqn wrt V/F
        result = 0
        for i in range(0, len(K)):
            result -= (K[i]-1)**2*z[i]/(1+(K[i]-1)*v)**2
        return result

    def calcX(self):
        # v = V/F
        result = []
        for i in range(0, len(self.K)):
            result.append(self.z[i] / (1+(self.K[i]-1)*(min(max(self.v, 0), 1))))
        return result
    
    def calcY(self,x):
        # v = V/F
        result = []
        for i in range(0, len(self.K)):
            result.append(x[i] * self.K[i])
        return result

    def checkState(self):
        if sum(self.x) <= 1.01 and sum(self.x) >= 0.99:
            if sum(self.y) <= 1.01 and sum(self.y) >= 0.99:
                return "VLE"
            else:
                return "Liquid"
        else:
            return "Vapor"

    def newtonMethod(self):
        # v is the V/F (vapour fraction)
        v = 1
        funcVal = self.RR(v, self.K, self.z)
        tol = 1e-6
        maxIter = 10000
        iter = 0
        while abs(funcVal) > tol and iter < maxIter:
            v = v - self.RR(v, self.K, self.z)/self.RRprime(v, self.K, self.z)
            funcVal = self.RR(v, self.K, self.z)
            iter += 1
        return v

    def getPureComponentBoilingTemp(self, component, pressure): # psia 
        if component in self.components:
            coeff = RachfordRice.McWilliam_Coeff[component]
            aT1 = coeff[0]
            aT2 = coeff[1]
            aT3 = coeff[2]
            ap1 = coeff[3]
            ap2 = coeff[4]
            ap3 = coeff[5]
            
            def equation(T):  # solve for T to make K = 1 
                lnK = aT1/(T**2) + aT2/T + aT3 + ap1*math.log(pressure) + ap2/(pressure**2) + ap3/pressure
                K = math.exp(lnK)
                return K - 1
            # returns temp in rankine

            try:
                result = solve(equation, 650).item(0) 
                return (result - 491.67) *(5/9)
            except ValueError:
                return None

    def getPureComponentBoilingPressure(self, component, temperature): # Rankine
        if component in self.components:
            coeff = RachfordRice.McWilliam_Coeff[component]
            aT1 = coeff[0]
            aT2 = coeff[1]
            aT3 = coeff[2]
            ap1 = coeff[3]
            ap2 = coeff[4]
            ap3 = coeff[5]
            
            def equation(P):  # solve for T to make K = 1 
                lnK = aT1/(temperature**2) + aT2/temperature + aT3 + ap1*math.log(P) + ap2/(P**2) + ap3/P
                K = math.exp(lnK)
                return K - 1

            # returns a pressure in psia

            with warnings.catch_warnings():
                warnings.filterwarnings('error')

                try:
                    a = Antoine(component, (temperature-491.67)*(5/9), self.P)
                    
                    estimate = a.calc_Psat()*0.145038
                    print(estimate)
                    result = solve(equation, estimate).item(0)
                    return result / 0.145038
                except RuntimeWarning:
                    return None

class Antoine:
    #Not all n-alkanes is available here https://onlinelibrary.wiley.com/doi/pdf/10.1002/9781118135341.app1
    #So i used http://teachers.iauo.ac.ir/images/Uploaded_files/ANTOINE_COEFFICIENTS_FOR_VAPOR_PRESSURE[1][4619259].PDF
    #It doesnt have n-alkanes but i used the non-isomer form for now
    #P in mmHg, T in C
    coeff = {
        'Methane'   : [6.84566, 435.621, 271.361], #Tmin, Tmax [-182.48,-82.57]
        'Ethylene'  : [6.96636, 649.806, 262.73],  #Tmin, Tmax [-169.14,9.21]
        'Ethane'    : [6.95335, 699.106, 260.264], #Tmin, Tmax [-182.8, 32.27] 
        'Propylene' : [7.01672, 860.992, 255.895], #Tmin, Tmax [-184.15,91.61]
        'Propane'   : [7.01887, 889.864, 257.084], #Tmin, Tmax [-187.69, 96.67]
        'Isobutane' : [6.93388, 953.92, 247.077],  #Tmin, Tmax [-159.61,134.99]
        'n-Butane'  : [7.00961,1022.48,248.145],   #Tmin, Tmax [-138.29, 152.03]
        'Isopentane': [7.03015, 1140.45, 247.012], #Tmin, Tmax [-159.9, 187.28]
        'n-Pentane' : [7.00877, 1134.15,238.678],  #Tmin, Tmax [-129.73, 196.5]
        'n-Hexane'  : [6.9895, 1216.92, 227.451],  #Tmin, Tmax [-95.31, 234.28]
        'n-Heptane' : [7.04605, 1341.89, 223.733], #Tmin, Tmax [-90.59, 267.11]
        'n-Octane'  : [7.14462, 1498.96, 225.874], #Tmin, Tmax [-56.77, 295.68]
        'n-Nonane'  : [7.1884, 1607.74, 222.414],  #Tmin, Tmax [-53.52, 322.5]
        'n-Decane'  : [7.21745,1693.93, 216.459]   #Tmin, Tmax [-29.66, 345.3]
     }

    params = {
        'Methane'   : [-182.48,-82.57],
        'Ethylene'  : [-169.14,9.21],
        'Ethane'    : [-182.8, 32.27],
        'Propylene' : [-184.15,91.61],
        'Propane'   : [-187.69, 96.67],
        'Isobutane' : [-159.61,134.99],
        'n-Butane'  : [-138.29, 152.0],
        'Isopentane': [-159.9, 187.28],
        'n-Pentane' : [-129.73, 196.5],
        'n-Hexane'  : [-95.31, 234.28],
        'n-Heptane' : [-90.59, 267.11],
        'n-Octane'  : [-56.77, 295.68],
        'n-Nonane'  : [-53.52, 322.5],
        'n-Decane'  : [-29.66, 345.3]
    }

    def __init__(self, component, T, P):
        self.component = component
        self.T = T
        self.P = P

    def calc_Psat(self):
        #Temperature is in C
        Ant_coeff = Antoine.coeff[self.component]
        A = Ant_coeff[0]
        B = Ant_coeff[1]
        C = Ant_coeff[2]   

        #P is in mmhg
        lgP = A - B/(C+self.T) 
        P = pow(10,lgP) * 101.35/760
        self.P = P
        return self.P
    
    def setT(self,T):
        self.T = T
        self.calc_Psat()
        return self.P

class VanDerWaalsEOS:
    
    # index 0 is temp in celcius, index 1s pressure in kPa
    params = {
        'Methane': [-82.6, 4595],
        'Ethylene': [9.2, 5040.8],
        'Ethane': [32.18, 4872],
        'Propylene': [92.42, 4664.6],
        'Propane':  [96.75, 4301],
        'Isobutane': [135, 3648.7],
        'n-Butane': [152.01, 3796],
        'Isopentane': [187.2, 3378],
        'n-Pentane': [196.55, 3367.5],
        'n-Hexane': [234.67, 3044.1],
        'n-Heptane': [266.98, 2736],
        'n-Octane': [295.59, 2483.6],
        'n-Nonane': [321.4, 2281],
        'n-Decane': [344.55, 2103]
    }

    R = 8.314
    
    def __init__(self, T, P, component):  # T in Kelvin, P in bar
        self.T = T
        self.P = P
        self.component = component

    def C2K(self):
        return self.T + 273.15

    def kPa2Pa(self):
        return self.P*1000

    def getTR(self):
        return self.C2K()/(VanDerWaalsEOS.params[self.component][0]+273.15)

    def getPR(self):
        return self.kPa2Pa()/(VanDerWaalsEOS.params[self.component][1]*1000)

    def get_a(self):
        return (27*VanDerWaalsEOS.R*VanDerWaalsEOS.R*(VanDerWaalsEOS.params[self.component][0]+273.15)**2)/(64*(VanDerWaalsEOS.params[self.component][1]*1000))

    def get_b(self):
        return VanDerWaalsEOS.R*(VanDerWaalsEOS.params[self.component][0]+273.15)/(8*(VanDerWaalsEOS.params[self.component][1]*1000))

    def exceed_T(self):
        if self.getTR() > 1:
            return True
        return False
    
    def exceed_P(self):
        if self.getPR() > 1:
            return True
        return False

class Steam:

    def __init__(self,T,P): # T in degrees C, P in kPa
        self.T = T
        self.P = P
        self.Pbar = P/100
        self.H = None # kJ/kg
        self.S = None  # kJ/kgC
        self.v = None
        self.G = None
        self.vapvol = None
        self.liqvol = None

    def getT(self):
        return self.T

    def getP(self):
        self.P = self.Pbar / 100
        return self.P

    def getH(self):
        return self.H

    def getmeanH(self):
        if self.v < 1 and self.v > 0:
            return self.v*self.H[1] + (1-self.v)*self.H[0]
        return self.H

    def getS(self):
        return self.S

    def getmeanS(self):
        if self.v < 1 and self.v > 0:
            return self.v*self.S[1] + (1-self.v)*self.S[0]
        return self.S

    def getVapFrac(self):
        return self.v

    def getG(self):
        return self.G

    def triplePointT(self):
        return 0.01  # T1

    def triplePointP(self):
        return steamTable.psat_t(0.01)

    def Tcrit(self):
        return 373.946 

    def Pcrit(self):
        return 220.6  # bar

    def setT(self,T):
        self.T = T
        return self.getboilingP()*100
    
    def getTotalVol(self):
        return self.vapvol + self.liqvol

    def getboilingT(self): #isothermal
        return steamTable.tsat_p(self.Pbar)

    def getvapcurveT(self,P):
        return steamTable.tsat_p(P)

    def getboilingP(self): #isobaric
        return steamTable.psat_t(self.T)

    def instantiate(self):
        if self.T != self.getboilingT():
            self.H = steamTable.h_pt(self.Pbar, self.T)
            self.S = steamTable.s_pt(self.Pbar, self.T)
            self.v = steamTable.x_ph(self.Pbar, self.H)
            if self.v == 0:
                self.liqvol = steamTable.v_pt(self.Pbar, self.T)
                self.vapvol = 0
            else:
                self.vapvol = steamTable.v_pt(self.Pbar, self.T)
                self.liqvol = 0
            
        else:
            self.H = [steamTable.hL_p(self.Pbar), steamTable.hV_p(self.Pbar)]
            self.S = [steamTable.sL_p(self.Pbar), steamTable.sV_p(self.Pbar)]
            self.v = random.random()
            self.vapvol = steamTable.vV_p(self.Pbar)*self.v
            self.liqvol = steamTable.vL_p(self.Pbar)*(1-self.v)
            
        self.G = self.getmeanH() - (273.15+self.T)*self.getmeanS()
        
    def addH(self):
        meanH = self.getmeanH()
        meanH += 10
        if meanH > steamTable.hL_p(self.Pbar) and meanH < steamTable.hV_p(self.Pbar):
            self.v = (meanH - steamTable.hL_p(self.Pbar)) / (steamTable.hV_p(self.Pbar) - steamTable.hL_p(self.Pbar))
            self.H = [steamTable.hL_p(self.Pbar), steamTable.hV_p(self.Pbar)]

        else: 
            self.H += 10

    def minusH(self):
        meanH = self.getmeanH()
        meanH -= 10
        if meanH > steamTable.hL_p(self.Pbar) and meanH < steamTable.hV_p(self.Pbar):
            self.v = (meanH - steamTable.hL_p(self.Pbar)) / (steamTable.hV_p(self.Pbar) - steamTable.hL_p(self.Pbar))
        else: 
            self.H -= 10

    def minusVol(self):
        if self.v == 0:
            pass
        elif self.vapvol < 0.001:
            self.vapvol = 0
            self.liqvol = steamTable.vL_p(self.Pbar)
            self.v = 0
            self.Pbar = steamTable.psat_t(self.T)
            self.S = steamTable.sL_t(self.T)
        elif self.v < 1:
            self.vapvol -= 0.001
            vol1 = self.vapvol
            self.vapvol -= 0.001
            self.Pbar = self.Pbar*vol1/self.vapvol
            self.v = steamTable.x_ph(self.Pbar, self.getmeanH())
            if self.v < 1 and self.v > 0:
                self.S = [steamTable.sL_t(self.T), steamTable.sV_t(self.T)]
            else:
                self.S = steamTable.s_ph(self.Pbar, self.getmeanH())
        self.G = self.getmeanH() - (273.15+self.T)*self.getmeanS()

    def addVol(self):
        vol1 = self.vapvol
        self.vapvol += 0.001
        self.Pbar = self.Pbar*vol1/self.vapvol
        print(self.Pbar)
        self.v = steamTable.x_ph(self.Pbar, self.getmeanH())
        if self.v < 1 and self.v > 0:
            self.S = [steamTable.sL_t(self.T), steamTable.sV_t(self.T)]
        else:
            print(self.v, self.getmeanH())
            self.S = steamTable.s_ph(self.Pbar, self.getmeanH())
        self.G = self.getmeanH() - (273.15+self.T)*self.getmeanS()

    def addP(self):
        self.Pbar += 0.25

    def minusP(self):
        self.Pbar -= 0.25

    def calculate_fixP(self, type):  # includes the adding/subtracting
        if type == "add":
            self.addH()
        else:
            self.minusH()
        self.T = steamTable.t_ph(self.Pbar, self.getmeanH())
        if self.v < 1 and self.v > 0:
            self.S = [steamTable.sL_p(self.Pbar), steamTable.sV_p(self.Pbar)]
            self.vapvol = steamTable.vV_p(self.Pbar)*self.v
            self.liqvol = steamTable.vL_p(self.Pbar)*(1-self.v)
        else:
            self.S = steamTable.s_ph(self.Pbar, self.H)
            if self.v == 0:
                self.liqvol = steamTable.v_pt(self.Pbar, self.T)
            else:
                self.vapvol = steamTable.v_pt(self.Pbar, self.T)
        self.G = self.getmeanH() - (273.15+self.T)*self.getmeanS()
        

    def calculate_fixT(self, type):
        if type == "add":
            self.addVol()
        else:
            self.minusVol()


# a = Steam(50,102)
# a.instantiate()
# print(a.liqvol)