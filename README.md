# 温室大棚传感器数据分析系统

## 项目简介

本项目是一个温室大棚传感器数据分析程序，用于分析温度、湿度、光照等传感器数据，并生成包含可视化图表的PDF分析报告。

## 功能特性

- 支持多种传感器数据分析：温度、湿度、光照强度、CO2浓度、土壤湿度、土壤温度
- 按时间生成各维度数据的折线图和柱状图
- 自动生成中文分析说明文字
- 输出完整的PDF分析报告
- 支持重复运行，自动覆盖之前的报告

## 目录结构

```
.
├── data/                    # 存放测试数据(CSV格式)
│   └── sensor_data.csv
├── output/                  # 存放生成的PDF报告
│   └── sensor_analysis_report.pdf
├── main.py                  # 主分析程序
├── generate_test_data.py    # 测试数据生成脚本
├── requirements.txt         # 依赖文件
└── README.md               # 项目说明文档
```

## 环境要求

- Python 3.9+
- 依赖库见 requirements.txt

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 生成测试数据

```bash
python generate_test_data.py
```

该脚本会在 `data/` 目录下生成 `sensor_data.csv` 文件，包含720条模拟数据（1天数据，每2分钟一条记录）。

测试数据模拟场景：
- 地区：东北地区
- 季节：12月份
- 环境：室内温室大棚

### 2. 运行分析程序

```bash
python main.py
```

程序会读取 `data/sensor_data.csv`，分析数据并在 `output/` 目录下生成 `sensor_analysis_report.pdf` 报告。

## 数据格式

输入CSV文件应包含以下字段：

| 字段名 | 说明 | 单位 |
|--------|------|------|
| timestamp | 时间戳 | YYYY-MM-DD HH:MM:SS |
| temperature | 空气温度 | °C |
| humidity | 空气湿度 | % |
| light_intensity | 光照强度 | lux |
| co2_concentration | CO2浓度 | ppm |
| soil_moisture | 土壤湿度 | % |
| soil_temperature | 土壤温度 | °C |

## 报告内容

生成的PDF报告包含：

1. **封面页**：报告标题、数据时间范围、生成时间
2. **各指标分析图表**：
   - 折线图：展示数据随时间的变化趋势
   - 柱状图：展示小时平均值分布
   - 分析文字：最高值、最低值、平均值、峰值时段等
3. **汇总页**：所有指标的统计汇总

## 代码规范

- 采用驼峰命名规范
- 所有日志输出使用英文
- 包含必要的中文注释

## 许可证

MIT License
