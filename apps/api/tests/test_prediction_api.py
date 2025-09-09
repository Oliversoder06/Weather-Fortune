"""
Test suite for Weather Fortune API
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import sys
import os

# Add the parent directory to the path so we can import the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

client = TestClient(app)


class TestPredictionAPI:
    """Test suite for the /api/predict endpoint"""
    
    def test_root_endpoint(self):
        """Test the root endpoint returns basic info"""
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()
    
    def test_short_term_prediction(self):
        """Test 0-10 day predictions use forecast directly"""
        future_date = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
        
        response = client.get("/api/predict", params={
            "lat": 60.4833,  # Borlänge, Sweden
            "lon": 15.4167,
            "date": future_date
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields exist
        assert "temp" in data
        assert "low80" in data
        assert "high80" in data
        assert "low95" in data
        assert "high95" in data
        assert "explain" in data
        
        # Check explanation structure
        explain = data["explain"]
        assert "anchor" in explain
        assert "climo" in explain
        assert "w_anchor" in explain
        assert "ai_offset" in explain
        assert "days_ahead" in explain
        
        # For short-term predictions, w_anchor should be 1.0 or close to 1.0
        assert explain["w_anchor"] >= 0.8
    
    def test_medium_term_prediction(self):
        """Test 10-15 day predictions use blending"""
        future_date = (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d")
        
        response = client.get("/api/predict", params={
            "lat": 59.3293,  # Stockholm, Sweden
            "lon": 18.0686,
            "date": future_date
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have blended prediction (w_anchor < 1.0)
        explain = data["explain"]
        assert explain["w_anchor"] < 1.0
        assert explain["w_anchor"] > 0.0
        
        # Temperature should be reasonable for Sweden
        assert -20 <= data["temp"] <= 30
    
    def test_long_term_prediction(self):
        """Test 30+ day predictions rely more on climatology"""
        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        
        response = client.get("/api/predict", params={
            "lat": 60.4833,
            "lon": 15.4167,
            "date": future_date
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have very low anchor weight for long-term
        explain = data["explain"]
        assert explain["w_anchor"] < 0.5
        
        # Uncertainty bands should be reasonable
        assert data["low80"] < data["temp"] < data["high80"]
        assert data["low95"] < data["low80"]
        assert data["high95"] > data["high80"]
    
    def test_uncertainty_bands(self):
        """Test that uncertainty bands are properly ordered"""
        future_date = (datetime.now() + timedelta(days=20)).strftime("%Y-%m-%d")
        
        response = client.get("/api/predict", params={
            "lat": 55.6761,  # Copenhagen
            "lon": 12.5683,
            "date": future_date
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Check band ordering: 95% should be wider than 80%
        assert data["low95"] <= data["low80"]
        assert data["high95"] >= data["high80"]
        
        # Temperature should be within both bands
        assert data["low80"] <= data["temp"] <= data["high80"]
        assert data["low95"] <= data["temp"] <= data["high95"]
    
    def test_invalid_date_format(self):
        """Test error handling for invalid date formats"""
        response = client.get("/api/predict", params={
            "lat": 60.4833,
            "lon": 15.4167,
            "date": "invalid-date"
        })
        
        assert response.status_code == 400
        assert "Invalid date format" in response.json()["detail"]
    
    def test_past_date(self):
        """Test error handling for past dates"""
        past_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        response = client.get("/api/predict", params={
            "lat": 60.4833,
            "lon": 15.4167,
            "date": past_date
        })
        
        assert response.status_code == 400
        assert "Cannot predict for past dates" in response.json()["detail"]
    
    def test_extreme_coordinates(self):
        """Test handling of extreme but valid coordinates"""
        future_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        
        # Test Arctic location
        response = client.get("/api/predict", params={
            "lat": 78.2232,  # Svalbard
            "lon": 15.6267,
            "date": future_date
        })
        
        assert response.status_code == 200
        
        # Test Antarctic location
        response = client.get("/api/predict", params={
            "lat": -77.8419,  # Antarctica
            "lon": 166.6863,
            "date": future_date
        })
        
        assert response.status_code == 200
    
    def test_missing_parameters(self):
        """Test error handling for missing required parameters"""
        future_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        
        # Missing lat
        response = client.get("/api/predict", params={
            "lon": 15.4167,
            "date": future_date
        })
        assert response.status_code == 422
        
        # Missing lon
        response = client.get("/api/predict", params={
            "lat": 60.4833,
            "date": future_date
        })
        assert response.status_code == 422
        
        # Missing date
        response = client.get("/api/predict", params={
            "lat": 60.4833,
            "lon": 15.4167
        })
        assert response.status_code == 422


class TestClimatologyModel:
    """Test the climatology function behavior"""
    
    def test_seasonal_variation(self):
        """Test that climatology shows seasonal variation"""
        # Test summer vs winter predictions for same location
        summer_date = "2025-07-15"
        winter_date = "2025-01-15"
        
        summer_response = client.get("/api/predict", params={
            "lat": 60.4833,
            "lon": 15.4167,
            "date": summer_date
        })
        
        winter_response = client.get("/api/predict", params={
            "lat": 60.4833,
            "lon": 15.4167,
            "date": winter_date
        })
        
        assert summer_response.status_code == 200
        assert winter_response.status_code == 200
        
        summer_climo = summer_response.json()["explain"]["climo"]
        winter_climo = winter_response.json()["explain"]["climo"]
        
        # Summer should be warmer than winter in Northern Hemisphere
        assert summer_climo > winter_climo
    
    def test_latitude_effect(self):
        """Test that climatology varies with latitude"""
        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        
        # Northern location
        north_response = client.get("/api/predict", params={
            "lat": 70.0,  # High latitude
            "lon": 20.0,
            "date": future_date
        })
        
        # Southern location  
        south_response = client.get("/api/predict", params={
            "lat": 30.0,  # Low latitude
            "lon": 20.0,
            "date": future_date
        })
        
        assert north_response.status_code == 200
        assert south_response.status_code == 200
        
        # Lower latitudes should generally be warmer
        # (This is a simplified test - real climatology is more complex)
        north_std = north_response.json()["explain"]["climo_std"]
        south_std = south_response.json()["explain"]["climo_std"]
        
        # Higher latitudes should have more variability
        assert north_std >= south_std


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
