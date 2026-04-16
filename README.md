# 📐 高精度视觉选型计算引擎

基于《高精度精密零件视觉检测系统技术方案论证报告》构建的在线选型工具。

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11+--blue?style=for-the-badge&logo=Python&logoColor=white)

## 🎯 功能特点

### ① 像素当量 & 相机选型
- 支持 8+ 款工业相机选型（Sony、Basler、海康、大华等）
- 实时计算像素当量和视野范围
- 自动匹配满足精度要求的相机

### ② 光通量等价 & 曝光可行性
- 计算闪光光源需求照度
- 评估光源峰值照度是否满足要求
- 提供光通量余量分析

### ③ 振动衰减 & 运动模糊校验
- 基于阻尼振动模型计算残余振幅
- 评估曝光时间内运动模糊
- 给出稳定时间建议

## 🚀 快速部署

### 方法一：Streamlit Cloud（推荐）

1. Fork 本仓库
2. 访问 [share.streamlit.io](https://share.streamlit.io)
3. 点击 "New app" → 选择本仓库
4. 点击 "Deploy!"

### 方法二：本地运行

```bash
# 克隆仓库
git clone https://github.com/你的用户名/vision-selector.git
cd vision-selector

# 安装依赖
pip install -r requirements.txt

# 运行
streamlit run app.py
```

## 📁 项目结构

```
vision-selector/
├── app.py              # 主程序
├── requirements.txt    # 依赖包
└── README.md           # 说明文档
```

## 🔧 配置说明

### 预设方案
工具提供 4 种预设配置：
- **1μm精度方案**：适用于高精度检测场景
- **2μm精度方案**：适用于常规精密检测
- **5μm精度方案**：适用于一般检测
- **自定义**：手动调整所有参数

### 相机库
预置相机型号：

| 型号 | 分辨率 | 像素尺寸 | 接口 |
|------|--------|----------|------|
| Sony IMX183 (20MP) | 5472×3648 | 1.0μm | USB3.0/GigE |
| Sony IMX253 (45MP) | 8192×5460 | 0.8μm | GigE |
| Sony IMX530 (65MP) | 9344×7000 | 1.067μm | CXP/USB3 |
| Sony IMX811 (151MP) | 14204×10652 | 0.7μm | CoaXPress |
| Sony IMX264 (5MP) | 2448×2048 | 3.45μm | USB3.0/GigE |
| Basler acA4096-30uc | 4096×3000 | 3.45μm | USB3.0 |
| 海康 MV-CA016-10GM | 4736×3456 | 3.45μm | GigE |
| 大华 DH-PG5014MC | 2448×2048 | 2.5μm | USB3.0 |

如需添加更多相机型号，修改 `app.py` 中的 `CAMERA_DB` 字典即可。

## 📊 使用流程

1. **输入检测需求**
   - 目标测量精度（如 1μm）
   - 安全系数（通常 2-3）
   - 视野范围（FOV）

2. **选择镜头倍率**
   - 根据视野需求选择合适倍率

3. **查看选型结果**
   - 绿色 ✅：满足精度和视野要求
   - 黄色 ⚠️：满足精度但视野不足
   - 红色 ❌：精度不满足要求

4. **评估光源和振动**
   - 确认光通量余量 ≥ 2x
   - 确认运动模糊 < 1/3 像素

## 📝 技术原理

### 像素当量计算
```
像素当量 = 像素尺寸 / 镜头倍率
目标像素当量 = 目标精度 / 安全系数
```

### 光通量等价
```
需求照度 = (参考照度 × 参考曝光) / 闪光曝光
```

### 振动衰减模型
```
残余振幅 = 初始振幅 × e^(-ζωt)
其中：ω = 2πf（固有频率）
```

### 运动模糊
```
运动模糊(px) = (速度 × 曝光时间) / 像素当量
```

## 👤 作者

**王宇康 (Wang Yukang)**
- AME 工程师
- Apple 供应链
- 技术博客：[待补充]

## 📄 许可证

MIT License

## 🙏 致谢

基于《高精度精密零件视觉检测系统技术方案论证报告 V2.0》
