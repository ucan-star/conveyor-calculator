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
        "⚙️ 5. 減速機輸出扭力與轉速計算",
        "🏗️ 6. 剪式升降機扭力計算",
        "🔩 7. 梯形螺桿計算",
        "⚡ 8. 馬達額定電流計算 (單/三相)" # [更新] 第8模組名稱
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
        slip = c5.number_input("馬達滑差率 (%)", value=6)
        eff_gear = c6.number_input("減速機效率 (%)", value=85)
        torque_loss_pct = c5.number_input("馬達扭力損失/機械損耗 (%)", value=5)
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
        slip = c1.number_input("馬達滑差率 (%)", value=6)
        
        submitted_speed = st.form_submit_button("🚀 計算線速度", use_container_width=True)

    if submitted_speed:
        try:
            radius = (diameter / 2) / 1000
            motor_rpm = (120 * freq / poles) * (1 - (slip / 100))
            drum_rpm = motor_rpm / ratio
            speed_m_min = drum_rpm * 2 * math.pi * radius
            
            st.success("✅ 速度計算完成：")
            col1, col2, col3 = st.columns(3)
            col1.metric("輸送帶線速度", f"{speed_m_min:.2f} M/min")
            col2.metric("馬達實際轉速", f"{motor_rpm:.0f} RPM")
            col3.metric("減速機輸出轉速", f"{drum_rpm:.1f} RPM")
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
        slip = c1.number_input("馬達滑差率 (%)", value=6)
        
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
            col1, col2, col3 = st.columns(3)
            col1.metric("精管理論減速比", f"1 : {exact_ratio:.2f}")
            col2.metric("馬達實際轉速", f"{motor_rpm:.0f} RPM")
            col3.metric("滾筒目標轉速", f"{req_drum_rpm:.1f} RPM")
            
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
        torque_loss_pct = c2.number_input("扭力損失 / 機械損耗 (%)", value=5)
        freq = c1.number_input("電源頻率 (Hz)", value=60)
        poles = c2.number_input("馬達極數 (Poles)", value=4)
        slip = c1.number_input("滑差率 (%)", value=6)
        
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
        poles = c2.number_input("2. 馬達極數 (Poles)", value=4)
        freq = c1.number_input("3. 電源頻率 (Hz)", value=60)
        slip = c2.number_input("4. 滑差率 (%)", value=6)
        torque_loss_pct = c1.number_input("5. 扭力損失 / 機械損耗 (%)", value=5)
        
        st.divider()
        
        st.subheader("⚙️ 減速機參數")
        c3, c4 = st.columns(2)
        ratio = c3.number_input("6. 減速比 (1:X)", value=20)
        eff_gear = c4.number_input("7. 減速機效率 (%)", value=85)
        
        submitted_mod5 = st.form_submit_button("🚀 計算輸出參數", use_container_width=True)

    if submitted_mod5:
        try:
            # 1. 計算馬達實際轉速
            sync_rpm = (120 * freq) / poles
            motor_rpm = sync_rpm * (1 - (slip / 100))
            
            # 2. 計算減速機輸出轉速
            output_rpm = motor_rpm / ratio
            
            # 3. 計算馬達原始扭力 (N·m 與 kg·m)
            motor_torque_nm = 9550 * (power_kw / motor_rpm)
            motor_torque_kgm = motor_torque_nm / 9.81
            
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
            res_col3.metric("1. 馬達原始扭力", f"{motor_torque_nm:.2f} N·m ({motor_torque_kgm:.2f} kg·m)")
            res_col4.metric("2. 最終輸出扭力", f"{output_torque_nm:.2f} N·m ({output_torque_kgm:.2f} kg·m)")
            
        except Exception as e:
            st.error("數值輸入有誤！請確認輸入的參數格式。")

# ==========================================
# 模組 6: 剪式升降機 (Scissor Lift) 扭力計算
# ==========================================
elif app_mode == "🏗️ 6. 剪式升降機扭力計算":
    st.title("🏗️ 剪式升降機 (Scissor Lift) 扭力計算")
    st.markdown("單層剪叉機構，馬達直接驅動螺桿（或將減速機視為馬達輸出端的一部份）。")
    
    with st.form("scissor_lift_form"):
        st.header("📝 參數設定")
        
        st.subheader("📦 已知條件 (負載與機構)")
        c1, c2 = st.columns(2)
        weight_kg = c1.number_input("1. 總載重 W (KG)", value=1021.0)
        angle_deg = c2.number_input("2. 初始夾角 θ (度)", value=15.0)
        layers = c1.number_input("3. 剪叉層數 n", value=1, step=1)
        speed_vy = c2.number_input("4. 垂直速度 Vy (m/min)", value=1.0)
        
        st.divider()
        
        st.subheader("🔩 螺桿與傳動條件")
        c3, c4 = st.columns(2)
        lead_mm = c3.number_input("5. 螺桿導程 p (mm)", value=5.0)
        eff_screw = c4.number_input("6. 螺桿效率 η", value=0.9, format="%.2f", help="滾珠螺桿約0.9，梯形螺桿約0.3~0.5")
        sf = c3.number_input("7. 安全係數 (Safety Factor)", value=2.0)
        
        st.divider()

        st.subheader("⚙️ 減速機選配評估")
        c5, c6 = st.columns(2)
        sel_motor_kw = c5.number_input("8. 選用馬達功率 (kW)", value=0.37)
        sel_motor_rpm = c6.number_input("9. 馬達轉速 (rpm)", value=1700)
        sel_ratio = c5.number_input("10. 選用減速比 (1:X)", value=30)
        eff_gearbox = c6.number_input("11. 減速機效率", value=0.9, format="%.2f")
        eff_mech = c5.number_input("12. 機械傳動效率", value=1.0, format="%.2f")
        
        submitted_mod6 = st.form_submit_button("🚀 執行計算", use_container_width=True)

    if submitted_mod6:
        try:
            # --- 基本轉換 ---
            g = 9.8 # 依照原表採用 9.8 進行換算
            weight_n = weight_kg * g
            lead_m = lead_mm / 1000
            
            # 角度轉換為弧度 (修正EXCEL直接計算tan(角度)的誤差問題)
            angle_rad = math.radians(angle_deg)
            tan_theta = math.tan(angle_rad)
            
            # --- 1. 計算推力與扭力 ---
            force_n = (layers * weight_n) / tan_theta
            torque_nm = (force_n * lead_m) / (2 * math.pi * eff_screw)
            torque_req = torque_nm * sf # 修正扭力 (乘上安全係數)
            
            # --- 2. 計算速度與功率 ---
            speed_vx = speed_vy * tan_theta
            req_rpm = speed_vx / lead_m
            req_kw = (torque_req * req_rpm) / 9550
            
            # --- 3. 減速機選配驗證 ---
            motor_t = 9550 * (sel_motor_kw / sel_motor_rpm)
            gearbox_out_t = motor_t * sel_ratio * eff_gearbox * eff_mech
            match_ratio = gearbox_out_t / torque_req
            
            st.success("✅ 計算成功！系統結果如下：")
            
            st.info("📊 核心推力與扭力需求")
            r1, r2, r3 = st.columns(3)
            r1.metric("最大水平推力 (F)", f"{force_n:.2f} N")
            r2.metric("基礎所需扭力 (T)", f"{torque_nm:.2f} Nm")
            r3.metric("修正扭力 (T2)", f"{torque_req:.2f} Nm", help="已乘上安全係數")
            
            st.divider()
            
            st.info("🔄 速度與馬達功率")
            r4, r5, r6 = st.columns(3)
            r4.metric("水平移動速度 (Vx)", f"{speed_vx:.4f} m/min")
            r5.metric("螺桿所需轉速 (N)", f"{req_rpm:.2f} rpm")
            r6.metric("建議馬達功率 (P)", f"{req_kw:.3f} kW")
            
            st.divider()
            
            # 依據倍率判斷扭力是否足夠，並給予不同顏色的提示
            if match_ratio >= 1.0:
                st.success(f"⚙️ 減速機選配評估：扭力充足")
            else:
                st.error(f"⚙️ 減速機選配評估：扭力不足")
                
            r7, r8, r9 = st.columns(3)
            r7.metric("選用馬達扭力", f"{motor_t:.2f} Nm")
            r8.metric("減速機輸出扭矩", f"{gearbox_out_t:.2f} Nm")
            r9.metric("選配結果 (倍)", f"{match_ratio:.2f} 倍")
            
        except Exception as e:
            st.error(f"數值輸入有誤！錯誤訊息：{e}")

# ==========================================
# 模組 7: 梯形螺桿計算
# ==========================================
elif app_mode == "🔩 7. 梯形螺桿計算":
    st.title("🔩 梯形螺桿推舉力與扭力計算")
    st.markdown("依據馬達與減速機構正向推算總推舉力 (Fa)，以及從已知推力反推需求扭力 (T)。")
    
    # 使用 Tabs 分開正向與反向計算，畫面更乾淨
    tab1, tab2 = st.tabs(["🚀 正向推算 (馬達 ➔ 推舉力)", "🔄 反向推算 (推舉力 ➔ 需求扭力)"])
    
    # ------------------ 正向計算區塊 ------------------
    with tab1:
        with st.form("screw_forward_form"):
            st.header("📝 參數設定 (正向)")
            
            st.subheader("⚡ 傳動與效率參數")
            c1, c2 = st.columns(2)
            gb_eff = c1.number_input("1. 減速機效率 (0~1)", value=0.82, format="%.2f")
            gb_ratio = c2.number_input("2. 減速機比數", value=15.0)
            lift_eff = c1.number_input("3. 升降機效率 (0~1)", value=0.80, format="%.2f")
            lift_ratio = c2.number_input("4. 升降機比數", value=13.5)
            
            st.divider()
            
            st.subheader("🔌 馬達與螺桿參數")
            c3, c4 = st.columns(2)
            motor_rpm = c3.number_input("5. 馬達轉速 (RPM)", value=1700.0)
            motor_hp = c4.number_input("6. 馬達功率 (HP)", value=0.5, format="%.2f")
            screw_eff = c3.number_input("7. 角牙效率 η (0~1)", value=0.20, format="%.2f")
            lead_mm = c4.number_input("8. 導程 R (mm)", value=9.0)
            
            submit_fwd = st.form_submit_button("🚀 執行正向計算", use_container_width=True)
            
        if submit_fwd:
            try:
                # 1. 扭力轉換計算: HP -> KgM (公式: T = 716.2 * HP / RPM)
                # 若直接帶入 EXCEL 數值 0.5HP / 1700RPM，算式結果約為 0.21 KgM
                motor_t_kgm = 716.2 * (motor_hp / motor_rpm) 
                
                # 2. 總輸出扭力 = 馬達扭力 * (比數相乘) * (效率相乘)
                total_t_kgm = motor_t_kgm * gb_ratio * lift_ratio * gb_eff * lift_eff
                
                # 3. 行程速度計算
                speed_mm_min = (motor_rpm / (gb_ratio * lift_ratio)) * lead_mm
                speed_mm_sec = speed_mm_min / 60
                
                # 4. 推舉力 Fa = (2 * pi * η * T) / (R * 10^-3)
                thrust_kg = (2 * math.pi * screw_eff * total_t_kgm) / (lead_mm * 0.001)
                
                st.success("✅ 正向推算成功！")
                
                st.info("🔄 速度與扭力轉換")
                res_c1, res_c2, res_c3 = st.columns(3)
                res_c1.metric("馬達扭力", f"{motor_t_kgm:.2f} KgM")
                res_c2.metric("總輸出扭力 (輸入扭力 T)", f"{total_t_kgm:.2f} KgM")
                res_c3.metric("行程速度", f"{speed_mm_min:.1f} mm/分", help=f"換算為 {speed_mm_sec:.2f} mm/秒")
                
                st.divider()
                
                st.info("💪 推舉力結果")
                res_c4, res_c5 = st.columns(2)
                res_c4.metric("產生之推舉力 (Fa)", f"{thrust_kg:.0f} KG")
                
            except Exception as e:
                st.error("數值輸入有誤，請檢查參數格式。")

    # ------------------ 反向計算區塊 ------------------
    with tab2:
        with st.form("screw_reverse_form"):
            st.header("📝 已知推力反推扭力")
            
            c5, c6 = st.columns(2)
            screw_eff_rev = c5.number_input("1. 角牙效率 η (0~1)", value=0.20, format="%.2f", key="rev_eff")
            lead_mm_rev = c6.number_input("2. 導程 R (mm)", value=9.0, key="rev_lead")
            thrust_kg_rev = c5.number_input("3. 推舉力 Fa (KG)", value=3710.0, key="rev_thrust")
            
            submit_rev = st.form_submit_button("🔄 執行反向計算", use_container_width=True)
            
        if submit_rev:
            try:
                # 公式: T = (Fa * R * 10^-3) / (2 * pi * η)
                req_t_kgm = (thrust_kg_rev * lead_mm_rev * 0.001) / (2 * math.pi * screw_eff_rev)
                
                st.success("✅ 反向推算成功！")
                
                st.info("📊 需求扭力結果")
                res_c6, res_c7 = st.columns(2)
                res_c6.metric("需求扭力 (輸入扭力 T)", f"{req_t_kgm:.2f} KgM")
                
            except Exception as e:
                st.error("數值輸入有誤，請檢查參數格式。")
                
# ==========================================
# 模組 8: 馬達額定電流計算 (單相/三相)
# ==========================================
elif app_mode == "⚡ 8. 馬達額定電流計算 (單/三相)":
    st.title("⚡ 馬達額定電流計算")
    st.markdown("依據馬達功率、電源相數、電壓、功率因數與效率，計算感應馬達的滿載額定電流。")

    with st.form("motor_current_form"):
        st.header("📝 參數設定")

        c1, c2 = st.columns(2)
        phase = c1.radio("1. 電源相數", ["三相 (3-Phase)", "單相 (1-Phase)"], horizontal=True)
        power_kw = c2.number_input("2. 馬達功率 (kW)", value=0.75, format="%.2f", help="1 HP ≒ 0.75 kW")
        voltage = c1.number_input("3. 額定電壓 (V)", value=220, step=10, help="三相常見 220/380V，單相常見 110/220V")
        pf = c2.number_input("4. 功率因數 (cosθ)", value=0.82, format="%.2f", help="一般馬達約在 0.75 ~ 0.90 之間")
        eff = c1.number_input("5. 馬達效率 (%)", value=80.0, format="%.1f", help="一般約 75% ~ 95%")

        submitted_current = st.form_submit_button("🚀 計算額定電流", use_container_width=True)

    if submitted_current:
        try:
            power_w = power_kw * 1000
            eff_decimal = eff / 100
            
            # 避免分母為0的錯誤
            if voltage > 0 and pf > 0 and eff_decimal > 0:
                # 依據單相或三相選擇對應公式
                if "三相" in phase:
                    # 三相公式：I = P / (√3 * V * cosθ * η)
                    current_a = power_w / (math.sqrt(3) * voltage * pf * eff_decimal)
                else:
                    # 單相公式：I = P / (V * cosθ * η)
                    current_a = power_w / (voltage * pf * eff_decimal)
                
                st.success("✅ 計算完成！")
                
                st.info("⚡ 滿載電流數據")
                col1, col2 = st.columns(2)
                col1.metric("馬達滿載額定電流 (I)", f"{current_a:.2f} A")
                col2.metric("輸入設定功率", f"{power_kw:.2f} kW")
                
            else:
                st.error("電壓、功率因數與效率必須大於 0。")

        except Exception as e:
            st.error(f"數值輸入有誤，請檢查參數格式！錯誤訊息：{e}")
