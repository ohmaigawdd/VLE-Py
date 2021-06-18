from flask import Flask, render_template, session #, request
from flask_wtf import FlaskForm
from wtforms.fields import SelectField, SubmitField, html5
'''import RachfordRice'''

app = Flask(__name__)

app.config["SECRET_KEY"] = "mykey"

class InfoForm(FlaskForm):

    componentA = SelectField("Component A: ", choices = [('met','Methane'),('ethy','Ethylene'),('eth','Ethane'),('propy','Propylene'),
    ('prop','Propane'), ('isob','Isobutane') , ('nbut','n-Butane'), ('isop','Isopentane'), ('npent','n-Pentane'),
    ('nhex','n-Hexane'), ('nhep','n-Heptane'), ('noct','n-Octane'),('nnon','n-Nonane'), ('ndec','n-Decane')])

    componentB = SelectField("Component B: ", choices = [('met','Methane'),('ethy','Ethylene'),('eth','Ethane'),('propy','Propylene'),
    ('prop','Propane'), ('isob','Isobutane') , ('nbut','n-Butane'), ('isop','Isopentane'), ('npent','n-Pentane'),
    ('nhex','n-Hexane'), ('nhep','n-Heptane'), ('noct','n-Octane'),('nnon','n-Nonane'), ('ndec','n-Decane')])

    plot_type = SelectField("Plot Type: ", choices = [("yxP","y-x (const P)"), ("yxT","y-x (const T)"), ("Txy","T-x-y"), ("Pxy","P-x-y")])

    T = html5.DecimalRangeField("Temperature: ")

    P = html5.DecimalRangeField("Pressure: ")

    z = html5.DecimalRangeField("Overall Composition: ")

    submit = SubmitField("Submit") 


@app.route("/", methods=["GET","POST"])
def index():

    form = InfoForm()

    chemicals = dict([('met','Methane'),('ethy','Ethylene'),('eth','Ethane'),('propy','Propylene'),
    ('prop','Propane'), ('isob','Isobutane') , ('nbut','n-Butane'), ('isop','Isopentane'), ('npent','n-Pentane'),
    ('nhex','n-Hexane'), ('nhep','n-Heptane'), ('noct','n-Octane'),('nnon','n-Nonane'), ('ndec','n-Decane')])

    plots = dict([("yxP","y-x (const P)"), ("yxT","y-x (const T)"), ("Txy","T-x-y"), ("Pxy","P-x-y")])
    
    if form.T.data==None and form.P.data==None and form.z.data==None:
        componentA = 'met'
        componentB = 'ethy'
        plot_type = 'yxP'        
        T = 0.00
        P = 101.00
        z = 0.00

    if form.validate_on_submit():

        componentA = form.componentA.data
        componentB = form.componentB.data
        plot_type = form.plot_type.data
        T = form.T.data
        P = form.P.data
        z = form.z.data

    return render_template("basic.html", form=form, componentA=componentA, componentB=componentB, plot_type=plot_type, T=T, P=P, z=z, chemicals=chemicals, plots=plots)


if __name__ == "__main__":
    app.run(debug=True)
