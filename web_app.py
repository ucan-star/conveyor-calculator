import streamlit as st
import math

# --- 1. 核心計算邏輯 (跟原本一模一樣，一行都不用改！) ---
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
    
    # 這裡其實你原本就有算出來 (torque_drum)，只是剛好之前沒在介面上顯示出來
    torque_drum = f_total * radius
    torque_motor = torque_drum / (gear_ratio * total_efficiency)
    
    speed_m_s = speed_m_min / 60
    power_w = (f_total * speed_m_s) / total_efficiency
    power_kw = power_w / 1000
    
    return motor_rpm, speed_m_min, f_total, torque_drum, torque_motor, power_kw


# --- 2. 網頁介面設計 (全新側邊欄與儀表板設計) ---

# 設定網頁標題
st.set_page_config(page_title="輸送機計算系統", page_icon="⚙️", layout="wide")
st.title("⚙️ 進階輸送機工程計算系統")
st.markdown("👉 **參數設定已移至左側選單**。(手機版請點擊左上角 `>` 展開選單)")

# 利用 st.sidebar.form 把輸入欄位移到側邊欄
with st.sidebar.form("calculator_form"):
    st.header("📝 參數設定")
    
    st.subheader("📦 負載與機械結構")
    diameter = st.number_input("1. 驅動輪直徑 (mm)", value=400.0)
    mass = st.number_input("2. 總負載質量 (kg)", value=500.0)
    mu = st.number_input("3. 摩擦係數 (μ)", value=0.05)
    angle = st.number_input("4. 傾斜角度 (度)", value=15.0)

    st.divider() 
    
    st.subheader("⚡ 馬達與傳動系統")
    freq = st.number_input("電源頻率 (Hz)", value=60.0)
    poles = st.number_input("馬達極數 (Poles)", value=4.0)
    ratio = st.number_input("減速比 (1:X)", value=20.0)
    
    # 使用 expander 把進階參數收納起來，讓介面更清爽
    with st.expander("⚙️ 進階參數 (點擊展開)"):
        slip = st.number_input("預估滑差率 (%)", value=2.7)
        eff_gear = st.number_input("減速機效率 (%)", value=85.0)
        eff_trans = st.number_input("傳動效率 (%)", value=95.0)
        sf = st.number_input("安全係數", value=1.2)

    # 執行計算的按鈕
    submitted = st.form_submit_button("🚀 執行計算", use_container_width=True)


# --- 3. 當按下按鈕後的顯示邏輯 (大字體儀表板) ---
if submitted:
    try:
        motor_rpm, speed_m_min, f_total, t_drum, t_motor, kw = calculate_full_system(
            mass, mu, diameter, angle, sf, ratio, eff_gear, eff_trans, freq, poles, slip
        )
        
        st.success("✅ 計算成功！系統結果如下：")
        
        # 第一排：速度與基礎數據
        st.info("🏃‍♂️ 速度與拉力數據")
        res_col1, res_col2, res_col3 = st.columns(3)
        res_col1.metric("實際馬達轉速", f"{motor_rpm:.0f} RPM")
        res_col2.metric("輸送帶線速度", f"{speed_m_min:.2f} M/min")
        res_col3.metric("總驅動拉力", f"{f_total:.2f} N")
        
        st.divider()
        
        # 第二排：核心扭力與功率對照 (新增了滾筒端扭力)
        st.info("🎯 核心驅動需求對照")
        res_col4, res_col5, res_col6 = st.columns(3)
        res_col4.metric("輸送帶需求扭力 (滾筒端)", f"{t_drum:.2f} N·m")
        res_col5.metric("馬達輸入扭力 (馬達端)", f"{t_motor:.2f} N·m")
        res_col6.metric("理論所需功率", f"{kw:.2f} kW")
        
        # 底部醒目提示框
        st.warning(f"💡 **工程建議**：選用之馬達功率需大於 **{kw:.2f} kW** (搭配減速比 1:{ratio:.0f})")
        
    except ZeroDivisionError:
        st.error("運算錯誤：極數或減速比不能為 0！")
    except Exception as e:
        st.error(f"發生未預期錯誤：{e}")
else:
    # 剛載入網頁、還沒按計算時的提示
    st.info("👈 請在左側選單輸入您的工程參數，並點擊「🚀 執行計算」。")
