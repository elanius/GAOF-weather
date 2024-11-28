## GAOF Weather Service

This FastAPI application provides weather information for GAOF zones using the OpenWeather API. It includes endpoints to fetch current weather data for a specific location or a rectangular zone.

### Features

- **`/weather`**: Get current weather for a specific latitude and longitude.
- **`/weather_zone`**: Get weather data for all cities within a specified rectangular geographical area.

---

### Requirements

- Python 3.12
- OpenWeather API Key

---

### Installation and Setup

#### 1. Clone the Repository

```bash
git clone https://github.com/sa8256_ATT/GAOF-weather.git
cd GAOF-weather
```

#### 2. Create a Virtual Environment

```bash
python3.12 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

#### 3. Install Dependencies

```bash
pip install .
```

#### 4. Set the OpenWeather API Key

Create a `.env` file in the project root:

```env
OPEN_WEATHER_API_KEY=your_api_key_here
```

---

### Running the Application

#### 1. Run Locally

```bash
uvicorn app.main:app --reload
```

The application will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000).

#### 2. Access Endpoints

- **Get weather for specific location**:
  ```
  GET /weather?lat=<latitude>&lon=<longitude>
  ```

- **Get weather for a rectangular zone**:
  ```
  GET /weather_zone?lon_left=<value>&lat_bottom=<value>&lon_right=<value>&lat_top=<value>
  ```

---

### Using Docker

#### 1. Build the Docker Image

```bash
docker build -t gaof-weather .
```

#### 2. Run the Docker Container

```bash
docker run -d -p 8000:8000 -e OPEN_WEATHER_API_KEY=your_api_key_here gaof-weather
```

The application will be accessible at [http://127.0.0.1:8000](http://127.0.0.1:8000).

---

### Using Docker Compose

#### 1. Start the Application

```bash
docker-compose up
```

---

### Testing the Endpoints

After starting the application, you can use the following URLs:

- **Weather for a location**:
  ```
  http://127.0.0.1:8000/weather?lat=40.7128&lon=-74.0060
  ```

- **Weather for a rectangular zone**:
  ```
  http://127.0.0.1:8000/weather_zone?lon_left=-74.2591&lat_bottom=40.4774&lon_right=-73.7002&lat_top=40.9176
  ```

---

### Notes

- Ensure your OpenWeather API key is valid.
- Modify the `uvicorn` command or `docker-compose.yml` as necessary for production deployments.
