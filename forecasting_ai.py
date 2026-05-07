# forecasting_ai.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta
import joblib
from data_store import LOGS_FILE

class CrowdingForecaster:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100)
        self.is_trained = False

    # forecasting_ai.py (Update this function)

    def _prepare_features(self, df):
        """
        Converts raw timestamps into numerical features the AI can understand.
        """
        # FIX: Added format='ISO8601' to handle varying precision in timestamps
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='ISO8601')
        
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['month'] = df['timestamp'].dt.month
        
        # Keep the rest of your logic...
        df['is_raining'] = np.random.choice([0, 1], size=len(df), p=[0.8, 0.2]) 
        df['is_holiday'] = df['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)
        
        return df[['hour', 'day_of_week', 'month', 'is_raining', 'is_holiday']]

    def train(self):
        """
        Loads mobility_logs.csv and trains the model.
        """
        try:
            df = pd.read_csv(LOGS_FILE)
            if len(df) < 50: # Minimum data threshold
                return False
            
            X = self._prepare_features(df)
            y = df['occupancy_percent']
            
            self.model.fit(X, y)
            self.is_trained = True
            return True
        except Exception as e:
            print(f"Training failed: {e}")
            return False

    def predict_future(self, target_time: datetime, is_raining: bool = False):
        """
        Predicts occupancy percent for a specific future point in time.
        """
        if not self.is_trained:
            return 25 # Fallback to a baseline occupancy
        
        features = pd.DataFrame([{
            'hour': target_time.hour,
            'day_of_week': target_time.dayofweek,
            'month': target_time.month,
            'is_raining': 1 if is_raining else 0,
            'is_holiday': 1 if target_time.dayofweek >= 5 else 0
        }])
        
        prediction = self.model.predict(features)[0]
        return round(float(prediction), 1)

forecaster = CrowdingForecaster()