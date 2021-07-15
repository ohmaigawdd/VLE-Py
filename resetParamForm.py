from flask_wtf import FlaskForm
from wtforms.fields import SelectField, SubmitField, FloatField
from wtforms.validators import NumberRange

class PureForm(FlaskForm):


    T = FloatField("Temperature (T): ", validators=[NumberRange(-70, 200, message=("Temperature out of range!"))])

    P = FloatField("Pressure (P): ", validators=[NumberRange(101.3, 6000, message=("Pressure out of range!"))])

    submit = SubmitField("Submit") 

class BinaryForm(FlaskForm):

    componentA = SelectField("Component A ", choices = [('met','Methane'),('ethy','Ethylene'),('eth','Ethane'),('propy','Propylene'),
    ('prop','Propane'), ('isob','Isobutane') , ('nbut','n-Butane'), ('isop','Isopentane'), ('npent','n-Pentane'),
    ('nhex','n-Hexane'), ('nhep','n-Heptane'), ('noct','n-Octane'),('nnon','n-Nonane'), ('ndec','n-Decane')])

    componentB = SelectField("Component B ", choices = [('met','Methane'),('ethy','Ethylene'),('eth','Ethane'),('propy','Propylene'),
    ('prop','Propane'), ('isob','Isobutane') , ('nbut','n-Butane'), ('isop','Isopentane'), ('npent','n-Pentane'),
    ('nhex','n-Hexane'), ('nhep','n-Heptane'), ('noct','n-Octane'),('nnon','n-Nonane'), ('ndec','n-Decane')])

    plot_type = SelectField("Plot Type: ", choices = [("yxP","y-x (const P)"), ("yxT","y-x (const T)"), ("Txy","T-x-y"), ("Pxy","P-x-y")])

    T = FloatField("Temperature (T): ", validators=[NumberRange(-70, 200, message=("Temperature out of range!"))])

    P = FloatField("Pressure (P): ", validators=[NumberRange(101.3, 6000, message=("Pressure out of range!"))])

    z = FloatField("Overall Composition (w.r.t. Component A): ", validators=[NumberRange(0, 1, message=("Composition out of range!"))])

    submit = SubmitField("Submit") 
