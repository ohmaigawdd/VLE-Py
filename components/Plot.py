from VLECalculations import RachfordRice
import plotly.graph_objects as go
import numpy as np

# Params is a dictionary with divID, Tmin/max, Pmin/max, numpoints
#self.params = params

class plot:
    def __init__(self,RR):
        # n,T,P, components, z in RR 
        self.RR = RR

    # Add a 45 degree line (For y-x graphs). The method needs the first comment first
    def add_45degLine(self):
        self.fig = go.Figure()
        x = np.linspace(0,1,endpoint=True)
        self.fig.add_trace(go.Scatter(x=x, y=x, mode = 'lines'))

    def generate_yx_constP_data(self):
        # zA = composition of component A in VLE
        # Generates (x,y,P) values using zA data at constant T
        points = []
        RR = self.RR  #Temp RR for iteration
        Tmax = self.RR.params['Tmax']
        Tmin = self.RR.params['Tmin']
        step = round((Tmax - Tmin) / 100)

        # @ selected zA, vary T to obtain [x,y,T,v] values
        for i in range(Tmin, Tmax, step):
            RR.setT(i)
            if 0 <= RR.v and RR.v <= 1:
                # points will have [[xA1,yA1,T1,v1],[xA1,yA1,T1,v1]]
                points.append([RR.x[0], RR.y[0], i, RR.v])

        #Sorted according to x
        points = sorted(points)
        return points

    def generate_yx_constT_data(self):
        # zA = composition of component A in VLE
        # Generates (x,y,P) values using zA data at constant T
        points = []
        RR = self.RR  #Temp RR for iteration
        Pmax = self.RR.params['Pmax']
        Pmin = self.RR.params['Pmin']
        step = round((Pmax - Pmin) / 100)

        # @ selected zA, vary T to obtain [x,y,T,v] values
        for i in range(Pmin, Pmax, step):
            RR.setP(i)
            if 0 <= RR.v and RR.v <= 1:
                # points will have [[xA1,yA1,P1,v1],[xA1,yA1,P1,v1]]
                points.append([RR.x[0], RR.y[0], i, RR.v])

        #Sorted according to x
        points = sorted(points)
        return points

    # Idea is on HTML, if y-x const P selected, run this method. Same for others
    # (1) Creates 45 degree line
    # (2) Generate x,y values (points[i][0]/points[i][1]) for all different values of T
    # (3) Add the trace to fig
    # (4) Plot it~ but dk if should do on html?
    def plot_yx_constP(self):
        self.add_45degLine()
        self.points = self.generate_yx_constP_data()
        x_arr = []
        y_arr = []
        for i in range(0,len(self.points)):
            x_arr.append(self.points[i][0])
            y_arr.append(self.points[i][1])

        # Adds the points to the fig and plots a line and marker chart
        self.fig.add_trace(go.Scatter(x=x_arr, y=y_arr, 
                                      mode='lines + markers'), 
                                      text="(x, y) \n T: {} ".format(self.RR.T))
        
    def plot_yx_constT(self):
        self.add_45degLine()
        self.points = self.generate_yx_constT_data()
        x_arr = []
        y_arr = []
        for i in range(0,len(self.points)):
            x_arr.append(self.points[i][0])
            y_arr.append(self.points[i][1])

        # Adds the points to the fig and plots a line and marker chart
        self.fig.add_trace(go.Scatter(x=x_arr, y=y_arr, 
                                      mode='lines + markers'), 
                                      text="(x, y) \n T: " + str(self.RR.T))
    
    def plot_Pxy(self):
        self.fig = go.Figure()
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
        self.fig = go.Figure()
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

#Testing functions
plot = plot(RachfordRice(2, 50, 101, ['n-Pentane','n-Heptane'], [0.3,0.7]))
plot.plot_Pxy()
plot.show()
#plot.add_45degLine()


'''
x = np.arange(10)
fig = go.Figure(data=go.Scatter(x=x,y=x, mode='lines',text="(x, y) \n T: {} ".format(50)))
fig.add_trace(go.Scatter(x=(1,2),y=(1,2),mode='lines'))
fig.show()
'''