#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Greenhouse Sensor Data Analysis Program
Analyzes sensor data from greenhouse environment and generates PDF report with charts.
Supports temperature, humidity, light intensity, CO2, soil moisture and soil temperature.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_pdf import PdfPages
from datetime import datetime
import numpy as np
import os
import sys

# Set matplotlib to support Chinese characters
plt.rcParams['font.sans-serif'] = ['Heiti TC', 'STHeiti', 'Songti SC', 'SimSong', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class GreenhouseDataAnalyzer:
    """
    Analyzer for greenhouse sensor data.
    Reads CSV data, performs analysis, and generates PDF reports with charts.
    """
    
    def __init__(self, dataPath="data/sensor_data.csv", outputPath="output/report.pdf"):
        """
        Initialize the analyzer.
        
        Args:
            dataPath: Path to the CSV sensor data file
            outputPath: Path to save the PDF report
        """
        self.dataPath = dataPath
        self.outputPath = outputPath
        self.data = None
        self.analysisResults = {}
        
    def loadData(self):
        """
        Load sensor data from CSV file.
        
        Returns:
            bool: True if successful, False otherwise
        """
        print(f"[INFO] Loading data from: {self.dataPath}")
        
        if not os.path.exists(self.dataPath):
            print(f"[ERROR] Data file not found: {self.dataPath}")
            return False
        
        try:
            self.data = pd.read_csv(self.dataPath)
            self.data['timestamp'] = pd.to_datetime(self.data['timestamp'])
            print(f"[INFO] Successfully loaded {len(self.data)} records")
            print(f"[INFO] Data columns: {list(self.data.columns)}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to load data: {str(e)}")
            return False
    
    def analyzeData(self):
        """
        Perform statistical analysis on sensor data.
        Calculates min, max, mean, and identifies peak periods for each metric.
        """
        print("[INFO] Starting data analysis")
        
        if self.data is None:
            print("[ERROR] No data loaded for analysis")
            return
        
        metrics = ['temperature', 'humidity', 'light_intensity', 
                   'co2_concentration', 'soil_moisture', 'soil_temperature']
        
        for metric in metrics:
            if metric not in self.data.columns:
                print(f"[WARNING] Metric not found: {metric}")
                continue
            
            values = self.data[metric]
            timestamps = self.data['timestamp']
            
            # Basic statistics
            minVal = values.min()
            maxVal = values.max()
            meanVal = values.mean()
            minIdx = values.idxmin()
            maxIdx = values.idxmax()
            minTime = timestamps.iloc[minIdx]
            maxTime = timestamps.iloc[maxIdx]
            
            # Calculate time ranges for max/min periods (±30 minutes)
            minTimeRange = f"{minTime.strftime('%H:%M')}"
            maxTimeRange = f"{maxTime.strftime('%H:%M')}"
            
            self.analysisResults[metric] = {
                'min': minVal,
                'max': maxVal,
                'mean': meanVal,
                'minTime': minTime,
                'maxTime': maxTime,
                'minTimeRange': minTimeRange,
                'maxTimeRange': maxTimeRange
            }
            
            print(f"[INFO] {metric}: min={minVal:.2f} at {minTimeRange}, max={maxVal:.2f} at {maxTimeRange}, mean={meanVal:.2f}")
        
        print("[INFO] Data analysis completed")
    
    def getMetricDisplayInfo(self, metric):
        """
        Get display information for a metric.
        
        Args:
            metric: Metric name
            
        Returns:
            dict: Display name, unit, and color for the metric
        """
        infoMap = {
            'temperature': {'name': '空气温度', 'unit': '°C', 'color': '#FF6B6B'},
            'humidity': {'name': '空气湿度', 'unit': '%', 'color': '#4ECDC4'},
            'light_intensity': {'name': '光照强度', 'unit': 'lux', 'color': '#FFE66D'},
            'co2_concentration': {'name': 'CO2浓度', 'unit': 'ppm', 'color': '#95E1D3'},
            'soil_moisture': {'name': '土壤湿度', 'unit': '%', 'color': '#A8E6CF'},
            'soil_temperature': {'name': '土壤温度', 'unit': '°C', 'color': '#FFB6C1'}
        }
        return infoMap.get(metric, {'name': metric, 'unit': '', 'color': '#666666'})
    
    def generateAnalysisText(self, metric):
        """
        Generate Chinese analysis text for a metric.
        
        Args:
            metric: Metric name
            
        Returns:
            str: Analysis text in Chinese
        """
        if metric not in self.analysisResults:
            return "暂无分析数据"
        
        result = self.analysisResults[metric]
        info = self.getMetricDisplayInfo(metric)
        
        texts = [
            f"本日{info['name']}统计：",
            f"  • 最高值：{result['max']:.2f}{info['unit']}，出现在 {result['maxTimeRange']}",
            f"  • 最低值：{result['min']:.2f}{info['unit']}，出现在 {result['minTimeRange']}",
            f"  • 平均值：{result['mean']:.2f}{info['unit']}",
        ]
        
        # Add specific analysis based on metric type
        if metric == 'temperature':
            tempRange = result['max'] - result['min']
            if tempRange > 8:
                texts.append(f"  • 昼夜温差较大({tempRange:.1f}°C)，建议加强温控管理")
            else:
                texts.append(f"  • 温差控制良好({tempRange:.1f}°C)，环境稳定")
        
        elif metric == 'humidity':
            if result['mean'] > 80:
                texts.append("  • 平均湿度偏高，注意通风防病害")
            elif result['mean'] < 60:
                texts.append("  • 平均湿度偏低，建议适当加湿")
            else:
                texts.append("  • 湿度水平适宜作物生长")
        
        elif metric == 'light_intensity':
            daylightHours = sum(1 for v in self.data[metric] if v > 1000) * 2 / 60
            texts.append(f"  • 有效光照时长约 {daylightHours:.1f} 小时")
        
        elif metric == 'co2_concentration':
            if result['max'] > 600:
                texts.append("  • 夜间CO2浓度较高，白天光合作用消耗明显")
        
        elif metric == 'soil_moisture':
            if result['mean'] < 60:
                texts.append("  • 土壤湿度偏低，建议适时灌溉")
            elif result['mean'] > 70:
                texts.append("  • 土壤湿度充足")
        
        elif metric == 'soil_temperature':
            diff = result['mean'] - self.analysisResults.get('temperature', {}).get('mean', 0)
            if abs(diff) < 2:
                texts.append("  • 土温与气温接近，热量交换正常")
            elif diff > 0:
                texts.append("  • 土温高于气温，土壤蓄热良好")
        
        return "\n".join(texts)
    
    def createChartPage(self, fig, metricsPage):
        """
        Create a page with charts for given metrics.
        Each metric gets its own chart with analysis text below.
        
        Args:
            fig: Matplotlib figure object
            metricsPage: List of metrics to display on this page
        """
        numMetrics = len(metricsPage)
        if numMetrics == 0:
            return
        
        # Create grid layout: each metric takes 2 rows (chart + text)
        # Use gridspec for better control
        from matplotlib.gridspec import GridSpec
        gs = GridSpec(numMetrics * 2, 1, figure=fig, hspace=0.3, 
                      height_ratios=[3, 1] * numMetrics)
        
        for idx, metric in enumerate(metricsPage):
            if metric not in self.data.columns:
                continue
            
            info = self.getMetricDisplayInfo(metric)
            values = self.data[metric]
            timestamps = self.data['timestamp']
            result = self.analysisResults.get(metric, {})
            
            # Create chart subplot
            axChart = fig.add_subplot(gs[idx * 2, 0])
            
            # Plot line
            axChart.plot(timestamps, values, color=info['color'], linewidth=1.5, label=info['name'])
            
            # Mark max and min points
            if 'maxTime' in result and 'minTime' in result:
                maxTime = result['maxTime']
                minTime = result['minTime']
                maxVal = result['max']
                minVal = result['min']
                
                axChart.scatter([maxTime], [maxVal], color='red', s=50, zorder=5)
                axChart.scatter([minTime], [minVal], color='blue', s=50, zorder=5)
                
                # Position annotations to avoid overlap
                axChart.annotate(f'最高: {maxVal:.1f}', xy=(maxTime, maxVal), 
                           xytext=(10, 10), textcoords='offset points',
                           fontsize=8, color='red', bbox=dict(boxstyle='round,pad=0.3', 
                           facecolor='white', alpha=0.7, edgecolor='red'))
                axChart.annotate(f'最低: {minVal:.1f}', xy=(minTime, minVal),
                           xytext=(10, -15), textcoords='offset points',
                           fontsize=8, color='blue', bbox=dict(boxstyle='round,pad=0.3',
                           facecolor='white', alpha=0.7, edgecolor='blue'))
            
            # Set title and labels
            axChart.set_title(f"{info['name']}变化趋势", fontsize=12, fontweight='bold', pad=10)
            axChart.set_ylabel(f"{info['name']} ({info['unit']})", fontsize=10)
            
            # Format x-axis
            axChart.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            axChart.xaxis.set_major_locator(mdates.HourLocator(interval=2))
            plt.setp(axChart.xaxis.get_majorticklabels(), rotation=45, ha='right')
            
            # Add grid
            axChart.grid(True, alpha=0.3, linestyle='--')
            
            # Remove x-label for upper chart if two charts on page
            if idx == 0 and numMetrics > 1:
                axChart.set_xlabel('')
            else:
                axChart.set_xlabel("时间", fontsize=10)
            
            # Create text subplot for analysis
            axText = fig.add_subplot(gs[idx * 2 + 1, 0])
            axText.axis('off')
            
            # Add analysis text
            analysisText = self.generateAnalysisText(metric)
            axText.text(0.05, 0.5, analysisText, transform=axText.transAxes,
                    fontsize=9, verticalalignment='center', horizontalalignment='left',
                    linespacing=1.5,
                    bbox=dict(boxstyle='round,pad=0.5', facecolor='wheat', alpha=0.3))
    
    def generateReport(self):
        """
        Generate PDF report with all charts and analysis.
        
        Returns:
            bool: True if successful, False otherwise
        """
        print(f"[INFO] Generating PDF report: {self.outputPath}")
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(self.outputPath), exist_ok=True)
        
        metrics = ['temperature', 'humidity', 'light_intensity', 
                   'co2_concentration', 'soil_moisture', 'soil_temperature']
        
        try:
            with PdfPages(self.outputPath) as pdf:
                # Cover page
                fig = plt.figure(figsize=(8.27, 11.69))  # A4 size
                ax = fig.add_subplot(111)
                ax.axis('off')
                
                coverText = [
                    "温室大棚传感器数据分析报告",
                    "",
                    f"报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    f"数据时间范围: {self.data['timestamp'].min().strftime('%Y-%m-%d %H:%M')} 至 {self.data['timestamp'].max().strftime('%H:%M')}",
                    f"数据记录数: {len(self.data)} 条",
                    "",
                    "监测指标:",
                    "  • 空气温度",
                    "  • 空气湿度", 
                    "  • 光照强度",
                    "  • CO2浓度",
                    "  • 土壤湿度",
                    "  • 土壤温度",
                    "",
                    "本报告基于温室大棚环境监测数据生成，",
                    "反映24小时内各环境参数的变化趋势。"
                ]
                
                ax.text(0.5, 0.5, "\n".join(coverText), transform=ax.transAxes,
                       fontsize=14, verticalalignment='center', horizontalalignment='center',
                       bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))
                
                pdf.savefig(fig, bbox_inches='tight', pad_inches=0.5)
                plt.close(fig)
                print("[INFO] Cover page created")
                
                # Create chart pages - one metric per page to avoid overlap
                for metric in metrics:
                    fig = plt.figure(figsize=(8.27, 11.69))
                    self.createChartPage(fig, [metric])
                    pdf.savefig(fig, bbox_inches='tight', pad_inches=0.5)
                    plt.close(fig)
                    print(f"[INFO] Chart page for {metric} created")
                
                # Summary page
                fig = plt.figure(figsize=(8.27, 11.69))
                ax = fig.add_subplot(111)
                ax.axis('off')
                
                summaryLines = ["数据汇总", "", "=" * 40, ""]
                
                for metric in metrics:
                    if metric in self.analysisResults:
                        info = self.getMetricDisplayInfo(metric)
                        result = self.analysisResults[metric]
                        summaryLines.extend([
                            f"{info['name']}:",
                            f"  最高: {result['max']:.2f}{info['unit']} ({result['maxTimeRange']})",
                            f"  最低: {result['min']:.2f}{info['unit']} ({result['minTimeRange']})",
                            f"  平均: {result['mean']:.2f}{info['unit']}",
                            ""
                        ])
                
                ax.text(0.5, 0.5, "\n".join(summaryLines), transform=ax.transAxes,
                       fontsize=11, verticalalignment='center', horizontalalignment='center',
                       bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.3))
                
                pdf.savefig(fig, bbox_inches='tight', pad_inches=0.5)
                plt.close(fig)
                print("[INFO] Summary page created")
            
            print(f"[INFO] PDF report generated successfully: {self.outputPath}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to generate PDF report: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def run(self):
        """
        Execute the complete analysis workflow.
        
        Returns:
            bool: True if successful, False otherwise
        """
        print("[INFO] Starting Greenhouse Data Analysis")
        print("=" * 50)
        
        if not self.loadData():
            return False
        
        self.analyzeData()
        
        if not self.generateReport():
            return False
        
        print("=" * 50)
        print("[INFO] Analysis completed successfully")
        return True


def main():
    """
    Main entry point for the program.
    """
    print("[INFO] Greenhouse Sensor Data Analysis Program")
    print("[INFO] Python version:", sys.version)
    
    # Check if test data exists, if not generate it
    dataPath = "data/sensor_data.csv"
    if not os.path.exists(dataPath):
        print("[INFO] Test data not found, generating...")
        try:
            from generate_test_data import generateGreenhouseData
            generateGreenhouseData(dataPath)
        except Exception as e:
            print(f"[ERROR] Failed to generate test data: {str(e)}")
            return 1
    
    # Run analysis
    analyzer = GreenhouseDataAnalyzer(dataPath=dataPath, outputPath="output/report.pdf")
    success = analyzer.run()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
