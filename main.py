#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
温室大棚传感器数据分析程序
功能：读取传感器CSV数据，生成包含可视化图表和统计分析的PDF报告
"""

import os
import logging
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

DATA_DIR = "data"
OUTPUT_DIR = "output"
CSV_FILE = os.path.join(DATA_DIR, "sensor_data.csv")
PDF_FILE = os.path.join(OUTPUT_DIR, "sensor_analysis_report.pdf")


def setupChineseFont():
    fontPaths = [
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/Library/Fonts/Arial Unicode.ttf"
    ]
    
    selectedFont = None
    fontName = None
    
    for fontPath in fontPaths:
        if os.path.exists(fontPath):
            selectedFont = fontPath
            if "STHeiti" in fontPath:
                fontName = "STHeiti"
            else:
                fontName = "ArialUnicode"
            break
    
    if selectedFont:
        logger.info(f"Using Chinese font: {selectedFont}")
        try:
            font_manager.fontManager.addfont(selectedFont)
            if "STHeiti" in selectedFont:
                plt.rcParams['font.sans-serif'] = ['STHeiti']
            else:
                plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
            plt.rcParams['axes.unicode_minus'] = False
            
            try:
                if "ttc" in selectedFont.lower():
                    pdfmetrics.registerFont(TTFont(fontName, selectedFont, subfontIndex=0))
                else:
                    pdfmetrics.registerFont(TTFont(fontName, selectedFont))
                logger.info(f"Successfully registered font: {fontName}")
            except Exception as e:
                logger.warning(f"Reportlab font registration failed, using fallback: {str(e)}")
                fontName = None
            
            return fontName
        except Exception as e:
            logger.warning(f"Font setup failed: {str(e)}")
            return None
    else:
        logger.warning("Chinese font not found, using default font")
        return None


def loadSensorData(filePath):
    logger.info(f"Loading sensor data from {filePath}")
    try:
        df = pd.read_csv(filePath)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        logger.info(f"Successfully loaded {len(df)} records")
        return df
    except Exception as e:
        logger.error(f"Failed to load data: {str(e)}")
        raise


def calculateStatistics(df):
    logger.info("Calculating statistics for sensor data")
    stats = {}
    
    for column in ['Temperature', 'Humidity', 'LightIntensity', 'CO2']:
        maxVal = df[column].max()
        minVal = df[column].min()
        meanVal = df[column].mean()
        
        maxTime = df.loc[df[column].idxmax(), 'Timestamp']
        minTime = df.loc[df[column].idxmin(), 'Timestamp']
        
        hourRange = df[(df['Timestamp'].dt.hour >= 10) & (df['Timestamp'].dt.hour <= 14)]
        dayMaxMean = hourRange[column].mean() if len(hourRange) > 0 else meanVal
        
        stats[column] = {
            'max': maxVal,
            'min': minVal,
            'mean': meanVal,
            'maxTime': maxTime,
            'minTime': minTime,
            'dayMaxMean': dayMaxMean
        }
        
        logger.info(f"{column}: max={maxVal:.2f}, min={minVal:.2f}, mean={meanVal:.2f}")
    
    return stats


def plotTimeSeries(df, column, title, ylabel, color, outputPath):
    logger.info(f"Generating time series plot for {column}")
    
    fig, ax = plt.subplots(figsize=(12, 6), dpi=100)
    
    ax.plot(df['Timestamp'], df[column], color=color, linewidth=1.5, alpha=0.8)
    ax.scatter(df['Timestamp'], df[column], color=color, s=15, alpha=0.6)
    
    maxVal = df[column].max()
    maxIdx = df[column].idxmax()
    maxTime = df.loc[maxIdx, 'Timestamp']
    
    minVal = df[column].min()
    minIdx = df[column].idxmin()
    minTime = df.loc[minIdx, 'Timestamp']
    
    if column == 'Temperature':
        unit = '°C'
        desc = f"一天最高温度的时间区间为上午10点至下午2点，最高温度 {maxVal:.1f}{unit} 出现在 {maxTime.strftime('%H:%M')}"
    elif column == 'Humidity':
        unit = '%'
        desc = f"湿度随温度反向变化，白天较低夜间较高，最低湿度 {minVal:.1f}{unit} 出现在 {minTime.strftime('%H:%M')}"
    elif column == 'LightIntensity':
        unit = 'Lux'
        desc = f"光照强度随日出日落变化，最强光照 {maxVal:.0f}{unit} 出现在 {maxTime.strftime('%H:%M')}"
    else:
        unit = 'ppm'
        desc = f"CO2浓度受植物光合作用影响，白天浓度较低，夜间浓度升高"
    
    ax.text(
        0.02, 0.98, desc,
        transform=ax.transAxes,
        fontsize=11,
        verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
        wrap=True
    )
    
    ax.set_title(title, fontsize=14, pad=20)
    ax.set_xlabel('时间', fontsize=12)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    plt.savefig(outputPath, dpi=100, bbox_inches='tight')
    plt.close()
    logger.info(f"Plot saved to {outputPath}")


def generateAllPlots(df):
    logger.info("Generating all visualization plots")
    
    plotConfigs = [
        ('Temperature', '温室大棚温度变化趋势', '温度 (°C)', '#FF6B6B', 'temperature_plot.png'),
        ('Humidity', '温室大棚湿度变化趋势', '相对湿度 (%)', '#4ECDC4', 'humidity_plot.png'),
        ('LightIntensity', '温室大棚光照强度变化趋势', '光照强度 (Lux)', '#FFE66D', 'light_plot.png'),
        ('CO2', '温室大棚CO2浓度变化趋势', 'CO2浓度 (ppm)', '#95E1D3', 'co2_plot.png')
    ]
    
    plotPaths = []
    for column, title, ylabel, color, filename in plotConfigs:
        outputPath = os.path.join(OUTPUT_DIR, filename)
        plotTimeSeries(df, column, title, ylabel, color, outputPath)
        plotPaths.append(outputPath)
    
    return plotPaths


def generatePdfReport(stats, plotPaths, chineseFontName):
    logger.info(f"Generating PDF report: {PDF_FILE}")
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    c = canvas.Canvas(PDF_FILE, pagesize=A4)
    width, height = A4
    
    fontName = chineseFontName if chineseFontName else 'Helvetica'
    
    c.setFont(fontName, 20)
    c.drawCentredString(width / 2, height - 2 * cm, "温室大棚传感器数据分析报告")
    
    c.setFont(fontName, 12)
    dateStr = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.drawCentredString(width / 2, height - 3 * cm, f"生成时间: {dateStr}")
    
    c.setFont(fontName, 14)
    c.drawString(2 * cm, height - 4.5 * cm, "数据统计摘要:")
    
    c.setFont(fontName, 10)
    yPos = height - 5.5 * cm
    lineHeight = 0.8 * cm
    
    descriptions = {
        'Temperature': ('温度', '°C'),
        'Humidity': ('湿度', '%'),
        'LightIntensity': ('光照强度', 'Lux'),
        'CO2': ('CO2浓度', 'ppm')
    }
    
    for key, (name, unit) in descriptions.items():
        stat = stats[key]
        c.drawString(2 * cm, yPos, f"{name}:")
        c.drawString(4 * cm, yPos, f"最高: {stat['max']:.2f}{unit} ({stat['maxTime'].strftime('%H:%M')})")
        c.drawString(9 * cm, yPos, f"最低: {stat['min']:.2f}{unit} ({stat['minTime'].strftime('%H:%M')})")
        c.drawString(14 * cm, yPos, f"平均: {stat['mean']:.2f}{unit}")
        yPos -= lineHeight
    
    yPos -= 1 * cm
    
    imageWidth = 16 * cm
    imageHeight = 8 * cm
    
    for i, plotPath in enumerate(plotPaths):
        if i > 0:
            c.showPage()
            c.setFont(fontName, 14)
            pageTitle = f"图{i+1}: {['温度变化', '湿度变化', '光照强度变化', 'CO2浓度变化'][i]}"
            c.drawString(2 * cm, height - 2 * cm, pageTitle)
        
        yImage = height - 10 * cm if i == 0 else height - 5 * cm
        c.drawImage(plotPath, 2 * cm, yImage - imageHeight, width=imageWidth, height=imageHeight)
    
    c.save()
    logger.info(f"PDF report generated successfully: {PDF_FILE}")


def cleanupTempFiles(plotPaths):
    logger.info("Cleaning up temporary image files")
    for plotPath in plotPaths:
        if os.path.exists(plotPath):
            os.remove(plotPath)
            logger.debug(f"Removed temporary file: {plotPath}")


def main():
    logger.info("=" * 50)
    logger.info("Starting sensor data analysis program")
    logger.info("=" * 50)
    
    chineseFontName = setupChineseFont()
    
    df = loadSensorData(CSV_FILE)
    
    stats = calculateStatistics(df)
    
    plotPaths = generateAllPlots(df)
    
    generatePdfReport(stats, plotPaths, chineseFontName)
    
    cleanupTempFiles(plotPaths)
    
    logger.info("=" * 50)
    logger.info("Sensor data analysis completed successfully")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
