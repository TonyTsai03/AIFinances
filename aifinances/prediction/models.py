import finlab
from finlab import data
import pandas as pd
import numpy as np
import joblib
import os
from django.conf import settings

class StockPredictor:
    def __init__(self):
        self.days = ['Day1', 'Day2', 'Day3', 'Day4', 'Day5']
        self.models_dir = os.path.join(settings.BASE_DIR, 'saved_models')
        print(f"Models directory: {self.models_dir}")  
        self.models = {day: self._load_day_models(day) for day in self.days}

    def _load_day_models(self, day):
        try:
            day_path = os.path.join(self.models_dir, day)
            print(f"Loading models from: {day_path}")  
            
            models = {}

            best_model_path = os.path.join(day_path, f'XGBoost_model.pkl')
            if os.path.exists(best_model_path):
                print(f"Loading best model from {best_model_path}")
                models['best'] = joblib.load(best_model_path)
            else:
                print(f"Warning: Best model not found for {day}")
                return None

            preprocessor_path = os.path.join(day_path, f'preprocessor_{day}.pkl')
            if os.path.exists(preprocessor_path):
                print(f"Loading preprocessor from {preprocessor_path}")
                models['preprocessor'] = joblib.load(preprocessor_path)

            features_path = os.path.join(day_path, f'selected_features_{day}.txt')
            if os.path.exists(features_path):
                print(f"Loading selected features from {features_path}")
                with open(features_path, 'r') as f:
                    models['selected_features'] = f.read().splitlines()

            return models

        except Exception as e:
            print(f"Error loading models for {day}: {str(e)}")
            return None

    def get_features(self, company_code):
        try:
            finlab.login('r0K9y4lF4EhgdSIjBVE5vY7ZKMhXqNr/N0yWFGz/keCB1a87U4N1xykyUlLu9B7S#vip_m')
            
            features = {
                '淨值成長率': 'fundamental_features:淨值成長率',
                '營收成長率': 'fundamental_features:營收成長率',
                '資產總額成長率': 'fundamental_features:營收成長率',
                '業外收支營收率': 'fundamental_features:業外收支營收率',
                '應收帳款週轉率': 'fundamental_features:應收帳款週轉率',
                '營業利益成長率': 'fundamental_features:營業利益成長率',
                '稅率': 'fundamental_features:稅率',
                '存貨週轉率': 'fundamental_features:存貨週轉率',
                '總資產週轉次數': 'fundamental_features:總資產週轉次數',
                '研究發展費用率': 'fundamental_features:研究發展費用率',
                '推銷費用率': 'fundamental_features:推銷費用率',
                '折舊': 'fundamental_features:折舊',
                '稅前淨利成長率': 'fundamental_features:稅前淨利成長率',
                '現金流量比率': 'fundamental_features:現金流量比率',
                '利息支出率': 'fundamental_features:利息支出率',
                '營業毛利成長率': 'fundamental_features:營業毛利成長率',
                '每股現金流量': 'fundamental_features:每股現金流量',
                '貝里比率': 'fundamental_features:貝里比率',
                '營運現金流': 'fundamental_features:營運現金流',
                'ROA綜合損益': 'fundamental_features:ROA綜合損益'
            }
            
            latest_features = {}
            for feature_name, feature_key in features.items():
                feature_data = data.get(feature_key)
                if company_code in feature_data:
                    latest_value = feature_data[company_code].dropna().iloc[-1]
                    latest_features[feature_name] = latest_value
                else:
                    latest_features[feature_name] = np.nan
                    
            return latest_features
            
        except Exception as e:
            print(f"Error getting features for {company_code}: {str(e)}")
            return None

    def predict(self, company_code):

        try:
            raw_features = self.get_features(company_code)
            if raw_features is None:
                return None

            predictions = {}

            for day in self.days:
                day_models = self.models[day]
                if day_models is None or 'best' not in day_models:
                    print(f"Skipping {day} - best model not loaded")
                    continue

                feature_df = pd.DataFrame([raw_features])

                if 'preprocessor' in day_models:
                    feature_df = day_models['preprocessor'].transform(feature_df)

                if 'selected_features' in day_models:
                    feature_df = feature_df[day_models['selected_features']]

                try:
                    pred = day_models['best'].predict(feature_df)[0]
                    predictions[day] = float(pred)
                except Exception as e:
                    print(f"Error predicting with {day}: {str(e)}")
                    predictions[day] = None

            return predictions

        except Exception as e:
            print(f"Error in prediction: {str(e)}")
            return None