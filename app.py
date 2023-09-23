from flask import Flask, request, render_template
import requests
import datetime

app = Flask(__name__)

api_key = "94953df9e840acc06f1d41401a594cee"

@app.route('/')
def index():
    return render_template('index.html')

def get_hourly_forecast(city):
    api_key = '94953df9e840acc06f1d41401a594cee'
    hourly_url = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}'
    response = requests.get(hourly_url)

    if response.status_code == 200:
        hourly_data = response.json()
        return hourly_data
    else:
        return None
    
@app.route('/get_weather', methods=['POST'])
def get_weather():
    city = request.form['city']

    weather_url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}'
    weather_response = requests.get(weather_url)

    geocoding_url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}'
    geocoding_response = requests.post(geocoding_url)

    if weather_response.status_code == 200:
        weather_data = weather_response.json()
        geocoding_data = geocoding_response.json()
        hourly_data = get_hourly_forecast(city)
        
        temperature = weather_data['main']['temp']
        weather_description = weather_data['weather'][0]['description']

        latitude = geocoding_data['coord']['lat']
        longitude = geocoding_data['coord']['lon']

        weather_layers = {
            'Clouds': f'https://tile.openweathermap.org/map/clouds_new/10/{latitude}/{longitude}.png?appid={api_key}',
            'Precipitation': f'https://tile.openweathermap.org/map/precipitation_new/10/{latitude}/{longitude}.png?appid={api_key}',
            'Pressure': f'https://tile.openweathermap.org/map/pressure_new/10/{latitude}/{longitude}.png?appid={api_key}',
            'Wind Speed': f'https://tile.openweathermap.org/map/wind_new/10/{latitude}/{longitude}.png?appid={api_key}',
            'Temperature': f'https://tile.openweathermap.org/map/temp_new/10/{latitude}/{longitude}.png?appid={api_key}'
        }
        
        coordinates = weather_data['coord']
        pressure = weather_data['main']['pressure']
        humidity = weather_data['main']['humidity']
        visibility = weather_data['visibility']
        wind_speed = weather_data['wind']['speed']
        cloud_cover = weather_data['clouds']['all']
        
        sunrise_timestamp = weather_data['sys']['sunrise']
        sunset_timestamp = weather_data['sys']['sunset']
        sunrise_datetime = datetime.datetime.utcfromtimestamp(sunrise_timestamp)
        sunset_datetime = datetime.datetime.utcfromtimestamp(sunset_timestamp)
        sunrise_time = sunrise_datetime.strftime('%H:%M:%S')
        sunset_time = sunset_datetime.strftime('%H:%M:%S')

        #Hourly Data
        hourly_data = get_hourly_forecast(city)

    if hourly_data:
        hourly_forecast_list = hourly_data.get('list', [])
        hourly_forecast_info = []
        for forecast in hourly_forecast_list:
            dt_txt = forecast['dt_txt']
            temperature = forecast['main']['temp']
            weather_description = forecast['weather'][0]['description']
            humidity = forecast['main']['humidity']
            wind_speed = forecast['wind']['speed']
            hourly_forecast_info.append({
                'dt_txt': dt_txt,
                'temperature': temperature,
                'weather_description': weather_description,
                'humidity': humidity,
                'wind_speed': wind_speed
            })
        return render_template('result.html', city=city, temperature=temperature, weather_description=weather_description,
                               coordinates=coordinates, pressure=pressure, humidity=humidity, visibility=visibility,
                               wind_speed=wind_speed, cloud_cover=cloud_cover,
                               sunrise_time=sunrise_time, sunset_time=sunset_time, weather_data=weather_data, hourly_forecast_info=hourly_forecast_info, weather_layers=weather_layers)
    else:
        error_message = "Failed to fetch weather data. Please check the city name and try again."
        return render_template('error.html', error_message=error_message)

if __name__ == '__main__':
    app.run(debug=True)
