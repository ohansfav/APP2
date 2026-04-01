"""
Flask Routes - Dashboard, CRUD Operations, and ML Prediction APIs
"""
from flask import Blueprint, render_template, request, jsonify, send_file, redirect, url_for, session
from models.database import db, Athlete, Event, Injury, TalentMetric, InjuryRiskAssessment
from ml.ml_models import InjuryRiskModel, TalentIdentificationModel
from datetime import datetime, timedelta
from sqlalchemy import func
import os
import csv
import io
from io import StringIO, BytesIO
from functools import wraps

# Create blueprints
main_bp = Blueprint('main', __name__)
api_bp = Blueprint('api', __name__)

# Initialize ML models
injury_risk_model = InjuryRiskModel()
talent_model = TalentIdentificationModel()

# Demo credentials
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

# ==================== AUTH ROUTES ====================

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Check credentials
        if username in DEMO_USERS and DEMO_USERS[username] == password:
            session['user_id'] = username
            session['user_name'] = username
            return redirect(url_for('main.dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@main_bp.route('/logout')
def logout():
    """Logout"""
    session.clear()
    return redirect(url_for('main.login'))

# ==================== MAIN ROUTES ====================

@main_bp.route('/')
@login_required
def dashboard():
    """Main dashboard view"""
    try:
        # Fetch statistics
        total_athletes = db.session.query(func.count(Athlete.id)).scalar() or 0
        total_events = db.session.query(func.count(Event.id)).scalar() or 0
        total_injuries = db.session.query(func.count(Injury.id)).scalar() or 0
        
        # Get recent events
        recent_events = Event.query.order_by(Event.date.desc()).limit(5).all()
        
        # Get sports breakdown
        sports_count = db.session.query(
            Athlete.sport,
            func.count(Athlete.id)
        ).group_by(Athlete.sport).all()
        
        # Get injury trends (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_injury_count = db.session.query(func.count(Injury.id)).filter(
            Injury.date_occurred >= thirty_days_ago
        ).scalar() or 0
        
        # Get top performers
        top_performers = Athlete.query.order_by(Athlete.performance_score.desc()).limit(5).all()
        
        context = {
            'total_athletes': total_athletes,
            'total_events': total_events,
            'total_injuries': total_injuries,
            'recent_injury_count': recent_injury_count,
            'recent_events': recent_events,
            'sports_count': sports_count,
            'top_performers': top_performers
        }
        
        return render_template('dashboard_new.html', **context)
    except Exception as e:
        print(f"Error: {e}")
        return render_template('dashboard_new.html', error=str(e))


@main_bp.route('/athletes')
@login_required
def athletes_list():
    """View all athletes"""
    try:
        page = request.args.get('page', 1, type=int)
        athletes = Athlete.query.paginate(page=page, per_page=20)
        return render_template('athletes.html', athletes=athletes)
    except Exception as e:
        return render_template('athletes.html', error=str(e))


@main_bp.route('/athlete/<int:athlete_id>')
@login_required
def athlete_detail(athlete_id):
    """View athlete detail and health metrics"""
    try:
        athlete = Athlete.query.get_or_404(athlete_id)
        injuries = Injury.query.filter_by(athlete_id=athlete_id).order_by(Injury.date_occurred.desc()).all()
        talent_metrics = TalentMetric.query.filter_by(athlete_id=athlete_id).order_by(TalentMetric.assessment_date.desc()).all()
        risk_assessments = InjuryRiskAssessment.query.filter_by(athlete_id=athlete_id).order_by(InjuryRiskAssessment.assessment_date.desc()).limit(5).all()
        
        return render_template('athlete_detail.html', 
                             athlete=athlete, 
                             injuries=injuries,
                             talent_metrics=talent_metrics,
                             risk_assessments=risk_assessments)
    except Exception as e:
        return render_template('athlete_detail.html', error=str(e))


@main_bp.route('/analytics')
@login_required
def analytics():
    """Predictive analytics dashboard"""
    try:
        # Get all athletes for analysis
        athletes = Athlete.query.all()
        
        # Get talent metrics summary
        talent_summary = db.session.query(
            TalentMetric.athlete_id,
            func.max(TalentMetric.talent_potential)
        ).group_by(TalentMetric.athlete_id).all()
        
        # Get risk assessments summary
        risk_summary = db.session.query(
            InjuryRiskAssessment.athlete_id,
            func.max(InjuryRiskAssessment.injury_risk_score)
        ).group_by(InjuryRiskAssessment.athlete_id).all()
        
        return render_template('analytics.html', 
                             athletes=athletes,
                             talent_summary=talent_summary,
                             risk_summary=risk_summary)
    except Exception as e:
        return render_template('analytics.html', error=str(e))


@main_bp.route('/events')
@login_required
def events_list():
    """View all events"""
    try:
        page = request.args.get('page', 1, type=int)
        events = Event.query.order_by(Event.date.desc()).paginate(page=page, per_page=20)
        return render_template('events.html', events=events)
    except Exception as e:
        return render_template('events.html', error=str(e))


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
        athlete = Athlete.query.get_or_404(athlete_id)
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
        athlete = Athlete.query.get_or_404(athlete_id)
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
        data = request.json
        
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
        events = Event.query.all()
        return jsonify([event.to_dict() for event in events])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_bp.route('/events', methods=['POST'])
def create_event():
    """Create new event"""
    try:
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
