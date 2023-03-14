from flask import Flask, render_template, session, request, Response
from resetParamForm import PureForm, BinaryForm, IdealReactorForm, RealReactorForm
from VLECalculations import RachfordRice, Antoine, Steam
from Plot import plot, plot_steam, GvsP, GvsT
from RTD import RTD
from Real_RTD import Real_RTD
from functools import wraps

app = Flask(__name__)

app.config["SECRET_KEY"] = "mykey"

def check_authTHERMO(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == 'student' and password == 'ChE_VLEapp'

def check_authRXT(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == 'student' and password == 'ChE_RTDapp'

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return render_template("error.html"), 401, {'WWW-Authenticate': 'Basic realm="Login Required"'}

def requires_authTHERMO(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_authTHERMO(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

def requires_authRXT(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_authRXT(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

###############################################################

# HOME PAGE
@app.route("/")
def home():
    return render_template("home.html")

###############################################################

# PURE VLE WRITE UP
@app.route("/purevleinfo")
@requires_authTHERMO
def purevleinfo():
    return render_template("purevleinfo.html")

# PURE VLE APP
@app.route("/purevle", methods=["GET","POST"])
@requires_authTHERMO
def purevle():

    form = PureForm()

    if form.T_isob.data==None and form.P_isob.data==None and form.T_isot.data==None and form.P_isot.data==None and form.processType.data==None:
        processType = "Isotherm"
        T = 50
        P = 100
        errors = False
    elif not form.validate_on_submit():
        processType = form.processType.data
        T = 50
        P = 100
        errors = True
    #if form is 100% okay
    elif form.validate_on_submit():
        processType = form.processType.data
        if processType == "Isobar":
            T = form.T_isob.data
            P = form.P_isob.data
        else:
            T = form.T_isot.data
            P = form.P_isot.data
        errors = False
    
    system = Steam(T, P)
    system.instantiate()
    plot = plot_steam(system)
    plot.plot_steamVLE()
    graphJSON = plot.generate()
    if processType == "Isotherm": #if isothermal
        Ggraph = GvsP(T)
        equi = int(system.getboilingP()*100)
    else: #if isobaric
        Ggraph = GvsT(P/100)
        equi = int(system.getboilingT())
    return render_template("purevle.html", equi=equi, errors=errors, form=form, system=system, graphJSON=graphJSON, Ggraph=Ggraph, processType=processType)

###############################################################

# BINARY VLE WRITE UP
@app.route("/binaryvleinfo")
@requires_authTHERMO
def binaryvleinfo():
    return render_template("binaryvleinfo.html")

# BINARY VLE PAGE
@app.route("/binaryvle", methods=["GET","POST"])
@requires_authTHERMO
def binaryvle():

    form = BinaryForm()

    chemicals = dict([('met','Methane'),('ethy','Ethylene'),('eth','Ethane'),('propy','Propylene'),
    ('prop','Propane'), ('isob','Isobutane') , ('nbut','n-Butane'), ('isop','Isopentane'), ('npent','n-Pentane'),
    ('nhex','n-Hexane'), ('nhep','n-Heptane'), ('noct','n-Octane'),('nnon','n-Nonane'), ('ndec','n-Decane'), ("none", "Not initialised")])

    plots = dict([("yxP","y-x (const P)"), ("yxT","y-x (const T)"), ("Txy","T-x-y"), ("Pxy","P-x-y"), ("none", "Not initialised")])
    
    #initialisation
    if form.T.data==None and form.P.data==None and form.z.data==None:
        componentA = "met"
        componentB = "ethy"
        plot_type = 'yxP'
        T = 100
        P = 500
        z = 0.3
        errors = False
    #if form has the same 2 components for A and B OR problem with T, P, z
    elif not form.validate_on_submit() or form.componentA.data == form.componentB.data:
        componentA = form.componentA.data
        componentB = form.componentB.data
        plot_type = form.plot_type.data
        T = 100
        P = 500
        z = 0.3
        errors = True
    #if form is 100% okay
    elif form.validate_on_submit():
        componentA = form.componentA.data
        componentB = form.componentB.data
        plot_type = form.plot_type.data
        T = form.T.data
        P = form.P.data
        z = form.z.data
        errors = False

    system = RachfordRice(2, T, P, [chemicals[componentA], chemicals[componentB]], [z, 1-z])
    #check if critical P and T are not exceeded:
    if system.exceedT == True or system.exceedP == True:
        exceed = True
    else:
        exceed = False

    if (system.checkBoilingPressure()==False and plot_type == "Pxy") or (system.checkBoilingTemp()==False and plot_type == "Txy"):
        errors = True
        graphJSON = None
        initial = None
        solver_limit = True
    else:
        initial = plot(system)
        if plot_type == "yxP":
            initial.plot_yx_constP()
        elif plot_type == "yxT":
            initial.plot_yx_constT()
        elif plot_type == "Txy":
            initial.plot_Pxy()
        else:
            initial.plot_Txy()
        graphJSON = initial.generate()
        solver_limit = False

    return render_template("binaryvle.html", solver_limit=solver_limit, form=form, graphJSON=graphJSON, plot_type=plot_type, system=system, chemicals=chemicals, plots=plots, errors=errors, exceed=exceed)

###############################################################

# REACTOR DESIGN AND ANALYSIS WRITE UP
@app.route("/reactorwriteup")
@requires_authRXT
def reactorwriteup():
    return render_template("reactorwriteup.html")

# IDEAL PFR/CSTR PAGE
@app.route("/idealreactors", methods=["GET","POST"])
@requires_authRXT
def idealreactors():

    form = IdealReactorForm()

    if form.reactorType.data==None:
        reactorType = "cstr"
        reactorVol = 10
        reactorFlow = 2
        tracerType = "pulse"
        errors = False
    elif not form.validate_on_submit():
        reactorType = "cstr"
        reactorVol = 10
        reactorFlow = 2
        tracerType = "pulse"
        errors = True
    elif form.validate_on_submit():
        reactorType = form.reactorType.data
        reactorVol = form.reactorVol.data
        reactorFlow = form.reactorFlow.data
        tracerType = form.tracerType.data
        errors = False
    
    if errors == False:
        system = RTD(reactorVol, reactorFlow, tracerType)
        if reactorType == "cstr":
            Cgraph = system.CSTR(1) #note that code now has this as "n"
            Egraph = system.CSTR_E(1)
            Fgraph = system.CSTR_F(1)
        elif reactorType == "pfr":
            Cgraph = system.PFR()
            Egraph = system.PFR_E()
            Fgraph = system.PFR_F()
    else:
        system = RTD(reactorVol, reactorFlow, tracerType)
        system.length = 0
        Cgraph = False
        Egraph = False
        Fgraph = False

    return render_template("idealreactors.html", reactorType=reactorType, tracerType=tracerType, system=system, form=form, errors=errors, Cgraph=Cgraph, Egraph=Egraph, Fgraph=Fgraph)

# REAL PFR/CSTR PAGE
@app.route("/realreactors", methods=["GET","POST"])
@requires_authRXT
def realreactors():

    form = RealReactorForm()
    # Profs told us to fix V and Q for real reactor application
    reactorVol = 20       #m3
    reactorFlow = 2      #m3/s
    # Array to check for real issues with reactors
    reasons_for_deadvol = ["poor impeller design", "reactor fouling"]
    reasons_for_bypass = ["poor outlet design", "poor bed packing"]
    # reasons_for_both = [] <- can add in when got more ideas

    if form.reactorType.data==None:
        reactorType = "cstr"
        tracerType = "pulse"
        problemType = "poor impeller design"
        errors = False
    elif not form.validate_on_submit():
        reactorType = "cstr"
        tracerType = "pulse"
        problemType = "poor impeller design"
        errors = True
    elif form.validate_on_submit():
        reactorType = form.reactorType.data
        tracerType = form.tracerType.data
        if reactorType == "cstr":
            problemType = form.problemType_cstr.data
        else:
            problemType = form.problemType_pfr.data
        errors = False

    if errors == False:
        idealsystem = RTD(reactorVol, reactorFlow, tracerType)
        realsystem = Real_RTD(reactorVol, reactorFlow, tracerType)
        if reactorType == "cstr":
            Cgraph = idealsystem.CSTR(1) #note that code now has this as "n"
            if problemType in reasons_for_deadvol:
                realCgraph = realsystem.CSTR_deadvol(1) 
                realEgraph = realsystem.CSTR_deadvol_E(1)
                realFgraph = realsystem.CSTR_deadvol_F(1)
                bypassdeadvolume = "Dead Volume"
            elif problemType in reasons_for_bypass:
                realCgraph = realsystem.CSTR_bypass(1) 
                realEgraph = realsystem.CSTR_bypass_E(1)
                realFgraph = realsystem.CSTR_bypass_F(1)
                bypassdeadvolume = "Reactor Bypass"
        elif reactorType == "pfr":
            Cgraph = idealsystem.PFR()
            if problemType in reasons_for_deadvol:
                realCgraph = realsystem.PFR_deadvol() 
                realEgraph = realsystem.PFR_deadvol_E()
                realFgraph = realsystem.PFR_deadvol_F()
                bypassdeadvolume = "Dead Volume"
            elif problemType in reasons_for_bypass:
                realCgraph = realsystem.PFR_bypass() 
                realEgraph = realsystem.PFR_bypass_E()
                realFgraph = realsystem.PFR_bypass_F()
                bypassdeadvolume = "Reactor Bypass"
    else:
        idealsystem = RTD(reactorVol, reactorFlow, tracerType)
        realsystem = Real_RTD(reactorVol, reactorFlow, tracerType)
        idealsystem.length = 0
        realsystem.length = 0
        Cgraph = False
        realCgraph = False
        realEgraph = False
        realFgraph = False

    return render_template("realreactors.html", form=form, errors=errors, tracerType=tracerType, reactorType=reactorType, problemType=problemType, idealsystem=idealsystem, realsystem=realsystem, Cgraph=Cgraph, realCgraph=realCgraph, realEgraph=realEgraph, realFgraph=realFgraph)

###############################################################

if __name__ == "__main__":
    app.run(debug=True)
