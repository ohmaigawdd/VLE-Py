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
import time


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
    # 3 methods for ideal PFR RTD:
    #   1) pfr = rtdpy.Pfr(tau = tau, dt=.01, time_end=100)
    #      plt.plot(pfr.time, pfr.exitage)
    #   2) imp = signal.unit_impulse(100)
    #      plt.plot(np.arange(0, 100), imp)

    def PFR(self):

        xdata = []
        ydata = []

        plt.show()
        
        axes = plt.gca()
        axes.set_xlim(0, 100)
        axes.set_ylim(0,1.4)
        line, = axes.plot(xdata, ydata, 'r-')
        plt.margins(0.1,0.1)
        plt.xlabel('Time')
        plt.ylabel('E',rotation=0)
        plt.grid(True)
        plt.title('PFR - Pulse: E against T')

        for i in range(100):
            if i != self.tau:
                xdata.append(i)
                ydata.append(0)
            else:
                xdata.append(i)
                ydata.append(1)
            line.set_xdata(xdata)
            line.set_ydata(ydata)
            plt.draw()
            plt.pause(1e-20)
            time.sleep(0.1)

        plt.show()

    def CSTR(self,n):
        #n = number of tanks, so we can allow them to select number of CSTRs
        xdata = []
        ydata = []
        #plt.show()

        axes = plt.gca()
        axes.set_xlim(0, 100)
        axes.set_ylim(0,0.05)
        line, = axes.plot(xdata, ydata, 'r-')
        plt.margins(0.1,0.1)
        plt.xlabel('Time')
        plt.ylabel('E',rotation=0)
        plt.grid(True)
        plt.title('nCSTR - Pulse: E against T')
        plt.legend()

        if type(n) == int:
            CSTR = rtdpy.Ncstr(tau=self.tau, n=n, dt=.01, time_end=100)
            for i in range(len(CSTR.time)):
                xdata.append(CSTR.time[i])
                ydata.append(CSTR.exitage[i])
                print(xdata)
                print(ydata)
                line.set_xdata(xdata)
                line.set_ydata(ydata)
                plt.draw()
                plt.pause(1e-20)
                time.sleep(0.1)
            #plt.show()
        if type(n) == list or type(n) == tuple:
            for n in n:
                CSTR = rtdpy.Ncstr(tau=self.tau, n=n, dt=.01, time_end=100)
                plt.plot(CSTR.time, CSTR.exitage, label=f"n={n}")
        else:
            pass


    def CSTR1(self,n):
       #n = number of tanks, so we can allow them to select number of CSTRs
        if type(n) == int:
            CSTR = rtdpy.Ncstr(tau=self.tau, n=n, dt=.01, time_end=100)
            plt.plot(CSTR.time, CSTR.exitage, label=f"n={n}")
        if type(n) == list or type(n) == tuple:
            for n in n:
                CSTR = rtdpy.Ncstr(tau=self.tau, n=n, dt=.01, time_end=100)
                plt.plot(CSTR.time, CSTR.exitage, label=f"n={n}")
        else:
            pass

        plt.xlabel('Time')
        plt.ylabel('E',rotation=0)
        plt.legend()
        plt.show()

    

a = pulse(50,1)
a.CSTR1(1)
