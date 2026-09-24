import os
from flask import Flask, render_template, send_from_directory, request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource, abort

# Initializing the Flask application instance
app = Flask(__name__)

#  Using an absolute path for SQLite to prevent 'unable to open database file' ---
basedir = os.path.abspath(os.path.dirname(__file__))
db_dir = os.path.join(basedir, 'database')
os.makedirs(db_dir, exist_ok=True)  # Ensures the 'database' folder always exists

app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(db_dir, "crime_data.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)  # Connects SQLAlchemy to Flask app
api = Api(app)

# Ensuring the database directory exists
os.makedirs(os.path.join(app.root_path, 'database'), exist_ok=True)


# SQLAlchemy Model Mapping to the Existing Table from DB
class ChicagoCrime(db.Model):
    __tablename__ = 'chicago_crime'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    case_number = db.Column(db.String(50), nullable=False, unique=True)
    date = db.Column(db.String(50), nullable=False)
    primary_type = db.Column(db.String(100), nullable=False)
    location_desc = db.Column(db.String(100), nullable=False)
    arrest = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f'<Crime(Case:{self.case_number}, Type:{self.primary_type})>'

    def to_dict(self):
        """Helper method to convert model instance to dictionary for JSON API response."""
        return {
            "id": self.id,
            "case_number": self.case_number,
            "date": self.date,
            "primary_type": self.primary_type,
            "location_desc": self.location_desc,
            "arrest": self.arrest
        }


# --- RESTful API Resources for CRUD Operations ---

class CrimeListResource(Resource):
    def get(self):
        """READ: Fetch all crime records."""
        crimes = ChicagoCrime.query.all()
        return [crime.to_dict() for crime in crimes], 200

    def post(self):
        """CREATE: Add a new crime record."""
        data = request.get_json()
        
        if not data or not all(k in data for k in ("case_number", "date", "primary_type", "location_desc", "arrest")):
            return {"message": "Missing required fields"}, 400
        case_num = data['case_number']
        # Checking if case_number already exists
        if ChicagoCrime.query.filter_by(case_number=case_num).first():
            return {"message": "Crime record with this case number already exists"}, 409

        new_crime = ChicagoCrime(
            
            case_number=data['case_number'],
            date=data['date'],
            primary_type=data['primary_type'],
            location_desc=data['location_desc'],
            arrest=bool(data['arrest'])
        )

        db.session.add(new_crime)
        db.session.commit()
        df= ChicagoCrime.query.all()
        print(len(df))
        
        return {"message": "Crime record created successfully", "case_number": case_num}, 201


class CrimeResource(Resource):
    def get(self, crime_id):
        """READ: Fetch a single crime record by ID."""
        crime = ChicagoCrime.query.get_or_404(crime_id)
        return crime.to_dict(), 200

    def put(self, crime_id):
        """UPDATE: Modify an existing crime record."""
        crime = ChicagoCrime.query.get_or_404(crime_id)
        data = request.get_json()

        if not data:
            return {"message": "No input data provided"}, 400

        crime.case_number = data.get('case_number', crime.case_number)
        crime.date = data.get('date', crime.date)
        crime.primary_type = data.get('primary_type', crime.primary_type)
        crime.location_desc = data.get('location_desc', crime.location_desc)
        crime.arrest = bool(data.get('arrest', crime.arrest))

        db.session.commit()
        return crime.to_dict(), 200

    def delete(self, crime_id):
        """DELETE: Remove a crime record by ID."""
        crime = ChicagoCrime.query.get_or_404(crime_id)
        
        db.session.delete(crime)
        db.session.commit()
        
        return {"message": f"Successfully deleted crime record with id {crime_id}"}, 200


# Registering API Endpoints
api.add_resource(CrimeListResource, '/api/crimes')
api.add_resource(CrimeResource, '/api/crimes/<int:crime_id>')


# --- UI & Static Routes ---

plot_folder = os.path.abspath('plots')

@app.route('/plots/<path:filename>')
def custom_plot_loader(filename):
    """Helper route to fetch individual saved charts from the local directory."""
    return send_from_directory(plot_folder, filename)

@app.route('/')
def home_dashboard():
    """Main route handler to fetch all generated graphs and render to the UI."""
    try:
        available_plots = [
            f for f in os.listdir(plot_folder) 
            if f.lower().endswith(('.png', '.jpg', '.jpeg'))
        ]
    except FileNotFoundError:
        available_plots = []  # Fallback if directory isn't found locally
    
    # Fetching all rows from the existing 'chicago_crime' table via SQLAlchemy
    crime_records = ChicagoCrime.query.all()
    print(f"DEBUG: Found {len(crime_records)} crime records in the database.")
    return render_template('dashboard.html', charts=available_plots[::-1],crimes=crime_records)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Creates database tables if they don't already exist
    app.run(debug=True)