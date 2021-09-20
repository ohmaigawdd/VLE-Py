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
import math
import scipy
from scipy.integrate import simps
from scipy import signal
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly
import json
#Instasll rtdpy first! (TRY INSTALL MANUALLY INSTEAD OF PIP) idk why it installed older version
import rtdpy
import time

class RTD:
    
    def __init__(self,V_reactor,flow, type):
        types = ['pulse', 'step']
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
        PFR = rtdpy.Pfr(tau=self.tau, dt=.25, time_end=self.tau*2)
        x = PFR.time
        if self.type == 'pulse':
            y = PFR.exitage*25
            if not self.tau.is_integer():
                y.fill(0)
            # print(y)
        else:
            y = PFR.stepresponse*100
            y = np.where(y < 50, 0, y)
            y = np.where(y >= 50, 100, y)
        
        if not self.tau.is_integer():
            x = list(x)
            x.append(round(self.tau,2))
            # print(x)
            x = sorted(x)
            index = x.index(round(self.tau, 2))
            # print(index)
            y = list(y)
            y.insert(index, 100)
            # print(y)
        
        self.x = list(x).copy()
        self.y = list(y).copy()
        self.length = self.x.index(float("{:.2f}".format(self.tau)))

        fig = go.Figure(
            data=[go.Scatter(x=[], y=[], name = "PFR")],
            layout=go.Layout(template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(range=[0, self.tau*2], autorange=False),
                yaxis=dict(range=[0, 110], autorange=False, showticklabels=False),
                xaxis_title="Time (s)",
                yaxis_title = "Concentration (mol/m3)",
                title="Ideal PFR: Plot of Concentration against Time",
            ),
        )
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    def PFR_E(self):
        xdata, ydata = [], []
        PFR = rtdpy.Pfr(tau=self.tau, dt=.01, time_end=self.tau*2)
        x = PFR.time
        y = PFR.exitage
        # x = x[::25]
        # y = y[::25]

        frames = [go.Frame(data=[go.Scatter(x=[x[i] for i in range(len(x))], y=[y[i] for i in range(len(y))])])]
        
        fig = go.Figure(
            data=[go.Scatter(x=xdata, y=ydata, name = "PFR")],
            layout=go.Layout(template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(range=[0, self.tau*2], autorange=False),
                yaxis=dict(range=[0, 110], autorange=False),
                xaxis_title="Time (s)",
                yaxis_title = "Exit Age Function (1/s)",
                title="Ideal PFR: Plot of E against Time",
                updatemenus=[dict(
                bgcolor = 'grey',
                font = dict(color = 'black', family="Helvetica Neue, monospace", size = 12),
                type="buttons",
               buttons=[dict(label="Display",
                            method="animate",
                            args=[None, {"frame": {"duration": 0, 
                                    "redraw": False},
                            "fromcurrent": True, 
                            "transition": {"duration": 0}}])])]
            ), frames = frames
        )

        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    def PFR_F(self):
        xdata, ydata = [], []
        PFR = rtdpy.Pfr(tau=self.tau, dt=.01, time_end=self.tau*2)
        x = PFR.time
        y = PFR.stepresponse 
        # x = x[::25]
        # y = y[::25]

        frames = [go.Frame(data=[go.Scatter(x=[x[i] for i in range(len(x))], y=[y[i] for i in range(len(y))])])]

        
        fig = go.Figure(
            data=[go.Scatter(x=xdata, y=ydata, name = "PFR")],
            layout=go.Layout(template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(range=[0, self.tau*2], autorange=False),
                yaxis=dict(range=[0, max(y)*1.1], autorange=False),
                xaxis_title="Time (s)",
                yaxis_title = "Cumulative Distribution Function",
                title="Ideal PFR: Plot of F against Time",
                updatemenus=[dict(
                bgcolor = 'grey',
                font = dict(color = 'black', family="Helvetica Neue, monospace", size = 12),
                type="buttons",
                buttons=[dict(label="Display",
                            method="animate",
                            args=[None, {"frame": {"duration": 0, 
                                    "redraw": False},
                            "fromcurrent": True, 
                            "transition": {"duration": 0}}])])]
            ), frames = frames
        )

        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        

    def CSTR(self, n):
        CSTR = rtdpy.Ncstr(tau=self.tau, n = n, dt=.25, time_end=self.tau*5)
        # x = np.arange(0, self.tau*5, 0.25)
        x = CSTR.time
        y = []

        if self.type == "pulse":
            for t in x:
                c = (100/self.V_reactor)*math.exp((-1)*self.flow*t/self.V_reactor)
                y.append(c)
        else:
            for t in x:
                c = (100/self.flow)*(1-math.exp((-1)*(self.flow)*t/self.V_reactor))
                y.append(c)

        self.x = list(x).copy()
        self.y = list(y).copy()
        self.length = len(self.x)

        fig = go.Figure(
            data=[go.Scatter(x=[], y=[])],
            layout=go.Layout(template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(range=[0, self.tau*5], autorange=False),
                yaxis=dict(range=[0, max(y)*1.1], autorange=False),
                xaxis_title="Time (s)",
                yaxis_title = "Concentration (mol/m3)",
                title="Ideal CSTR: Plot of Concentration against Time"
            )
        )

        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    def CSTR_E(self,n):

        CSTR = rtdpy.Ncstr(tau=self.tau, n = n, dt=.01, time_end=self.tau*5)
        xdata, ydata = [], []
        x = CSTR.time
        y = CSTR.exitage
            
        frames = [go.Frame(data=[go.Scatter(x=[x[i] for i in range(len(x))], y=[y[i] for i in range(len(y))])])]

        fig = go.Figure(
            data=[go.Scatter(x=xdata, y=ydata)],
            layout=go.Layout(template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(range=[0, self.tau*5], autorange=False),
                yaxis=dict(range=[0, max(y)*1.1], autorange=False),
                xaxis_title="Time (s)",
                yaxis_title = "Exit Age Function (1/s)",
                title="Ideal CSTR: Plot of E against Time",
                updatemenus=[dict(
                bgcolor = 'grey',
                font = dict(color = 'black', family="Helvetica Neue, monospace", size = 12),
                type="buttons",
                buttons=[dict(label="Display",
                            method="animate",
                            args=[None, {"frame": {"duration": 0, 
                                    "redraw": False},
                            "fromcurrent": True, 
                            "transition": {"duration": 0}}])])]
            ), frames = frames
        )

        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


    def CSTR_F(self,n):

        CSTR = rtdpy.Ncstr(tau=self.tau, n = n, dt=.01, time_end=self.tau*5)
        xdata, ydata = [], []
        x = CSTR.time
        y = CSTR.stepresponse

        frames = [go.Frame(data=[go.Scatter(x=[x[i] for i in range(len(x))], y=[y[i] for i in range(len(y))])])]

        fig = go.Figure(
            data=[go.Scatter(x=xdata, y=ydata)],
            layout=go.Layout(template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(range=[0, self.tau*5], autorange=False),
                yaxis=dict(range=[0, max(y)*1.1], autorange=False),
                xaxis_title="Time (s)",
                yaxis_title = "Cumulative Distribution Function",
                title="Ideal CSTR: Plot of F against Time",
                updatemenus=[dict(
                bgcolor = 'grey',
                font = dict(color = 'black', family="Helvetica Neue, monospace", size = 12),
                type="buttons",
                buttons=[dict(label="Display",
                            method="animate",
                            args=[None, {"frame": {"duration": 0, 
                                    "redraw": False},
                            "fromcurrent": True, 
                            "transition": {"duration": 0}}])])]
            ), frames = frames
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

# a = RTD(50,2,'pulse')  # esp for PFR, ONLY INTEGER VALUES
# a.CSTR(1)

