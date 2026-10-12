# Building Energy Benchmark

一个标准库 Python 命令行小项目，用可复现的仿真数据比较 8 栋教学用建筑的能耗强度，并展示一个透明的天气归一化方法。

## 运行

需要 Python 3.10 或更高版本，不需要安装第三方包。

```powershell
python building_energy_benchmark.py
python -m unittest discover -s tests -v
```

运行后生成 `data/simulated_buildings.csv` 和 `results/benchmark.json`。可用 `--output-dir 路径` 将生成文件写到指定目录。

## 指标

- EUI（Energy Use Intensity，能耗强度）：年度用电量除以建筑面积，单位为 kWh/m²。
- 天气指数：人为构造的相对天气严酷度；1.0 表示参考天气。
- 天气敏感占比：仿真中被假设为受天气影响的能耗比例。
- 基准指数：归一化能耗强度相对仿真样本中位数的指数，中位数约为 100；数值较低只表示在本组模拟建筑中能耗强度较低。

归一化公式为 `raw_eui / (1 + (weather_index - 1) * weather_sensitive_share)`。它是为了教学而设定的简化公式，不是建筑能效认证、工程诊断或标准化天气校正方法。

## 数据边界

所有建筑名称、面积、能耗、天气指数和参数均为确定性合成数据，随机种子固定。没有使用真实校园抄表数据，也没有声称节能量或碳减排量。真实比较还需要统一建筑用途、气候区、计量边界、占用率和数据质量，并由专业人员选择适当的方法。
