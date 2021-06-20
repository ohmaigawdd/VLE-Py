import math
import warnings
from scipy import optimize
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
        pass

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


    def getPureComponentBoilingTemp(self, component, pressure):  # pressure is to be in psia. ouput in CELCIUS
        if component in self.components:
            coeff = RachfordRice.McWilliam_Coeff[component]
            aT1 = coeff[0]
            aT2 = coeff[1]
            aT3 = coeff[2]
            ap1 = coeff[3]
            ap2 = coeff[4]
            ap3 = coeff[5]
            
            def equation(T):  # solve for T to make K = 1 
                lnK = aT1/(T**2) + aT2/T + aT3 + ap1*math.log(pressure) + ap2/(pressure**2) + ap3/pressure # in psia and rankine
                K = math.exp(lnK)
                return K - 1

            try:
                result = (solve(equation, 650).item(0) - 491.67) *(5/9)
                print(equation(result*(9/5)+491.67))
                return result
            except ValueError:
                return None

    def getPureComponentBoilingPressure(self, component, temperature):  # temperature is to be in rankine. output in PSIA
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

            with warnings.catch_warnings():
                warnings.filterwarnings('error')

                try:
                    # result = solve(equation, 8).item(0)
                    result = optimize.newton(equation, 1)
                    return result
                except RuntimeWarning or ValueError:
                    return None
        

    
# # Test functions
# test = RachfordRice(2, -100, 500, ['n-Octane','n-Octane'], [0.3,0.7])
# print(test.params['Tmax'])
# print(test.get_dets())
# print(test.x)
# print(test.y)
# print(test.v)
# print(test.checkState())

## Testing add_chemical function
# dict = {'n-Decane': [0, -9760.45703, 13.80354, -0.71470, 0, 0, 5.79]}
# test.add_chemical(dict)
# print(test.McWilliam_Coeff)

test = RachfordRice(2, 50, 105, ['n-Octane','Ethane'], [0.3,0.7])
print(test.getPureComponentBoilingTemp('Ethane', 15.23)) 
print(test.getPureComponentBoilingPressure('Ethane', 581.67))
print(test.getPureComponentBoilingPressure('n-Octane', 581.67))
