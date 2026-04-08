"""
Flask Routes - Dashboard, CRUD Operations, and ML Prediction APIs
"""
from flask import Blueprint, render_template, request, jsonify, send_file, redirect, url_for, session
from models.database import db, User, Athlete, Event, Injury, TalentMetric, InjuryRiskAssessment, TrainingSession
from ml.ml_models import InjuryRiskModel, TalentIdentificationModel
from datetime import datetime, timedelta
from sqlalchemy import func
import os
import csv
import io
from io import StringIO, BytesIO
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash

# Create blueprints
main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__)

# Initialize ML models
injury_risk_model = InjuryRiskModel()
talent_model = TalentIdentificationModel()

# Demo credentials (kept for testing)
DEMO_USERS = {
    'admin': 'admin123'
}

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

# Role-based access control decorators
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('main.login'))
        if session.get('user_role') != 'admin':
            return redirect(url_for('main.dashboard'))  # Redirect non-admin users
        return f(*args, **kwargs)
    return decorated_function

def coach_or_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('main.login'))
        role = session.get('user_role')
        if role not in ['admin', 'coach']:
            return redirect(url_for('main.dashboard'))  # Redirect non-coach/admin users
        return f(*args, **kwargs)
    return decorated_function

# ==================== AUTH ROUTES ====================

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Try to find user in database first
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['user_name'] = user.username
            session['user_role'] = user.role
            session['user_sport'] = user.sport_specialization
            return redirect(url_for('main.dashboard'))
        
        return render_template('login.html', error='Invalid credentials', tab='login')
    
    return render_template('login.html', tab='login')

@main_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """Signup page"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        full_name = request.form.get('full_name', '').strip()
        role = request.form.get('role', 'user').strip()  # admin, coach, or user
        sport_specialization = request.form.get('sport_specialization', '').strip() if role == 'coach' else None
        
        # Validation
        if not username or len(username) < 3:
            return render_template('login.html', error='Username must be at least 3 characters', tab='signup')
        
        if not email or '@' not in email:
            return render_template('login.html', error='Please enter a valid email', tab='signup')
        
        if not password or len(password) < 6:
            return render_template('login.html', error='Password must be at least 6 characters', tab='signup')
        
        if password != confirm_password:
            return render_template('login.html', error='Passwords do not match', tab='signup')
        
        if role == 'coach' and not sport_specialization:
            return render_template('login.html', error='Please select a sport for coaching', tab='signup')
        
        if role not in ['coach', 'user']:
            return render_template('login.html', error='Invalid role selected', tab='signup')
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            return render_template('login.html', error='Username already exists', tab='signup')
        
        if User.query.filter_by(email=email).first():
            return render_template('login.html', error='Email already registered', tab='signup')
        
        # Create new user
        try:
            new_user = User(
                username=username,
                email=email,
                password=generate_password_hash(password),
                full_name=full_name,
                role=role,
                sport_specialization=sport_specialization
            )
            db.session.add(new_user)
            db.session.commit()
            
            # Log them in
            session['user_id'] = new_user.id
            session['user_name'] = new_user.username
            session['user_role'] = new_user.role
            session['user_sport'] = new_user.sport_specialization
            return redirect(url_for('main.dashboard'))
        except Exception as e:
            db.session.rollback()
            return render_template('login.html', error=f'Signup failed: {str(e)}', tab='signup')
    
    return render_template('login.html', tab='signup')

@main_bp.route('/logout')
def logout():
    """Logout"""
    session.clear()
    return redirect(url_for('main.login'))

# ==================== MAIN ROUTES ====================

@main_bp.route('/')
@main_bp.route('/')
@login_required
def dashboard():
    """Main dashboard view"""
    try:
        user_role = session.get('user_role', 'user')
        user_sport = session.get('user_sport')
        
        # Build query based on role - create fresh queries for each operation
        if user_role == 'coach':
            # Coaches see only their sport
            total_athletes = Athlete.query.filter_by(sport=user_sport).count()
            total_events = Event.query.count()
            injury_query_base = Injury.query.join(Athlete).filter(Athlete.sport == user_sport)
            total_injuries = injury_query_base.count()
            
            # Get injury trends (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_injury_count = injury_query_base.filter(
                Injury.date_occurred >= thirty_days_ago
            ).count()
            
            top_performers = Athlete.query.filter_by(sport=user_sport).order_by(Athlete.performance_score.desc()).limit(4).all()
            recent_events = Event.query.order_by(Event.date.desc()).limit(5).all()
            all_athletes = Athlete.query.filter_by(sport=user_sport).all()
            
        elif user_role == 'user':
            # Users see only their sport (but limited data)
            if user_sport:
                total_athletes = Athlete.query.filter_by(sport=user_sport).count()
                all_athletes = Athlete.query.filter_by(sport=user_sport).all()
                top_performers = Athlete.query.filter_by(sport=user_sport).order_by(Athlete.performance_score.desc()).limit(4).all()
            else:
                total_athletes = 0
                all_athletes = []
                top_performers = []
            
            total_events = 0  # Users can't see events
            total_injuries = 0  # Users can't see injury data
            recent_injury_count = 0
            recent_events = []
            
        else:
            # Admin sees all
            total_athletes = Athlete.query.count()
            total_events = Event.query.count()
            injury_query_base = Injury.query
            total_injuries = injury_query_base.count()
            
            # Get injury trends (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_injury_count = injury_query_base.filter(
                Injury.date_occurred >= thirty_days_ago
            ).count()
            
            top_performers = Athlete.query.order_by(Athlete.performance_score.desc()).limit(4).all()
            recent_events = Event.query.order_by(Event.date.desc()).limit(5).all()
            all_athletes = Athlete.query.all()
        
        # Get sports count
        sports_count = {}
        for athlete in all_athletes:
            sports_count[athlete.sport] = sports_count.get(athlete.sport, 0) + 1
        
        context = {
            'total_athletes': total_athletes,
            'total_events': total_events,
            'total_injuries': total_injuries,
            'recent_injury_count': recent_injury_count,
            'top_performers': top_performers,
            'recent_events': recent_events,
            'sports_count': list(sports_count.items()) if sports_count else [],
            'athletes': all_athletes,
            'user_role': user_role,
            'user_sport': user_sport
        }
        
        return render_template('dashboard.html', **context)
    except Exception as e:
        print(f"Error: {e}")
        return render_template('dashboard.html', **{'error': str(e), 'total_athletes': 0, 'total_events': 0, 'total_injuries': 0, 'recent_injury_count': 0, 'top_performers': [], 'recent_events': [], 'sports_count': [], 'user_role': session.get('user_role', 'user')})


@main_bp.route('/athletes')
@login_required
def athletes_list():
    """View all athletes"""
    try:
        user_role = session.get('user_role', 'user')
        user_sport = session.get('user_sport')
        
        # Filter based on role
        if user_role == 'coach':
            # Coaches see only their sport
            athletes = Athlete.query.filter_by(sport=user_sport).order_by(Athlete.performance_score.desc()).all()
        elif user_role == 'user':
            # Users see only their sport
            athletes = Athlete.query.filter_by(sport=user_sport).order_by(Athlete.performance_score.desc()).all() if user_sport else []
        else:
            # Admin sees all
            athletes = Athlete.query.order_by(Athlete.performance_score.desc()).all()
        
        return render_template('athletes.html', athletes=athletes, user_role=user_role, user_sport=user_sport)
    except Exception as e:
        return render_template('athletes.html', error=str(e), user_role=session.get('user_role', 'user'))


@main_bp.route('/athlete/add', methods=['POST'])
@coach_or_admin_required
def add_athlete():
    """Add new athlete via form"""
    try:
        user_role = session.get('user_role', 'user')
        user_sport = session.get('user_sport')
        
        name = request.form.get('name', '').strip()
        sport = request.form.get('sport', '').strip()
        age = request.form.get('age', '20')
        
        # Coaches can only add athletes for their sport
        if user_role == 'coach':
            sport = user_sport  # Override with coach's sport
        
        # Validate inputs
        if not name or not sport:
            print("Error: Name and sport are required")
            return redirect(url_for('main.athletes_list'))
        
        try:
            age = int(age) if age else 20
        except ValueError:
            age = 20
        
        # Generate a registration number
        import uuid
        registration_number = f"ATH-{uuid.uuid4().hex[:8].upper()}"
        
        # System will predict performance score - start with default
        athlete = Athlete(
            name=name,
            registration_number=registration_number,
            age=age,
            sport=sport,
            performance_score=50.0,  # Default score, system will improve this
            training_hours_pw=10,
            sleep_hours=8
        )
        
        db.session.add(athlete)
        db.session.commit()
        
        # Generate initial injury risk assessment for new athlete
        import random
        initial_assessment = InjuryRiskAssessment(
            athlete_id=athlete.id,
            training_hours_pw=10,
            prev_injuries=0,
            sleep_hours=8,
            injury_risk_score=random.uniform(0.2, 0.5),  # Start with low-medium risk
            risk_category='Low',
            main_risk_factor='No significant risk factors',
            recommendations='Maintain current training load and sleep schedule. Focus on building fitness gradually.',
            model_confidence=0.75
        )
        db.session.add(initial_assessment)
        db.session.commit()
        
        print(f"Successfully added athlete: {name} with initial risk assessment")
        
        return redirect(url_for('main.athletes_list'))
    except Exception as e:
        print(f"Error adding athlete: {e}")
        db.session.rollback()
        return redirect(url_for('main.athletes_list'))


@main_bp.route('/delete_athlete', methods=['POST'])
@coach_or_admin_required
def delete_athlete_form():
    """Delete athlete via form POST"""
    try:
        user_role = session.get('user_role', 'user')
        user_sport = session.get('user_sport')
        
        athlete_id = request.form.get('athlete_id')
        athlete = Athlete.query.get(athlete_id)
        
        if athlete:
            # Coaches can only delete athletes from their sport
            if user_role == 'coach' and athlete.sport != user_sport:
                print(f"Error: Coach cannot delete athlete from {athlete.sport}")
                return redirect(url_for('main.athletes_list'))
            
            db.session.delete(athlete)
            db.session.commit()
        
        return redirect(url_for('main.athletes_list'))
    except Exception as e:
        print(f"Error deleting athlete: {e}")
        return redirect(url_for('main.athletes_list'))


@main_bp.route('/athlete/<int:athlete_id>/delete', methods=['POST'])
@login_required
def delete_athlete_route(athlete_id):
    """Delete athlete via POST"""
    try:
        athlete = Athlete.query.get(athlete_id)
        if athlete:
            db.session.delete(athlete)
            db.session.commit()
            return jsonify({'success': True})
        return jsonify({'error': 'Athlete not found'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@main_bp.route('/athlete/<int:athlete_id>')
@login_required
def athlete_detail(athlete_id):
    """View athlete detail and health metrics"""
    try:
        athlete = Athlete.query.get_or_404(athlete_id)
        injuries = Injury.query.filter_by(athlete_id=athlete_id).order_by(Injury.date_occurred.desc()).all()
        talent_metrics = TalentMetric.query.filter_by(athlete_id=athlete_id).order_by(TalentMetric.assessment_date.desc()).all()
        risk_assessments = InjuryRiskAssessment.query.filter_by(athlete_id=athlete_id).order_by(InjuryRiskAssessment.assessment_date.desc()).limit(5).all()
        training_sessions = TrainingSession.query.filter_by(athlete_id=athlete_id).order_by(TrainingSession.session_date.desc()).all()
        
        return render_template('athlete_detail.html', 
                             athlete=athlete, 
                             injuries=injuries,
                             talent_metrics=talent_metrics,
                             risk_assessments=risk_assessments,
                             training_sessions=training_sessions)
    except Exception as e:
        return render_template('athlete_detail.html', error=str(e))


# ==================== TRAINING SESSION ROUTES ====================

@main_bp.route('/athlete/<int:athlete_id>/training/add', methods=['POST'])
@coach_or_admin_required
def add_training_session(athlete_id):
    """Add training session data for an athlete"""
    try:
        athlete = Athlete.query.get_or_404(athlete_id)
        user_role = session.get('user_role', 'user')
        user_sport = session.get('user_sport')
        
        # Coaches can only add training for their sport
        if user_role == 'coach' and athlete.sport != user_sport:
            return jsonify({'error': 'Not authorized'}), 403
        
        performance_rating = request.form.get('performance_rating', '').strip()
        injury_severity = request.form.get('injury_severity', 'no injury').strip()
        notes = request.form.get('notes', '').strip()
        session_date = request.form.get('session_date', '')
        
        # Validate performance rating
        valid_ratings = ['poor', 'good', 'very good', 'excellent']
        if performance_rating not in valid_ratings:
            return jsonify({'error': 'Invalid performance rating'}), 400
        
        # Validate injury severity
        valid_injuries = ['no injury', 'minor injury', 'severe injury']
        if injury_severity not in valid_injuries:
            return jsonify({'error': 'Invalid injury severity'}), 400
        
        # Convert performance rating to percentage
        rating_percentages = {
            'poor': 25,
            'good': 50,
            'very good': 75,
            'excellent': 95
        }
        performance_percentage = rating_percentages.get(performance_rating, 50)
        
        # Parse session date
        try:
            from datetime import datetime
            if session_date:
                try:
                    session_date_obj = datetime.fromisoformat(session_date)
                except:
                    session_date_obj = datetime.strptime(session_date, '%Y-%m-%d')
            else:
                session_date_obj = datetime.utcnow()
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400
        
        # Create training session
        training = TrainingSession(
            athlete_id=athlete_id,
            session_date=session_date_obj,
            performance_rating=performance_rating,
            performance_percentage=performance_percentage,
            injury_severity=injury_severity,
            notes=notes
        )
        
        db.session.add(training)
        
        # Create Injury record if injury severity is not "no injury"
        if injury_severity != 'no injury':
            severity_map = {
                'minor injury': 'Mild',
                'severe injury': 'Severe'
            }
            injury = Injury(
                athlete_id=athlete_id,
                injury_type=f'Training Injury - {performance_rating.capitalize()}',
                severity=severity_map.get(injury_severity, 'Mild'),
                date_occurred=session_date_obj,
                notes=notes or f'Recorded during {performance_rating} performance training'
            )
            db.session.add(injury)
        
        # Create TalentMetric based on training performance
        talent_score = (performance_percentage / 100) * 100  # Use training performance as base
        talent_metric = TalentMetric(
            athlete_id=athlete_id,
            assessment_date=session_date_obj,
            speed_score=talent_score * 0.8,
            strength_score=talent_score * 0.9,
            endurance_score=talent_score,
            agility_score=talent_score * 0.85,
            technique_score=talent_score * 0.95,
            talent_potential=talent_score,
            model_confidence=0.8,
            notes=f'Auto-generated from {performance_rating} training session'
        )
        db.session.add(talent_metric)
        
        # Update athlete's overall performance score based on recent training sessions
        # Calculate average performance from recent sessions
        recent_sessions = TrainingSession.query.filter_by(
            athlete_id=athlete_id
        ).order_by(TrainingSession.session_date.desc()).limit(10).all()
        
        if recent_sessions:
            avg_performance = sum([s.performance_percentage for s in recent_sessions]) / len(recent_sessions)
            athlete.performance_score = avg_performance
        
        # Calculate and update injury risk assessment based on training data
        severe_injury_count = sum([1 for s in recent_sessions if s.injury_severity == 'severe injury'])
        minor_injury_count = sum([1 for s in recent_sessions if s.injury_severity == 'minor injury'])
        total_sessions = len(recent_sessions)
        
        # Calculate injury risk score based on injury data
        injury_risk_score = 0.0
        if total_sessions > 0:
            injury_risk_score = (severe_injury_count * 0.3 + minor_injury_count * 0.1) / total_sessions
            injury_risk_score = min(0.95, injury_risk_score)  # Cap at 0.95
        
        # Determine risk category
        if injury_risk_score < 0.4:
            risk_category = 'Low'
        elif injury_risk_score < 0.7:
            risk_category = 'Medium'
        else:
            risk_category = 'High'
        
        # Determine main risk factor and recommendations
        main_risk_factor = 'Unknown'
        recommendations = 'Continue monitoring athlete performance.'
        
        if severe_injury_count > 0:
            main_risk_factor = 'Previous severe injuries'
            recommendations = 'Focus on injury prevention and rehabilitation. Consider reducing training intensity.'
        elif minor_injury_count >= 2:
            main_risk_factor = 'Multiple minor injuries'
            recommendations = 'Increase focus on proper form and recovery time between sessions.'
        elif athlete.training_hours_pw > 15:
            main_risk_factor = 'High training load'
            recommendations = 'Reduce weekly training hours or increase recovery time.'
        elif athlete.sleep_hours < 6:
            main_risk_factor = 'Insufficient sleep'
            recommendations = 'Improve sleep hygiene. Aim for 7-9 hours per night.'
        elif risk_category == 'Low':
            main_risk_factor = 'Low injury risk factors'
            recommendations = 'Continue current training regimen. Maintain good sleep and recovery habits.'
        
        # Update or create injury risk assessment
        latest_assessment = InjuryRiskAssessment.query.filter_by(
            athlete_id=athlete_id
        ).order_by(InjuryRiskAssessment.assessment_date.desc()).first()
        
        if latest_assessment:
            # Update existing assessment
            latest_assessment.training_hours_pw = athlete.training_hours_pw
            latest_assessment.prev_injuries = severe_injury_count + minor_injury_count
            latest_assessment.sleep_hours = athlete.sleep_hours
            latest_assessment.injury_risk_score = injury_risk_score
            latest_assessment.risk_category = risk_category
            latest_assessment.main_risk_factor = main_risk_factor
            latest_assessment.recommendations = recommendations
            latest_assessment.assessment_date = datetime.utcnow()
            latest_assessment.model_confidence = 0.85
        else:
            # Create new assessment
            new_assessment = InjuryRiskAssessment(
                athlete_id=athlete_id,
                training_hours_pw=athlete.training_hours_pw,
                prev_injuries=severe_injury_count + minor_injury_count,
                sleep_hours=athlete.sleep_hours,
                injury_risk_score=injury_risk_score,
                risk_category=risk_category,
                main_risk_factor=main_risk_factor,
                recommendations=recommendations,
                model_confidence=0.85
            )
            db.session.add(new_assessment)
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Training session added successfully'})
    except Exception as e:
        print(f"Error adding training session: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@main_bp.route('/athlete/<int:athlete_id>/training/<int:training_id>/delete', methods=['POST'])
@coach_or_admin_required
def delete_training_session(athlete_id, training_id):
    """Delete a training session and related records"""
    try:
        athlete = Athlete.query.get_or_404(athlete_id)
        training = TrainingSession.query.get_or_404(training_id)
        user_role = session.get('user_role', 'user')
        user_sport = session.get('user_sport')
        
        # Coaches can only delete training for their sport
        if user_role == 'coach' and athlete.sport != user_sport:
            return jsonify({'error': 'Not authorized'}), 403
        
        # Verify training belongs to athlete
        if training.athlete_id != athlete_id:
            return jsonify({'error': 'Training session not found'}), 404
        
        # Store the training session date to clean up related records
        training_date = training.session_date
        
        # Delete related Injury records from the same date
        injuries_to_delete = Injury.query.filter_by(
            athlete_id=athlete_id
        ).filter(Injury.date_occurred == training_date).all()
        
        for injury in injuries_to_delete:
            db.session.delete(injury)
        
        # Delete related TalentMetric records from the same date
        metrics_to_delete = TalentMetric.query.filter_by(
            athlete_id=athlete_id
        ).filter(TalentMetric.assessment_date == training_date).all()
        
        for metric in metrics_to_delete:
            db.session.delete(metric)
        
        # Delete the training session itself
        db.session.delete(training)
        
        # Recalculate athlete's performance score
        recent_sessions = TrainingSession.query.filter_by(
            athlete_id=athlete_id
        ).order_by(TrainingSession.session_date.desc()).limit(10).all()
        
        if recent_sessions:
            avg_performance = sum([s.performance_percentage for s in recent_sessions]) / len(recent_sessions)
            athlete.performance_score = avg_performance
        else:
            athlete.performance_score = 50.0  # Reset to default
        
        # Recalculate injury risk assessment
        severe_injury_count = sum([1 for s in recent_sessions if s.injury_severity == 'severe injury'])
        minor_injury_count = sum([1 for s in recent_sessions if s.injury_severity == 'minor injury'])
        total_sessions = len(recent_sessions)
        
        # Calculate injury risk score
        injury_risk_score = 0.0
        if total_sessions > 0:
            injury_risk_score = (severe_injury_count * 0.3 + minor_injury_count * 0.1) / total_sessions
            injury_risk_score = min(0.95, injury_risk_score)
        
        # Determine risk category
        if injury_risk_score < 0.4:
            risk_category = 'Low'
        elif injury_risk_score < 0.7:
            risk_category = 'Medium'
        else:
            risk_category = 'High'
        
        # Determine main risk factor and recommendations
        main_risk_factor = 'Unknown'
        recommendations = 'Continue monitoring athlete performance.'
        
        if severe_injury_count > 0:
            main_risk_factor = 'Previous severe injuries'
            recommendations = 'Focus on injury prevention and rehabilitation. Consider reducing training intensity.'
        elif minor_injury_count >= 2:
            main_risk_factor = 'Multiple minor injuries'
            recommendations = 'Increase focus on proper form and recovery time between sessions.'
        elif athlete.training_hours_pw > 15:
            main_risk_factor = 'High training load'
            recommendations = 'Reduce weekly training hours or increase recovery time.'
        elif athlete.sleep_hours < 6:
            main_risk_factor = 'Insufficient sleep'
            recommendations = 'Improve sleep hygiene. Aim for 7-9 hours per night.'
        elif risk_category == 'Low':
            main_risk_factor = 'Low injury risk factors'
            recommendations = 'Continue current training regimen. Maintain good sleep and recovery habits.'
        
        # Update injury risk assessment
        latest_assessment = InjuryRiskAssessment.query.filter_by(
            athlete_id=athlete_id
        ).order_by(InjuryRiskAssessment.assessment_date.desc()).first()
        
        if latest_assessment:
            latest_assessment.training_hours_pw = athlete.training_hours_pw
            latest_assessment.prev_injuries = severe_injury_count + minor_injury_count
            latest_assessment.sleep_hours = athlete.sleep_hours
            latest_assessment.injury_risk_score = injury_risk_score
            latest_assessment.risk_category = risk_category
            latest_assessment.main_risk_factor = main_risk_factor
            latest_assessment.recommendations = recommendations
            latest_assessment.assessment_date = datetime.utcnow()
            latest_assessment.model_confidence = 0.85
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Training session deleted successfully'})
    except Exception as e:
        print(f"Error deleting training session: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@main_bp.route('/athlete/<int:athlete_id>/training/api', methods=['GET'])
@login_required
def get_training_sessions_api(athlete_id):
    """Get training sessions as JSON for AJAX"""
    try:
        athlete = Athlete.query.get_or_404(athlete_id)
        user_role = session.get('user_role', 'user')
        user_sport = session.get('user_sport')
        
        # Coaches can only view training for their sport
        if user_role == 'coach' and athlete.sport != user_sport:
            return jsonify({'error': 'Not authorized'}), 403
        
        training_sessions = TrainingSession.query.filter_by(athlete_id=athlete_id).order_by(
            TrainingSession.session_date.desc()
        ).all()
        
        sessions_data = [s.to_dict() for s in training_sessions]
        
        return jsonify({'success': True, 'sessions': sessions_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main_bp.route('/analytics')
@login_required
def analytics():
    """Predictive analytics dashboard"""
    try:
        # Get all athletes
        athletes = Athlete.query.all()
        total_athletes = len(athletes)
        
        # Get injury risk assessments
        injury_risks = []
        for athlete in athletes:
            latest_assessment = InjuryRiskAssessment.query.filter_by(
                athlete_id=athlete.id
            ).order_by(InjuryRiskAssessment.assessment_date.desc()).first()
            
            if latest_assessment:
                risk_level = 'Low' if latest_assessment.injury_risk_score < 0.4 else 'Medium' if latest_assessment.injury_risk_score < 0.7 else 'High'
                injury_risks.append({
                    'athlete_name': athlete.name,
                    'sport': athlete.sport,
                    'risk_level': risk_level,
                    'risk_score': latest_assessment.injury_risk_score,
                    'recommendations': 'Regular monitoring recommended'
                })
        
        # Calculate statistics
        high_risk_count = len([r for r in injury_risks if r['risk_level'] == 'High'])
        avg_performance = db.session.query(func.avg(Athlete.performance_score)).scalar() or 50
        healthy_count = total_athletes - high_risk_count
        
        # Count talented athletes (top performers)
        total_talents = len([a for a in athletes if a.performance_score >= 75])
        
        # Get sports data for chart
        sports_data = {}
        for athlete in athletes:
            if athlete.sport not in sports_data:
                sports_data[athlete.sport] = []
            sports_data[athlete.sport].append(athlete.performance_score)
        
        sport_labels = list(sports_data.keys())
        sport_performance = [sum(scores) / len(scores) if scores else 0 for scores in sports_data.values()]
        sports_count = [(label, len(sports_data[label])) for label in sport_labels]
        
        # Get training sessions analytics
        all_training_sessions = TrainingSession.query.all()
        training_data = {
            'total_sessions': len(all_training_sessions),
            'performance_ratings': {},
            'injury_severity': {
                'no injury': 0,
                'minor injury': 0,
                'severe injury': 0
            },
            'athletes_with_training': len(set([s.athlete_id for s in all_training_sessions]))
        }
        
        # Count performance ratings
        for session in all_training_sessions:
            rating = session.performance_rating
            if rating:
                training_data['performance_ratings'][rating] = training_data['performance_ratings'].get(rating, 0) + 1
            
            # Count injury severity
            if session.injury_severity:
                training_data['injury_severity'][session.injury_severity] = training_data['injury_severity'].get(session.injury_severity, 0) + 1
        
        return render_template('analytics.html', 
                             injury_risks=injury_risks,
                             high_risk_count=high_risk_count,
                             average_performance=avg_performance,
                             total_athletes=total_athletes,
                             healthy_count=healthy_count,
                             total_talents=total_talents,
                             athletes=athletes,
                             sport_data=sport_labels,
                             sport_performance=sport_performance,
                             sports_count=sports_count,
                             training_data=training_data)
    except Exception as e:
        print(f"Analytics error: {e}")
        return render_template('analytics.html', 
                             injury_risks=[],
                             high_risk_count=0,
                             average_performance=0,
                             total_athletes=0,
                             healthy_count=0,
                             total_talents=0,
                             athletes=[],
                             sport_data=[],
                             sport_performance=[],
                             sports_count=[],
                             training_data={'total_sessions': 0, 'performance_ratings': {}, 'injury_severity': {}, 'athletes_with_training': 0},
                             error=str(e))


@main_bp.route('/events')
@login_required
def events_list():
    """View all events"""
    try:
        user_role = session.get('user_role', 'user')
        
        # Users cannot view events
        if user_role == 'user':
            return redirect(url_for('main.dashboard'))
        
        page = request.args.get('page', 1, type=int)
        events = Event.query.order_by(Event.date.desc()).paginate(page=page, per_page=20)
        return render_template('events.html', events=events, user_role=user_role)
    except Exception as e:
        return render_template('events.html', error=str(e), user_role=session.get('user_role', 'user'))


@main_bp.route('/event/add', methods=['POST'])
@coach_or_admin_required
def add_event():
    """Add new event via form"""
    try:
        event_name = request.form.get('event_name', '').strip()
        event_type = request.form.get('event_type', 'Training').strip()
        location = request.form.get('location', '').strip()
        event_date = request.form.get('event_date', '')
        description = request.form.get('description', '').strip()
        
        # Validate inputs
        if not event_name or not event_date:
            print("Error: Event name and date are required")
            return redirect(url_for('main.events_list'))
        
        try:
            from datetime import datetime
            # Handle different date formats
            try:
                event_date_obj = datetime.fromisoformat(event_date)
            except:
                event_date_obj = datetime.strptime(event_date, '%Y-%m-%d')
        except ValueError:
            print("Error: Invalid date format")
            return redirect(url_for('main.events_list'))
        
        event = Event(
            event_name=event_name,
            event_type=event_type,
            location=location,
            date=event_date_obj,
            description=description
        )
        
        db.session.add(event)
        db.session.commit()
        print(f"Successfully added event: {event_name}")
        
        return redirect(url_for('main.events_list'))
    except Exception as e:
        print(f"Error adding event: {e}")
        db.session.rollback()
        return redirect(url_for('main.events_list'))


# ==================== EXPORT ROUTES (CSV/DOWNLOAD) ====================

@main_bp.route('/export/athletes')
@login_required
def export_athletes_csv():
    """
    Export Athlete Registry to CSV format.
    Useful for administrative reports, printing, and data backup.
    """
    try:
        athletes = Athlete.query.all()
        
        # Create CSV in memory
        output = StringIO()
        writer = csv.writer(output)
        
        # Write headers
        headers = [
            'ID', 'Name', 'Registration Number', 'Age', 'Sport',
            'Height (cm)', 'Weight (kg)', 'Performance Score',
            'Training Hours/Week', 'Sleep Hours/Day', 'Date Joined'
        ]
        writer.writerow(headers)
        
        # Write athlete data
        for athlete in athletes:
            writer.writerow([
                athlete.id,
                athlete.name,
                athlete.registration_number,
                athlete.age,
                athlete.sport,
                athlete.height_cm or 'N/A',
                athlete.weight_kg or 'N/A',
                athlete.performance_score,
                athlete.training_hours_pw,
                athlete.sleep_hours,
                athlete.date_joined.strftime('%Y-%m-%d')
            ])
        
        # Create response
        output.seek(0)
        response = BytesIO(output.getvalue().encode('utf-8'))
        
        return send_file(
            response,
            mimetype='text/csv',
            as_attachment=True,
            download_name='athlete_registry_{}.csv'.format(datetime.utcnow().strftime('%Y%m%d_%H%M%S'))
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main_bp.route('/export/predictions')
@login_required
def export_predictions_csv():
    """
    Export All Injury Risk Predictions to CSV format.
    Includes athlete details and their latest risk assessment.
    """
    try:
        # Get latest risk assessment for each athlete
        assessments = db.session.query(
            InjuryRiskAssessment
        ).order_by(
            InjuryRiskAssessment.athlete_id,
            InjuryRiskAssessment.assessment_date.desc()
        ).distinct(InjuryRiskAssessment.athlete_id).all()
        
        # Create CSV in memory
        output = StringIO()
        writer = csv.writer(output)
        
        # Write headers
        headers = [
            'Athlete ID', 'Athlete Name', 'Sport', 'Training Hours/Week',
            'Previous Injuries', 'Sleep Hours/Day', 'Risk Score',
            'Risk Category', 'Model Confidence', 'Assessment Date'
        ]
        writer.writerow(headers)
        
        # Write prediction data
        for assessment in assessments:
            athlete = Athlete.query.get(assessment.athlete_id)
            if athlete:
                writer.writerow([
                    athlete.id,
                    athlete.name,
                    athlete.sport,
                    assessment.training_hours_pw,
                    assessment.prev_injuries,
                    assessment.sleep_hours,
                    round(assessment.injury_risk_score, 3),
                    assessment.risk_category,
                    round(assessment.model_confidence, 3),
                    assessment.assessment_date.strftime('%Y-%m-%d %H:%M')
                ])
        
        # Create response
        output.seek(0)
        response = BytesIO(output.getvalue().encode('utf-8'))
        
        return send_file(
            response,
            mimetype='text/csv',
            as_attachment=True,
            download_name='injury_predictions_{}.csv'.format(datetime.utcnow().strftime('%Y%m%d_%H%M%S'))
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== API ROUTES (JSON) ====================

@api_bp.route('/athletes', methods=['GET'])
def get_athletes():
    """Get all athletes as JSON"""
    try:
        athletes = Athlete.query.all()
        return jsonify([athlete.to_dict() for athlete in athletes])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/athletes', methods=['POST'])
def create_athlete():
    """
    Create new athlete with comprehensive validation.
    Validates: Unique registration number, realistic metric ranges
    """
    try:
        data = request.json
        
        # ===== SERVER-SIDE VALIDATION =====
        # Validate required fields
        required_fields = ['name', 'registration_number', 'age', 'sport']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate unique registration number
        existing_athlete = Athlete.query.filter_by(
            registration_number=data.get('registration_number')
        ).first()
        if existing_athlete:
            return jsonify({'error': 'Registration number already exists. Must be unique.'}), 400
        
        # Validate age (reasonable range)
        age = data.get('age')
        if not isinstance(age, int) or age < 12 or age > 50:
            return jsonify({'error': 'Age must be between 12 and 50 years.'}), 400
        
        # Validate training hours (0-24 range)
        training_hours = data.get('training_hours_pw', 10.0)
        if not (0 <= training_hours <= 24):
            return jsonify({'error': 'Training hours per week must be between 0 and 24.'}), 400
        
        # Validate sleep hours (0-24 range)
        sleep_hours = data.get('sleep_hours', 7.0)
        if not (0 <= sleep_hours <= 24):
            return jsonify({'error': 'Sleep hours per day must be between 0 and 24.'}), 400
        
        # Validate height (if provided, reasonable range in cm)
        if 'height_cm' in data and data['height_cm']:
            height = data.get('height_cm')
            if not (120 <= height <= 220):
                return jsonify({'error': 'Height must be between 120 and 220 cm.'}), 400
        
        # Validate weight (if provided, reasonable range in kg)
        if 'weight_kg' in data and data['weight_kg']:
            weight = data.get('weight_kg')
            if not (30 <= weight <= 200):
                return jsonify({'error': 'Weight must be between 30 and 200 kg.'}), 400
        
        # Validate performance score (0-100)
        perf_score = data.get('performance_score', 50.0)
        if not (0 <= perf_score <= 100):
            return jsonify({'error': 'Performance score must be between 0 and 100.'}), 400
        
        # ===== IF ALL VALIDATIONS PASS, CREATE ATHLETE =====
        athlete = Athlete(
            name=data.get('name'),
            registration_number=data.get('registration_number'),
            age=age,
            sport=data.get('sport'),
            height_cm=data.get('height_cm'),
            weight_kg=data.get('weight_kg'),
            performance_score=perf_score,
            training_hours_pw=training_hours,
            sleep_hours=sleep_hours
        )
        
        db.session.add(athlete)
        db.session.commit()
        
        return jsonify({
            'message': 'Athlete created successfully',
            'athlete': athlete.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/athletes/<int:athlete_id>', methods=['GET'])
def get_athlete(athlete_id):
    """Get specific athlete"""
    try:
        athlete = Athlete.query.get_or_404(athlete_id)
        return jsonify(athlete.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 404


@api_bp.route('/athletes/<int:athlete_id>', methods=['PUT'])
def update_athlete(athlete_id):
    """
    Update athlete with validation.
    Ensures metrics remain within realistic ranges.
    """
    try:
        # Check permissions
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        user_role = session.get('user_role', 'user')
        user_sport = session.get('user_sport')
        
        if user_role == 'user':
            return jsonify({'error': 'Users cannot update athlete data'}), 403
        
        athlete = Athlete.query.get_or_404(athlete_id)
        
        # Coaches can only update athletes from their sport
        if user_role == 'coach' and athlete.sport != user_sport:
            return jsonify({'error': 'You can only update athletes from your sport'}), 403
        
        data = request.json
        
        # ===== VALIDATION FOR UPDATES =====
        # Validate age if provided
        if 'age' in data:
            age = data.get('age')
            if not isinstance(age, int) or age < 12 or age > 50:
                return jsonify({'error': 'Age must be between 12 and 50 years.'}), 400
            athlete.age = age
        
        # Validate training hours if provided
        if 'training_hours_pw' in data:
            training_hours = data.get('training_hours_pw')
            if not (0 <= training_hours <= 24):
                return jsonify({'error': 'Training hours per week must be between 0 and 24.'}), 400
            athlete.training_hours_pw = training_hours
        
        # Validate sleep hours if provided
        if 'sleep_hours' in data:
            sleep_hours = data.get('sleep_hours')
            if not (0 <= sleep_hours <= 24):
                return jsonify({'error': 'Sleep hours per day must be between 0 and 24.'}), 400
            athlete.sleep_hours = sleep_hours
        
        # Validate height if provided
        if 'height_cm' in data and data['height_cm']:
            height = data.get('height_cm')
            if not (120 <= height <= 220):
                return jsonify({'error': 'Height must be between 120 and 220 cm.'}), 400
            athlete.height_cm = height
        
        # Validate weight if provided
        if 'weight_kg' in data and data['weight_kg']:
            weight = data.get('weight_kg')
            if not (30 <= weight <= 200):
                return jsonify({'error': 'Weight must be between 30 and 200 kg.'}), 400
            athlete.weight_kg = weight
        
        # Validate performance score if provided
        if 'performance_score' in data:
            perf_score = data.get('performance_score')
            if not (0 <= perf_score <= 100):
                return jsonify({'error': 'Performance score must be between 0 and 100.'}), 400
            athlete.performance_score = perf_score
        
        # Update other fields without strict validation
        athlete.name = data.get('name', athlete.name)
        athlete.sport = data.get('sport', athlete.sport)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Athlete updated successfully',
            'athlete': athlete.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/athletes/<int:athlete_id>', methods=['DELETE'])
def delete_athlete(athlete_id):
    """Delete athlete"""
    try:
        # Check permissions
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        user_role = session.get('user_role', 'user')
        user_sport = session.get('user_sport')
        
        if user_role == 'user':
            return jsonify({'error': 'Users cannot delete athlete data'}), 403
        
        athlete = Athlete.query.get_or_404(athlete_id)
        
        # Coaches can only delete athletes from their sport
        if user_role == 'coach' and athlete.sport != user_sport:
            return jsonify({'error': 'You can only delete athletes from your sport'}), 403
        
        db.session.delete(athlete)
        db.session.commit()
        return jsonify({'message': 'Athlete deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== ML PREDICTION APIs ====================

@api_bp.route('/predict/injury-risk', methods=['POST'])
def predict_injury_risk():
    """
    Predict injury risk for an athlete
    Body: {athlete_id, training_hours_pw, prev_injuries, sleep_hours}
    """
    try:
        data = request.json
        athlete_id = data.get('athlete_id')
        
        # Get risk prediction
        risk_score, risk_category, confidence = injury_risk_model.predict(
            training_hours=data.get('training_hours_pw'),
            prev_injuries=data.get('prev_injuries'),
            sleep_hours=data.get('sleep_hours')
        )
        
        # Save assessment to database
        assessment = InjuryRiskAssessment(
            athlete_id=athlete_id,
            training_hours_pw=data.get('training_hours_pw'),
            prev_injuries=data.get('prev_injuries'),
            sleep_hours=data.get('sleep_hours'),
            injury_risk_score=risk_score,
            risk_category=risk_category,
            model_confidence=confidence
        )
        
        db.session.add(assessment)
        db.session.commit()
        
        return jsonify({
            'athlete_id': athlete_id,
            'injury_risk_score': round(risk_score, 3),
            'risk_category': risk_category,
            'model_confidence': round(confidence, 3),
            'recommendation': get_injury_recommendation(risk_category)
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/predict/talent-potential', methods=['POST'])
def predict_talent_potential():
    """
    Predict talent potential for an athlete
    Body: {athlete_id, performance_score, age, speed_score, strength_score, endurance_score, agility_score, technique_score}
    """
    try:
        data = request.json
        athlete_id = data.get('athlete_id')
        
        # Get talent prediction
        talent_score, talent_category, confidence = talent_model.predict(
            performance_score=data.get('performance_score'),
            age=data.get('age')
        )
        
        # Save talent metric to database
        metric = TalentMetric(
            athlete_id=athlete_id,
            speed_score=data.get('speed_score'),
            strength_score=data.get('strength_score'),
            endurance_score=data.get('endurance_score'),
            agility_score=data.get('agility_score'),
            technique_score=data.get('technique_score'),
            talent_potential=talent_score,
            model_confidence=confidence
        )
        
        db.session.add(metric)
        db.session.commit()
        
        return jsonify({
            'athlete_id': athlete_id,
            'talent_potential': round(talent_score, 1),
            'talent_category': talent_category,
            'model_confidence': round(confidence, 3),
            'recommendation': get_talent_recommendation(talent_category)
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/injuries', methods=['GET'])
def get_injuries():
    """Get all injuries"""
    try:
        injuries = Injury.query.all()
        return jsonify([injury.to_dict() for injury in injuries])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/injuries', methods=['POST'])
def log_injury():
    """Log new injury"""
    try:
        # Check permissions
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        user_role = session.get('user_role', 'user')
        user_sport = session.get('user_sport')
        
        if user_role == 'user':
            return jsonify({'error': 'Users cannot log injury data'}), 403
        
        data = request.json
        athlete_id = data.get('athlete_id')
        athlete = Athlete.query.get(athlete_id)
        
        if not athlete:
            return jsonify({'error': 'Athlete not found'}), 404
        
        # Coaches can only log injuries for their sport
        if user_role == 'coach' and athlete.sport != user_sport:
            return jsonify({'error': 'You can only log injuries for athletes in your sport'}), 403
        
        injury = Injury(
            athlete_id=data.get('athlete_id'),
            injury_type=data.get('injury_type'),
            severity=data.get('severity'),
            date_occurred=datetime.fromisoformat(data.get('date_occurred')) if data.get('date_occurred') else datetime.utcnow(),
            recovery_duration_days=data.get('recovery_duration_days'),
            notes=data.get('notes')
        )
        
        db.session.add(injury)
        db.session.commit()
        
        return jsonify({
            'message': 'Injury logged successfully',
            'injury': injury.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/events', methods=['GET'])
def get_events():
    """Get all events"""
    try:
        # Check if user is logged in and has permission
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        user_role = session.get('user_role', 'user')
        if user_role == 'user':
            return jsonify({'error': 'Users do not have access to events'}), 403
        
        events = Event.query.all()
        return jsonify([event.to_dict() for event in events])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/events', methods=['POST'])
def create_event():
    """Create new event"""
    try:
        # Check if user is logged in
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized'}), 401
        
        # Check if user has permission (only admin and coach)
        user_role = session.get('user_role', 'user')
        if user_role not in ['admin', 'coach']:
            return jsonify({'error': 'Only admins and coaches can create events'}), 403
        
        data = request.json
        
        event = Event(
            event_name=data.get('event_name'),
            event_type=data.get('event_type'),
            date=datetime.fromisoformat(data.get('date')),
            location=data.get('location'),
            description=data.get('description')
        )
        
        db.session.add(event)
        db.session.commit()
        
        return jsonify({
            'message': 'Event created successfully',
            'event': event.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@api_bp.route('/dashboard-stats', methods=['GET'])
def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        total_athletes = db.session.query(func.count(Athlete.id)).scalar() or 0
        total_events = db.session.query(func.count(Event.id)).scalar() or 0
        total_injuries = db.session.query(func.count(Injury.id)).scalar() or 0
        
        # Injuries in last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_injuries = db.session.query(func.count(Injury.id)).filter(
            Injury.date_occurred >= thirty_days_ago
        ).scalar() or 0
        
        # Sports distribution
        sports = db.session.query(
            Athlete.sport,
            func.count(Athlete.id).label('count')
        ).group_by(Athlete.sport).all()
        
        # High risk athletes
        high_risk = db.session.query(
            func.count(InjuryRiskAssessment.id)
        ).filter(
            InjuryRiskAssessment.risk_category == 'high'
        ).scalar() or 0
        
        # High potential athletes
        high_potential = db.session.query(
            func.count(TalentMetric.id)
        ).filter(
            TalentMetric.talent_potential >= 67
        ).scalar() or 0
        
        return jsonify({
            'total_athletes': total_athletes,
            'total_events': total_events,
            'total_injuries': total_injuries,
            'recent_injuries': recent_injuries,
            'high_risk_athletes': high_risk,
            'high_potential_athletes': high_potential,
            'sports_distribution': [
                {'sport': s[0], 'count': s[1]} for s in sports
            ]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== HELPER FUNCTIONS ====================

def get_injury_recommendation(risk_category):
    """
    Generate 3 specific, actionable recommendation tips for injury prevention.
    Based on risk category, provides concrete guidance for coaches.
    """
    recommendations = {
        'low': {
            'summary': '✅ Low Injury Risk - Maintain Current Status',
            'tips': [
                '1. Continue current training regimen with 2-3 rest days per week for active recovery',
                '2. Maintain 7-9 hours of sleep nightly and ensure 2-3 stretching sessions weekly',
                '3. Schedule monthly performance assessments to track metrics and adjust training if needed'
            ]
        },
        'medium': {
            'summary': '⚠️ Moderate Injury Risk - Increase Preventive Measures',
            'tips': [
                '1. Reduce high-intensity drills by 20% for the next 2 weeks and add 1 extra rest day',
                '2. Focus on mobility and stretching routines: 15-20 minutes daily (yoga, foam rolling)',
                '3. Ensure 8+ hours of sleep for the next 3 consecutive days; track sleep quality'
            ]
        },
        'high': {
            'summary': '🚨 High Injury Risk - Immediate Intervention Required',
            'tips': [
                '1. Reduce training intensity by 40% immediately; focus on technique drills instead of high-demand workouts',
                '2. Implement mandatory 10+ hours of sleep per night for 1 week + daily physical therapy/massage',
                '3. Conduct full physical assessment; consider temporary training suspension until clearance'
            ]
        }
    }
    
    risk_data = recommendations.get(risk_category, {
        'summary': 'Monitor athlete closely.',
        'tips': ['Contact coaching staff for detailed assessment']
    })
    
    return risk_data


def get_talent_recommendation(talent_category):
    """
    Generate 3 specific, actionable recommendations for talent development.
    Tailored to athlete's career progression stage.
    """
    recommendations = {
        'developing': {
            'summary': '📈 Developing Talent - Focus on Fundamentals',
            'tips': [
                '1. Prioritize skill refinement: 60% of training on technique, 30% on drills, 10% on competition prep',
                '2. Assign experienced mentor for 1-on-1 coaching; schedule 2 coaching sessions weekly',
                '3. Track consistency KPIs: attendance, punctuality, effort scores; celebrate weekly improvements'
            ]
        },
        'promising': {
            'summary': '⭐ Promising Athlete - Accelerate Development',
            'tips': [
                '1. Increase competition opportunities: Enroll in 2-3 tournaments per quarter to build experience',
                '2. Develop specialized training plan; allocate 20% of time to weakness refinement',
                '3. Schedule monthly 1-on-1 reviews; set SMART goals (Specific, Measurable, Achievable, Relevant, Time-bound)'
            ]
        },
        'elite': {
            'summary': '🏆 Elite Potential - Maximize Excellence',
            'tips': [
                '1. Enroll in advanced training program; assign elite coach or sports science specialist',
                '2. Implement sports science monitoring: Weekly fitness assessments, nutrition plans, mental coaching',
                '3. Prepare for representation opportunities: University showcase events, scouting meetings, sponsorship'
            ]
        }
    }
    
    talent_data = recommendations.get(talent_category, {
        'summary': 'Continue performance tracking.',
        'tips': ['Schedule review with coaching staff for guidance']
    })
    
    return talent_data
