import streamlit as st
import math

# --- CSS 隱藏 Number Input 的加減按鈕 ---
hide_st_style = """
<style>
/* 隱藏 Streamlit 預設的 +/- 按鈕 */
[data-testid="stNumberInputStepUp"], [data-testid="stNumberInputStepDown"] {
    display: none !important;
}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)


# --- 1. 核心計算邏輯 ---
def calculate_full_system(mass, mu, diameter_mm, angle_deg, sf, gear_ratio, eff_gear, eff_trans, frequency, poles, slip_percent):
    g = 9.81
    radius = (diameter_mm / 2) / 1000
    
    sync_rpm = (120 * frequency) / poles
    motor_rpm = sync_rpm * (1 - (slip_percent / 100))
    
    drum_rpm = motor_rpm / gear_ratio
    speed_m_min = drum_rpm * 2 * math.pi * radius 
    
    angle_rad = math.radians(angle_deg)
    f_friction = mu * mass * g * math.cos(angle_rad)
    f_gravity = mass * g * math.sin(angle_rad)
    f_total = (f_friction + f_gravity) * sf
    
    total_efficiency = (eff_gear / 100) * (eff_trans / 100)
    
    torque_drum = f_total * radius
    torque_motor = torque_drum / (gear_ratio * total_efficiency)
    
    speed_m_s = speed_m_min / 60
    power_w = (f_total * speed_m_s) / total_efficiency
    power_kw = power_w / 1000
    
    return motor_rpm, drum_rpm, speed_m_min, f_total, torque_drum, torque_motor, power_kw


# --- 2. 網頁介面設計 ---

st.set_page_config(page_title="輸送機動力計算", page_icon="⚙️", layout="wide")
st.title("⚙️ 輸送機動力計算")
st.markdown("👉 **參數設定已移至左側選單**。(手機版請點擊左上角 `>>` 展開選單)")

# 建立馬達資料庫 (常見規格)
motor_database = {
    "手動自訂參數": {"poles": 4, "slip": 2.7, "eff": 95.0},
    "MS系列 0.5 HP (4P)": {"poles": 4, "slip": 5.0, "eff": 75.0},
    "MS系列 1 HP (4P)": {"poles": 4, "slip": 4.0, "eff": 78.0},
    "MS系列 2 HP (4P)": {"poles": 4, "slip": 3.0, "eff": 81.0},
    "MS系列 3 HP (4P)": {"poles": 4, "slip": 2.5, "eff": 84.0}
}

st.sidebar.header("📝 參數設定")

# 快捷選單放在 form 外面，選擇後才能即時連動下方的預設值
selected_motor = st.sidebar.selectbox(
    "📌 快速載入馬達預設值", 
    list(motor_database.keys()),
    help="選擇後會自動帶入進階參數中的滑差率與效率"
)

with st.sidebar.form("calculator_form"):
    
    st.subheader("📦 負載與機械結構")
    # value 改為整數 (例如 400)，就不會顯示 .00
    diameter = st.number_input("1. 驅動輪直徑 (mm)", value=400)
    mass = st.number_input("2. 總負載質量 (kg)", value=500)
    mu = st.number_input("3. 摩擦係數 (μ)", value=0.15, format="%.2f")
    angle = st.number_input("4. 傾斜角度 (度)", value=0)

    st.divider() 
    
    st.subheader("⚡ 馬達與傳動系統")
    freq = st.number_input("電源頻率 (Hz)", value=60)
    ratio = st.number_input("減速比 (1:X)", value=10)
    
    with st.expander("⚙️ 進階參數 (點擊展開)"):
        # 根據上面的選單自動帶入數值
        default_poles = motor_database[selected_motor]["poles"]
        default_slip = motor_database[selected_motor]["slip"]
        default_eff = motor_database[selected_motor]["eff"]
        
        if selected_motor != "手動自訂參數":
            st.info(f"已自動套用 {selected_motor} 預設值，您仍可微調。")
            
        poles = st.number_input("馬達極數 (Poles)", value=default_poles)
        slip = st.number_input("馬達滑差率 (%)", value=float(default_slip))
        eff_gear = st.number_input("減速機效率 (%)", value=90)
        eff_trans = st.number_input("馬達效率 (%)", value=float(default_eff))
        sf = st.number_input("安全係數", value=1.25)

    submitted = st.form_submit_button("🚀 執行計算", use_container_width=True)


# --- 3. 當按下按鈕後的顯示邏輯 ---
if submitted:
    try:
        motor_rpm, drum_rpm, speed_m_min, f_total, t_drum, t_motor, kw = calculate_full_system(
            mass, mu, diameter, angle, sf, ratio, eff_gear, eff_trans, freq, poles, slip
        )
        
        st.success("✅ 計算成功！系統結果如下：")
        
        st.info("🏃‍♂️ 系統速度數據")
        res_col1, res_col2, res_col3 = st.columns(3)
        res_col1.metric("1. 輸送帶線速度", f"{speed_m_min:.2f} M/min")
        res_col2.metric("2. 實際馬達轉速", f"{motor_rpm:.0f} RPM")
        res_col3.metric("3. 減速機輸出轉速", f"{drum_rpm:.1f} RPM")
        
        st.divider()
        
        st.info("🎯 核心驅動需求對照")
        res_col4, res_col5, res_col6 = st.columns(3)
        res_col4.metric("1. 理論所需功率", f"{kw:.2f} kW")
        res_col5.metric("2. 馬達扭力 (馬達端)", f"{t_motor:.2f} N·m")
        res_col6.metric("3. 輸送帶需求扭力 (滾筒端)", f"{t_drum:.2f} N·m")
        
        st.warning(f"💡 **工程建議**：選用之馬達功率需大於 **{kw:.2f} kW** (搭配減速比 1:{ratio})")
        
    except ZeroDivisionError:
        st.error("運算錯誤：極數或減速比不能為 0！")
    except Exception as e:
        st.error(f"發生未預期錯誤：{e}")
else:
    st.info("👈 請在左側選單輸入您的工程參數，並點擊「🚀 執行計算」。")
