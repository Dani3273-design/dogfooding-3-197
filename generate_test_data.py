#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test data generator for greenhouse sensor data analysis.
Generates 720 records of simulated greenhouse sensor data (1 day, every 2 minutes).
Simulates indoor greenhouse environment in Northeast China, December.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os


def generateGreenhouseData(outputPath="data/sensor_data.csv", recordCount=720):
    """
    Generate simulated greenhouse sensor data.
    
    Args:
        outputPath: Path to save the CSV file
        recordCount: Number of records to generate (default 720 for 1 day, every 2 minutes)
    """
    print(f"[INFO] Starting test data generation, target records: {recordCount}")
    
    # Base date: December 15, 2024 (Northeast China winter)
    baseDate = datetime(2024, 12, 15, 0, 0, 0)
    
    # Generate timestamps (every 2 minutes)
    timestamps = [baseDate + timedelta(minutes=2 * i) for i in range(recordCount)]
    
    # Convert to hours for temperature calculation (0-24 hours)
    hours = np.array([(t - baseDate).total_seconds() / 3600 for t in timestamps])
    
    # Temperature simulation (greenhouse indoor, Northeast China December)
    # Outdoor temperature range: -15°C to -5°C
    # Indoor temperature controlled: 18°C to 28°C
    # Temperature follows daily pattern: lower at night, higher during day
    # Peak temperature around 14:00, lowest around 06:00
    baseTemp = 23.0  # Base temperature
    tempAmplitude = 5.0  # Temperature variation amplitude
    tempPhase = 14.0  # Peak temperature hour
    
    # Sinusoidal temperature pattern with some noise
    temperature = baseTemp + tempAmplitude * np.sin(2 * np.pi * (hours - tempPhase) / 24)
    # Add random noise (±1°C)
    temperature += np.random.normal(0, 0.5, recordCount)
    # Ensure temperature stays in reasonable range
    temperature = np.clip(temperature, 18.0, 28.0)
    
    # Humidity simulation (inverse relationship with temperature)
    # Higher humidity at night (70-90%), lower during day (50-70%)
    baseHumidity = 70.0
    humidityAmplitude = 15.0
    humidity = baseHumidity - humidityAmplitude * np.sin(2 * np.pi * (hours - tempPhase) / 24)
    humidity += np.random.normal(0, 3, recordCount)
    humidity = np.clip(humidity, 50.0, 95.0)
    
    # Light intensity simulation (lux)
    # Sunrise around 07:00, sunset around 16:30 in Northeast China December
    # Peak around 12:00
    lightIntensity = np.zeros(recordCount)
    for i, h in enumerate(hours):
        if 7 <= h <= 16.5:  # Daylight hours
            # Parabolic curve for light intensity
            lightIntensity[i] = 50000 * (1 - ((h - 11.75) / 4.75) ** 2)
            if lightIntensity[i] < 0:
                lightIntensity[i] = 0
        else:
            lightIntensity[i] = np.random.uniform(0, 100)  # Minimal light at night
    lightIntensity += np.random.normal(0, 500, recordCount)
    lightIntensity = np.clip(lightIntensity, 0, 55000)
    
    # CO2 concentration (ppm)
    # Higher at night (400-600 ppm), lower during day due to photosynthesis (300-450 ppm)
    baseCo2 = 450.0
    co2Amplitude = 100.0
    co2Concentration = baseCo2 + co2Amplitude * np.cos(2 * np.pi * (hours - tempPhase) / 24)
    co2Concentration += np.random.normal(0, 20, recordCount)
    co2Concentration = np.clip(co2Concentration, 300.0, 650.0)
    
    # Soil moisture (%)
    # Relatively stable, slight decrease during day due to evaporation
    baseSoilMoisture = 65.0
    soilMoisture = baseSoilMoisture - 5 * np.sin(2 * np.pi * (hours - 12) / 24)
    soilMoisture += np.random.normal(0, 2, recordCount)
    soilMoisture = np.clip(soilMoisture, 55.0, 75.0)
    
    # Soil temperature (°C)
    # Slightly lower than air temperature, more stable
    soilTemperature = temperature * 0.9 + 2
    soilTemperature += np.random.normal(0, 0.3, recordCount)
    soilTemperature = np.clip(soilTemperature, 16.0, 26.0)
    
    # Create DataFrame
    df = pd.DataFrame({
        'timestamp': timestamps,
        'temperature': np.round(temperature, 2),
        'humidity': np.round(humidity, 2),
        'light_intensity': np.round(lightIntensity, 2),
        'co2_concentration': np.round(co2Concentration, 2),
        'soil_moisture': np.round(soilMoisture, 2),
        'soil_temperature': np.round(soilTemperature, 2)
    })
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(outputPath), exist_ok=True)
    
    # Save to CSV
    df.to_csv(outputPath, index=False, encoding='utf-8')
    print(f"[INFO] Test data generated successfully: {outputPath}")
    print(f"[INFO] Total records: {len(df)}")
    print(f"[INFO] Time range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    
    return df


if __name__ == "__main__":
    print("[INFO] Greenhouse Sensor Test Data Generator")
    print("[INFO] Simulating Northeast China greenhouse environment, December")
    generateGreenhouseData()
    print("[INFO] Test data generation completed")
