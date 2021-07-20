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
import plotly.graph_objects as go
import json
import plotly
#Instasll rtdpy first! (TRY INSTALL MANUALLY INSTEAD OF PIP) idk why it installed older version
import rtdpy
import time

types = ['pulse', 'step']

class RTD:
    def __init__(self,V_reactor,flow, type):
        if type in types:
            self.V_reactor = V_reactor
            self.flow = flow
            self.tau = self.V_reactor / self.flow
            self.type = type

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
        PFR = rtdpy.Pfr(tau=self.tau, dt=.01, time_end=self.tau*2)
        x = PFR.time
        if self.type == 'pulse':
            y = PFR.exitage
        else:
            y = PFR.stepresponse        
        x = x[::25]
        y = y[::25]
        frames = []
        for i in range(len(x)-1):
            frame = go.Frame(data=[go.Scatter(x=[x[i] for i in range(i)], y=[y[i] for i in range(i)], mode = 'lines')])
            frames.append(frame)

        fig = go.Figure(
            data=[go.Scatter(x=xdata, y=ydata, name = "PFR")],
            layout=go.Layout(template='plotly_dark',
                xaxis=dict(range=[0, self.tau*2], autorange=False),
                yaxis=dict(range=[0, max(y)*1.1], autorange=False),
                xaxis_title="Time",
                yaxis_title = "Exit Age Function",
                title="PFR E against time",
                updatemenus=[dict(
                    bgcolor = 'grey',
                    font = dict(color = 'black', family="Helvetica Neue, monospace", size = 12),
                    type="buttons",
                    buttons=[dict(label="Play",
                                method="animate",
                                args = [None, {"frame": {"duration": 50, 
                                                            "redraw": False},
                                                                    "fromcurrent": True, 
                                                                    "transition": {"duration": 0}}])])],
                    legend=dict(title='Legend',
                                orientation="h",
                                yanchor="bottom",
                                y=1.02,
                                xanchor="right",
                                x=1
            ),
            ),
            frames=frames
        )

    def CSTR(self,n):

        xdata = []
        ydata = []
        CSTR = rtdpy.Ncstr(tau=self.tau, n = n, dt=.01, time_end=self.tau*5)
        x = CSTR.time
        if self.type == 'pulse':
            y = CSTR.exitage
        else:
            y = CSTR.stepresponse
        x = x[::25]
        y = y[::25]
        frames = []
        for i in range(len(x)-1):
            frame = go.Frame(data=[go.Scatter(x=[x[i] for i in range(i)], y=[y[i] for i in range(i)], mode = 'lines')])
            frames.append(frame)

        fig = go.Figure(
            data=[go.Scatter(x=xdata, y=ydata, name = "n = " + str(n))],
            layout=go.Layout(template='plotly_dark',
                xaxis=dict(range=[0, self.tau*5], autorange=False),
                yaxis=dict(range=[0, max(y)*1.1], autorange=False),
                xaxis_title="Time",
                yaxis_title = "Exit Age Function",
                title="nCSTR E against time, n=" + str(n),
                updatemenus=[dict(
                    bgcolor = 'grey',
                    font = dict(color = 'black', family="Helvetica Neue, monospace", size = 12),
                    type="buttons",
                    buttons=[dict(label="Play",
                                method="animate",
                                args = [None, {"frame": {"duration": 50, 
                                                            "redraw": False},
                                                                    "fromcurrent": True, 
                                                                    "transition": {"duration": 0}}])])],
                    legend=dict(title='Legend',
                                orientation="h",
                                yanchor="bottom",
                                y=1.02,
                                xanchor="right",
                                x=1
            ),
            ),
            frames=frames
        )

    def generate(self):
        return json.dumps(self.fig, cls=plotly.utils.PlotlyJSONEncoder)

    

        # elif type(n) == list or type(n) == tuple:
        #     CSTR = {}
        #     x = {}
        #     y = {}
        #     xdata= [[] for i in range(len(n))]
        #     ydata= [[] for i in range(len(n))]
        #     handles = [("n = " + str(i)) for i in n]

        #     for count, elem in enumerate(n):
        #         CSTR[elem] = rtdpy.Ncstr(tau=self.tau, n=elem, dt=.01, time_end=5*self.tau)
        #         x[elem] = CSTR[elem].time[::100]
        #         if self.type == "pulse":
        #             y[elem] = CSTR[elem].exitage[::100]
        #         else:
        #             y[elem] = CSTR[elem].stepresponse[::100]

        #     for i in range(len(x[n[0]][0:200000])):
        #         for j in range(len(n)):   
        #             xdata[j].append(x[n[j]][i])
        #             ydata[j].append(y[n[j]][i])
        #             line.set_xdata(xdata)
        #             line.set_ydata(ydata)
        #         for j in range(len(n)):
        #             plt.plot(xdata[j], ydata[j])
                    

        #         plt.pause(1e-20)
        #     plt.show()
        # else:
        #     pass

# a = RTD(50,2,'step')  # esp for PFR, ONLY INTEGER VALUES
# a.PFR()
