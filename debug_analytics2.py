#!/usr/bin/env python
import sys
sys.path.insert(0, '/Users/ohanu/OneDrive/Desktop/final year project 2')

from app import create_app, db
from models.database import Athlete, Event, Injury, TalentMetric, InjuryRiskAssessment
from flask import Flask
from sqlalchemy import func

# Create app context
app = create_app()

with app.app_context():
    try:
        # Get all athletes
        athletes = Athlete.query.all()
        print(f"Total athletes: {len(athletes)}")
        
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
        
        print(f"Injury risks: {len(injury_risks)}")
        
        # Calculate statistics
        high_risk_count = len([r for r in injury_risks if r['risk_level'] == 'High'])
        avg_performance = db.session.query(func.avg(Athlete.performance_score)).scalar() or 50
        healthy_count = len(athletes) - high_risk_count
        
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
        
        print(f"Sports count: {sports_count}")
        print(f"Avg performance: {avg_performance}")
        print(f"Healthy count: {healthy_count}")
        
        # Test template rendering
        from flask import render_template
        html = render_template('analytics.html', 
                             injury_risks=injury_risks,
                             high_risk_count=high_risk_count,
                             average_performance=avg_performance,
                             total_athletes=len(athletes),
                             healthy_count=healthy_count,
                             total_talents=total_talents,
                             athletes=athletes,
                             sport_data=sport_labels,
                             sport_performance=sport_performance,
                             sports_count=sports_count)
        
        print("SUCCESS! Template rendered successfully")
        print(f"HTML length: {len(html)}")
        if '```' in html:
            print("WARNING: Found code blocks in HTML!")
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
