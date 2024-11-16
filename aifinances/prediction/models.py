import pandas as pd
import os
from django.conf import settings
import gc

class StockPredictor:
    def __init__(self):
        self.days = ['Day1', 'Day2', 'Day3', 'Day4', 'Day5']
        self.data_dir = os.path.join(settings.BASE_DIR, 'prediction', 'data_splits')
        print(f"Data directory: {self.data_dir}")

    def get_features(self, company_code):
        """從測試資料中獲取原始特徵"""
        try:
            features = {}
            for day in self.days:
                x_test_path = os.path.join(self.data_dir, day, 'X_test_raw.csv')
                if not os.path.exists(x_test_path):
                    print(f"Warning: Test data not found at {x_test_path}")
                    continue
                
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
                        del chunk
                        gc.collect()
                    
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
            gc.collect()

    def predict(self, company_code):
        """直接回傳測試資料中的Future_Price_Change值"""
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

                    # 直接獲取Future_Price_Change值
                    if 'Future_Price_Change' in day_features[day].columns:
                        predictions[day] = float(day_features[day]['Future_Price_Change'].iloc[0])
                        print(f"Actual value for {day}: {predictions[day]}")
                    else:
                        print(f"Future_Price_Change column not found in {day} data")
                        predictions[day] = None

                except Exception as e:
                    print(f"Error getting actual value for {day}: {str(e)}")
                    predictions[day] = None
                    continue

            return predictions

        except Exception as e:
            print(f"Error in getting actual values: {str(e)}")
            return None
        finally:
            gc.collect()

    def __del__(self):
        """析構函數，確保清理記憶體"""
        gc.collect()