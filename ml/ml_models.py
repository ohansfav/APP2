"""
Machine Learning Models - Random Forest (Injury Prediction) & Logistic Regression (Talent Identification)
"""
import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from datetime import datetime


class InjuryRiskModel:
    """Random Forest classifier for injury risk prediction"""
    
    def __init__(self, model_path='ml/injury_model.pkl'):
        self.model_path = model_path
        self.scaler_path = 'ml/injury_scaler.pkl'
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = ['training_hours_pw', 'prev_injuries', 'sleep_hours']
    
    def train(self, csv_path='mock_athletes.csv'):
        """Train Random Forest model on athlete data"""
        print("🔄 Training Injury Risk Prediction Model (Random Forest)...")
        
        # Load data
        df = pd.read_csv(csv_path)
        
        # Prepare features and target
        X = df[self.feature_names].copy()
        y = df['injury_occurred'].copy()
        
        # Normalize features
        X_scaled = self.scaler.fit_transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Train model
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        
        print(f"   📊 Accuracy: {accuracy*100:.2f}%")
        print(f"   📊 Precision: {precision*100:.2f}%")
        print(f"   📊 Recall: {recall*100:.2f}%")
        print(f"   📊 F1-Score: {f1*100:.2f}%")
        
        # Feature importance
        importances = self.model.feature_importances_
        for feat, imp in zip(self.feature_names, importances):
            print(f"   📌 {feat}: {imp*100:.1f}%")
        
        # Save model and scaler
        self.save()
        print(f"   ✅ Model saved to {self.model_path}")
    
    def predict(self, training_hours, prev_injuries, sleep_hours):
        """
        Predict injury risk
        Returns: risk_score (0-1), risk_category, confidence
        """
        if self.model is None:
            self.load()
        
        # Prepare input
        X = np.array([[training_hours, prev_injuries, sleep_hours]])
        X_scaled = self.scaler.transform(X)
        
        # Get prediction and probability
        prediction = self.model.predict(X_scaled)[0]
        probability = self.model.predict_proba(X_scaled)[0]
        risk_score = probability[1]  # Probability of injury
        confidence = max(probability)
        
        # Categorize risk
        if risk_score < 0.33:
            risk_category = 'low'
        elif risk_score < 0.67:
            risk_category = 'medium'
        else:
            risk_category = 'high'
        
        return risk_score, risk_category, confidence
    
    def save(self):
        """Persist model to disk"""
        os.makedirs('ml', exist_ok=True)
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.scaler, self.scaler_path)
    
    def load(self):
        """Load model from disk"""
        if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
            self.model = joblib.load(self.model_path)
            self.scaler = joblib.load(self.scaler_path)
        else:
            raise FileNotFoundError(f"Model files not found. Train first.")


class TalentIdentificationModel:
    """Logistic Regression classifier for talent identification"""
    
    def __init__(self, model_path='ml/talent_model.pkl'):
        self.model_path = model_path
        self.scaler_path = 'ml/talent_scaler.pkl'
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = ['performance_score', 'age']
    
    def train(self, csv_path='mock_athletes.csv'):
        """Train Logistic Regression model on athlete data"""
        print("🔄 Training Talent Identification Model (Logistic Regression)...")
        
        # Load data
        df = pd.read_csv(csv_path)
        
        # Prepare features and target
        X = df[self.feature_names].copy()
        y = df['is_high_potential'].copy()
        
        # Normalize features
        X_scaled = self.scaler.fit_transform(X)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Train model
        self.model = LogisticRegression(
            max_iter=1000,
            random_state=42,
            solver='lbfgs'
        )
        self.model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        
        print(f"   📊 Accuracy: {accuracy*100:.2f}%")
        print(f"   📊 Precision: {precision*100:.2f}%")
        print(f"   📊 Recall: {recall*100:.2f}%")
        print(f"   📊 F1-Score: {f1*100:.2f}%")
        
        # Model coefficients (interpretability)
        for feat, coef in zip(self.feature_names, self.model.coef_[0]):
            direction = "increases" if coef > 0 else "decreases"
            print(f"   📌 {feat} {direction} talent potential by {abs(coef)*100:.1f}%")
        
        # Save model and scaler
        self.save()
        print(f"   ✅ Model saved to {self.model_path}")
    
    def predict(self, performance_score, age):
        """
        Predict talent potential
        Returns: talent_score (0-100), category, confidence
        """
        if self.model is None:
            self.load()
        
        # Prepare input
        X = np.array([[performance_score, age]])
        X_scaled = self.scaler.transform(X)
        
        # Get prediction and probability
        prediction = self.model.predict(X_scaled)[0]
        probability = self.model.predict_proba(X_scaled)[0]
        
        # Talent score as percentage
        talent_score = probability[1] * 100
        confidence = max(probability)
        
        # Categorize talent
        if talent_score < 33:
            talent_category = 'developing'
        elif talent_score < 67:
            talent_category = 'promising'
        else:
            talent_category = 'elite'
        
        return talent_score, talent_category, confidence
    
    def save(self):
        """Persist model to disk"""
        os.makedirs('ml', exist_ok=True)
        joblib.dump(self.model, self.model_path)
        joblib.dump(self.scaler, self.scaler_path)
    
    def load(self):
        """Load model from disk"""
        if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
            self.model = joblib.load(self.model_path)
            self.scaler = joblib.load(self.scaler_path)
        else:
            raise FileNotFoundError(f"Model files not found. Train first.")


def train_all_models(csv_path='mock_athletes.csv'):
    """Train and save all ML models"""
    print("\n" + "="*60)
    print("🎯 INTELLIGENT SPORTS MANAGEMENT SYSTEM - ML TRAINING")
    print("="*60 + "\n")
    
    # Train injury risk model
    injury_model = InjuryRiskModel()
    injury_model.train(csv_path)
    
    print()
    
    # Train talent identification model
    talent_model = TalentIdentificationModel()
    talent_model.train(csv_path)
    
    print("\n" + "="*60)
    print("✨ All models trained and saved successfully!")
    print("="*60 + "\n")


if __name__ == "__main__":
    train_all_models()
