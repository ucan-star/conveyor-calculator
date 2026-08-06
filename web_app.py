import streamlit as st
import math

# --- CSS 隱藏 Number Input 的加減按鈕 ---
hide_st_style = """
<style>
[data-testid="stNumberInputStepUp"], [data-testid="stNumberInputStepDown"] {
    display: none !important;
}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

st.set_page_config(page_title="輸送機工程計算系統", page_icon="⚙️", layout="wide")

# ==========================================
# 側邊欄：功能導覽選單 (僅保留選單)
# ==========================================
st.sidebar.title("📌 工程計算工具箱")
app_mode = st.sidebar.radio(
    "請選擇計算模組：",
    [
        "⚙️ 1. 輸送機動力計算 (主系統)", 
        "🏃‍♂️ 2. 輸送帶線速度計算", 
        "🔄 3. 目標速度反推減速比", 
        "⚡ 4. 馬達轉速與扭力計算",
        "⚙️ 5. 減速機輸出扭力與轉速計算" # [新增] 第5模組
    ]
)
st.sidebar.divider()

# ==========================================
# 模組 1: 輸送機動力計算 (主系統)
# ==========================================
if app_mode == "⚙️ 1. 輸送機動力計算 (主系統)":
    st.title("⚙️ 輸送機動力計算")

    with st.form("calculator_form"):
        st.header("📝 參數設定")
        
        st.subheader("📦 負載與機械結構")
        c1, c2 = st.columns(2)
        diameter = c1.number_input("1. 驅動輪直徑 (mm)", value=100)
        mass = c2.number_input("2. 總負載質量 (kg)", value=500)
        mu = c1.number_input("3. 摩擦係數 (μ)", value=0.20, format="%.2f")
        angle = c2.number_input("4. 傾斜角度 (度)", value=0)

        st.divider() 
        
        st.subheader("⚡ 馬達與傳動系統")
        c3, c4 = st.columns(2)
        freq = c3.number_input("電源頻率 (Hz)", value=60)
        poles = c4.number_input("馬達極數 (Poles)", value=4)
        ratio = c3.number_input("減速比 (1:X)", value=20)
        
        st.divider()

        st.subheader("⚙️ 進階參數")
        c5, c6 = st.columns(2)
        slip = c5.number_input("馬達滑差率 (%)", value=5.5)
        eff_gear = c6.number_input("減速機效率 (%)", value=85)
        torque_loss_pct = c5.number_input("扭力損失 / 機械損耗 (%)", value=5.5)
        sf = c6.number_input("安全係數", value=1.25)

        submitted_main = st.form_submit_button("🚀 執行計算", use_container_width=True)

    if submitted_main:
        try:
            g = 9.81
            radius = (diameter / 2) / 1000
            
            motor_rpm = (120 * freq / poles) * (1 - (slip / 100))
            drum_rpm = motor_rpm / ratio
            speed_m_min = drum_rpm * 2 * math.pi * radius 
            
            angle_rad = math.radians(angle)
            f_total = ((mu * mass * g * math.cos(angle_rad)) + (mass * g * math.sin(angle_rad))) * sf
            
            # 效率與扭力計算
            total_efficiency = (eff_gear / 100) * (1 - (torque_loss_pct / 100))
            torque_drum = f_total * radius
            
            # 減速機端輸出扭力 (滾筒需求扭力加上機械損耗)
            torque_gearbox = torque_drum / (1 - (torque_loss_pct / 100))
            
            # 馬達端輸出扭力
            torque_motor = torque_drum / (ratio * total_efficiency)
            
            kw = ((f_total * (speed_m_min / 60)) / total_efficiency) / 1000
            
            st.success("✅ 計算成功！系統結果如下：")
            
            st.info("🏃‍♂️ 系統速度數據")
            res_col1, res_col2, res_col3 = st.columns(3)
            res_col1.metric("1. 輸送帶線速度", f"{speed_m_min:.2f} M/min")
            res_col2.metric("2. 實際馬達轉速", f"{motor_rpm:.0f} RPM")
            res_col3.metric("3. 減速機輸出轉速", f"{drum_rpm:.1f} RPM")
            
            st.divider()
            
            st.info("🎯 核心驅動需求對照")
            # 採用 2x2 雙欄位設計，手機與電腦版皆易於閱讀
            res_col4, res_col5 = st.columns(2)
            res_col4.metric("1. 理論所需功率", f"{kw:.2f} kW")
            res_col5.metric("2. 馬達扭力 (馬達端)", f"{torque_motor:.2f} N·m")
            
            res_col6, res_col7 = st.columns(2)
            res_col6.metric("3. 減速機扭力 (減速機端)", f"{torque_gearbox:.2f} N·m")
            res_col7.metric("4. 輸送帶需求扭力 (滾筒端)", f"{torque_drum:.2f} N·m")
            
            st.warning(f"💡 **工程建議**：選用之馬達功率需大於 **{kw:.2f} kW** (搭配減速比 1:{ratio})")
            
        except Exception as e:
            st.error(f"發生未預期錯誤：{e}")


# ==========================================
# 模組 2: 輸送帶線速度計算
# ==========================================
elif app_mode == "🏃‍♂️ 2. 輸送帶線速度計算":
    st.title("🏃‍♂️ 輸送帶線速度計算")
    st.markdown("單純計算現有設備的運行速度。")
    
    with st.form("speed_form"):
        st.header("📝 參數設定")
        c1, c2 = st.columns(2)
        diameter = c1.number_input("驅動輪直徑 (mm)", value=100)
        ratio = c2.number_input("減速比 (1:X)", value=20)
        freq = c1.number_input("電源頻率 (Hz)", value=60)
        poles = c2.number_input("馬達極數 (Poles)", value=4)
        slip = c1.number_input("馬達滑差率 (%)", value=5.5)
        
        submitted_speed = st.form_submit_button("🚀 計算線速度", use_container_width=True)

    if submitted_speed:
        try:
            radius = (diameter / 2) / 1000
            motor_rpm = (120 * freq / poles) * (1 - (slip / 100))
            drum_rpm = motor_rpm / ratio
            speed_m_min = drum_rpm * 2 * math.pi * radius
            
            st.success("✅ 速度計算完成：")
            col1, col2 = st.columns(2)
            col1.metric("輸送帶線速度", f"{speed_m_min:.2f} M/min")
            col2.metric("減速機輸出轉速", f"{drum_rpm:.1f} RPM")
        except Exception as e:
            st.error("數值輸入有誤！")


# ==========================================
# 模組 3: 目標速度反推減速比
# ==========================================
elif app_mode == "🔄 3. 目標速度反推減速比":
    st.title("🔄 目標速度反推減速比")
    st.markdown("已知需要的輸送速度，反推應該購買多大的減速比。")
    
    with st.form("ratio_form"):
        st.header("📝 參數設定")
        c1, c2 = st.columns(2)
        target_speed = c1.number_input("目標線速度 (M/min)", value=15.0, format="%.1f")
        diameter = c2.number_input("驅動輪直徑 (mm)", value=100)
        freq = c1.number_input("電源頻率 (Hz)", value=60)
        poles = c2.number_input("馬達極數 (Poles)", value=4)
        slip = c1.number_input("馬達滑差率 (%)", value=5.5)
        
        submitted_ratio = st.form_submit_button("🚀 反推減速比", use_container_width=True)

    if submitted_ratio:
        try:
            radius = (diameter / 2) / 1000
            motor_rpm = (120 * freq / poles) * (1 - (slip / 100))
            
            # 反推滾筒需要的轉速
            req_drum_rpm = target_speed / (2 * math.pi * radius)
            # 反推精確減速比
            exact_ratio = motor_rpm / req_drum_rpm
            
            st.success("✅ 減速比計算完成：")
            col1, col2 = st.columns(2)
            col1.metric("精管理論減速比", f"1 : {exact_ratio:.2f}")
            col2.metric("滾筒目標轉速", f"{req_drum_rpm:.1f} RPM")
            st.info("💡 建議：請選擇市面上最接近上述數值的標準減速比 (例如 1:10, 1:15, 1:20 等)。")
        except Exception as e:
            st.error("數值輸入有誤！")


# ==========================================
# 模組 4: 馬達轉速與扭力計算
# ==========================================
elif app_mode == "⚡ 4. 馬達轉速與扭力計算":
    st.title("⚡ 馬達基本參數計算")
    st.markdown("計算標準交流馬達的實際轉速與額定輸出扭力，並扣除機械損耗。")
    
    with st.form("motor_form"):
        st.header("📝 參數設定")
        c1, c2 = st.columns(2)
        power_kw = c1.number_input("馬達功率 (kW)", value=0.75, format="%.2f", help="1 HP ≒ 0.75 kW")
        torque_loss_pct = c2.number_input("扭力損失 / 機械損耗 (%)", value=5.5)
        freq = c1.number_input("電源頻率 (Hz)", value=60)
        poles = c2.number_input("馬達極數 (Poles)", value=4)
        slip = c1.number_input("滑差率 (%)", value=5.5)
        
        submitted_motor = st.form_submit_button("🚀 計算馬達參數", use_container_width=True)

    if submitted_motor:
        try:
            sync_rpm = (120 * freq) / poles
            motor_rpm = sync_rpm * (1 - (slip / 100))
            
            # 扭力公式：T = 9550 * (kW / RPM)
            rated_torque_nm = 9550 * (power_kw / motor_rpm)
            
            # 計算扣除損失後的實際扭力
            actual_torque_nm = rated_torque_nm * (1 - (torque_loss_pct / 100))
            
            # 換算 kg·m (1 kg·m ≒ 9.81 N·m)
            rated_torque_kgm = rated_torque_nm / 9.81
            actual_torque_kgm = actual_torque_nm / 9.81
            
            st.success("✅ 馬達參數計算完成：")
            
            st.info("🔄 轉速數據")
            col1, col2 = st.columns(2)
            col1.metric("1. 同步轉速 (無載)", f"{sync_rpm:.0f} RPM")
            col2.metric("2. 馬達實際轉速", f"{motor_rpm:.0f} RPM")
            
            st.divider()
            
            st.info("💪 扭力數據")
            col3, col4 = st.columns(2)
            col3.metric("1. 理論額定扭力", f"{rated_torque_nm:.2f} N·m ({rated_torque_kgm:.2f} kg·m)")
            col4.metric("2. 實際輸出扭力 (扣除損耗)", f"{actual_torque_nm:.2f} N·m ({actual_torque_kgm:.2f} kg·m)")
            
        except Exception as e:
            st.error("數值輸入有誤！")

# ==========================================
# 模組 5: 減速機輸出扭力與轉速計算
# ==========================================
elif app_mode == "⚙️ 5. 減速機輸出扭力與轉速計算":
    st.title("⚙️ 減速機輸出參數計算")
    st.markdown("計算馬達經過減速機降速，並扣除傳動效率與機械損耗後的最終輸出轉速與扭力。")
    
    with st.form("gearbox_output_form"):
        st.header("📝 參數設定")
        
        st.subheader("⚡ 馬達參數")
        c1, c2 = st.columns(2)
        power_kw = c1.number_input("1. 馬達功率 (kW)", value=0.75, format="%.2f")
        freq = c2.number_input("2. 電源頻率 (Hz)", value=60)
        poles = c1.number_input("3. 馬達極數 (Poles)", value=4)
        slip = c2.number_input("4. 滑差率 (%)", value=5.5)
        
        st.divider()
        
        st.subheader("⚙️ 減速機與損耗參數")
        c3, c4 = st.columns(2)
        ratio = c3.number_input("5. 減速比 (1:X)", value=20)
        eff_gear = c4.number_input("6. 減速機效率 (%)", value=85)
        torque_loss_pct = c3.number_input("7. 扭力損失 / 機械損耗 (%)", value=5.5)
        
        submitted_mod5 = st.form_submit_button("🚀 計算輸出參數", use_container_width=True)

    if submitted_mod5:
        try:
            # 1. 計算馬達實際轉速
            sync_rpm = (120 * freq) / poles
            motor_rpm = sync_rpm * (1 - (slip / 100))
            
            # 2. 計算減速機輸出轉速
            output_rpm = motor_rpm / ratio
            
            # 3. 計算馬達原始扭力 (N·m)
            motor_torque_nm = 9550 * (power_kw / motor_rpm)
            
            # 4. 計算綜合效率 (減速機效率 * 機械損耗)
            total_eff = (eff_gear / 100) * (1 - (torque_loss_pct / 100))
            
            # 5. 計算最終輸出扭力 (N·m 與 kg·m)
            output_torque_nm = motor_torque_nm * ratio * total_eff
            output_torque_kgm = output_torque_nm / 9.81
            
            st.success("✅ 計算成功！輸出結果如下：")
            
            st.info("🔄 轉速數據")
            res_col1, res_col2 = st.columns(2)
            res_col1.metric("1. 馬達實際轉速", f"{motor_rpm:.0f} RPM")
            res_col2.metric("2. 減速機輸出轉速", f"{output_rpm:.1f} RPM")
            
            st.divider()
            
            st.info("💪 扭力數據")
            res_col3, res_col4 = st.columns(2)
            res_col3.metric("1. 馬達原始扭力", f"{motor_torque_nm:.2f} N·m")
            res_col4.metric("2. 最終輸出扭力", f"{output_torque_nm:.2f} N·m ({output_torque_kgm:.2f} kg·m)")
            
        except Exception as e:
            st.error("數值輸入有誤！請確認輸入的參數格式。")
