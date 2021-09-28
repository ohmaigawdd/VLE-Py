from flask_wtf import FlaskForm
from wtforms.fields import SelectField, SubmitField, FloatField, IntegerField
from wtforms.validators import NumberRange

class RealReactorForm(FlaskForm):

    reactorType = SelectField("Type of Reactor: ", choices = [("cstr","CSTR"), ("pfr","PFR")], render_kw={'onchange': "optionChange()"})

    tracerType = SelectField("Type of Tracer Input: ", choices = [("pulse","Pulse"), ("step","Step")])

    problemType_cstr = SelectField("Type of Non-ideality: ", choices = [("poor impeller design","Poor Impeller Design"), ("poor outlet design","Poor Outlet Design")])
    problemType_pfr = SelectField("Type of Non-ideality: ", choices = [("reactor fouling","Reactor Fouling"), ("poor bed packing","Poor Bed Packing")])

    submit = SubmitField("Submit") 

class IdealReactorForm(FlaskForm):
    
    reactorType = SelectField("Type of Reactor: ", choices = [("cstr","CSTR"), ("pfr","PFR")])

    reactorVol = IntegerField("Reactor Volume (V): ", validators=[NumberRange(0, 20, message=("Volume out of range!"))], render_kw={'placeholder': "From 0 - 20"})

    reactorFlow = IntegerField("Flow Rate (Q): ", validators=[NumberRange(0, 5, message=("Flow rate out of range!"))], render_kw={'placeholder': "From 0 - 5"})

    tracerType = SelectField("Type of Tracer Input: ", choices = [("pulse","Pulse"), ("step","Step")])

    submit = SubmitField("Submit") 

class PureForm(FlaskForm):

    #Range of T and P as given by Pyxsteam
    T_isot = IntegerField("Start Temperature (T in \u00b0C): ", validators=[NumberRange(1, 374, message=("Temperature out of range!"))], render_kw={'placeholder': "From 1 - 374"})
    T_isob = IntegerField("Start Temperature (T in \u00b0C): ", validators=[NumberRange(1, 374, message=("Temperature out of range!"))], render_kw={'placeholder': "From 1 - 374"})

    P_isot = IntegerField("Start Pressure (P in kPa): ", validators=[NumberRange(100, 22100, message=("Pressure out of range!"))], render_kw={'placeholder': "From 100 - 22100"})
    P_isob = IntegerField("Start Pressure (P in kPa): ", validators=[NumberRange(100, 4154, message=("Pressure out of range!"))], render_kw={'placeholder': "From 100 - 4154"})
    
    processType = SelectField("Process: ", choices = [("Isotherm","Isothermal"), ("Isobar","Isobaric")], render_kw={'onchange': "optionChange()"})

    submit = SubmitField("Submit") 

class BinaryForm(FlaskForm):

    componentA = SelectField("Component A ", choices = [('met','Methane'),('ethy','Ethylene'),('eth','Ethane'),('propy','Propylene'),
    ('prop','Propane'), ('isob','Isobutane') , ('nbut','n-Butane'), ('isop','Isopentane'), ('npent','n-Pentane'),
    ('nhex','n-Hexane'), ('nhep','n-Heptane'), ('noct','n-Octane'),('nnon','n-Nonane'), ('ndec','n-Decane')])

    componentB = SelectField("Component B ", choices = [('met','Methane'),('ethy','Ethylene'),('eth','Ethane'),('propy','Propylene'),
    ('prop','Propane'), ('isob','Isobutane') , ('nbut','n-Butane'), ('isop','Isopentane'), ('npent','n-Pentane'),
    ('nhex','n-Hexane'), ('nhep','n-Heptane'), ('noct','n-Octane'),('nnon','n-Nonane'), ('ndec','n-Decane')])

    plot_type = SelectField("Plot Type: ", choices = [("Pxy","P-x-y"), ("Txy","T-x-y"), ("yxP","y-x (const P)"), ("yxT","y-x (const T)")])

    T = FloatField("Temperature (T in \u00b0C): ", validators=[NumberRange(-70, 200, message=("Temperature out of range!"))], render_kw={'placeholder': "From -70 - 200"})

    P = FloatField("Pressure (P in kPa): ", validators=[NumberRange(101.3, 6000, message=("Pressure out of range!"))], render_kw={'placeholder': "From 101.3 - 6000"})

    z = FloatField("Overall Composition (w.r.t. Component A): ", validators=[NumberRange(0, 1, message=("Composition out of range!"))], render_kw={'placeholder': "From 0.00 - 1.00"})

    submit = SubmitField("Submit") 
