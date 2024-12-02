import requests
from datetime import datetime
from decimal import Decimal
from django.utils import timezone
import os
from dotenv import load_dotenv

load_dotenv()

class WAQIDataService:
    BASE_URL = "https://api.waqi.info"
    API_KEY = os.getenv('WAQI_API_KEY')

    @classmethod
    def fetch_city_data(cls, city):
        """
        Fetch current data for a city
        """
        try:
            url = f"{cls.BASE_URL}/feed/{city}/?token={cls.API_KEY}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if data.get('status') != 'ok':
                return False, "Error fetching data"

            return True, data['data']

        except requests.RequestException as e:
            return False, f"API request failed: {str(e)}"
        except Exception as e:
            return False, f"Error processing data: {str(e)}"

def save_waqi_data(location, data):
    """
    Save WAQI data to database models
    Only save historical and current data, not future forecasts
    """
    from dashboard.models import Metric, AirQualityIndex

    try:
        # Get the current time for filtering
        current_time = timezone.now()
        
        # Parse the data timestamp
        data_time = datetime.fromisoformat(data['time']['iso'].replace('Z', '+00:00'))
        
        # Get current measurements from iaqi
        iaqi = data.get('iaqi', {})
        
        # Create current metric entry
        metric = Metric.objects.create(
            location=location,
            timestamp=data_time,
            pm25=Decimal(str(iaqi.get('pm25', {}).get('v', 0))),
            pm10=Decimal(str(iaqi.get('pm10', {}).get('v', 0))),
            o3=Decimal(str(iaqi.get('o3', {}).get('v', 0))),
            no2=Decimal(str(iaqi.get('no2', {}).get('v', 0))),
            so2=Decimal(str(iaqi.get('so2', {}).get('v', 0))),
            temperature=Decimal(str(iaqi.get('t', {}).get('v', 0))),
            humidity=Decimal(str(iaqi.get('h', {}).get('v', 0)))
        )

        # Create AQI entry
        AirQualityIndex.objects.create(
            location=location,
            timestamp=data_time,
            aqi_value=data.get('aqi', 0),
            category=get_aqi_category(data.get('aqi', 0)),
            dominant_pollutant=data.get('dominentpol', 'pm25'),
            health_implications=get_health_implications(get_aqi_category(data.get('aqi', 0)))
        )

        # Process historical data from forecast section
        forecast = data.get('forecast', {}).get('daily', {})
        
        # Process PM2.5 historical data (not forecasts)
        for pm25_data in forecast.get('pm25', []):
            date = datetime.strptime(pm25_data['day'], '%Y-%m-%d')
            
            # Skip if the date is in the future
            if date.date() >= current_time.date():
                continue
                
            # Create historical metric
            Metric.objects.create(
                location=location,
                timestamp=date,
                pm25=Decimal(str(pm25_data.get('avg', 0))),
                pm10=Decimal(str(get_forecast_value(forecast, 'pm10', date))),
                o3=Decimal(str(get_forecast_value(forecast, 'o3', date)))
            )

            # Create historical AQI
            AirQualityIndex.objects.create(
                location=location,
                timestamp=date,
                aqi_value=int(pm25_data.get('avg', 0)),
                category=get_aqi_category(pm25_data.get('avg', 0)),
                dominant_pollutant='pm25',
                health_implications=get_health_implications(get_aqi_category(pm25_data.get('avg', 0)))
            )

        return True, "Data saved successfully"
    except Exception as e:
        return False, f"Error saving data: {str(e)}"

def get_forecast_value(forecast, pollutant, date):
    """Helper function to get historical value for a specific date and pollutant"""
    date_str = date.strftime('%Y-%m-%d')
    for item in forecast.get(pollutant, []):
        if item['day'] == date_str:
            return item.get('avg', 0)
    return 0

def get_aqi_category(aqi_value):
    """Convert numerical AQI to category"""
    aqi_value = float(aqi_value)
    if aqi_value <= 50:
        return 'Good'
    elif aqi_value <= 100:
        return 'Moderate'
    elif aqi_value <= 150:
        return 'Unhealthy for Sensitive Groups'
    elif aqi_value <= 200:
        return 'Unhealthy'
    elif aqi_value <= 300:
        return 'Very Unhealthy'
    return 'Hazardous'

def get_health_implications(category):
    """Get health implications based on AQI category"""
    implications = {
        'Good': 'Air quality is satisfactory, and air pollution poses little or no risk.',
        'Moderate': 'Air quality is acceptable. However, there may be a risk for some people.',
        'Unhealthy for Sensitive Groups': 'Members of sensitive groups may experience health effects.',
        'Unhealthy': 'Everyone may begin to experience health effects.',
        'Very Unhealthy': 'Health alert: everyone may experience more serious health effects.',
        'Hazardous': 'Health warning of emergency conditions.'
    }
    return implications.get(category, '')