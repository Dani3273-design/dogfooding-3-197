#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Data Generator for Greenhouse Sensor Analysis
Generates 720 records (1 day, 2-minute intervals) simulating
a greenhouse in Northeast China during December.
"""

import csv
import math
import random
from datetime import datetime, timedelta
from pathlib import Path


def generateTestData():
    outputDir = Path(__file__).parent / "data"
    outputDir.mkdir(parents=True, exist_ok=True)
    outputFile = outputDir / "sensor_data.csv"
    
    startTime = datetime(2024, 12, 15, 0, 0, 0)
    records = []
    
    for i in range(720):
        currentTime = startTime + timedelta(minutes=2 * i)
        hour = currentTime.hour + currentTime.minute / 60.0
        
        temperature = generateTemperature(hour)
        humidity = generateHumidity(hour, temperature)
        lightIntensity = generateLightIntensity(hour)
        co2Concentration = generateCO2(hour, lightIntensity)
        soilMoisture = generateSoilMoisture(hour)
        soilTemperature = generateSoilTemperature(hour, temperature)
        
        records.append({
            "timestamp": currentTime.strftime("%Y-%m-%d %H:%M:%S"),
            "temperature": round(temperature, 2),
            "humidity": round(humidity, 2),
            "light_intensity": round(lightIntensity, 2),
            "co2_concentration": round(co2Concentration, 2),
            "soil_moisture": round(soilMoisture, 2),
            "soil_temperature": round(soilTemperature, 2)
        })
    
    fieldnames = [
        "timestamp", "temperature", "humidity", "light_intensity",
        "co2_concentration", "soil_moisture", "soil_temperature"
    ]
    
    with open(outputFile, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)
    
    print(f"[INFO] Generated {len(records)} records to {outputFile}")
    return outputFile


def generateTemperature(hour):
    baseTemp = 18.0
    amplitude = 8.0
    peakHour = 14.0
    
    phase = (hour - peakHour) * math.pi / 12
    temp = baseTemp + amplitude * math.cos(phase)
    
    noise = random.gauss(0, 0.5)
    temp += noise
    
    if 6 <= hour <= 18:
        temp += random.uniform(0, 2)
    else:
        temp -= random.uniform(0, 1)
    
    return max(10, min(35, temp))


def generateHumidity(hour, temperature):
    baseHumidity = 70.0
    tempEffect = (20 - temperature) * 0.8
    
    if 6 <= hour <= 18:
        humidity = baseHumidity + tempEffect - 10
    else:
        humidity = baseHumidity + tempEffect + 5
    
    noise = random.gauss(0, 3)
    humidity += noise
    
    if 5 <= hour <= 8:
        humidity += 10
    
    return max(30, min(100, humidity))


def generateLightIntensity(hour):
    if hour < 6 or hour > 18:
        return 0.0
    
    peakHour = 12.0
    maxIntensity = 50000.0
    
    phase = (hour - peakHour) * math.pi / 12
    intensity = maxIntensity * math.cos(phase)
    
    if intensity < 0:
        intensity = 0
    
    noise = random.gauss(0, maxIntensity * 0.1)
    intensity += noise
    
    cloudFactor = random.uniform(0.7, 1.0)
    intensity *= cloudFactor
    
    return max(0, intensity)


def generateCO2(hour, lightIntensity):
    baseCO2 = 400.0
    
    if lightIntensity > 1000:
        co2 = baseCO2 - (lightIntensity / 1000) * 30
    else:
        co2 = baseCO2 + random.uniform(0, 50)
    
    if 8 <= hour <= 17:
        co2 -= random.uniform(20, 50)
    else:
        co2 += random.uniform(10, 30)
    
    noise = random.gauss(0, 15)
    co2 += noise
    
    return max(300, min(800, co2))


def generateSoilMoisture(hour):
    baseMoisture = 60.0
    
    if 6 <= hour <= 8:
        moisture = baseMoisture + random.uniform(5, 10)
    elif 12 <= hour <= 14:
        moisture = baseMoisture - random.uniform(3, 8)
    else:
        moisture = baseMoisture
    
    noise = random.gauss(0, 2)
    moisture += noise
    
    return max(30, min(90, moisture))


def generateSoilTemperature(hour, airTemp):
    delayHours = 2.0
    delayedHour = hour - delayHours
    if delayedHour < 0:
        delayedHour += 24
    
    baseTemp = 10.0
    amplitude = 6.0
    peakHour = 16.0
    
    phase = (delayedHour - peakHour) * math.pi / 12
    soilTemp = baseTemp + amplitude * math.cos(phase)
    
    soilTemp = soilTemp * 0.7 + airTemp * 0.3
    
    noise = random.gauss(0, 0.3)
    soilTemp += noise
    
    return max(5, min(25, soilTemp))


if __name__ == "__main__":
    generateTestData()
