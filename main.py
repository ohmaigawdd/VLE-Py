from flask import Flask, render_template, session, request
from resetParamForm import PureForm, BinaryForm
from VLECalculations import RachfordRice, Antoine, Steam
from Plot import plot

app = Flask(__name__)

app.config["SECRET_KEY"] = "mykey"

# HOME PAGE
@app.route("/")
def home():
    return render_template("home.html")

# PURE VLE PAGE
@app.route("/purevle", methods=["GET","POST"])
def purevle():

    form = PureForm()

    chemicals = dict([('met','Methane'),('ethy','Ethylene'),('eth','Ethane'),('propy','Propylene'),
    ('prop','Propane'), ('isob','Isobutane') , ('nbut','n-Butane'), ('isop','Isopentane'), ('npent','n-Pentane'),
    ('nhex','n-Hexane'), ('nhep','n-Heptane'), ('noct','n-Octane'),('nnon','n-Nonane'), ('ndec','n-Decane'), ("none", "Not initialised")])

    if form.T.data==None and form.P.data==None:
        component = "met"
        T = 100
        P = 500
        errors = False
    elif not form.validate_on_submit():
        component = form.component.data
        T = 100
        P = 500
        errors = True
    #if form is 100% okay
    elif form.validate_on_submit():
        component = form.component.data
        T = form.T.data
        P = form.P.data
        errors = False
    
    system = Antoine(chemicals[component], T, P)
    return render_template("purevle.html", errors=errors, form=form, chemicals=chemicals, system=system)

# BINARY VLE PAGE
@app.route("/binaryvle", methods=["GET","POST"])
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

    return render_template("binaryvle.html", form=form, graphJSON=graphJSON, plot_type=plot_type, system=system, chemicals=chemicals, plots=plots, errors=errors, exceed=exceed)

@app.route("/steam", methods=["GET","POST"])
def steam():
    if request.method == "GET":
        system = Steam(50, 100)
        system.instantiate()
        return render_template("steam.html", v = system.v)
    
    else:
        T = flask.request.values.get('T')
        P = flask.request.values.get('P')
        system = Steam(T, P)
        system.instantiate()
        return render_template("steam.html", v = system.v)


if __name__ == "__main__":
    app.run(debug=True)
