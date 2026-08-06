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

with st.sidebar.form("calculator_form"):
    st.header("📝 參數設定")
    
    st.subheader("📦 負載與機械結構")
    # value 設為整數，將不會顯示小數點
    diameter = st.number_input("1. 驅動輪直徑 (mm)", value=90)
    mass = st.number_input("2. 總負載質量 (kg)", value=1000)
    mu = st.number_input("3. 摩擦係數 (μ)", value=0.2, format="%.2f")
    angle = st.number_input("4. 傾斜角度 (度)", value=0)

    st.divider() 
    
    st.subheader("⚡ 馬達與傳動系統")
    freq = st.number_input("電源頻率 (Hz)", value=60)
    poles = st.number_input("馬達極數 (Poles)", value=4)
    ratio = st.number_input("減速比 (1:X)", value=10)
    
    with st.expander("⚙️ 進階參數 (點擊展開)"):
        slip = st.number_input("馬達滑差率 (%)", value=8)
        eff_gear = st.number_input("減速機效率 (%)", value=90)
        eff_trans = st.number_input("馬達效率 (%)", value=95)
        sf = st.number_input("安全係數", value=1.3)

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
