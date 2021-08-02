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
        PFR = rtdpy.Pfr(tau=self.tau, dt=.01, time_end=self.tau*2)
        x = PFR.time
        if self.type == 'pulse':
            y = PFR.exitage
        else:
            y = PFR.stepresponse*100        
        x = x[::25]
        y = y[::25]
        self.x = list(x).copy()
        self.y = list(y).copy()
        
        fig = go.Figure(
            data=[go.Scatter(x=[], y=[], name = "PFR")],
            layout=go.Layout(template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(range=[0, self.tau*2], autorange=False),
                yaxis=dict(range=[0, max(y)*1.1], autorange=False),
                xaxis_title="Time (s)",
                yaxis_title = "Concentration",
                title="PFR: Plot of Concentration against Time",
            ),
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    def PFR_E(self):
        PFR = rtdpy.Pfr(tau=self.tau, dt=.01, time_end=self.tau*2)
        x = PFR.time
        y = PFR.exitage    
        x = x[::25]
        y = y[::25]

        frames = []

        for i in range(len(x)-1):
            fx = [x[i], x[i+1]]
            fy = [y[i], y[i+1]]
            frame = go.Frame(data=[go.Scatter(x=fx, y=fy)])
            frames.append(frame)
        
        fig = go.Figure(
            data=[go.Scatter(x=x, y=y, name = "PFR")],
            layout=go.Layout(template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(range=[0, self.tau*2], autorange=False),
                yaxis=dict(range=[0, max(y)*1.1], autorange=False),
                xaxis_title="Time (s)",
                yaxis_title = "Exit Age Function",
                title="PFR: Plot of E against Time",
                updatemenus=[dict(
                type="buttons",
                buttons=[dict(label="Play",
                            method="animate",
                            args=[None])])]
            ), frames = frames
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    def PFR_F(self):
        PFR = rtdpy.Pfr(tau=self.tau, dt=.01, time_end=self.tau*2)
        x = PFR.time
        y = PFR.stepresponse 
        x = x[::25]
        y = y[::25]

        frames = []

        for i in range(len(x)-1):
            fx = [x[i], x[i+1]]
            fy = [y[i], y[i+1]]
            frame = go.Frame(data=[go.Scatter(x=fx, y=fy)])
            frames.append(frame)
        
        fig = go.Figure(
            data=[go.Scatter(x=x, y=y, name = "PFR")],
            layout=go.Layout(template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(range=[0, self.tau*2], autorange=False),
                yaxis=dict(range=[0, max(y)*1.1], autorange=False),
                xaxis_title="Time (s)",
                yaxis_title = "Cumulative Distribution Function",
                title="PFR: Plot of F against Time",
                updatemenus=[dict(
                type="buttons",
                buttons=[dict(label="Play",
                            method="animate",
                            args=[None])])]
            ), frames = frames
        ),

        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    def CSTR(self, n):
        xdata = []
        ydata = []
        x = np.arange(0, self.tau*5, 0.25)
        y = []

        for t in x:
            c = (100/self.V_reactor)*math.exp((-1)*self.flow*t/self.V_reactor)
            y.append(c)

        self.x = list(x).copy()
        self.y = list(y).copy()

        fig = go.Figure(
            data=[go.Scatter(x=[], y=[], name = "n = " + str(n))],
            layout=go.Layout(template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(range=[0, self.tau*5], autorange=False),
                yaxis=dict(range=[0, max(y)*1.1], autorange=False),
                xaxis_title="Time (s)",
                yaxis_title = "Concentration",
                title="n CSTR: Plot of Concentration against Time, n=" + str(n)
            )
        )

        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    def CSTR_E(self,n):

        # x = np.arange(0, self.tau*5, 0.25)
        # y = []

        # for t in x:
        #     c = (100/self.V_reactor)*math.exp((-1)*self.flow*t/self.V_reactor)
        #     y.append(c)

        CSTR = rtdpy.Ncstr(tau=self.tau, n = n, dt=.01, time_end=self.tau*5)
        x = CSTR.time

        y = CSTR.exitage

        x = x[::25]
        y = y[::25]

        frames = []

        for i in range(len(x)-1):
            fx = [x[i], x[i+1]]
            fy = [y[i], y[i+1]]
            frame = go.Frame(data=[go.Scatter(x=fx, y=fy)])
            frames.append(frame)

        fig = go.Figure(
            data=[go.Scatter(x=x, y=y, name = "n = " + str(n))],
            layout=go.Layout(template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(range=[0, self.tau*5], autorange=False),
                yaxis=dict(range=[0, max(y)*1.1], autorange=False),
                xaxis_title="Time (s)",
                yaxis_title = "Exit Age Function",
                title="n CSTR: Plot of E against Time, n=" + str(n),
                updatemenus=[dict(
                type="buttons",
                buttons=[dict(label="Play",
                            method="animate",
                            args=[None])])]
            ), frames = frames
        )

        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


    def CSTR_F(self,n):

        # x = np.arange(0, self.tau*5, 0.25)
        # y = []

        # for t in x:
        #     c = (100/self.V_reactor)*math.exp((-1)*self.flow*t/self.V_reactor)
        #     y.append(c)

        CSTR = rtdpy.Ncstr(tau=self.tau, n = n, dt=.01, time_end=self.tau*5)
        x = CSTR.time
        y = CSTR.stepresponse
        x = x[::25]
        y = y[::25]

        frames = []

        for i in range(len(x)-1):
            fx = [x[i], x[i+1]]
            fy = [y[i], y[i+1]]
            frame = go.Frame(data=[go.Scatter(x=fx, y=fy)])
            frames.append(frame)

        fig = go.Figure(
            data=[go.Scatter(x=x, y=y, name = "n = " + str(n))],
            layout=go.Layout(template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(range=[0, self.tau*5], autorange=False),
                yaxis=dict(range=[0, max(y)*1.1], autorange=False),
                xaxis_title="Time (s)",
                yaxis_title = "Cumulative Distribution Function",
                title="n CSTR: Plot of F against Time, n=" + str(n),
                updatemenus=[dict(
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

# a = RTD(50,2,'pulse')  # esp for PFR, ONLY INTEGER VALUES
# a.CSTR(1)
