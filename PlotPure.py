from VLECalculations import RachfordRice, Antoine, VanDerWaalsEOS
import plotly
import json
import plotly.graph_objects as go
import numpy as np

# Params is a dictionary with divID, Tmin/max, Pmin/max, numpoints
#self.params = params

#rename plot_binary
class plotPure:
    def __init__(self,sys):
        # n,T,P, components, z in RR 
        self.sys = sys
        
    def create_plot(self):
        self.fig = go.Figure()
        self.fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)')

    def create_isotherm(self):
        self.create_plot()
        P_points, V_points = [],[]
        P = self.sys.P
        T = self.sys.C2K()
        R = 8.314

        for v in np.arange(0.05, 3.5, 0.01):
            p = (R*T/(v-self.sys.get_b()))-self.sys.get_a() / (v**2)
            P_points.append(p)
            V_points.append(v)

        self.fig.update_layout(
            title="<b>Van der Waals curves " + str(self.sys.component),
            xaxis_title="V/m3",
            yaxis_title = "P/kPa",
            font=dict(
                family="Helvetica Neue, monospace",
                size=12,
                color="#FFFFFF"
            )
        )

        self.fig.add_trace(go.Scatter(x=V_points, y=P_points, 
                                mode='lines', name="Isotherm", line_color = "#FF00FF",
                                hovertemplate =
                                'x: %{x:.2f}' +
                                '<br>y: %{y:.2f}'))

        print(V_points)
        print(P_points)

    def show(self):
        self.fig.update_xaxes(showspikes=True)
        self.fig.update_yaxes(showspikes=True)
        self.fig.show()

# plot = plotPure(VanDerWaalsEOS(-100, 150, 'n-Octane'))
# plot.create_isotherm()
# plot.show()

# print(plot.sys.component, plot.sys.get_a(), plot.sys.get_b())