#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据生成脚本
生成东北地区12月份温室大棚传感器模拟数据
"""

import csv
import random
from datetime import datetime, timedelta
import math
import os


def generateSensorData():
    print("Generating test sensor data for greenhouse...")
    
    baseDate = datetime(2024, 12, 15, 0, 0, 0)
    records = []
    
    for i in range(720):
        timestamp = baseDate + timedelta(minutes=2 * i)
        hour = timestamp.hour + timestamp.minute / 60
        
        hourAngle = (hour - 4) * math.pi / 12
        
        baseTemp = 18 + 8 * math.sin(max(0, hourAngle)) * math.exp(-((hour - 12) / 6) ** 2)
        temperature = baseTemp + random.uniform(-0.5, 0.5)
        
        humidityBase = 75 - 20 * math.sin(max(0, hourAngle)) * math.exp(-((hour - 12) / 6) ** 2)
        humidity = humidityBase + random.uniform(-2, 2)
        humidity = max(40, min(95, humidity))
        
        if 6 <= hour <= 18:
            lightAngle = (hour - 6) * math.pi / 12
            baseLight = 30000 * math.sin(lightAngle)
            lightIntensity = baseLight + random.uniform(-2000, 2000)
        else:
            lightIntensity = random.uniform(0, 50)
        
        co2Base = 1000 - 300 * math.sin(max(0, hourAngle)) * math.exp(-((hour - 13) / 5) ** 2)
        co2 = co2Base + random.uniform(-30, 30)
        
        records.append({
            'Timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'Temperature': round(temperature, 2),
            'Humidity': round(humidity, 2),
            'LightIntensity': round(lightIntensity, 2),
            'CO2': round(co2, 2)
        })
    
    return records


def saveToCsv(records, filePath):
    os.makedirs(os.path.dirname(filePath), exist_ok=True)
    
    with open(filePath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['Timestamp', 'Temperature', 'Humidity', 'LightIntensity', 'CO2'])
        writer.writeheader()
        writer.writerows(records)
    
    print(f"Successfully generated {len(records)} records")
    print(f"Data saved to: {filePath}")
    print("\nData summary:")
    print(f"  Time range: {records[0]['Timestamp']} - {records[-1]['Timestamp']}")
    print(f"  Temperature range: {min(r['Temperature'] for r in records)} - {max(r['Temperature'] for r in records)} °C")
    print(f"  Humidity range: {min(r['Humidity'] for r in records)} - {max(r['Humidity'] for r in records)} %")
    print(f"  Max Light Intensity: {max(r['LightIntensity'] for r in records):.0f} Lux")
    print(f"  CO2 range: {min(r['CO2'] for r in records):.0f} - {max(r['CO2'] for r in records):.0f} ppm")


if __name__ == "__main__":
    records = generateSensorData()
    saveToCsv(records, 'data/sensor_data.csv')
