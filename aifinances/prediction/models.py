import pandas as pd
import numpy as np
import joblib
import os
from django.conf import settings
import gc  # 添加垃圾回收模組

class StockPredictor:
    def __init__(self):
        self.days = ['Day1', 'Day2', 'Day3', 'Day4', 'Day5']
        self.models_dir = os.path.join(settings.BASE_DIR, 'prediction', 'saved_models')
        self.data_dir = os.path.join(settings.BASE_DIR, 'prediction', 'data_splits')
        print(f"Models directory: {self.models_dir}")
        print(f"Data directory: {self.data_dir}")
        # 改為延遲載入模型
        self.models = {}

    def _load_day_models(self, day):
        """延遲載入模型，只在需要時載入"""
        try:
            # 如果模型已經載入，直接返回
            if day in self.models and self.models[day] is not None:
                return self.models[day]

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

            # 儲存已載入的模型
            self.models[day] = models
            return models

        except Exception as e:
            print(f"Error loading models for {day}: {str(e)}")
            return None

    def get_features(self, company_code):
        """從測試資料中獲取原始特徵，使用更有效率的讀取方式"""
        try:
            features = {}
            for day in self.days:
                x_test_path = os.path.join(self.data_dir, day, 'X_test_raw.csv')
                if not os.path.exists(x_test_path):
                    print(f"Warning: Test data not found at {x_test_path}")
                    continue
                
                # 只讀取需要的行，使用更有效的方式
                try:
                    # 首先只讀取Company Code列
                    df_iterator = pd.read_csv(x_test_path, chunksize=1000)
                    found = False
                    for chunk in df_iterator:
                        if int(company_code) in chunk['Company Code'].values:
                            stock_data = chunk[chunk['Company Code'] == int(company_code)].copy()
                            features[day] = stock_data
                            found = True
                            break
                        del chunk  # 釋放記憶體
                        gc.collect()  # 強制垃圾回收
                    
                    if not found:
                        print(f"Warning: Company code {company_code} not found in {day} test data")
                        features[day] = None
                    
                except Exception as e:
                    print(f"Error reading CSV for {day}: {str(e)}")
                    features[day] = None
                    
            return features
            
        except Exception as e:
            print(f"Error getting features for {company_code}: {str(e)}")
            return None
        finally:
            gc.collect()  # 確保記憶體被釋放

    def predict(self, company_code):
        """對指定股票進行預測，優化記憶體使用"""
        try:
            predictions = {}
            day_features = self.get_features(company_code)
            
            if day_features is None:
                print("Failed to get features")
                return None

            for day in self.days:
                try:
                    if day not in day_features or day_features[day] is None:
                        print(f"No features available for {day}")
                        continue

                    # 延遲載入模型
                    day_models = self._load_day_models(day)
                    if day_models is None or 'best' not in day_models:
                        print(f"Skipping {day} - models not properly loaded")
                        continue

                    # 獲取該天的原始特徵
                    raw_features = day_features[day]
                    columns_to_drop = ['Future_Price_Change', 'Year', 'Month', 'Day_Date']
                    features_for_model = raw_features.drop(columns=columns_to_drop)

                    # 使用預處理器
                    if 'preprocessor' in day_models:
                        processed_features = day_models['preprocessor'].transform(features_for_model)
                        processed_features = pd.DataFrame(
                            processed_features,
                            columns=features_for_model.columns
                        )
                    else:
                        processed_features = features_for_model

                    # 特徵選擇
                    if 'selected_features' in day_models:
                        selected_features = processed_features[day_models['selected_features']]
                    else:
                        selected_features = processed_features

                    # 預測
                    pred = day_models['best'].predict(selected_features)[0]
                    predictions[day] = float(pred)
                    print(f"Prediction for {day}: {pred}")

                    # 清理不需要的變數
                    del processed_features
                    del selected_features
                    gc.collect()

                except Exception as e:
                    print(f"Error in prediction process for {day}: {str(e)}")
                    predictions[day] = None
                    continue

            return predictions

        except Exception as e:
            print(f"Error in prediction: {str(e)}")
            return None
        finally:
            gc.collect()

    def __del__(self):
        """析構函數，確保清理記憶體"""
        self.models.clear()
        gc.collect()