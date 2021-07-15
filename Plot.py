## Only import below if testing code ##
from VLECalculations import RachfordRice, Antoine, Steam
import plotly
import json
import plotly.graph_objects as go
import numpy as np

# Params is a dictionary with divID, Tmin/max, Pmin/max, numpoints
#self.params = params

#rename plot_binary
class plot:
    def __init__(self,RR):
        # n,T,P, components, z in RR 
        self.RR = RR
        
    def create_plot(self):
        self.fig = go.Figure()
        self.fig.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)')

    # Add a 45 degree line (For y-x graphs)
    def add_45degLine(self):
        self.create_plot()
        x_data = np.linspace(0,1,num=20,endpoint=True)
        self.fig.add_trace(go.Scatter(x=x_data, y=x_data, mode = 'lines', name="x = y", line_color = "#FFFF00"))

    def create_tieline(self):
        x = self.RR.x
        y = self.RR.y
        z = self.RR.z
        P = self.RR.P
        T = self.RR.T
        
        # Check if the point chosen for Z is within VLE and put points into x_arr. If not VLE, just get z point
        if 0 < self.RR.v and self.RR.v < 1:
            if x[0] < y[0]:
                x_arr = [x[0], z[0], y[0]]
                labels = ['x', 'z', 'y']
            else:
                x_arr = [y[0], z[0], x[0]]
                labels = ['y', 'z', 'x']
            # Check for plotID to determine which y-axis
            if self.plotID == 'Txy':
                y_arr = [P, P, P]
                type = 'P'
            else:
                y_arr = [T, T, T]
                type = 'T'
        
        else:
            x_arr = [z[0]]
            labels = ['z']
            if self.plotID == 'Txy':
                y_arr = [P]
                type = 'P'
                print("i ran")
            else:
                y_arr = [T]
                type = 'T'
                print("i ran")

        
        if type == 'T':
            self.fig.add_trace(go.Scatter(x=x_arr, y=y_arr, 
                                        mode='lines+markers', name="Tie Line",
                                        marker = dict(size=10), 
                                        hovertemplate =
                                        '%{text}' + 
                                        ': %{x:.2f}' +
                                        '<br>T: %{y:.2f}' + chr(176)+ 'C',
                                        text = ['{}'.format(i) for i in labels]))
        else:
            self.fig.add_trace(go.Scatter(x=x_arr, y=y_arr, 
                                        mode='lines+markers', name="Tie Line",
                                        marker = dict(size=10), 
                                        hovertemplate =
                                        '%{text}' + 
                                        ': %{x:.2f}' +
                                        '<br>P: %{y:.2f}' + 'kPa',
                                        text = ['{}'.format(i) for i in labels]))

    def generate_yx_constP_data(self):
        # zA = composition of component A in VLE
        # Generates (x,y,P) values using zA data at constant T
        points = []
        Tmax = self.RR.params['Tmax']
        Tmin = self.RR.params['Tmin']
        step = round((Tmax - Tmin) / 50)

        # @ selected zA, vary T to obtain [x,y,T,v] values
        temporaryobject = RachfordRice(self.RR.n, self.RR.T, self.RR.P, self.RR.components, self.RR.z)
        for i in range(Tmin, Tmax, step):
            temporaryobject.setT(i)
            if 0 <= temporaryobject.v and temporaryobject.v <= 1:
                # points will have [[xA1,yA1,T1,v1],[xA1,yA1,T1,v1]]
                points.append([temporaryobject.x[0], temporaryobject.y[0], i, temporaryobject.v])# reset temp

        #Sorted according to x
        points = sorted(points)
        if points:
            bps = [self.RR.getPureComponentBoilingTemp(self.RR.components[0],self.RR.P_psia), self.RR.getPureComponentBoilingTemp(self.RR.components[1],self.RR.P_psia)]
            if bps[0] > bps[1]: # first component is lighter
                bp_light, bp_heavy = bps[0], bps[1]
                points.insert(0,[0,0, bp_heavy, None])
                points.append([1,1,bp_light, None])
            else: 
                bp_light, bp_heavy = bps[1], bps[0]
                points.insert(0,[0,0, bp_light, None])
                points.append([1,1,bp_heavy, None])

        return points

    def generate_yx_constT_data(self):
        # zA = composition of component A in VLE
        # Generates (x,y,P) values using zA data at constant T
        points = []
        Pmax = self.RR.params['Pmax']
        Pmin = self.RR.params['Pmin']
        step = round((Pmax - Pmin) / 100)

        # @ selected zA, vary P to obtain [x,y,P,v] values
        temporaryobject = RachfordRice(self.RR.n, self.RR.T, self.RR.P, self.RR.components, self.RR.z)
        for i in range(Pmin, Pmax, step):
            temporaryobject.setP(i)
            if 0 <= temporaryobject.v and temporaryobject.v <= 1:
                # points will have [[xA1,yA1,P1,v1],[xA2,yA2,P2,v2]]
                points.append([temporaryobject.x[0], temporaryobject.y[0], i, temporaryobject.v])

        #Sorted according to x
        points = sorted(points)
        if points:
            bps = [self.RR.getPureComponentBoilingPressure(self.RR.components[0], self.RR.T_degR), self.RR.getPureComponentBoilingPressure(self.RR.components[1],self.RR.T_degR)]
            
            if bps[0] < bps[1]: # first component is lighter
                bp_light, bp_heavy = bps[0], bps[1]
                points.insert(0,[0,0, bp_heavy, None])
                points.append([1,1,bp_light, None])
            else: 
                bp_light, bp_heavy = bps[1], bps[0]
                points.insert(0,[0,0, bp_light, None])
                points.append([1,1,bp_heavy, None])
        return points

    # Idea is on HTML, if y-x const P selected, run this method. Same for others
    # (1) Creates 45 degree line
    # (2) Generate x,y values (points[i][0]/points[i][1]) for all different values of T
    # (3) Add the trace to fig
    # (4) Plot it~ but dk if should do on html?
    def plot_yx_constP(self):
        self.add_45degLine()
        self.points = self.generate_yx_constP_data()
        self.plotID = 'yxP'
        x_arr = [0]
        y_arr = [0]
        for i in range(0,len(self.points)):
            x_arr.append(self.points[i][0])
            y_arr.append(self.points[i][1])
        x_arr.append(1)
        y_arr.append(1)

        # Adds the points to the fig and plots a line and marker chart
        pressure = self.RR.P
        component = self.RR.components[0]
        self.fig.update_layout(
            title="<b>x-y Plot at Constant Pressure of " + str(pressure) + "kPa</b>",
            xaxis_title="x (" + component + ")",
            yaxis_title = "y (" + component + ")",
            legend=dict(
                title='Legend',
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            font=dict(
                family="Helvetica Neue, monospace",
                size=12,
                color="#FFFFFF"
            )
        )

        self.fig.add_trace(go.Scatter(x=x_arr, y=y_arr, 
                                      mode='markers+lines', name="Equilibrium Line", line_color = "#FF00FF",
                                      hovertemplate =
                                      'x: %{x:.2f}' +
                                      '<br>y: %{y:.2f}'))

        currentTemp = self.RR.T
        current_x = [self.RR.x[0]]
        current_y = [self.RR.y[0]]
        self.fig.add_trace(go.Scatter(x=current_x, y=current_y, mode='markers', name="Current Temperature",
                                      marker = dict(size=10),
                                      hovertemplate =
                                      'x: %{x:.2f}' +
                                      '<br>y: %{y:.2f}<br>' +
                                      '%{text}', text = [f'Temperature: {currentTemp}'+ chr(176) + "C"]))
        
        self.fig.update_xaxes(showspikes=True, range = [0, 1])
        self.fig.update_yaxes(showspikes=True, range = [0, 1], scaleanchor = "x", scaleratio = 1)
        
    def plot_yx_constT(self):
        self.add_45degLine()
        self.points = self.generate_yx_constT_data()
        self.plotID = 'yxT'
        x_arr = [0]
        y_arr = [0]
        for i in range(0,len(self.points)):
            x_arr.append(self.points[i][0])
            y_arr.append(self.points[i][1])
        x_arr.append(1)
        y_arr.append(1)

        # Adds the points to the fig and plots a line and marker chart
        temperature = self.RR.T
        component = self.RR.components[0]
        self.fig.update_layout(
            title="<b>x-y Plot at Constant Temperature of " + str(temperature) + chr(176) + "C</b>",
            xaxis_title="x (" + component + ")",
            yaxis_title = "y (" + component + ")",
            legend=dict(
                title = 'Legend',
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            font=dict(
                family="Helvetica Neue, monospace",
                size=12,
                color="#FFFFFF"
            )
        )
        self.fig.add_trace(go.Scatter(x=x_arr, y=y_arr, 
                                      mode='lines + markers', name="Equilibrium Line", line_color = "#FF00FF",
                                      hovertemplate =
                                      'x: %{x:.2f}' +
                                      '<br>y: %{y:.2f}'))

        currentPressure = self.RR.P
        current_x = [self.RR.x[0]]
        current_y = [self.RR.y[0]]
        self.fig.add_trace(go.Scatter(x=current_x, y=current_y, mode='markers', name="Current Pressure",
                                      marker = dict(size=10),
                                      hovertemplate =
                                      'x: %{x:.2f}' +
                                      '<br>y: %{y:.2f}<br>' +
                                      '%{text}', text = [f'Pressure: {currentPressure} kPa']))

        self.fig.update_xaxes(showspikes=True, range = [0, 1])
        self.fig.update_yaxes(showspikes=True, range = [0, 1], scaleanchor = "x", scaleratio = 1)
    
    def plot_Pxy(self):
        self.create_plot()
        self.points = self.generate_yx_constP_data()
        self.plotID = 'Pxy'
        x_arr = []
        y_arr = []
        P_arr = []
        for i in range(0,len(self.points)):
            x_arr.append(self.points[i][0])
            y_arr.append(self.points[i][1])
            P_arr.append(self.points[i][2])
        
        # Adds the points for P-x and P-y to plot saturated lines

        pressure = self.RR.P
        component = self.RR.components[0]
        self.fig.update_layout(
            title="<b>T-x-y Plot at Constant Pressure of " + str(pressure) + "kPa</b>",
            xaxis_title="x (" + component + ")/y (" + component + ")",
            yaxis_title = "Temperature ("+chr(176)+"C)",
            legend=dict(
                title = 'Legend',
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            font=dict(
                family="Helvetica Neue, monospace",
                size=12,
                color="#FFFFFF"
            )
        )



        self.fig.add_trace(go.Scatter(x=x_arr, y=P_arr,
                                      mode="lines", name="Bubble Line", line_color = "#FF00FF",
                                      hovertemplate =
                                      'x: %{x:.2f}' +
                                      '<br>T: %{y:.2f}' + chr(176)+ 'C'))
        self.fig.add_trace(go.Scatter(x=y_arr, y=P_arr,
                                      mode="lines", name="Dew Line", line_color = "#FFFF00",
                                      hovertemplate =
                                      'y: %{x:.2f}' +
                                      '<br>T: %{y:.2f}' + chr(176)+ 'C'))
        self.create_tieline()

        self.fig.update_xaxes(showspikes=True)
        self.fig.update_yaxes(showspikes=True)
                                      
    def plot_Txy(self):
        self.create_plot()
        self.points = self.generate_yx_constT_data()
        self.plotID = 'Txy'
        x_arr = []
        y_arr = []
        T_arr = []
        for i in range(0,len(self.points)):
            x_arr.append(self.points[i][0])
            y_arr.append(self.points[i][1])
            T_arr.append(self.points[i][2])
        
        # Adds the points for T-x and T-y to plot saturated lines
        temperature = self.RR.T
        component = self.RR.components[0]
        self.fig.update_layout(
            title="<b>P-x-y Plot at Constant Temperature of " + str(temperature) + chr(176) + "C</b>",
            xaxis_title = "x (" + component + ")/y (" + component + ")",
            yaxis_title="Pressure (kPa)",
            legend=dict(
                title = 'Legend',
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            font=dict(
                family="Helvetica Neue, monospace",
                size=12,
                color="#FFFFFF"
            )
        )

        self.fig.add_trace(go.Scatter(x=x_arr, y=T_arr,
                                      mode="lines", name="Bubble Line", line_color = "#FF00FF",
                                      hovertemplate =
                                      'x: %{x:.2f}' +
                                      '<br>P: %{y:.2f} kPa'))
        self.fig.add_trace(go.Scatter(x=y_arr, y=T_arr,
                                      mode="lines", name="Dew Line", line_color = "#FFFF00",
                                      hovertemplate =
                                      'y: %{x:.2f}' +
                                      '<br>P: %{y:.2f} kPa'))
        self.create_tieline()

        self.fig.update_xaxes(showspikes=True)
        self.fig.update_yaxes(showspikes=True)

    # To generate or show the graph plotted
    def generate(self):
        return json.dumps(self.fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def show(self):
        self.fig.update_xaxes(showspikes=True)
        self.fig.update_yaxes(showspikes=True)
        self.fig.show()

class plot_pure:
    def __init__(self, Ant):
        #Component, T, P in Ant
        self.Ant = Ant

    def plot_pureVLE(self):
        self.create_plot()
        self.points = self.generate_Psat()
        T_arr = []
        P_arr = []
        for i in range(0,len(self.points)):
            T_arr.append(self.points[i][0])
            P_arr.append(self.points[i][1])
        
        self.fig.add_trace(go.Scatter(x=T_arr, y=P_arr,
                                        mode="lines", name="Equilibrium Line", line_color = "#FF00FF",
                                        hovertemplate =
                                        'T: %{x:.2f} C' +
                                        '<br>P: %{y:.2f} kPa'))
        self.fig.update_xaxes(showspikes=True)
        self.fig.update_yaxes(showspikes=True)

    def generate_Psat(self):
        points = []
        Tmax = self.Ant.params[self.Ant.component][1]
        Tmin = self.Ant.params[self.Ant.component][0]
        step = round((Tmax - Tmin) / 100)

        tempobject = Antoine(self.Ant.component, self.Ant.T, self.Ant.P)
        for i in range(round(Tmin), round(Tmax), step):
            points.append([tempobject.T,tempobject.setT(i)])

        points = sorted(points)
        return points

    create_plot = plot.__dict__["create_plot"]
    generate = plot.__dict__["generate"]
    show = plot.__dict__["show"]


class plot_steam:
    def __init__(self,sys):
        self.sys = sys #sys is based on Steam class in VLE calculations e.g Steam(T,P)

    def generate_Tpoints(self):
        points = []
        Tmax = 375
        Tmin = -50
        step = round((Tmax - Tmin) / 425)

        tempobject = Steam(self.sys.T, self.sys.P)
        for i in range(round(Tmin), round(Tmax), step):
            points.append([tempobject.T,tempobject.setT(i)])

        points = sorted(points)
        return points

    def plot_steamVLE(self):
        self.create_plot()
        self.points = self.generate_Tpoints()
        T_arr = []
        P_arr = []
        for i in range(0,len(self.points)):
            T_arr.append(self.points[i][0])
            P_arr.append(self.points[i][1])
        
        self.fig.add_trace(go.Scatter(x=T_arr, y=P_boil_arr,
                                        mode="lines", name="Boiling Equilibrium Line", line_color = "#FF00FF",
                                        hovertemplate =
                                        'T: %{x:.2f} C' +
                                        '<br>P: %{y:.2f} kPa'))
        self.fig.update_xaxes(showspikes=True)
        self.fig.update_yaxes(showspikes=True)

    create_plot = plot.__dict__["create_plot"]
    generate = plot.__dict__["generate"]
    show = plot.__dict__["show"]

# Testing functions
# plot = plot(RachfordRice(2, 150, 101.3, ['n-Hexane','n-Octane'], [0.6,0.4]))
# plot.plot_Pxy()
# plot.show()
# print(plot.RR.x, plot.RR.y, plot.RR.v)

# plot = plot_steam(Steam(100, 100))
# plot.plot_steamVLE()
# plot.show()

'''
x = np.arange(10)
fig = go.Figure(data=go.Scatter(x=x,y=x, mode='lines',text="(x, y) \n T: {} ".format(50)))
fig.add_trace(go.Scatter(x=(1,2),y=(1,2),mode='lines'))
fig.show()
'''