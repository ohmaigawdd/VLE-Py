from VLECalculations import RachfordRice
import plotly.graph_objects as go
import numpy as np

# Params is a dictionary with divID, Tmin/max, Pmin/max, numpoints
#self.params = params

class plot:
    def __init__(self,RR):
        # n,T,P, components, z in RR 
        self.RR = RR
        
    def create_plot(self):
        self.fig = go.Figure()

    # Add a 45 degree line (For y-x graphs). The method needs the first comment first
    def add_45degLine(self):
        self.create_plot()
        x = np.linspace(0,1,endpoint=True)
        self.fig.add_trace(go.Scatter(x=x, y=x, mode = 'lines'))

    def generate_yx_constP_data(self):
        # zA = composition of component A in VLE
        # Generates (x,y,P) values using zA data at constant T
        points = []
        RR = self.RR  #Temp RR for iteration
        Tmax = self.RR.params['Tmax']
        Tmin = self.RR.params['Tmin']
        step = round((Tmax - Tmin) / 500)

        # @ selected zA, vary T to obtain [x,y,T,v] values
        for i in range(Tmin, Tmax, step):
            RR.setT(i)
            if 0 <= RR.v and RR.v <= 1:
                # points will have [[xA1,yA1,T1,v1],[xA1,yA1,T1,v1]]
                points.append([RR.x[0], RR.y[0], i, RR.v])

        #Sorted according to x
        points = sorted(points)
        if points:
            bps = [RR.getPureComponentBoilingTemp(RR.components[0],RR.P*0.145038), RR.getPureComponentBoilingTemp(RR.components[1],RR.P*0.145038)]
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
        RR = self.RR  #Temp RR for iteration
        Pmax = self.RR.params['Pmax']
        Pmin = self.RR.params['Pmin']
        step = round((Pmax - Pmin) / 1000)

        # @ selected zA, vary T to obtain [x,y,T,v] values
        for i in range(Pmin, Pmax, step):
            RR.setP(i)
            if 0 <= RR.v and RR.v <= 1:
                # points will have [[xA1,yA1,P1,v1],[xA1,yA1,P1,v1]]
                points.append([RR.x[0], RR.y[0], i, RR.v])

        #Sorted according to x
        points = sorted(points)
        print(RR.T*(9/5)+491.67)
        if points:
            bps = [RR.getPureComponentBoilingPressure(RR.components[0], RR.T*(9/5)+491.67), RR.getPureComponentBoilingPressure(RR.components[1],RR.T*(9/5)+491.67)]
            
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
        x_arr = [0]
        y_arr = [0]
        for i in range(0,len(self.points)):
            x_arr.append(self.points[i][0])
            y_arr.append(self.points[i][1])
        x_arr.append(1)
        y_arr.append(1)

        # Adds the points to the fig and plots a line and marker chart
        self.fig.add_trace(go.Scatter(x=x_arr, y=y_arr, 
                                      mode='lines + markers'))
        
    def plot_yx_constT(self):
        self.add_45degLine()
        self.points = self.generate_yx_constT_data()
        x_arr = [0]
        y_arr = [0]
        for i in range(0,len(self.points)):
            x_arr.append(self.points[i][0])
            y_arr.append(self.points[i][1])
        x_arr.append(1)
        y_arr.append(1)

        # Adds the points to the fig and plots a line and marker chart
        self.fig.add_trace(go.Scatter(x=x_arr, y=y_arr, 
                                      mode='lines + markers'))
    
    def plot_Pxy(self):
        self.create_plot()
        self.points = self.generate_yx_constP_data()
        x_arr = []
        y_arr = []
        P_arr = []
        for i in range(0,len(self.points)):
            x_arr.append(self.points[i][0])
            y_arr.append(self.points[i][1])
            P_arr.append(self.points[i][2])
        
        # Adds the points for P-x and P-y to plot saturated lines

        self.fig.add_trace(go.Scatter(x=x_arr, y=P_arr,
                                      mode="lines"))
        self.fig.add_trace(go.Scatter(x=y_arr, y=P_arr,
                                      mode="lines"))
                                      
    def plot_Txy(self):
        self.create_plot()
        self.points = self.generate_yx_constT_data()
        x_arr = []
        y_arr = []
        T_arr = []
        for i in range(0,len(self.points)):
            x_arr.append(self.points[i][0])
            y_arr.append(self.points[i][1])
            T_arr.append(self.points[i][2])
        
        # Adds the points for T-x and T-y to plot saturated lines
        self.fig.add_trace(go.Scatter(x=x_arr, y=T_arr,
                                      mode="lines"))
        self.fig.add_trace(go.Scatter(x=y_arr, y=T_arr,
                                      mode="lines"))

    def show(self):
        self.fig.show()

# Things to add on:
# (1) TieLine
# (2) Show selected option marker. Best if use fig.add_annotation(current)
# (3) Senior's one able to show live update if increase T/P/z. Since we doing rerendering 
#     should consider showing the previous plot to compare

# Testing functions
plot = plot(RachfordRice(2, 50, 105, ['Ethane','n-Octane'], [0.3,0.7]))
plot.plot_Txy()
plot.show()


'''
x = np.arange(10)
fig = go.Figure(data=go.Scatter(x=x,y=x, mode='lines',text="(x, y) \n T: {} ".format(50)))
fig.add_trace(go.Scatter(x=(1,2),y=(1,2),mode='lines'))
fig.show()
'''