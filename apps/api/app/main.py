from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, date
from typing import Optional
import httpx
import math
from pydantic import BaseModel

app = FastAPI(title="Weather Fortune API", version="1.0.0")

# Add CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PredictionResponse(BaseModel):
    temp: float
    low80: float
    high80: float
    low95: float
    high95: float
    explain: dict

@app.get("/")
async def root():
    return {"message": "Weather Fortune API"}

@app.get("/api/predict", response_model=PredictionResponse)
async def predict_weather(
    lat: float,
    lon: float,
    date: str,  # YYYY-MM-DD format
):
    """
    Predict weather for a given location and date.
    Blends short-term forecasts with climatology for longer ranges.
    """
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
        today = datetime.now().date()
        days_ahead = (target_date - today).days
        
        if days_ahead < 0:
            raise HTTPException(status_code=400, detail="Cannot predict for past dates")
        
        # Get forecast data and climatology
        anchor_temp = await get_forecast_anchor(lat, lon, days_ahead)
        climo_temp, climo_std = get_climatology(lat, lon, target_date)
        
        # Blend based on time distance
        if days_ahead <= 10:
            # Use forecast directly for short term
            if anchor_temp is not None:
                predicted_temp = anchor_temp
                w_anchor = 1.0
            else:
                # Fallback to climatology if forecast fails
                predicted_temp = climo_temp
                w_anchor = 0.0
        else:
            # Blend forecast anchor with climatology
            w_anchor = 0.5 ** ((days_ahead - 10) / 7)
            if anchor_temp is not None:
                predicted_temp = w_anchor * anchor_temp + (1 - w_anchor) * climo_temp
            else:
                # Fallback to climatology if forecast fails
                predicted_temp = climo_temp
                w_anchor = 0.0
        
        # Add AI offset (placeholder for now)
        ai_offset = 0.0  # Will implement AI model later
        final_temp = predicted_temp + ai_offset
        
        # Calculate uncertainty bands
        base_uncertainty = max(1.0, 0.6 * climo_std + 0.1 * days_ahead)
        band80 = base_uncertainty
        band95 = 1.6 * band80
        
        return PredictionResponse(
            temp=round(final_temp, 1),
            low80=round(final_temp - band80, 1),
            high80=round(final_temp + band80, 1),
            low95=round(final_temp - band95, 1),
            high95=round(final_temp + band95, 1),
            explain={
                "anchor": round(anchor_temp, 1) if anchor_temp else None,
                "climo": round(climo_temp, 1),
                "w_anchor": round(w_anchor, 2),
                "ai_offset": round(ai_offset, 1),
                "days_ahead": days_ahead,
                "climo_std": round(climo_std, 1)
            }
        )
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


async def get_forecast_anchor(lat: float, lon: float, days_ahead: int) -> Optional[float]:
    """
    Fetch weather forecast from Open-Meteo API.
    Returns the forecast temperature for the anchor point (day 10 or actual day if within 10 days).
    """
    try:
        anchor_day = min(days_ahead, 10)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "daily": "temperature_2m_mean",
                    "forecast_days": anchor_day + 1,
                    "timezone": "auto"
                },
                timeout=10.0
            )
            response.raise_for_status()
            
            data = response.json()
            
            if "daily" in data and "temperature_2m_mean" in data["daily"]:
                temps = data["daily"]["temperature_2m_mean"]
                if len(temps) > anchor_day:
                    return temps[anchor_day]
            
            return None
            
    except Exception as e:
        print(f"Error fetching forecast: {e}")
        return None


def get_climatology(lat: float, lon: float, target_date: date) -> tuple[float, float]:
    """
    Get climatological temperature for a given location and date.
    For now, uses a simple seasonal cycle based on latitude.
    TODO: Replace with real historical data from Meteostat or ERA5.
    """
    # Simple seasonal model based on day of year and latitude
    day_of_year = target_date.timetuple().tm_yday
    
    # Seasonal cycle (cosine with peak around July 15 for NH, Jan 15 for SH)
    if lat >= 0:  # Northern Hemisphere
        peak_day = 196  # July 15
    else:  # Southern Hemisphere
        peak_day = 15   # January 15
    
    # Phase shift for hemisphere
    seasonal_phase = 2 * math.pi * (day_of_year - peak_day) / 365.25
    seasonal_amplitude = abs(lat) * 0.4  # Larger amplitude at higher latitudes
    
    # Base temperature decreases with latitude
    base_temp = 25 - abs(lat) * 0.6
    
    # Add seasonal variation
    climo_temp = base_temp + seasonal_amplitude * math.cos(seasonal_phase)
    
    # Standard deviation increases with latitude and distance from summer
    base_std = 2.0 + abs(lat) * 0.05
    seasonal_std_factor = 1.0 + 0.5 * abs(math.cos(seasonal_phase))
    climo_std = base_std * seasonal_std_factor
    
    return climo_temp, climo_std


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
