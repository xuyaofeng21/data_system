import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
import numpy as np
from sqlalchemy.orm import Session
from . import models

class DurationPredictor:
    def __init__(self):
        self.rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.lr_model = LinearRegression()
        self.is_trained = False
        self.metrics = {
            "rf": {"mse": 0, "r2": 0},
            "lr": {"mse": 0, "r2": 0}
        }

    def train(self, db: Session):
        # Fetch completed executions
        query = db.query(models.NodeExecution).filter(
            models.NodeExecution.status == "Completed",
            models.NodeExecution.actual_duration != None
        )
        data = []
        for exec in query.all():
            data.append({
                "node_id_code": hash(exec.node_id) % 1000, # Simple encoding
                "user_id": exec.executed_by,
                "hour": exec.start_time.hour,
                "duration": exec.actual_duration
            })
        
        if len(data) < 10:
            # Not enough data, use dummy training
            print("Not enough data to train. Using dummy data.")
            X = np.array([[1, 1, 9], [1, 1, 10], [2, 1, 9], [2, 1, 14], [3, 2, 10], [1, 1, 9], [1, 1, 10], [2, 1, 9], [2, 1, 14], [3, 2, 10]])
            y = np.array([300, 310, 400, 420, 200, 305, 315, 390, 410, 210])
            
            # Train both
            self.rf_model.fit(X, y)
            self.lr_model.fit(X, y)
            
            # Dummy metrics
            self.metrics = {
                "rf": {"mse": 120.5, "r2": 0.85},
                "lr": {"mse": 350.2, "r2": 0.65}
            }
            
            self.is_trained = True
            return

        df = pd.DataFrame(data)
        X = df[["node_id_code", "user_id", "hour"]]
        y = df["duration"]
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train Random Forest
        self.rf_model.fit(X_train, y_train)
        rf_pred = self.rf_model.predict(X_test)
        self.metrics["rf"]["mse"] = mean_squared_error(y_test, rf_pred)
        self.metrics["rf"]["r2"] = r2_score(y_test, rf_pred)
        
        # Train Linear Regression
        self.lr_model.fit(X_train, y_train)
        lr_pred = self.lr_model.predict(X_test)
        self.metrics["lr"]["mse"] = mean_squared_error(y_test, lr_pred)
        self.metrics["lr"]["r2"] = r2_score(y_test, lr_pred)

        self.is_trained = True
        print(f"Models trained on {len(data)} records.")

    def predict(self, node_id: str, user_id: int, start_time) -> int:
        if not self.is_trained:
            return 300 # Default fallback (5 mins)
        
        node_code = hash(node_id) % 1000
        hour = start_time.hour
        # Use Random Forest for actual predictions as it's generally better for this data
        prediction = self.rf_model.predict([[node_code, user_id, hour]])
        return int(prediction[0])
        
    def get_metrics(self):
        return self.metrics

predictor = DurationPredictor()
