'''Flow pattern in Ideal Reactors

Objective: 
Demonstrate response-stimuli experiment (RTD)
Visualize flow (mixing) behaviour in ideal reactor

Experiment:
1. Choose Ideal Reactor (PFR/CSTR)
2. Choose Experiment parameters:
    Tracer input (Step: Concentration / Pulse: Amount)
    Flow Rate
3. Measure exit concentration
4. Plot concentration profile
'''
import numpy as np
import scipy
from scipy.integrate import simps
from scipy import signal
import matplotlib.pyplot as plt
import plotly as plot
#Instasll rtdpy first! (TRY INSTALL MANUALLY INSTEAD OF PIP) idk why it installed older version
import rtdpy

class pulse:
    def __init__(self,V_reactor,flow):
        self.V_reactor = V_reactor
        self.flow = flow
        self.tau = self.V_reactor / self.flow

    '''
    def exptRTD(self,t,c):
        t_data = t.astype(float)
        C_data = c.astype(float)
        def fun_data(t):
             return np.interp(t, t_data, C_data, left=0, right=0)
        rtdmodel_data = rtdpy.Arbitrary(fun_data, dt=.01, time_end=20)

        # Plot arbitrary models
        plt.plot(rtdmodel_data.time, rtdmodel_data.exitage, label="Data RTD")
        plt.xlabel('Time')
        plt.ylabel('Exit Age Function')
        plt.legend()
        print(f"Data RTD mean residence time: {rtdmodel_data.mrt():.1f}")
        #Data RTD mean residence time: 1.7
        plt.show()
    '''

    #rtdpy not as nice as signal.unit_impulse for PFR
    #pfr = rtdpy.Pfr(tau = tau, dt=.01, time_end=100)
    #plt.plot(pfr.time, pfr.exitage)
    def PFR(self):
        imp = signal.unit_impulse(100, int(self.tau))
        plt.plot(np.arange(0, 100), imp)

        plt.margins(0.1,0.1)
        plt.xlabel('Time')
        plt.ylabel('E',rotation=0)
        plt.grid(True)
        plt.show()

    def CSTR(self,n):
        #n = number of tanks, so we can allow them to select number of CSTRs
        if type(n) == int:
            CSTR = rtdpy.Ncstr(tau=self.tau, n=n, dt=.01, time_end=100)
            plt.plot(CSTR.time, CSTR.exitage, label=f"n={n}")
        if type(n) == list or type(n) == tuple:
            for n in n:
                CSTR = rtdpy.Ncstr(tau=self.tau, n=n, dt=.01, time_end=100)
                plt.plot(CSTR.time, CSTR.exitage, label=f"n={n}")
        else:
            print("lmao list or int plz")

        plt.xlabel('Time')
        plt.ylabel('E')
        plt.legend()
        plt.show()

a = pulse(50,1)
t = np.array([0, 1, 2, 3, 4, 5])
C = np.array([0.5, 0.2, 0.3, 0.15, 0.1, 0.0])
a.CSTR((2,))

