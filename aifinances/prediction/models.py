import pandas as pd
import numpy as np
import joblib
import os
from django.conf import settings

class StockPredictor:
    def __init__(self):
        self.days = ['Day1', 'Day2', 'Day3', 'Day4', 'Day5']
        self.models_dir = os.path.join(settings.BASE_DIR, 'prediction', 'saved_models')
        self.data_dir = os.path.join(settings.BASE_DIR, 'prediction', 'data_splits')
        print(f"Models directory: {self.models_dir}")
        print(f"Data directory: {self.data_dir}")
        self.models = {day: self._load_day_models(day) for day in self.days}

    def _load_day_models(self, day):
        """載入指定天數的模型和相關組件"""
        try:
            day_path = os.path.join(self.models_dir, day)
            print(f"Loading models from: {day_path}")  
            
            models = {}
            
            # 載入XGBoost模型
            best_model_path = os.path.join(day_path, f'XGBoost_model.pkl')
            if os.path.exists(best_model_path):
                print(f"Loading best model from {best_model_path}")
                models['best'] = joblib.load(best_model_path)
            else:
                print(f"Warning: Best model not found at {best_model_path}")
                return None

            # 載入預處理器
            preprocessor_path = os.path.join(day_path, f'preprocessor_{day}.pkl')
            if os.path.exists(preprocessor_path):
                print(f"Loading preprocessor from {preprocessor_path}")
                models['preprocessor'] = joblib.load(preprocessor_path)
            else:
                print(f"Warning: Preprocessor not found at {preprocessor_path}")

            # 載入特徵列表
            features_path = os.path.join(day_path, f'selected_features_{day}.txt')
            if os.path.exists(features_path):
                print(f"Loading selected features from {features_path}")
                with open(features_path, 'r', encoding='utf-8') as f:
                    models['selected_features'] = [line.strip() for line in f.readlines()]
            else:
                print(f"Warning: Selected features not found at {features_path}")

            return models

        except Exception as e:
            print(f"Error loading models for {day}: {str(e)}")
            return None

    def get_features(self, company_code):
        """從測試資料中獲取原始特徵"""
        try:
            features = {}
            for day in self.days:
                x_test_path = os.path.join(self.data_dir, day, 'X_test_raw.csv')
                if not os.path.exists(x_test_path):
                    print(f"Warning: Test data not found at {x_test_path}")
                    continue
                
                # 讀取CSV檔案
                x_test = pd.read_csv(x_test_path, encoding='utf-8')
                
                # 檢查股票代碼是否在資料中
                if 'Company Code' in x_test.columns and int(company_code) in x_test['Company Code'].values:
                    # 獲取該股票的資料行
                    stock_data = x_test[x_test['Company Code'] == int(company_code)].copy()
                    features[day] = stock_data
                else:
                    print(f"Warning: Company code {company_code} not found in {day} test data")
                    features[day] = None
                    
            return features
            
        except Exception as e:
            print(f"Error getting features for {company_code}: {str(e)}")
            return None

    def predict(self, company_code):
        """對指定股票進行預測"""
        try:
            # 獲取原始特徵
            day_features = self.get_features(company_code)
            if day_features is None:
                print("Failed to get features")
                return None

            predictions = {}

            for day in self.days:
                if day not in day_features or day_features[day] is None:
                    print(f"No features available for {day}")
                    continue

                day_models = self.models[day]
                if day_models is None or 'best' not in day_models:
                    print(f"Skipping {day} - models not properly loaded")
                    continue

                # 獲取該天的原始特徵
                raw_features = day_features[day]
                
                # 只移除不需要的欄位，保留Company Code
                columns_to_drop = ['Future_Price_Change', 'Year', 'Month', 'Day_Date']
                features_for_model = raw_features.drop(columns=columns_to_drop)

                try:
                    # 1. 使用預處理器
                    if 'preprocessor' in day_models:
                        print(f"Applying preprocessor for {day}")
                        processed_features = day_models['preprocessor'].transform(features_for_model)
                        # 將numpy array轉換回DataFrame，保持特徵名稱
                        processed_features = pd.DataFrame(
                            processed_features,
                            columns=features_for_model.columns
                        )
                    else:
                        print(f"No preprocessor found for {day}")
                        processed_features = features_for_model

                    # 2. 應用特徵選擇
                    if 'selected_features' in day_models:
                        print(f"Selecting features for {day}")
                        selected_features = processed_features[day_models['selected_features']]
                    else:
                        print(f"No selected features found for {day}")
                        selected_features = processed_features

                    # 3. 進行預測
                    print(f"Making prediction for {day}")
                    pred = day_models['best'].predict(selected_features)[0]
                    predictions[day] = float(pred)
                    print(f"Prediction for {day}: {pred}")

                except Exception as e:
                    print(f"Error in prediction process for {day}: {str(e)}")
                    print(f"Error details: {str(e.__class__.__name__)}")
                    print(f"Error message: {str(e)}")
                    predictions[day] = None
                    continue

            return predictions

        except Exception as e:
            print(f"Error in prediction: {str(e)}")
            return None