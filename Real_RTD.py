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
from RTD import RTD

class Real_RTD:
    
    def __init__(self,V_reactor,flow, type):
        types = ['pulse', 'step']
        if type in types:
            self.V_reactor = V_reactor
            self.flow = flow
            self.tau = self.V_reactor / self.flow
            self.type = type
            #bypass and deadvol are in fractions
            self.bypass = 0.2
            self.deadvol = 10
            self.bypass_tau = self.V_reactor / ((1-self.bypass)*self.flow)
            self.deadvol_tau = (self.V_reactor-self.deadvol) / self.flow
            self.ideal = RTD(20,2,self.type)

    #rtdpy not as nice as signal.unit_impulse for PFR
    # 3 methods for ideal PFR RTD:
    #   1) pfr = rtdpy.Pfr(tau = tau, dt=.01, time_end=100)
    #      plt.plot(pfr.time, pfr.exitage)
    #   2) imp = signal.unit_impulse(100)
    #      plt.plot(np.arange(0, 100), imp)

    def PFR_bypass(self):
        xdata = []
        ydata = []
        PFR_Real = rtdpy.Pfr(tau=self.bypass_tau, dt=.25, time_end=self.tau*2)
        x = PFR_Real.time

        if self.type == 'pulse':
            y = PFR_Real.exitage*25*(1-self.bypass)
            y[0] = self.bypass*100 #bypass amount
            if not self.bypass_tau.is_integer():
                y.fill(0)
            # print(y)
        else:
            y = PFR_Real.stepresponse*100
            y = np.where(y < 50, 20, y)
            y = np.where(y >= 50, 100, y)
        
        if not self.bypass_tau.is_integer():
            x = list(x)
            x.append(round(self.bypass_tau,2))
            # print(x)
            x = sorted(x)
            index = x.index(round(self.bypass_tau, 2))
            # print(index)
            y = list(y)
            y.insert(index, 100)
            # print(y)
        
        self.x = list(x).copy()
        self.y = list(y).copy()
        self.length = self.x.index(float("{:.2f}".format(self.bypass_tau)))
        self.length2 = len(self.x)

        fig = go.Figure(
            data=[go.Scatter(x=[], y=[], name = "PFR_Real")],
            layout=go.Layout(template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(range=[0, self.tau*2], autorange=False),
                yaxis=dict(range=[0, max(y)*1.1], autorange=False),
                xaxis_title="Time (s)",
                yaxis_title = "Concentration",
                title="Real PFR: Plot of Concentration against Time",
            ),
        )

        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    def PFR_bypass_E(self):
        xdata, ydata = [], []
        PFR_Real = rtdpy.Pfr(tau=self.bypass_tau, dt=.01, time_end=self.tau*2)
        x = PFR_Real.time
        y = PFR_Real.exitage*(1-self.bypass)
        y[0] = self.bypass*100
        # x = x[::25]
        # y = y[::25]

        PFR_Ideal = rtdpy.Pfr(tau=self.tau, dt=.01, time_end=self.tau*2)
        x1 = PFR_Ideal.time
        y1 = PFR_Ideal.exitage

        frames = [go.Frame(data=[go.Scatter(x=[x[i] for i in range(len(x))], y=[y[i] for i in range(len(y))])])]
        
        fig = go.Figure(
            data=[go.Scatter(x=xdata, y=ydata, name="Real", showlegend=True),go.Scatter(x=x1, y=y1, name = "Ideal", showlegend=True)],
            layout=go.Layout(template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(range=[0, self.tau*2], autorange=False),
                yaxis=dict(range=[0, max(y1)*1.1], autorange=False),
                xaxis_title="Time (s)",
                yaxis_title = "Exit Age Function",
                title="PFR: Plot of E against Time",
                legend=dict(title = 'Legend', orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                updatemenus=[dict(
                bgcolor = 'grey',
                font = dict(color = 'black', family="Helvetica Neue, monospace", size = 12),
                type="buttons",
               buttons=[dict(label="Display",
                            method="animate",
                            args=[None, {"frame": {"duration": 0, 
                                    "redraw": True},
                            "fromcurrent": True, 
                            "transition": {"duration": 0}}])])]
            ), frames = frames
        )

        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    def PFR_bypass_F(self):
        xdata, ydata = [], []
        PFR_Real = rtdpy.Pfr(tau=self.bypass_tau, dt=.01, time_end=self.tau*2)
        x = PFR_Real.time
        y = PFR_Real.stepresponse
        #Temp solution for single bypass at start only
        y = np.where(y <= (1-self.bypass), self.bypass, y)
        y = np.where(y > (1-self.bypass), 1, y)
        # x = x[::25]
        # y = y[::25]

        PFR_Ideal = rtdpy.Pfr(tau=self.tau, dt=.01, time_end=self.tau*2)
        x1 = PFR_Ideal.time
        y1 = PFR_Ideal.stepresponse 

        frames = [go.Frame(data=[go.Scatter(x=[x[i] for i in range(len(x))], y=[y[i] for i in range(len(y))])])]

        fig = go.Figure(
            data=[go.Scatter(x=xdata, y=ydata, name="Real", showlegend=True),go.Scatter(x=x1, y=y1, name = "Ideal", showlegend=True)],
            layout=go.Layout(template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(range=[0, self.tau*2], autorange=False),
                yaxis=dict(range=[0, max(y)*1.1], autorange=False),
                xaxis_title="Time (s)",
                yaxis_title = "Cumulative Distribution Function",
                title="PFR: Plot of F against Time",
                legend=dict(title = 'Legend', orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                updatemenus=[dict(
                bgcolor = 'grey',
                font = dict(color = 'black', family="Helvetica Neue, monospace", size = 12),
                type="buttons",
                buttons=[dict(label="Display",
                            method="animate",
                            args=[None, {"frame": {"duration": 0, 
                                    "redraw": True},
                            "fromcurrent": True, 
                            "transition": {"duration": 0}}])])]
            ), frames = frames
        )

        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
      
    def PFR_deadvol(self):
        xdata = []
        ydata = []
        PFR_Real = rtdpy.Pfr(tau=self.deadvol_tau, dt=.25, time_end=self.tau*2)
        x = PFR_Real.time
        if self.type == 'pulse':
            y = PFR_Real.exitage*25
            if not self.deadvol_tau.is_integer():
                y.fill(0)
            # print(y)
        else:
            y = PFR_Real.stepresponse*100
            y = np.where(y < 50, 0, y)
            y = np.where(y >= 50, 100, y)
        
        if not self.deadvol_tau.is_integer():
            x = list(x)
            x.append(round(self.deadvol_tau,2))
            # print(x)
            x = sorted(x)
            index = x.index(round(self.deadvol_tau, 2))
            # print(index)
            y = list(y)
            y.insert(index, 100)
            # print(y)
        
        self.x = list(x).copy()
        self.y = list(y).copy()
        self.length = self.x.index(float("{:.2f}".format(self.bypass_tau)))
        self.length2 = len(self.x)

        fig = go.Figure(
            data=[go.Scatter(x=[], y=[], name = "PFR Real")],
            layout=go.Layout(template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(range=[0, self.tau*2], autorange=False),
                yaxis=dict(range=[0, max(y)*1.1], autorange=False),
                xaxis_title="Time (s)",
                yaxis_title = "Concentration",
                title="Real PFR: Plot of Concentration against Time",
            ),
        )
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    def PFR_deadvol_E(self):
        xdata, ydata = [], []
        PFR_Real = rtdpy.Pfr(tau=self.deadvol_tau, dt=.01, time_end=self.tau*2)
        x = PFR_Real.time
        y = PFR_Real.exitage
        # x = x[::25]
        # y = y[::25]

        PFR_Ideal = rtdpy.Pfr(tau=self.tau, dt=.01, time_end=self.tau*2)
        x1 = PFR_Ideal.time
        y1 = PFR_Ideal.exitage

        frames = [go.Frame(data=[go.Scatter(x=[x[i] for i in range(len(x))], y=[y[i] for i in range(len(y))])])]
        
        fig = go.Figure(
            data=[go.Scatter(x=xdata, y=ydata, name="Real", showlegend=True), go.Scatter(x=x1, y=y1, name = "Ideal", showlegend=True)],
            layout=go.Layout(template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(range=[0, self.tau*2], autorange=False),
                yaxis=dict(range=[0, max(y)*1.1], autorange=False),
                xaxis_title="Time (s)",
                yaxis_title = "Exit Age Function",
                title="PFR: Plot of E against Time",
                legend=dict(title = 'Legend', orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                updatemenus=[dict(
                bgcolor = 'grey',
                font = dict(color = 'black', family="Helvetica Neue, monospace", size = 12),
                type="buttons",
               buttons=[dict(label="Display",
                            method="animate",
                            args=[None, {"frame": {"duration": 0, 
                                    "redraw": True},
                            "fromcurrent": True, 
                            "transition": {"duration": 0}}])])]
            ), frames = frames
        )

        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    def PFR_deadvol_F(self):
        xdata, ydata = [], []
        PFR_Real = rtdpy.Pfr(tau=self.deadvol_tau, dt=.01, time_end=self.tau*2)
        x = PFR_Real.time
        y = PFR_Real.stepresponse
        # x = x[::25]
        # y = y[::25]

        PFR_Ideal = rtdpy.Pfr(tau=self.tau, dt=.01, time_end=self.tau*2)
        x1 = PFR_Ideal.time
        y1 = PFR_Ideal.stepresponse 

        frames = [go.Frame(data=[go.Scatter(x=[x[i] for i in range(len(x))], y=[y[i] for i in range(len(y))])])]
        
        fig = go.Figure(
            data=[go.Scatter(x=xdata, y=ydata, name="Real", showlegend=True), go.Scatter(x=x1, y=y1, name = "Ideal", showlegend=True)],
            layout=go.Layout(template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(range=[0, self.tau*2], autorange=False),
                yaxis=dict(range=[0, max(y)*1.1], autorange=False),
                xaxis_title="Time (s)",
                yaxis_title = "Cumulative Distribution Function",
                title="PFR: Plot of F against Time",
                legend=dict(title = 'Legend', orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                updatemenus=[dict(
                bgcolor = 'grey',
                font = dict(color = 'black', family="Helvetica Neue, monospace", size = 12),
                type="buttons",
                buttons=[dict(label="Display",
                            method="animate",
                            args=[None, {"frame": {"duration": 0, 
                                    "redraw": True},
                            "fromcurrent": True, 
                            "transition": {"duration": 0}}])])]
            ), frames = frames
        )

        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    def CSTR_bypass(self, n):
        CSTR = rtdpy.Ncstr(tau=self.bypass_tau, n = n, dt=.25, time_end=self.tau*5)
        # x = np.arange(0, self.tau*5, 0.25)
        x = CSTR.time
        y = []

        if self.type == "pulse":
            for t in x:
                #need to check if Concentration curve is liddat
                c = (100/self.V_reactor)*math.exp((-1)*t/self.bypass_tau)
                y.append(c)
        else:
            for t in x:
                #need to check if Concentration curve is liddat
                c = (100/self.flow)*(1-math.exp((-1)*t/self.bypass_tau))
                y.append(c)

        self.x = list(x).copy()
        self.y = list(y).copy()
        self.length = self.x.index(float("{:.2f}".format(self.tau)))
        self.length2 = len(self.x)

        fig = go.Figure(
            data=[go.Scatter(x=[], y=[], name = "n = " + str(n))],
            layout=go.Layout(template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(range=[0, self.tau*5], autorange=False),
                yaxis=dict(range=[0, max(y)*1.1], autorange=False),
                xaxis_title="Time (s)",
                yaxis_title = "Concentration",
                title="n Real CSTR: Plot of Concentration against Time, n=" + str(n)
            )
        )

        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    def CSTR_bypass_E(self,n):

        # x = np.arange(0, self.tau*5, 0.25)
        # y = []

        # for t in x:
        #     c = (100/self.V_reactor)*math.exp((-1)*self.flow*t/self.V_reactor)
        #     y.append(c)

        CSTR_Real = rtdpy.Ncstr(tau=self.bypass_tau, n = n, dt=.01, time_end=self.tau*5)
        xdata, ydata = [], []
        x = CSTR_Real.time
        x = np.append(x, [self.tau*5+1])
        y = [self.bypass*self.flow/self.flow]

        for t in x:
            e = ((1-self.bypass)*self.flow)**2/(self.V_reactor*self.flow)*math.exp((-1)*t/self.deadvol_tau)
            y.append(e)

        CSTR_Ideal = rtdpy.Ncstr(tau=self.tau, n = n, dt=.01, time_end=self.tau*5)
        x1 = CSTR_Ideal.time
        y1 = CSTR_Ideal.exitage

        # x = x[::25]
        # y = y[::25]

        # frames = []

        # for i in range(len(x)-1):
        #     fx = [x[j] for j in range(i)]
        #     fy = [y[j] for j in range(i)]
        #     frame = go.Frame(data=[go.Scatter(x=fx, y=fy)])
        #     frames.append(frame)
            
        frames = [go.Frame(data=[go.Scatter(x=[x[i] for i in range(len(x))], y=[y[i] for i in range(len(y))])])]

        fig = go.Figure(
            data=[go.Scatter(x=xdata, y=ydata, name="Real", showlegend=True), go.Scatter(x=x1, y=y1, name = "Ideal", showlegend=True)],
            layout=go.Layout(template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(range=[0, self.tau*5], autorange=False),
                yaxis=dict(range=[0, max(y)*1.1], autorange=False),
                xaxis_title="Time (s)",
                yaxis_title = "Exit Age Function",
                title="n CSTR: Plot of E against Time, n=" + str(n),
                legend=dict(title = 'Legend', orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                updatemenus=[dict(
                bgcolor = 'grey',
                font = dict(color = 'black', family="Helvetica Neue, monospace", size = 12),
                type="buttons",
                buttons=[dict(label="Display",
                            method="animate",
                            args=[None, {"frame": {"duration": 0, 
                                    "redraw": True},
                            "fromcurrent": True, 
                            "transition": {"duration": 0}}])])]
            ), frames = frames
        )

        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    def CSTR_bypass_F(self,n):

        # x = np.arange(0, self.tau*5, 0.25)
        # y = []

        # for t in x:
        #     c = (100/self.V_reactor)*math.exp((-1)*self.flow*t/self.V_reactor)
        #     y.append(c)

        CSTR_Real = rtdpy.Ncstr(tau=self.deadvol_tau, n = n, dt=.01, time_end=self.tau*5)
        xdata, ydata = [], []
        timelost = []
        x = CSTR_Real.time
        y = [self.bypass*self.flow/self.flow]
        data = CSTR_Real.stepresponse
        for val in data:
            if val >= y[0]:
                y.append(val)
            else:
                pass

        CSTR_Ideal = rtdpy.Ncstr(tau=self.tau, n = n, dt=.01, time_end=self.tau*5)
        x1 = CSTR_Ideal.time
        y1 = CSTR_Ideal.stepresponse
        
        #Will lose the first few t so need to somehow extrapolate graph
        #while len(y) < len(x):
        #    y.append(1)

        # x = x[::25]
        # y = y[::25]

        # frames = []

        # for i in range(len(x)-1):
        #     fx = [x[j] for j in range(i)]
        #     fy = [y[j] for j in range(i)]
        #     frame = go.Frame(data=[go.Scatter(x=fx, y=fy)])
        #     frames.append(frame)

        frames = [go.Frame(data=[go.Scatter(x=[x[i] for i in range(len(x))], y=[y[i] for i in range(len(y))])])]

        fig = go.Figure(
            data=[go.Scatter(x=xdata, y=ydata, name="Real", showlegend=True), go.Scatter(x=x1, y=y1, name = "Ideal", showlegend=True)],
            layout=go.Layout(template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(range=[0, self.tau*5], autorange=False),
                yaxis=dict(range=[0, max(y)*1.1], autorange=False),
                xaxis_title="Time (s)",
                yaxis_title = "Cumulative Distribution Function",
                title="n CSTR: Plot of F against Time, n=" + str(n),
                legend=dict(title = 'Legend', orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                updatemenus=[dict(
                bgcolor = 'grey',
                font = dict(color = 'black', family="Helvetica Neue, monospace", size = 12),
                type="buttons",
                buttons=[dict(label="Display",
                            method="animate",
                            args=[None, {"frame": {"duration": 0, 
                                    "redraw": True},
                            "fromcurrent": True, 
                            "transition": {"duration": 0}}])])]
            ), frames = frames
        )

        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    def CSTR_deadvol(self, n):
        CSTR = rtdpy.Ncstr(tau=self.tau, n = n, dt=.25, time_end=self.tau*5)
        # x = np.arange(0, self.tau*5, 0.25)
        x = CSTR.time
        y = []

        if self.type == "pulse":
            for t in x:
                c = (100/self.V_reactor)*math.exp((-1)*t/self.deadvol_tau)
                y.append(c)
        else:
            for t in x:
                c = (100/self.flow)*(1-math.exp((-1)*t/self.deadvol_tau))
                y.append(c)

        self.x = list(x).copy()
        self.y = list(y).copy()
        self.length = len(self.x)

        fig = go.Figure(
            data=[go.Scatter(x=[], y=[], name = "n = " + str(n))],
            layout=go.Layout(template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(range=[0, self.tau*5], autorange=False),
                yaxis=dict(range=[0, max(y)*1.1], autorange=False),
                xaxis_title="Time (s)",
                yaxis_title = "Concentration",
                title="n Real CSTR: Plot of Concentration against Time, n=" + str(n)
            )
        )

        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    def CSTR_deadvol_E(self,n):

        # x = np.arange(0, self.tau*5, 0.25)
        # y = []

        # for t in x:
        #     c = (100/self.V_reactor)*math.exp((-1)*self.flow*t/self.V_reactor)
        #     y.append(c)

        CSTR_Real = rtdpy.Ncstr(tau=self.deadvol_tau, n = n, dt=.01, time_end=self.tau*5)
        xdata, ydata = [], []
        x = CSTR_Real.time
        y = CSTR_Real.exitage

        CSTR_Ideal = rtdpy.Ncstr(tau=self.tau, n = n, dt=.01, time_end=self.tau*5)
        x1 = CSTR_Ideal.time
        y1 = CSTR_Ideal.exitage

        # x = x[::25]
        # y = y[::25]
        # frames = []

        # for i in range(len(x)-1):
        #     fx = [x[j] for j in range(i)]
        #     fy = [y[j] for j in range(i)]
        #     frame = go.Frame(data=[go.Scatter(x=fx, y=fy)])
        #     frames.append(frame)
            
        frames = [go.Frame(data=[go.Scatter(x=[x[i] for i in range(len(x))], y=[y[i] for i in range(len(y))])])]

        fig = go.Figure(
            data=[go.Scatter(x=xdata, y=ydata, name="Real", showlegend=True), go.Scatter(x=x1, y=y1, name = "Ideal", showlegend=True)],
            layout=go.Layout(template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(range=[0, self.tau*5], autorange=False),
                yaxis=dict(range=[0, max(y)*1.1], autorange=False),
                xaxis_title="Time (s)",
                yaxis_title = "Exit Age Function",
                title="n CSTR: Plot of E against Time, n=" + str(n),
                legend=dict(title = 'Legend', orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                updatemenus=[dict(
                bgcolor = 'grey',
                font = dict(color = 'black', family="Helvetica Neue, monospace", size = 12),
                type="buttons",
                buttons=[dict(label="Display",
                            method="animate",
                            args=[None, {"frame": {"duration": 0, 
                                    "redraw": True},
                            "fromcurrent": True, 
                            "transition": {"duration": 0}}])])]
            ), frames = frames
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    def CSTR_deadvol_F(self,n):

        # x = np.arange(0, self.tau*5, 0.25)
        # y = []

        # for t in x:
        #     c = (100/self.V_reactor)*math.exp((-1)*self.flow*t/self.V_reactor)
        #     y.append(c)

        CSTR_Real = rtdpy.Ncstr(tau=self.deadvol_tau, n = n, dt=.01, time_end=self.tau*5)
        xdata, ydata = [], []
        x = CSTR_Real.time
        y = CSTR_Real.stepresponse

        CSTR_Ideal = rtdpy.Ncstr(tau=self.tau, n = n, dt=.01, time_end=self.tau*5)
        x1 = CSTR_Ideal.time
        y1 = CSTR_Ideal.stepresponse
        
        frames = [go.Frame(data=[go.Scatter(x=[x[i] for i in range(len(x))], y=[y[i] for i in range(len(y))], name="Real")])]

        fig = go.Figure(
            data=[go.Scatter(x=xdata, y=ydata, showlegend=True), go.Scatter(x=x1, y=y1, name = "Ideal", showlegend=True)],
            layout=go.Layout(template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(range=[0, self.tau*5], autorange=False),
                yaxis=dict(range=[0, max(y)*1.1], autorange=False),
                xaxis_title="Time (s)",
                yaxis_title = "Cumulative Distribution Function",
                title="n CSTR: Plot of F against Time, n=" + str(n),
                legend=dict(title = 'Legend', orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                updatemenus=[dict(
                bgcolor = 'grey',
                font = dict(color = 'black', family="Helvetica Neue, monospace", size = 12),
                type="buttons",
                buttons=[dict(label="Display",
                            method="animate",
                            args=[None, {"frame": {"duration": 0, 
                                    "redraw": True},
                            "fromcurrent": True, 
                            "transition": {"duration": 0}}])])]
            ), frames = frames)
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    # def CSTRstep(self, n):
    #     xdata = []
    #     ydata = []
    #     ysum = [0]
    #     CSTR = rtdpy.Ncstr(tau=self.tau, n = n, dt=.01, time_end=self.tau*5)
    #     x = CSTR.time
    #     if self.type == 'pulse':
    #         y = CSTR.exitage
    #     else:
    #         y = CSTR.stepresponse
    #     x = x[::25]
    #     y = y[::25]
    #     for i in range(len(x)):
    #         ysum.append(ysum[-1] + y[i])
    #     self.x = list(x).copy()
    #     self.y = list(ysum).copy()

    #     fig = go.Figure(
    #         data=[go.Scatter(x=xdata, y=ysum, name = "n = " + str(n))],
    #         layout=go.Layout(template='plotly_dark',
    #             paper_bgcolor='rgba(0,0,0,0)',
    #             xaxis=dict(range=[0, self.tau*5], autorange=False),
    #             yaxis=dict(range=[0, max(y)*1.1], autorange=False),
    #             xaxis_title="Time (s)",
    #             yaxis_title = "Exit Age Function",
    #             title="n CSTR: Plot of E against Time, n=" + str(n),
    #         )
    #     )
    #     # self.fig = fig
    #     fig.show()


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

#a = Real_RTD(20,2,'step')  # esp for PFR, ONLY INTEGER VALUES
#a.CSTR_bypass_F(1)

