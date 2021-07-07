from flask import Flask, json,render_template,request,redirect,session
from flask.helpers import url_for
from flask_sqlalchemy import SQLAlchemy
from flask_googlemaps import GoogleMaps
import csv


app = Flask(__name__)
app.secret_key = "my secret key // will be updated"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///application.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id_no = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(50),nullable=False)
    lastName = db.Column(db.String(50))
    email = db.Column(db.String(50),nullable=False)
    password = db.Column(db.String(100),nullable=False)
    mobile = db.Column(db.String(20),nullable=False)
    id_proof = db.Column(db.String(200),nullable=False)
    village_id = db.Column(db.Integer, default = -1)
    def __repr__(self) -> str:
        return f"{self.id_no} - {self.firstName}"

class Village(db.Model):
    village_id = db.Column(db.Integer, primary_key=True)
    village_name = db.Column(db.String(50),nullable=False)
    district = db.Column(db.String(50),nullable=False)
    state = db.Column(db.String(50),nullable=False)
    pincode = db.Column(db.String(50),nullable=False)
    head_email = db.Column(db.String(50),nullable=False)
    population = db.Column(db.Integer,default=0)
    def __repr__(self) -> str:
        return f"{self.village_id} - {self.village_name}"

class Image(db.Model):
    image_id = db.Column(db.Integer, primary_key=True)
    image_title = db.Column(db.String(50),nullable=False)
    image_description = db.Column(db.String(200),nullable=False)
    image_url = db.Column(db.String(300),nullable=False)
    village_id = db.Column(db.Integer,nullable=False)
    def __repr__(self) -> str:
        return f"{self.image_title}"

class Issue(db.Model):
    issue_id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(50),nullable=False)
    description = db.Column(db.String(200),nullable=False)
    status = db.Column(db.String(10),default="Open")
    raised_by = db.Column(db.String(50),nullable=False)
    village_id = db.Column(db.Integer,nullable=False)
    def __repr__(self) -> str:
        return f"{self.issue_id} - {self.subject}"


@app.route('/admin',methods=['GET','POST'])
def admin():
    if request.method == 'POST':
        village_name = request.form['village_name']
        district = request.form['district']
        state = request.form['state']
        # pincode = request.form['pincode']
        # lat = request.form['lat']
        # long = request.form['long']
        # headsemail = request.form['headsemail']
        village  = Village(
            village_name = village_name,
            district = district,
            state = state,
            pincode = 100,
            head_email = 'headsemail'
        )
        db.session.add(village)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('admin.html')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if 'user' in session:
        session.pop('user')
    if 'village' in session:
        session.pop('village')
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        allUsers = User.query.all()
        userFound = False
        for user in allUsers:
            print(user.email,user.password)
            print('entered',email,password)
            if user.email == email and user.password == password:
                userFound = True
                if user.village_id == -1:
                    session['user'] = {
                        "email": user.email,
                        "first_name": user.firstName,
                    }
                else:
                    session['user'] = {
                        "email": user.email,
                        "first_name": user.firstName,
                        'village_id': str(user.village_id),
                    }
                    village = Village.query.filter_by(village_id = user.village_id).first()
                    session['village'] = {
                        'village_id': village.village_id,
                        'village_name': village.village_name,
                        'district': village.district,
                        'state': village.state,
                        'pincode': village.pincode,
                        'head_email': village.head_email,
                        'population': village.population,
                    }
                # return render_template('dashboard.html',user = session['user'])
            if userFound:
                return redirect(url_for('dashboard'))
        if userFound == False:
            return render_template('index.html',us="invalid credentials")
    return render_template('index.html')

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        firstName = request.form['firstname']
        lastName = request.form['lastname']
        email = request.form['email']
        mobile = request.form['mobile']
        password = request.form['password']
        id_proof = request.files['idfile']
        filePath = './static/' + email + '_' +  id_proof.filename
        id_proof.save(filePath)
        user = User(firstName=firstName,lastName=lastName,email=email,mobile=mobile,password=password,id_proof=filePath)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    print(session['user'])
    if 'village_id' in session['user']:
        print(session['village'])
    allVillages = Village.query.all()
    if 'village' in session:
        return render_template('dashboard.html',user = session['user'], village = session['village'])    
    return render_template('dashboard.html',user = session['user'],allVillages=allVillages)

@app.route('/add_village', methods=['POST'])
def add_village():
    village_name = request.form['village']
    print(village_name)
    try:
        village = Village.query.filter_by(village_name = village_name).first()
        print(village)
        if village is not None:
            user = User.query.filter_by(email = session['user']['email']).first()
            print(user)
            print(session['user']['email'])
            user.village_id = village.village_id
            village.population += 1
            try:
                session.pop('user')
                session['user'] = {
                    "email": user.email,
                    "first_name": user.firstName,
                    'village_id': str(user.village_id),
                }
                session['village'] = {
                    'village_id': village.village_id,
                    'village_name': village.village_name,
                    'district': village.district,
                    'state': village.state,
                    'pincode': village.pincode,
                    'head_email': village.head_email,
                    'population': village.population,
                }
            except Exception as e:
                print(e)
            print(session['user'])
            print(session['village'])
            db.session.add(user)
            db.session.add(village)
            db.session.commit()
        else:
            print("[info] : no village found of that name")
    except:
        print("[error] : no village found of that name")
    print(village)
    return redirect(url_for('dashboard',))
    # return render_template('dashboard.html',user = session['user'])

@app.route('/leave_village')
def leave_village():
    try:
        user = User.query.filter_by(email = session['user']['email']).first()
        user.village_id = -1
        session.pop('user')
        session['user'] = {
            'email': user.email,
            "first_name": user.firstName,
        }
        db.session.add(user)
        db.session.commit()

        village = Village.query.filter_by(village_id = session['village']['village_id']).first()
        village.population -= 1
        db.session.add(village)
        db.session.commit()
        session.pop('village')
        
        print()
    except Exception as e:
        print(e)
    return redirect(url_for('dashboard',))

@app.route('/village_gallary')
def village_gallary():
    if 'user' not in session:
        return redirect(url_for('login'))
    if 'village' in session:
        allImages = Image.query.filter_by(village_id = session['village']['village_id']).all()
        return render_template('village_gallary.html',user = session['user'], allImages = allImages)    
    return render_template('village_gallary.html',user = session['user'])

@app.route('/add_image', methods=['GET','POST'])
def add_image():
    if request.method == 'POST':
        image_title = request.form['image_title']
        image_description = request.form['image_description']
        image_url = request.files['imagefile']
        village_id = session['village']['village_id']
        filePath = './static/images/' + str(village_id) + '_' + image_title +  image_url.filename
        image_url.save(filePath)
        image = Image(image_title=image_title, image_description=image_description, image_url=filePath, village_id=village_id)
        db.session.add(image)
        db.session.commit()
    return redirect(url_for('village_gallary',))
    
@app.route('/villagers')
def villagers():
    if 'user' not in session:
        return redirect(url_for('login'))
    if 'village' in session:
        villagers = User.query.filter_by(village_id = session['village']['village_id']).all()
        return render_template('villagers.html',user = session['user'], villagers = villagers)    
    return render_template('villagers.html',user = session['user'])

@app.route('/issues')
def issues():
    if 'user' not in session:
        return redirect(url_for('login'))
    if 'village' in session:
        allIssues = Issue.query.filter_by(village_id = session['user']['village_id']).all()
        allIssues.sort(key=lambda x: x.status, reverse=True)
        print(allIssues)
        return render_template('issues.html',user = session['user'], allIssues=allIssues)
    return render_template('issues.html',user = session['user'])
    

@app.route('/add_issue', methods=['GET','POST'])
def add_issue():
    if request.method == 'POST':
        subject = request.form['subject']
        description = request.form['description']
        issue = Issue(subject=subject, description=description, raised_by=session['user']['first_name'], village_id = session['user']['village_id'])
        db.session.add(issue)
        db.session.commit()
    return redirect(url_for('issues',))

@app.route('/close_issue/<int:issue_id>')
def close_issue(issue_id):
    issue = Issue.query.filter_by(issue_id = issue_id).first()
    issue.status = "Closed"
    db.session.add(issue)
    db.session.commit()
    return redirect(url_for('issues',))

@app.route('/myprofile')
def myprofile():
    if 'user' not in session:
        return redirect(url_for('login'))
    userdetails = User.query.filter_by(email = session['user']['email']).first()
    return render_template('myprofile.html',user = session['user'], userdetails=userdetails)

@app.route('/update_details',methods=['GET','POST'])
def update_details():
    userdetails = User.query.filter_by(email = session['user']['email']).first()
    if request.method == 'GET':
        return render_template('update_details.html', userdetails = userdetails)
    else:
        firstName = request.form['firstname']
        lastName = request.form['lastname']
        email = request.form['email']
        mobile = request.form['mobile']
        userdetails.firstName = firstName
        userdetails.lastName = lastName
        userdetails.email = email
        userdetails.mobile = mobile
        db.session.add(userdetails)
        db.session.commit()
        session.pop('user')
        return redirect(url_for('login'))

@app.route('/update_password',methods=['GET','POST'])
def update_password():
    if request.method == 'GET':
        return render_template('update_password.html')
    else:
        userdetails = User.query.filter_by(email = session['user']['email']).first()
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        conf_password = request.form['conf_password']
        if userdetails.password != old_password:
            return render_template('update_password.html', wrong=True)
        elif new_password != conf_password:
            return render_template('update_password.html', mismatch=True)
        else:
            userdetails.password = new_password
            db.session.add(userdetails)
            db.session.commit()
            return redirect(url_for('login'))

@app.route('/contact_admin')
def contact_admin():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('contact_admin.html',user = session['user'])

@app.route('/logout')
def logout():
    if 'user' in session:
        session.pop('user')
    return redirect(url_for('home'))

@app.route('/test')
def test():
    return render_template('temp.html')

if __name__ == '__main__':
    app.run(debug=True)