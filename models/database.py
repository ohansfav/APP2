"""
Database Models - SQLite Schema for Intelligent Sports Management System
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import func

db = SQLAlchemy()

class User(db.Model):
    """User Account Model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    full_name = db.Column(db.String(120))
    role = db.Column(db.String(20), default='user', nullable=False)  # 'admin', 'coach', 'user'
    sport_specialization = db.Column(db.String(100))  # Sport that coach specializes in (null for admin/user)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'sport_specialization': self.sport_specialization,
            'created_at': self.created_at.strftime('%Y-%m-%d')
        }

class Athlete(db.Model):
    """Athlete Profile Model"""
    __tablename__ = 'athletes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    registration_number = db.Column(db.String(50), unique=True, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    sport = db.Column(db.String(50), nullable=False)
    height_cm = db.Column(db.Float)
    weight_kg = db.Column(db.Float)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    performance_score = db.Column(db.Float, default=50.0)
    training_hours_pw = db.Column(db.Float, default=10.0)
    sleep_hours = db.Column(db.Float, default=7.0)
    
    # Relationships
    injuries = db.relationship('Injury', backref='athlete', lazy=True, cascade='all, delete-orphan')
    events = db.relationship('Event', secondary='athlete_events', backref='participants')
    talent_metrics = db.relationship('TalentMetric', backref='athlete', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Athlete {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'registration_number': self.registration_number,
            'age': self.age,
            'sport': self.sport,
            'height_cm': self.height_cm,
            'weight_kg': self.weight_kg,
            'date_joined': self.date_joined.strftime('%Y-%m-%d'),
            'performance_score': self.performance_score,
            'training_hours_pw': self.training_hours_pw,
            'sleep_hours': self.sleep_hours
        }


class Injury(db.Model):
    """Injury Tracking Model"""
    __tablename__ = 'injuries'
    
    id = db.Column(db.Integer, primary_key=True)
    athlete_id = db.Column(db.Integer, db.ForeignKey('athletes.id'), nullable=False)
    injury_type = db.Column(db.String(100), nullable=False)
    severity = db.Column(db.String(20), nullable=False)  # 'mild', 'moderate', 'severe'
    date_occurred = db.Column(db.DateTime, default=datetime.utcnow)
    recovery_duration_days = db.Column(db.Integer)
    date_recovered = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Injury {self.injury_type} - {self.severity}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'athlete_id': self.athlete_id,
            'injury_type': self.injury_type,
            'severity': self.severity,
            'date_occurred': self.date_occurred.strftime('%Y-%m-%d'),
            'recovery_duration_days': self.recovery_duration_days,
            'date_recovered': self.date_recovered.strftime('%Y-%m-%d') if self.date_recovered else None,
            'notes': self.notes
        }


class Event(db.Model):
    """Event Tracking Model"""
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(150), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)  # 'competition', 'training', 'tournament'
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(150))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Event {self.event_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'event_name': self.event_name,
            'event_type': self.event_type,
            'date': self.date.strftime('%Y-%m-%d %H:%M'),
            'location': self.location,
            'description': self.description,
            'participant_count': len(self.participants)
        }


# Association table for many-to-many relationship
athlete_events = db.Table(
    'athlete_events',
    db.Column('athlete_id', db.Integer, db.ForeignKey('athletes.id'), primary_key=True),
    db.Column('event_id', db.Integer, db.ForeignKey('events.id'), primary_key=True)
)


class TalentMetric(db.Model):
    """Talent Identification Metrics Model"""
    __tablename__ = 'talent_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    athlete_id = db.Column(db.Integer, db.ForeignKey('athletes.id'), nullable=False)
    assessment_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Performance indicators
    speed_score = db.Column(db.Float)  # 0-100
    strength_score = db.Column(db.Float)  # 0-100
    endurance_score = db.Column(db.Float)  # 0-100
    agility_score = db.Column(db.Float)  # 0-100
    technique_score = db.Column(db.Float)  # 0-100
    
    # Computed talent potential score
    talent_potential = db.Column(db.Float)  # 0-100
    model_confidence = db.Column(db.Float)  # 0-1
    
    notes = db.Column(db.Text)
    
    def __repr__(self):
        return f'<TalentMetric Athlete#{self.athlete_id} - {self.talent_potential}%>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'athlete_id': self.athlete_id,
            'assessment_date': self.assessment_date.strftime('%Y-%m-%d'),
            'speed_score': self.speed_score,
            'strength_score': self.strength_score,
            'endurance_score': self.endurance_score,
            'agility_score': self.agility_score,
            'technique_score': self.technique_score,
            'talent_potential': self.talent_potential,
            'model_confidence': self.model_confidence,
            'notes': self.notes
        }


class InjuryRiskAssessment(db.Model):
    """Injury Risk Prediction Assessment Model"""
    __tablename__ = 'injury_risk_assessments'
    
    id = db.Column(db.Integer, primary_key=True)
    athlete_id = db.Column(db.Integer, db.ForeignKey('athletes.id'), nullable=False)
    assessment_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Input features
    training_hours_pw = db.Column(db.Float, nullable=False)
    prev_injuries = db.Column(db.Integer, nullable=False)
    sleep_hours = db.Column(db.Float, nullable=False)
    
    # Prediction output
    injury_risk_score = db.Column(db.Float)  # 0-1 probability
    risk_category = db.Column(db.String(20))  # 'low', 'medium', 'high'
    model_confidence = db.Column(db.Float)  # 0-1
    
    def __repr__(self):
        return f'<InjuryRisk Athlete#{self.athlete_id} - {self.risk_category}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'athlete_id': self.athlete_id,
            'assessment_date': self.assessment_date.strftime('%Y-%m-%d'),
            'training_hours_pw': self.training_hours_pw,
            'prev_injuries': self.prev_injuries,
            'sleep_hours': self.sleep_hours,
            'injury_risk_score': round(self.injury_risk_score, 3),
            'risk_category': self.risk_category,
            'model_confidence': round(self.model_confidence, 3)
        }
