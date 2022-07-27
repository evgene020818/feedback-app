from flask import Flask, render_template, request, redirect, Response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import uuid

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///feedback.db'
db = SQLAlchemy(app)

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(2000), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return '<Feedback %r>' % self.id

def log_action(action, form):
  in_file = open('logs.json', 'r')
  logs = json.load(in_file)
  in_file.close()
  log = {
    "id": len(logs['logs']),
    "action": action,
    "form": {
      'id': form.id,
      'first_name': form.first_name,
      'last_name': form.last_name,
      'email': form.email,
      'content': form.content
    },
    "created_at": str(datetime.utcnow())
  }
  logs['logs'].append(log)
  print(logs)
  out_file = open("logs.json", "w")
  json.dump(logs, out_file, indent = 4)
  out_file.close()

@app.route('/', methods=['GET', 'POST'])
def index():
  if request.method == 'POST':
    first_name = request.form['firstName']
    last_name = request.form['lastName']
    email = request.form['email']
    content = request.form['feedback']
    new_feedback = Feedback(
      first_name=first_name,
      last_name=last_name,
      email=email,
      content=content)
    try:
      db.session.add(new_feedback)
      db.session.commit()
      log_action('create', new_feedback)
      return redirect('/')
    except:
      err = 'There was a problem submitting your feedback'
      return render_template('404.html', errMsg=err)

  else:
    list = Feedback.query.order_by(Feedback.created_at).all()
    return render_template('index.html', feedback_list=list)

@app.route('/feedback-form/<int:id>')
def get_form(id):
  try:
    form = Feedback.query.get_or_404(id)
    return render_template('form.html', form=form)
  except:
    errMsg='There is no feedback form with this id.'
    return render_template('404.html', err_msg=errMsg)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_form(id):
  try:
    form = Feedback.query.get_or_404(id)
    if request.method == 'POST':
      form.first_name = request.form['firstName']
      form.last_name = request.form['lastName']
      form.email = request.form['email']
      form.content = request.form['feedback']
      try:
        db.session.commit()
        log_action('edit', form)
        return render_template('edit.html', form=form, success=True)
      except:
        err_msg='There was a problem updating the form'
        return render_template('404.html', err_msg)
    else:
      return render_template('edit.html', form=form)
    
  except:
    err_msg='There is no feedback form with this id.'
    return render_template('404.html', err_msg=err_msg)
    
@app.route('/delete/<int:id>')
def delete(id):
    form_to_delete = Feedback.query.get_or_404(id)

    try:
        db.session.delete(form_to_delete)
        db.session.commit()
        log_action('delete', form_to_delete)
        return redirect('/')
    except:
        err_msg = 'There was a problem deleting the form'
        return render_template('404.html', err_msg)

# see logs.json file
@app.route('/logs')
def get_logs():
  try:
    in_file = open('logs.json', 'r')
    log_file_content = json.load(in_file)
    return render_template('logs.html', logs=log_file_content['logs'])
  except:
    errMsg='There is no feedback form with this id.'
    return render_template('404.html', err_msg=errMsg)

# get logs.json file
@app.route('/get_logs_file')
def get_logs_file():
  with open('logs.json') as f:
    feedback = json.load(f)

  return Response(json.dumps(feedback),
    mimetype='application/json',
    headers={'Content-Disposition': 'attachment; filename=logs.json'})


if __name__ == "__main__":
  app.run(debug=True)