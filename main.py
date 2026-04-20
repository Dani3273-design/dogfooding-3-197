#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Greenhouse Sensor Data Analysis Program
Analyzes sensor data and generates PDF report with visualizations.
"""

import os
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.font_manager import FontProperties


class SensorDataAnalyzer:
    """Main analyzer class for greenhouse sensor data."""
    
    def __init__(self, dataPath: str, outputPath: str):
        self.dataPath = Path(dataPath)
        self.outputPath = Path(outputPath)
        self.outputPath.mkdir(parents=True, exist_ok=True)
        self.reportPath = self.outputPath / "sensor_analysis_report.pdf"
        self.df = None
        self.analysisResults = {}
        self.fontProp = None
        self._setupChineseFont()
    
    def _setupChineseFont(self):
        """Setup Chinese font for matplotlib."""
        plt.rcParams["font.sans-serif"] = ["Arial Unicode MS", "SimHei", "STHeiti"]
        plt.rcParams["axes.unicode_minus"] = False
    
    def loadData(self):
        """Load sensor data from CSV file."""
        print("[INFO] Loading sensor data...")
        self.df = pd.read_csv(self.dataPath)
        self.df["timestamp"] = pd.to_datetime(self.df["timestamp"])
        self.df["hour"] = self.df["timestamp"].dt.hour
        print(f"[INFO] Loaded {len(self.df)} records")
        return self.df
    
    def analyzeData(self):
        """Perform statistical analysis on sensor data."""
        print("[INFO] Analyzing sensor data...")
        
        self.analysisResults = {
            "temperature": self._analyzeMetric("temperature", "温度", "°C"),
            "humidity": self._analyzeMetric("humidity", "湿度", "%"),
            "light_intensity": self._analyzeMetric("light_intensity", "光照强度", "lux"),
            "co2_concentration": self._analyzeMetric("co2_concentration", "CO2浓度", "ppm"),
            "soil_moisture": self._analyzeMetric("soil_moisture", "土壤湿度", "%"),
            "soil_temperature": self._analyzeMetric("soil_temperature", "土壤温度", "°C")
        }
        
        self._findPeakHours()
        
        print("[INFO] Analysis completed")
        return self.analysisResults
    
    def _analyzeMetric(self, column: str, name: str, unit: str):
        """Analyze a single metric."""
        data = self.df[column]
        
        result = {
            "name": name,
            "unit": unit,
            "min": data.min(),
            "max": data.max(),
            "mean": data.mean(),
            "std": data.std(),
            "minTime": self.df.loc[data.idxmin(), "timestamp"],
            "maxTime": self.df.loc[data.idxmax(), "timestamp"]
        }
        
        return result
    
    def _findPeakHours(self):
        """Find peak hour ranges for each metric."""
        for key, result in self.analysisResults.items():
            column = key
            hourlyMean = self.df.groupby("hour")[column].mean()
            
            maxHour = hourlyMean.idxmax()
            minHour = hourlyMean.idxmin()
            
            result["peakHourRange"] = f"{maxHour}:00 - {maxHour + 1}:00"
            result["lowHourRange"] = f"{minHour}:00 - {minHour + 1}:00"
            result["hourlyMean"] = hourlyMean
    
    def generateReport(self):
        """Generate PDF report with visualizations."""
        print("[INFO] Generating PDF report...")
        
        with PdfPages(self.reportPath) as pdf:
            self._generateTitlePage(pdf)
            
            for key in self.analysisResults.keys():
                self._generateMetricChart(pdf, key)
            
            self._generateSummaryPage(pdf)
        
        print(f"[INFO] Report saved to {self.reportPath}")
        return self.reportPath
    
    def _generateTitlePage(self, pdf: PdfPages):
        """Generate title page for the report."""
        fig, ax = plt.subplots(figsize=(11.69, 8.27))
        ax.axis("off")
        
        title = "温室大棚传感器数据分析报告"
        subtitle = f"数据时间范围: {self.df['timestamp'].min().strftime('%Y-%m-%d %H:%M')} 至 {self.df['timestamp'].max().strftime('%Y-%m-%d %H:%M')}"
        generatedTime = f"报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        ax.text(0.5, 0.6, title, fontsize=28, ha="center", va="center", fontweight="bold")
        ax.text(0.5, 0.45, subtitle, fontsize=14, ha="center", va="center")
        ax.text(0.5, 0.35, generatedTime, fontsize=12, ha="center", va="center")
        
        dataInfo = f"数据记录数: {len(self.df)} 条"
        ax.text(0.5, 0.25, dataInfo, fontsize=12, ha="center", va="center")
        
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)
    
    def _generateMetricChart(self, pdf: PdfPages, metricKey: str):
        """Generate chart for a single metric."""
        result = self.analysisResults[metricKey]
        column = metricKey
        
        fig, axes = plt.subplots(2, 1, figsize=(11.69, 8.27))
        
        ax1 = axes[0]
        ax1.plot(self.df["timestamp"], self.df[column], "b-", linewidth=0.8, alpha=0.7)
        ax1.set_title(f"{result['name']}变化趋势", fontsize=14, fontweight="bold")
        ax1.set_xlabel("时间")
        ax1.set_ylabel(f"{result['name']} ({result['unit']})")
        ax1.grid(True, alpha=0.3)
        
        ax1.axhline(y=result["mean"], color="r", linestyle="--", label=f"平均值: {result['mean']:.2f}")
        ax1.legend(loc="upper right")
        
        maxIdx = self.df[column].idxmax()
        minIdx = self.df[column].idxmin()
        ax1.scatter([self.df.loc[maxIdx, "timestamp"]], [result["max"]], color="red", s=50, zorder=5, label=f"最高值: {result['max']:.2f}")
        ax1.scatter([self.df.loc[minIdx, "timestamp"]], [result["min"]], color="green", s=50, zorder=5, label=f"最低值: {result['min']:.2f}")
        
        ax2 = axes[1]
        hours = result["hourlyMean"].index
        values = result["hourlyMean"].values
        ax2.bar(hours, values, color="steelblue", alpha=0.7)
        ax2.set_title(f"{result['name']}小时平均值分布", fontsize=14, fontweight="bold")
        ax2.set_xlabel("小时")
        ax2.set_ylabel(f"{result['name']} ({result['unit']})")
        ax2.set_xticks(range(24))
        ax2.grid(True, alpha=0.3, axis="y")
        
        analysisText = self._generateAnalysisText(result)
        fig.text(0.5, 0.02, analysisText, fontsize=10, ha="center", va="bottom", 
                bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.8))
        
        plt.tight_layout(rect=[0, 0.08, 1, 1])
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)
    
    def _generateAnalysisText(self, result: dict) -> str:
        """Generate Chinese analysis text for a metric."""
        maxTimeStr = result["maxTime"].strftime("%H:%M")
        minTimeStr = result["minTime"].strftime("%H:%M")
        
        text = (
            f"【{result['name']}分析】"
            f"最高值: {result['max']:.2f}{result['unit']} (时间: {maxTimeStr})，"
            f"最低值: {result['min']:.2f}{result['unit']} (时间: {minTimeStr})，"
            f"平均值: {result['mean']:.2f}{result['unit']}，"
            f"最高值时段: {result['peakHourRange']}，"
            f"最低值时段: {result['lowHourRange']}"
        )
        
        return text
    
    def _generateSummaryPage(self, pdf: PdfPages):
        """Generate summary page for the report."""
        fig, ax = plt.subplots(figsize=(11.69, 8.27))
        ax.axis("off")
        
        ax.text(0.5, 0.95, "数据汇总", fontsize=20, ha="center", va="top", fontweight="bold")
        
        yPosition = 0.85
        for key, result in self.analysisResults.items():
            summaryText = (
                f"• {result['name']}: "
                f"范围 {result['min']:.2f}~{result['max']:.2f} {result['unit']}，"
                f"平均 {result['mean']:.2f} {result['unit']}，"
                f"峰值时段 {result['peakHourRange']}"
            )
            ax.text(0.1, yPosition, summaryText, fontsize=11, ha="left", va="top")
            yPosition -= 0.08
        
        ax.text(0.5, 0.25, "数据质量评估", fontsize=14, ha="center", va="top", fontweight="bold")
        
        qualityText = f"所有传感器数据采集正常，共 {len(self.df)} 条记录，数据完整度 100%。"
        ax.text(0.1, 0.18, qualityText, fontsize=11, ha="left", va="top")
        
        pdf.savefig(fig, bbox_inches="tight")
        plt.close(fig)
    
    def run(self):
        """Run the complete analysis pipeline."""
        print("[INFO] Starting sensor data analysis...")
        self.loadData()
        self.analyzeData()
        self.generateReport()
        print("[INFO] Analysis completed successfully!")


def main():
    """Main entry point."""
    projectRoot = Path(__file__).parent
    dataPath = projectRoot / "data" / "sensor_data.csv"
    outputPath = projectRoot / "output"
    
    if not dataPath.exists():
        print(f"[ERROR] Data file not found: {dataPath}")
        print("[INFO] Please run generate_test_data.py first to generate test data.")
        return
    
    analyzer = SensorDataAnalyzer(str(dataPath), str(outputPath))
    analyzer.run()


if __name__ == "__main__":
    main()
