import joblib
import pickle
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

# Создаем FastAPI приложение
app = FastAPI(title="Модель предсказания целевых действий",
              description="API для предсказания вероятности совершения целевого действия на сайте",
              version="1.0.0")

# Загрузка модели
model = joblib.load("model.joblib")

# Загружаем сохраненные энкодеры
with open('my_encoder_encoders.pkl', 'rb') as f:
    encoders = pickle.load(f)

# Определяем структуру входных данных
class SessionData(BaseModel):
    utm_campaign: Optional[str] = "(not set)"
    device_category: Optional[str] = "(not set)"
    device_os: Optional[str] = "(not set)"
    device_brand: Optional[str] = "(not set)"
    device_browser: Optional[str] = "(not set)"
    geo_city: Optional[str] = "(not set)"
    visit_number: int
    visit_date: str
    visit_time: str

# Определяем структуру ответа модели
class PredictionResponse(BaseModel):
    probability: float
    target_class: int

# Функция для подготовки данных
def prepare_data(session: SessionData):
    # Создаем DataFrame из входных данных
    df = pd.DataFrame([session.model_dump()])
    
    # Заполняем пропуски
    columns_to_exclude = ['visit_date', 'visit_time', 'visit_number']
    columns_to_convert = [col for col in df.columns if col not in columns_to_exclude]
    for col in columns_to_convert:
        df[col] = df[col].fillna('(not set)')
    
    # Преобразуем дату и время, получаем час
    df['visit_date'] = pd.to_datetime(df['visit_date'] + ' ' + df['visit_time'])
    df['hour'] = df['visit_date'].dt.hour
    df = df.drop(columns=['visit_date', 'visit_time'])
    
    # Кодируем переменную visit_number
    df['visit_number_1'] = (df['visit_number'] == 1).astype(int)
    df['visit_number_2_10'] = ((df['visit_number'] >= 2) & (df['visit_number'] <= 10)).astype(int)
    df['visit_number_11'] = (df['visit_number'] > 10).astype(int)
    df = df.drop(columns=['visit_number'])
    
    # Обрабатываем города
    allowed_cities = ['Moscow', 'Saint Petersburg', '(not set)', 'Yekaterinburg', 'Krasnodar',
                     'Kazan', 'Samara', 'Nizhny Novgorod', 'Ufa', 'Novosibirsk',
                     'Krasnoyarsk', 'Chelyabinsk', 'Tula', 'Voronezh', 'Rostov-on-Don',
                     'Irkutsk', 'Grozny', 'Balashikha', 'Vladivostok']
    if df['geo_city'].iloc[0] not in allowed_cities:
        df['geo_city'] = 'others'
    
    # Применяем One-Hot Encoding с использованием загруженных энкодеров
    for col, encoder in encoders.items():
        if col in df.columns:
            encoded_cols = encoder.get_feature_names_out([col])
            encoded_data = encoder.transform(df[[col]])
            encoded_df = pd.DataFrame(encoded_data, columns=encoded_cols, index=df.index)
            
            # Добавляем закодированные колонки
            df = pd.concat([df, encoded_df], axis=1)
            
            # Удаляем исходную колонку
            df = df.drop(columns=[col])
    
    return df

@app.post("/predict", response_model=PredictionResponse)
async def predict(session: SessionData):
    try:
        # Подготавливаем данные
        prepared_data = prepare_data(session)
        
        # Получаем вероятность положительного класса
        probability = model.predict_proba(prepared_data)[0][1]
        
        # Получаем предсказанный класс
        predicted_class = 1 if probability >= 0.5 else 0
        
        return PredictionResponse(
            probability=float(probability),
            target_class=int(predicted_class)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при предсказании: {str(e)}")

@app.get("/")
async def root():
    return {"message": "API для предсказания целевых действий пользователей на сайте"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
