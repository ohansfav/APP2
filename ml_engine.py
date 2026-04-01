"""
ML Engine - Legacy Training Script
This script provides direct access to model training functionality.
For complete system setup, use: python setup.py
"""
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import os
from generate_mock_data import generate_athlete_data

def train_and_save_models(csv_path='mock_athletes.csv'):
    """
    Train and save ML models for injury prediction and talent identification
    """
    print("\n" + "="*60)
    print("🤖 TRAINING MACHINE LEARNING MODELS")
    print("="*60 + "\n")
    
    # Generate data if not exists
    if not os.path.exists(csv_path):
        print(f"📊 Generating mock data to: {csv_path}")
        df = generate_athlete_data(n=200)
        df.to_csv(csv_path, index=False)
    else:
        print(f"📂 Loading data from: {csv_path}")
        df = pd.read_csv(csv_path)

    # ============ 1. INJURY RISK PREDICTION (Random Forest) ============
    print("\n" + "-"*60)
    print("🏃 Training Injury Risk Prediction Model (Random Forest)")
    print("-"*60)
    
    # Feature selection
    X_injury = df[['training_hours_pw', 'prev_injuries', 'sleep_hours']].copy()
    y_injury = df['injury_occurred'].copy()
    
    # Feature scaling
    scaler_injury = StandardScaler()
    X_injury_scaled = scaler_injury.fit_transform(X_injury)
    
    # Train/test split
    X_train_inj, X_test_inj, y_train_inj, y_test_inj = train_test_split(
        X_injury_scaled, y_injury, test_size=0.2, random_state=42, stratify=y_injury
    )

    # Train model
    injury_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    injury_model.fit(X_train_inj, y_train_inj)
    
    # Evaluate
    y_pred_inj = injury_model.predict(X_test_inj)
    inj_acc = accuracy_score(y_test_inj, y_pred_inj)
    inj_prec = precision_score(y_test_inj, y_pred_inj, zero_division=0)
    inj_rec = recall_score(y_test_inj, y_pred_inj, zero_division=0)
    inj_f1 = f1_score(y_test_inj, y_pred_inj, zero_division=0)
    
    print(f"   ✅ Accuracy:  {inj_acc*100:.2f}%")
    print(f"   ✅ Precision: {inj_prec*100:.2f}%")
    print(f"   ✅ Recall:    {inj_rec*100:.2f}%")
    print(f"   ✅ F1-Score:  {inj_f1*100:.2f}%")
    
    # Feature importance
    print("\n   📊 Feature Importance:")
    features = ['training_hours_pw', 'prev_injuries', 'sleep_hours']
    for feat, imp in zip(features, injury_model.feature_importances_):
        print(f"      • {feat}: {imp*100:.1f}%")

    # ============ 2. TALENT IDENTIFICATION (Logistic Regression) ============
    print("\n" + "-"*60)
    print("⭐ Training Talent Identification Model (Logistic Regression)")
    print("-"*60)
    
    # Feature selection
    X_talent = df[['performance_score', 'age']].copy()
    y_talent = df['is_high_potential'].copy()
    
    # Feature scaling
    scaler_talent = StandardScaler()
    X_talent_scaled = scaler_talent.fit_transform(X_talent)
    
    # Train/test split
    X_train_tal, X_test_tal, y_train_tal, y_test_tal = train_test_split(
        X_talent_scaled, y_talent, test_size=0.2, random_state=42, stratify=y_talent
    )

    # Train model
    talent_model = LogisticRegression(
        max_iter=1000,
        random_state=42,
        solver='lbfgs'
    )
    talent_model.fit(X_train_tal, y_train_tal)
    
    # Evaluate
    y_pred_tal = talent_model.predict(X_test_tal)
    tal_acc = accuracy_score(y_test_tal, y_pred_tal)
    tal_prec = precision_score(y_test_tal, y_pred_tal, zero_division=0)
    tal_rec = recall_score(y_test_tal, y_pred_tal, zero_division=0)
    tal_f1 = f1_score(y_test_tal, y_pred_tal, zero_division=0)
    
    print(f"   ✅ Accuracy:  {tal_acc*100:.2f}%")
    print(f"   ✅ Precision: {tal_prec*100:.2f}%")
    print(f"   ✅ Recall:    {tal_rec*100:.2f}%")
    print(f"   ✅ F1-Score:  {tal_f1*100:.2f}%")
    
    # Model coefficients
    print("\n   📊 Feature Coefficients:")
    features_tal = ['performance_score', 'age']
    for feat, coef in zip(features_tal, talent_model.coef_[0]):
        direction = "↑" if coef > 0 else "↓"
        print(f"      • {feat}: {direction} {abs(coef):.4f}")

    # ============ 3. SAVE MODELS ============
    print("\n" + "-"*60)
    print("💾 Saving Models to Disk")
    print("-"*60)
    
    os.makedirs('ml', exist_ok=True)
    
    # Save injury model
    joblib.dump(injury_model, 'ml/injury_model.pkl')
    joblib.dump(scaler_injury, 'ml/injury_scaler.pkl')
    print("   ✅ Saved: ml/injury_model.pkl & ml/injury_scaler.pkl")
    
    # Save talent model
    joblib.dump(talent_model, 'ml/talent_model.pkl')
    joblib.dump(scaler_talent, 'ml/talent_scaler.pkl')
    print("   ✅ Saved: ml/talent_model.pkl & ml/talent_scaler.pkl")

    print("\n" + "="*60)
    print("✨ Models trained and saved successfully!")
    print("="*60 + "\n")

if __name__ == "__main__":
    train_and_save_models()
    train_and_save_models()
