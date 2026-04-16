"""
高精度视觉选型计算引擎
基于《高精度精密零件视觉检测系统技术方案论证报告》构建
Author: Wang Yukang
Version: 1.0.0
"""

import streamlit as st
import math
from datetime import datetime

# 页面配置
st.set_page_config(
    page_title="高精度视觉选型引擎",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1E88E5;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
    }
    .error-box {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
    }
</style>
""", unsafe_allow_html=True)


# ==================== 相机数据库 ====================
CAMERA_DB = {
    "Sony IMX183 (20MP)": {
        "px": 1.0, "res_x": 5472, "res_y": 3648,
        "sensor": "1\"", "interface": "USB3.0/GigE",
        "max_fps": 19, "price_range": "¥3,000-5,000"
    },
    "Sony IMX253 (45MP)": {
        "px": 0.8, "res_x": 8192, "res_y": 5460,
        "sensor": "1.1\"", "interface": "GigE",
        "max_fps": 8, "price_range": "¥8,000-15,000"
    },
    "Sony IMX530 (65MP)": {
        "px": 1.067, "res_x": 9344, "res_y": 7000,
        "sensor": "2.3\"", "interface": "CoaXPress/USB3",
        "max_fps": 32, "price_range": "¥15,000-25,000"
    },
    "Sony IMX811 (151MP)": {
        "px": 0.7, "res_x": 14204, "res_y": 10652,
        "sensor": "2.74\"", "interface": "CoaXPress",
        "max_fps": 6.3, "price_range": "¥50,000+"
    },
    "Sony IMX264 (5MP)": {
        "px": 3.45, "res_x": 2448, "res_y": 2048,
        "sensor": "1/2.9\"", "interface": "USB3.0/GigE",
        "max_fps": 35, "price_range": "¥1,500-2,500"
    },
    "Basler acA4096-30uc": {
        "px": 3.45, "res_x": 4096, "res_y": 3000,
        "sensor": "1\"", "interface": "USB3.0",
        "max_fps": 30, "price_range": "¥4,000-6,000"
    },
    "海康 MV-CA016-10GM": {
        "px": 3.45, "res_x": 4736, "res_y": 3456,
        "sensor": "1\"", "interface": "GigE",
        "max_fps": 10, "price_range": "¥2,000-3,000"
    },
    "大华 DH-PG5014MC": {
        "px": 2.5, "res_x": 2448, "res_y": 2048,
        "sensor": "1/2\"", "interface": "USB3.0",
        "max_fps": 45, "price_range": "¥1,200-2,000"
    },
}

# 镜头倍率选项
LENS_MAGNIFICATIONS = [0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 7.5, 10.0]


def calculate_pixel_equivalent(pixel_size_um: float, magnification: float) -> float:
    """计算像素当量（μm/像素）"""
    return pixel_size_um / magnification


def calculate_fov(pixel_size_um: float, resolution: int, magnification: float) -> float:
    """计算视野范围（mm）"""
    return (resolution * pixel_size_um / 1000) / magnification


def calculate_flash_illuminance_required(
    t_const: float, e_const: float, t_flash: float
) -> float:
    """计算闪光需求照度（lux）"""
    return (e_const * t_const) / t_flash


def calculate_vibration_decay(
    a0: float, zeta: float, f_vib: float, t_settle: float
) -> tuple[float, float]:
    """计算振动衰减后的振幅和速度
    
    Returns:
        (残余振幅 μm, 速度 m/s)
    """
    omega_n = 2 * math.pi * f_vib
    amp_after = a0 * math.exp(-zeta * omega_n * t_settle)
    vel_after = amp_after * omega_n * 1e-6
    return amp_after, vel_after


def calculate_motion_blur(
    vel_m_per_s: float, t_exp_s: float, pixel_eq_um: float
) -> float:
    """计算运动模糊（像素）"""
    displacement_um = vel_m_per_s * t_exp_s * 1e6
    return displacement_um / pixel_eq_um


# ==================== 侧边栏配置 ====================
def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        st.header("⚙️ 系统配置")
        
        # 单位选择
        st.subheader("显示单位")
        unit_system = st.radio(
            "单位制",
            ["公制 (μm)", "英制 (mil)"],
            horizontal=True,
            label_visibility="collapsed"
        )
        
        st.divider()
        
        # 预设方案
        st.subheader("📁 预设方案")
        preset = st.selectbox(
            "选择预设配置",
            ["自定义", "1μm精度方案", "2μm精度方案", "5μm精度方案"]
        )
        
        preset_values = {
            "1μm精度方案": {
                "target_accuracy": 1.0, "safety_factor": 3.0,
                "fov_x": 3.32, "fov_y": 2.49,
                "lens_mag": 3.0
            },
            "2μm精度方案": {
                "target_accuracy": 2.0, "safety_factor": 2.5,
                "fov_x": 6.0, "fov_y": 4.5,
                "lens_mag": 2.0
            },
            "5μm精度方案": {
                "target_accuracy": 5.0, "safety_factor": 2.0,
                "fov_x": 10.0, "fov_y": 7.5,
                "lens_mag": 1.0
            },
        }
        
        st.divider()
        
        # 关于
        st.subheader("ℹ️ 关于")
        st.caption("基于《技术方案论证报告 V2.0》")
        st.caption(f"版本: 1.0.0")
        st.caption(f"更新: {datetime.now().strftime('%Y-%m-%d')}")
        
        return preset_values.get(preset, None), unit_system


# ==================== 主界面 ====================
def render_header():
    """渲染标题区"""
    st.markdown('<p class="main-header">📐 高精度视觉选型计算引擎</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">基于《高精度精密零件视觉检测系统技术方案论证报告》—— AME 实战工具</p>',
        unsafe_allow_html=True
    )


def render_pixel_equivalent_section(col, preset_values=None):
    """渲染像素当量 & 相机选型模块"""
    with col:
        st.header("① 像素当量 & 相机选型")
        
        # 输入参数
        if preset_values:
            target_accuracy = st.number_input(
                "目标测量精度 (μm)",
                value=preset_values["target_accuracy"],
                min_value=0.1, max_value=100.0, step=0.1, format="%.1f",
                key="accuracy_preset"
            )
            safety_factor = st.slider(
                "安全系数",
                min_value=1.0, max_value=5.0,
                value=preset_values["safety_factor"], step=0.5,
                help="通常选择2-3，确保测量可靠性",
                key="safety_preset"
            )
            fov_x = st.number_input(
                "视野 FOV_X (mm)",
                value=preset_values["fov_x"], min_value=0.1, step=0.1, format="%.2f",
                key="fov_x_preset"
            )
            fov_y = st.number_input(
                "视野 FOV_Y (mm)",
                value=preset_values["fov_y"], min_value=0.1, step=0.1, format="%.2f",
                key="fov_y_preset"
            )
        else:
            target_accuracy = st.number_input(
                "目标测量精度 (μm)",
                value=1.0, min_value=0.1, max_value=100.0, step=0.1, format="%.1f"
            )
            safety_factor = st.slider(
                "安全系数",
                min_value=1.0, max_value=5.0,
                value=3.0, step=0.5,
                help="通常选择2-3，确保测量可靠性"
            )
            fov_x = st.number_input(
                "视野 FOV_X (mm)",
                value=3.32, min_value=0.1, step=0.1, format="%.2f"
            )
            fov_y = st.number_input(
                "视野 FOV_Y (mm)",
                value=2.49, min_value=0.1, step=0.1, format="%.2f"
            )
        
        # 计算目标像素当量
        pixel_eq_target = target_accuracy / safety_factor
        
        st.divider()
        
        # 目标像素当量展示
        st.markdown(f"""
        <div class="metric-card">
            <h3>🎯 目标像素当量 ≤ {pixel_eq_target:.3f} μm/像素</h3>
            <p style="color: #666; font-size: 0.9rem;">
                计算公式：目标精度 ÷ 安全系数 = {target_accuracy} ÷ {safety_factor}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # 镜头倍率选择
        default_mag_idx = LENS_MAGNIFICATIONS.index(3.0) if preset_values and "lens_mag" in preset_values else 2
        lens_mag = st.selectbox(
            "🔍 镜头倍率",
            LENS_MAGNIFICATIONS,
            index=default_mag_idx,
            format_func=lambda x: f"{x}x"
        )
        
        st.divider()
        
        # 相机选型结果
        st.subheader("📷 相机选型结果")
        
        results = []
        for name, spec in CAMERA_DB.items():
            pixel_eq = calculate_pixel_equivalent(spec["px"], lens_mag)
            fov_actual_x = calculate_fov(spec["px"], spec["res_x"], lens_mag)
            fov_actual_y = calculate_fov(spec["px"], spec["res_y"], lens_mag)
            
            # 状态判断
            if pixel_eq <= pixel_eq_target and fov_actual_x >= fov_x and fov_actual_y >= fov_y:
                status = "✅ 满足"
                status_class = "success-box"
            elif pixel_eq <= pixel_eq_target:
                status = "⚠️ 视野不足"
                status_class = "warning-box"
            else:
                status = "❌ 精度不足"
                status_class = "error-box"
            
            results.append({
                "camera": name,
                "pixel_eq": pixel_eq,
                "fov_x": fov_actual_x,
                "fov_y": fov_actual_y,
                "status": status,
                "status_class": status_class,
                **spec
            })
        
        # 按状态排序（满足的在前）
        results.sort(key=lambda x: (0 if "✅" in x["status"] else 1 if "⚠️" in x["status"] else 2))
        
        # 展示结果
        for r in results:
            with st.container():
                cols = st.columns([3, 1, 1, 1, 1, 2])
                with cols[0]:
                    st.write(f"**{r['camera']}**")
                    st.caption(f"{r['res_x']}×{r['res_y']} @ {r['px']}μm | {r['interface']}")
                with cols[1]:
                    st.metric("像素当量", f"{r['pixel_eq']:.3f}μm")
                with cols[2]:
                    st.metric("FOV_X", f"{r['fov_x']:.2f}mm")
                with cols[3]:
                    st.metric("FOV_Y", f"{r['fov_y']:.2f}mm")
                with cols[4]:
                    st.metric("帧率", f"{r['max_fps']}fps")
                with cols[5]:
                    st.write(f"{r['status']}")
                st.divider()
        
        return {
            "target_accuracy": target_accuracy,
            "safety_factor": safety_factor,
            "fov_x": fov_x,
            "fov_y": fov_y,
            "lens_mag": lens_mag,
            "pixel_eq_target": pixel_eq_target,
            "results": results
        }


def render_illuminance_section(col):
    """渲染光通量等价 & 曝光可行性模块"""
    with col:
        st.header("② 光通量等价 & 曝光可行性")
        
        # 输入参数
        t_const = st.number_input(
            "常亮参考曝光时间 (ms)",
            value=10.0, min_value=0.1, step=1.0, format="%.1f"
        ) / 1000
        
        e_const = st.number_input(
            "常亮参考照度 (lux)",
            value=10000.0, min_value=100, step=1000.0, format="%.0f"
        )
        
        t_flash = st.number_input(
            "目标闪光曝光时间 (μs)",
            value=450.0, min_value=1.0, step=10.0, format="%.0f"
        ) / 1_000_000
        
        e_flash_required = calculate_flash_illuminance_required(t_const, e_const, t_flash)
        
        st.divider()
        
        # 可用照度输入
        e_flash_available = st.number_input(
            "光源峰值照度 (lux)",
            value=1_410_000.0, min_value=10000, step=10000.0, format="%.0f",
            help="LED光源峰值照度，通常在 datasheet 中可查"
        )
        
        # 计算光通量余量
        margin = e_flash_available / e_flash_required if e_flash_required > 0 else 0
        
        st.divider()
        
        # 指标展示
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 需求照度", f"{e_flash_required:,.0f} lux")
        with col2:
            st.metric("💡 可用照度", f"{e_flash_available:,.0f} lux")
        with col3:
            delta = "充足 ✅" if margin > 2 else ("临界 ⚠️" if margin > 1 else "不足 ❌")
            st.metric("📈 光通量余量", f"{margin:.1f}x", delta=delta)
        
        st.divider()
        
        # 推荐说明
        if margin > 2:
            st.markdown("""
            <div class="success-box">
                <h4>✅ 光通量充足</h4>
                <p>光源配置满足要求，建议保持当前参数设置。</p>
            </div>
            """, unsafe_allow_html=True)
        elif margin > 1:
            st.markdown("""
            <div class="warning-box">
                <h4>⚠️ 光通量临界</h4>
                <p>建议增加光源功率或延长曝光时间，以确保成像稳定性。</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="error-box">
                <h4>❌ 光通量不足</h4>
                <p>需要更换更高功率的光源，或增加曝光时间、减小工作距离。</p>
            </div>
            """, unsafe_allow_html=True)
        
        return {
            "t_const": t_const * 1000,
            "e_const": e_const,
            "t_flash": t_flash * 1_000_000,
            "e_flash_required": e_flash_required,
            "e_flash_available": e_flash_available,
            "margin": margin
        }


def render_vibration_section(col, pixel_eq_target=1.0):
    """渲染振动衰减 & 运动模糊校验模块"""
    with col:
        st.header("③ 振动衰减 & 运动模糊校验")
        
        # 输入参数
        f_vib = st.number_input(
            "残余振动频率 (Hz)",
            value=100.0, min_value=10.0, step=10.0, format="%.0f",
            help="设备稳定后的残余振动频率，通常 50-200Hz"
        )
        
        a0 = st.number_input(
            "初始振幅 (μm)",
            value=5.0, min_value=0.1, step=0.5, format="%.1f",
            help="运动停止瞬间的振幅"
        )
        
        zeta = st.number_input(
            "阻尼比 ζ",
            value=0.3, min_value=0.01, max_value=1.0, step=0.05, format="%.2f",
            help="系统阻尼比，通常机械系统 0.2-0.5"
        )
        
        t_settle = st.number_input(
            "稳定等待时间 (ms)",
            value=100.0, min_value=10.0, step=10.0, format="%.0f"
        ) / 1000
        
        # 计算振动衰减
        amp_after, vel_after = calculate_vibration_decay(a0, zeta, f_vib, t_settle)
        
        # 计算运动模糊
        t_exp_us = st.number_input(
            "实际曝光时间 (μs)",
            value=450.0, min_value=1.0, step=10.0, format="%.0f"
        )
        t_exp_s = t_exp_us / 1_000_000
        
        blur_px = calculate_motion_blur(vel_after, t_exp_s, pixel_eq_target)
        
        st.divider()
        
        # 指标展示
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📉 残余振幅", f"{amp_after:.3f} μm")
        with col2:
            st.metric("⚡ 瞬时速度", f"{vel_after * 1e6:.4f} μm/s")
        with col3:
            st.metric("🔲 运动模糊", f"{blur_px:.3f} px")
        
        st.divider()
        
        # 判断结果
        threshold = 0.33  # 1/3 像素
        
        if blur_px < threshold:
            st.markdown(f"""
            <div class="success-box">
                <h4>✅ 运动模糊可接受</h4>
                <p>运动模糊 = {blur_px:.3f} px < {threshold} px (1/3像素)，满足高精度检测要求。</p>
                <p>建议保持当前稳定时间 <b>{t_settle*1000:.0f}ms</b>。</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            needed_time = st.number_input(
                "计算所需稳定时间",
                value=150.0, min_value=10.0, step=10.0, format="%.0f",
                key="needed_time"
            ) / 1000
            amp_needed, _ = calculate_vibration_decay(a0, zeta, f_vib, needed_time)
            blur_needed = calculate_motion_blur(amp_needed * omega_n := 2 * math.pi * f_vib, t_exp_s, pixel_eq_target) / 1e6 * amp_needed * omega_n * 1e6
            
            st.markdown(f"""
            <div class="error-box">
                <h4>❌ 运动模糊过大</h4>
                <p>运动模糊 = {blur_px:.3f} px > {threshold} px，不满足要求。</p>
                <p><b>建议：</b></p>
                <ul>
                    <li>增加稳定等待时间至 {needed_time*1000:.0f}ms</li>
                    <li>或减小曝光时间至 {int(t_exp_us * threshold / blur_px):.0f}μs</li>
                    <li>或增加阻尼比（加装减振垫）</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        return {
            "f_vib": f_vib,
            "a0": a0,
            "zeta": zeta,
            "t_settle": t_settle * 1000,
            "amp_after": amp_after,
            "vel_after": vel_after,
            "blur_px": blur_px
        }


def render_footer():
    """渲染页脚"""
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #999; font-size: 0.8rem;">
        <p>注：所有计算基于《技术方案论证报告 V2.0》中的物理模型</p>
        <p>理论计算结果仅供参考，实际应用需结合现场测试验证</p>
    </div>
    """, unsafe_allow_html=True)


# ==================== 主程序 ====================
def main():
    # 渲染标题
    render_header()
    
    # 渲染侧边栏
    preset_values, unit_system = render_sidebar()
    
    # 主内容区 - 3列布局
    col1, col2, col3 = st.columns(3)
    
    # 第一列：像素当量 & 相机选型
    calc_results = render_pixel_equivalent_section(col1, preset_values)
    
    # 第二列：光通量等价
    illum_results = render_illuminance_section(col2)
    
    # 第三列：振动衰减
    vib_results = render_vibration_section(col3, calc_results["pixel_eq_target"])
    
    # 页脚
    render_footer()
    
    # 存储计算结果到 session_state（用于导出）
    st.session_state["last_calculation"] = {
        "timestamp": datetime.now().isoformat(),
        "pixel_equivalent": calc_results,
        "illuminance": illum_results,
        "vibration": vib_results
    }


if __name__ == "__main__":
    main()
