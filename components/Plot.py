from VLECalculations import RachfordRice
import plotly.graph_objects as go
import numpy as np

# Params is a dictionary with divID, Tmin/max, Pmin/max, numpoints
#self.params = params

class plot:
    def __init__(self,RR):
        # n,T,P, components, z in RR 
        self.RR = RR

        # self.cache = [
        # {name: "yx_constP", args:[0,0,0,"",""], data:[], layout:undefined},
        # {name: "yx_constT", args:[0,0,0,"",""], data:[],layout:undefined},
        # {name: "Txy", args:[0,0,0,"",""], data:[], layout:undefined},
        # {name: "Pxy", args:[0,0,0,"",""], data:[], layout:undefined}
        # ];
        # args = [T,P,z,components]
        pass
    
    # Add a 45 degree line (For y-x graphs). The method needs the first comment first
    def add_45degLine(self):
        self.fig = go.Figure()
        x = np.linspace(0,1,endpoint=True)
        self.fig.add_trace(go.Scatter(x=x, y=x, mode = 'lines'))

    # Not sure the use of creating such small steps yet but following
    def generateZ_arr(self):
        # Set at smaller steps for now
        z_arr = np.arange(0,1,0.1)
        return z_arr

    def generate_yx_constP_data(self,zA_arr):
        # zA = composition of component A in VLE
        # Generates (x,y,P) values using zA data at constant T
        points = []
        RR = self.RR  #Temp RR for iteration
        Tmax = self.RR.params['Tmax']
        Tmin = self.RR.params['Tmin']
        step = round((Tmax - Tmin) / 100)

        # Iterate through z_arr to obtain different y-x values at diff T
        # zA_arr contains [0,0.001,0.002,...,0.999,1]
        for zA in zA_arr:
            RR.setZ([zA,1-zA])
            # @ selected zA, vary T to obtain [x,y,T,v] values
            for i in range(Tmin, Tmax, step):
                RR.setT(i)
                if 0 <= RR.v and RR.v <= 1:
                    # points will have 
                    points.append([RR.x[0], RR.y[0], i, RR.v])

        #Sorted according to 
        points = sorted(points)
        return points

    '''def create_trace_yx(self, points):
        x_arr = points[0]
        y_arr = points[1]
    '''

    # Idea is on HTML, if y-x const P selected, run this method
    # (1) Creates 45 degree line
    # (2) Generates the zA_arr to be calculated (Maybe should be done in class)
    # (3) Generate x,y values (points[i][0]/points[i][1]) for all different values of T
    # 
    def calc_yx_constP(self):
        self.add_45degLine()
        self.z_arr = self.generateZ_arr()
        self.points = self.generate_yx_constP_data(self.z_arr)
        self.fig.add_trace(go.Scatter(x=self.points()))
        
        


#Testing functions
plot = plot(RachfordRice(2, 50, 101, ['n-Pentane','n-Heptane'], [0.3,0.7]))
# plot.add_45degLine()
print(plot.generate_yx_constP_data(plot.generateZ_arr()))

'''
x = np.arange(10)
fig = go.Figure(data=go.Scatter(x=x,y=x, mode='lines'))
fig.show()
'''