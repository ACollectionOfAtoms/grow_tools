import sqlite3
from contextlib import closing
from flask import Flask, request, redirect, url_for, render_template, jsonify, \
                  g, session, url_for, abort, render_template, flash
from wtforms import Form, BooleanField, TextField, validators

DEBUG = True
SECRET_KEY = 'super secret key'
DATABASE = '/tmp/plants.db'

app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route('/')
def show_results():
    form = PlantForm(request.form)
    return render_template('index.html', form=form)

@app.route('/submit', methods=['GET', 'POST'])
def submit_form():
    form = PlantForm(request.form)
    if request.method == 'POST' and form.validate():
        g.db.execute('insert into plants (plant_name, sci_name) values (?, ?)',
                      [form.plant_name.data, form.sci_name.data])
        g.db.commit()
        cur = g.db.execute('select plant_name, sci_name from plants order by id desc')
        entries = [dict(plant_name=row[0], sci_name=[1]) for row in cur.fetchall()]
        flash('Plant data saved')
        return render_template('success.html',plants=entries)

class PlantForm(Form):
    plant_name = TextField('Plant Name', [validators.Length(min=2)])
    sci_name = TextField('Scientific Name', [validators.Length(min=5)])

if __name__ == '__main__':
    app.run()
