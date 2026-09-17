import math
import os
import urllib.request
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

st.set_page_config(page_title="가설방음판넬 저감효과 다중 산정 프로그램", layout="wide")

# --- CSS 주입: 표 글씨 크기 일치, 데이터프레임 헤더/셀 가운데 정렬 및 볼드체 처리 ---
st.markdown(
    """
    <style>
    [data-testid="stDataFrame"] div[data-testid="stTable"] td,
    .stDataFrame table tr td,
    div.stDataFrame td {
        text-align: center !important;
        text-h-align: center !important;
        font-size: 14px !important;
    }
    
    [data-testid="stDataFrame"] div[data-testid="stTable"] th,
    .stDataFrame table tr th,
    div.stDataFrame th, div.stDataFrame [data-testid="stTable"] th {
        text-align: center !important;
        text-h-align: center !important;
        font-size: 14px !important;
        font-weight: bold !important;
    }
    
    .custom-table-header {
        text-align: center !important;
        font-size: 14px !important;
        font-weight: bold !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🛡️ 가설방음판넬 설치 후 소음 예측 프로그램")

# --- 서버 환경 한글 폰트 자동 설정 ---
font_path = "NanumGothic.ttf"
if not os.path.exists(font_path):
    try:
        url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"
        urllib.request.urlretrieve(url, font_path)
    except:
        pass

if os.path.exists(font_path):
    fm.fontManager.addfont(font_path)
    font_name = fm.FontProperties(fname=font_path).get_name()
    plt.rcParams['font.family'] = font_name
else:
    plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.unicode_minus'] = False

# --- 초기 기본 데이터 정의 ---
initial_data = [
    {"정온시설명": "A주택", "이격거리(m)": 50.0, "저감전 소음도[dB(A)]": 69.5, "가설방음판넬 높이(m)": 3.0, "소음환경기준[dB(A)]": 65.0},
    {"정온시설명": "B농장", "이격거리(m)": 100.0, "저감전 소음도[dB(A)]": 63.5, "가설방음판넬 높이(m)": 3.0, "소음환경기준[dB(A)]": 60.0},
    {"정온시설명": "C초등학교", "이격거리(m)": 150.0, "저감전 소음도[dB(A)]": 60.0, "가설방음판넬 높이(m)": 3.0, "소음환경기준[dB(A)]": 55.0},
]
df_sample = pd.DataFrame(initial_data)

# --- 세션 상태 초기화 ---
if "df_facilities" not in st.session_state:
    st.session_state["df_facilities"] = df_sample.copy()

if "widget_version" not in st.session_state:
    st.session_state["widget_version"] = 0

# --- 사이드바 설정 ---
with st.sidebar:
    st.header("🛠️ 1단계 : 입력 방식 선택")
    input_mode = st.radio("입력 방식을 선택하세요:", ["✒️데이터 수동 입력", "📁 CSV 파일 업로드"])
    
    if input_mode == "📁 CSV 파일 업로드":
        st.markdown("---")
        st.subheader("📁 샘플 양식 다운로드")
        sample_csv = df_sample.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 샘플 CSV 양식 다운로드",
            data=sample_csv,
            file_name="정온시설_입력양식_샘플.csv",
            mime="text/csv",
            help="이 샘플 파일을 다운로드한 뒤 내용을 수정하여 업로드하실 수 있습니다."
        )
        st.markdown("---")
        
        uploaded_file = st.file_uploader("정온시설 데이터 CSV 파일", type=["csv"])
        if uploaded_file is not None:
            # 파일이 변경되었거나 처음 업로드된 경우
            if "last_uploaded_file" not in st.session_state or st.session_state["last_uploaded_file"] != uploaded_file.name:
                try:
                    df_uploaded = pd.read_csv(uploaded_file, encoding='utf-8-sig')
                except:
                    try:
                        df_uploaded = pd.read_csv(uploaded_file, encoding='cp949')
                    except:
                        df_uploaded = pd.read_csv(uploaded_file, encoding='euc-kr')
                
                # 필수 컬럼 검증 및 데이터 완벽 교체
                required_cols = ["정온시설명", "이격거리(m)", "저감전 소음도[dB(A)]", "가설방음판넬 높이(m)", "소음환경기준[dB(A)]"]
                if all(col in df_uploaded.columns for col in required_cols):
                    st.session_state["df_facilities"] = df_uploaded[required_cols].copy()
                else:
                    st.session_state["df_facilities"] = df_uploaded.copy()
                
                st.session_state["last_uploaded_file"] = uploaded_file.name
                st.session_state["widget_version"] += 1  # 위젯 키 갱신 버전 증가
                st.rerun()
            
            st.success("CSV 파일이 성공적으로 로드되었습니다!")
        else:
            if "last_uploaded_file" in st.session_state:
                del st.session_state["last_uploaded_file"]
                st.session_state["df_facilities"] = df_sample.copy()
                st.session_state["widget_version"] += 1
                st.rerun()
            st.info("위의 샘플 양식을 다운받거나, 필요한 컬럼이 포함된 CSV를 업로드해주세요.")
    else:
        if "last_uploaded_file" in st.session_state:
            del st.session_state["last_uploaded_file"]
            st.session_state["df_facilities"] = df_sample.copy()
            st.session_state["widget_version"] += 1
            st.rerun()
            
        if st.button("기본 데이터로 초기화"):
            st.session_state["df_facilities"] = df_sample.copy()
            st.session_state["widget_version"] += 1
            st.rerun()

    st.markdown("---")
    st.header("💻 2단계 : 공통 설계 제원 설정")
    freq = st.number_input("대표주파수 (Hz)", value=500.0, step=1.0, format="%.0f")
    tl_option = st.number_input("투과손실치 (dB)", value=15.0, step=0.5, format="%.1f")
    h_source_rel = st.number_input("음원 높이 (Hs, m)", value=1.2, step=0.1, format="%.1f")
    h_rcv_common = st.number_input("수음점 높이 (Hr, m)", value=1.5, step=0.1, format="%.1f")
    dist_sb_fixed = st.number_input("음원~방음판넬 거리 (m)", value=10.0, step=0.5, format="%.1f")
    g_source = 0.0

    st.markdown("---")
    st.header("⛰️ 3단계 : 지반고 입력 (선택사항)")
    g_barrier = st.number_input("방음판넬 설치위치 지반고(m)", value=0.0, step=0.5, format="%.1f")
    g_rcv = st.number_input("수음정 지반고(m)", value=0.0, step=0.5, format="%.1f")

st.markdown("### 📋 정온시설별 조건 입력표")

col_btn1, col_btn2, _ = st.columns([1.5, 1.5, 5])
with col_btn1:
    if st.button("➕ 정온시설 추가"):
        new_row = {"정온시설명": f"새시설_{len(st.session_state['df_facilities'])+1}", "이격거리(m)": 100.0, "저감전 소음도[dB(A)]": 70.0, "가설방음판넬 높이(m)": 3.0, "소음환경기준[dB(A)]": 65.0}
        st.session_state["df_facilities"] = pd.concat([st.session_state["df_facilities"], pd.DataFrame([new_row])], ignore_index=True)
        st.session_state["widget_version"] += 1
        st.rerun()
with col_btn2:
    if st.button("🔄 전체 초기화"):
        st.session_state["df_facilities"] = df_sample.copy()
        st.session_state["widget_version"] += 1
        st.rerun()

st.info("💡 각 항목의 값을 직접 입력하여 수정할 수 있으며, 우측의 **[🗑️]** 버튼으로 행을 삭제할 수 있습니다.")

header_cols = st.columns([2.0, 1.5, 1.8, 2.0, 1.5, 0.8])
header_cols[0].markdown("<div class='custom-table-header'>정온시설명</div>", unsafe_allow_html=True)
header_cols[1].markdown("<div class='custom-table-header'>이격거리(m)</div>", unsafe_allow_html=True)
header_cols[2].markdown("<div class='custom-table-header'>저감전 소음도[dB(A)]</div>", unsafe_allow_html=True)
header_cols[3].markdown("<div class='custom-table-header'>방음판넬 높이(m)</div>", unsafe_allow_html=True)
header_cols[4].markdown("<div class='custom-table-header'>소음환경기준[dB(A)]</div>", unsafe_allow_html=True)
header_cols[5].markdown("<div class='custom-table-header'>삭제</div>", unsafe_allow_html=True)

st.markdown("---")

indices_to_delete = []
v_id = st.session_state["widget_version"]

for idx, row in st.session_state["df_facilities"].iterrows():
    row_cols = st.columns([2.0, 1.5, 1.8, 2.0, 1.5, 0.8])
    
    with row_cols[0]:
        current_name = str(row["정온시설명"])
        new_name = st.text_input("시설명", value=current_name, key=f"name_{v_id}_{idx}", label_visibility="collapsed")
        if new_name != current_name:
            st.session_state["df_facilities"].at[idx, "정온시설명"] = new_name

    with row_cols[1]:
        current_dist = float(row["이격거리(m)"])
        new_dist = st.number_input("이격거리", min_value=0.1, max_value=5000.0, value=current_dist, step=10.0, format="%.1f", key=f"dist_{v_id}_{idx}", label_visibility="collapsed")
        if new_dist != current_dist:
            st.session_state["df_facilities"].at[idx, "이격거리(m)"] = new_dist

    with row_cols[2]:
        current_noise = float(row["저감전 소음도[dB(A)]"])
        new_noise = st.number_input("저감전소음", min_value=0.0, max_value=150.0, value=current_noise, step=0.5, format="%.1f", key=f"noise_{v_id}_{idx}", label_visibility="collapsed")
        if new_noise != current_noise:
            st.session_state["df_facilities"].at[idx, "저감전 소음도[dB(A)]"] = new_noise

    with row_cols[3]:
        current_h = float(row["가설방음판넬 높이(m)"])
        new_h_input = st.number_input("높이", min_value=0.0, max_value=30.0, value=current_h, step=0.5, format="%.1f", key=f"input_h_{v_id}_{idx}", label_visibility="collapsed")
        if new_h_input != current_h:
            st.session_state["df_facilities"].at[idx, "가설방음판넬 높이(m)"] = new_h_input

    with row_cols[4]:
        current_env = float(row["소음환경기준[dB(A)]"])
        new_env = st.number_input("환경기준", min_value=0.0, max_value=120.0, value=current_env, step=1.0, format="%.1f", key=f"env_{v_id}_{idx}", label_visibility="collapsed")
        if new_env != current_env:
            st.session_state["df_facilities"].at[idx, "소음환경기준[dB(A)]"] = new_env

    with row_cols[5]:
        if st.button("🗑️", key=f"del_{v_id}_{idx}"):
            indices_to_delete.append(idx)

if indices_to_delete:
    st.session_state["df_facilities"] = st.session_state["df_facilities"].drop(indices_to_delete).reset_index(drop=True)
    st.session_state["widget_version"] += 1
    st.rerun()

# --- 회절감쇠 산정 함수 (Kurze & Anderson) ---
def get_diffraction_attenuation(n_val):
    if n_val <= 0:
        return 0.0
    elif n_val <= 0.1:
        return 7.5 + 0.6 * math.log10(n_val) if n_val > 0 else 0.0
    elif n_val <= 0.8:
        return 10 + 3 * math.log10(n_val)
    elif n_val <= 30:
        return 11 + 7 * math.log10(n_val)
    elif n_val <= 60:
        return 12 + 6 * math.log10(n_val)
    else:
        return 22.0

# --- 각 행별 소음 저감효과 자동 연산 ---
results = []
y_src = g_source + h_source_rel

for idx, row in st.session_state["df_facilities"].iterrows():
    name = row["정온시설명"]
    if not name or pd.isna(name):
        continue  
        
    try:
        dist_total = float(row["이격거리(m)"]) if row["이격거리(m)"] is not None else 0.0
        noise_before = float(row["저감전 소음도[dB(A)]"]) if row["저감전 소음도[dB(A)]"] is not None else 0.0
        h_bar = float(row["가설방음판넬 높이(m)"]) if row["가설방음판넬 높이(m)"] is not None else 4.0
        target_env = float(row["소음환경기준[dB(A)]"]) if row["소음환경기준[dB(A)]"] is not None else 65.0
    except (ValueError, TypeError):
        continue  

    if dist_total <= dist_sb_fixed:
        dist_sb = dist_total * 0.5
        dist_bo = dist_total * 0.5
    else:
        dist_sb = dist_sb_fixed
        dist_bo = dist_total - dist_sb_fixed

    y_barrier = g_barrier + h_bar
    y_rcv_abs = g_rcv + h_rcv_common
    
    dist_A1 = math.sqrt(dist_sb**2 + (y_barrier - y_src)**2)
    dist_B1 = math.sqrt(dist_bo**2 + (y_barrier - y_rcv_abs)**2)
    dist_D1 = math.sqrt(dist_total**2 + (y_rcv_abs - y_src)**2)
    delta_1 = (dist_A1 + dist_B1) - dist_D1
    fresnel_N1 = delta_1 * (2.0 * freq / 340.0)
    delta_ldi = get_diffraction_attenuation(fresnel_N1)
    
    y_source_ref = 2 * g_source - y_src
    dist_A2 = math.sqrt(dist_sb**2 + (y_barrier - y_source_ref)**2)
    dist_B2 = math.sqrt(dist_bo**2 + (y_barrier - y_rcv_abs)**2)
    dist_D2 = math.sqrt(dist_total**2 + (y_rcv_abs - y_source_ref)**2)
    delta_2 = (dist_A2 + dist_B2) - dist_D2
    fresnel_N2 = delta_2 * (2.0 * freq / 340.0)
    delta_ldr = get_diffraction_attenuation(fresnel_N2)
    
    try:
        val_di = 10 ** (-delta_ldi / 10.0)
        val_dr = 10 ** (-delta_ldr / 10.0)
        delta_ld_total = -10 * math.log10(val_di + val_dr)
    except:
        delta_ld_total = delta_ldi
        
    tl_energy = 10 ** (-tl_option / 10.0)
    try:
        delta_li = -10 * math.log10(val_di + tl_energy)
    except:
        delta_li = min(delta_ld_total, tl_option)
        
    noise_after = max(0.0, noise_before - delta_li)
    satisfy = "만족" if noise_after <= target_env else "초과"
    
    results.append({
        "정온시설": name,
        "이격거리(m)": round(dist_total, 1),
        "저감전 소음도[dB(A)]": round(noise_before, 1),
        "가설방음판넬 높이(m)": round(h_bar, 1),
        "경로차 (δ, m)": round(delta_1, 3),
        "회절감쇠 (ΔLd)": round(delta_ld_total, 1),
        "투과손실 (ΔLt)": round(tl_option, 1),
        "삽입손실(총 저감치)": round(delta_li, 1),
        "저감후 소음도[dB(A)]": round(noise_after, 1),
        "소음환경기준[dB(A)]": round(target_env, 1),
        "만족여부": satisfy
    })

if results:
    result_df = pd.DataFrame(results)
    result_df.index = range(1, len(result_df) + 1)

    st.markdown("---")
    st.markdown("### 📊 가설방음판넬 설치 후 소음 예측 결과표")
    
    numeric_cols = [
        "이격거리(m)", "저감전 소음도[dB(A)]", "가설방음판넬 높이(m)", "경로차 (δ, m)", 
        "회절감쇠 (ΔLd)", "투과손실 (ΔLt)", "삽입손실(총 저감치)", 
        "저감후 소음도[dB(A)]", "소음환경기준[dB(A)]"
    ]
    
    format_dict = {col: ("{:.3f}" if col == "경로차 (δ, m)" else "{:.1f}") for col in numeric_cols}
    styled_df = result_df.style.format(format_dict).set_properties(**{'text-align': 'center'})
    styled_df = styled_df.set_table_styles([{'selector': 'th', 'props': [('text-align', 'center'), ('font-weight', 'bold')]}])
    
    st.dataframe(styled_df, use_container_width=True)

    csv_data = result_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 산정 결과표 엑셀(CSV) 다운로드",
        data=csv_data,
        file_name="가설방음판넬_소음예측결과.csv",
        mime="text/csv",
    )

    st.markdown("---")
    st.markdown("### 🔍 정온시설별 소음원-가설방음판넬-수음원 횡단면도")

    selected_facility = st.selectbox(
        "상세 단면도를 확인할 정온시설을 선택하세요:",
        options=result_df["정온시설"].tolist()
    )

    if selected_facility:
        sel_row = st.session_state["df_facilities"][st.session_state["df_facilities"]["정온시설명"] == selected_facility].iloc[0]
        dist_total = float(sel_row["이격거리(m)"])
        h_bar = float(sel_row["가설방음판넬 높이(m)"])
        
        if dist_total <= dist_sb_fixed:
            dist_sb = dist_total * 0.5
            dist_bo = dist_total * 0.5
        else:
            dist_sb = dist_sb_fixed
            dist_bo = dist_total - dist_sb_fixed

        y_barrier = g_barrier + h_bar
        y_rcv_abs = g_rcv + h_rcv_common
        
        fig, ax = plt.subplots(figsize=(10, 4.8))
        x_src = 0.0
        x_bar = dist_sb
        x_rcv = dist_total
        
        dist_A = math.sqrt(dist_sb**2 + (y_barrier - y_src)**2)
        dist_B = math.sqrt(dist_bo**2 + (y_barrier - y_rcv_abs)**2)
        dist_D = math.sqrt(dist_total**2 + (y_rcv_abs - y_src)**2)
        
        ax.plot([x_src, x_bar, x_rcv], [g_source, g_barrier, g_rcv], color='saddlebrown', linewidth=3, label='지형 단면')
        
        ax.scatter([x_src], [y_src], color='red', s=100, zorder=5)
        ax.text(x_src, y_src + 0.3, f'소음원 S (Z={y_src:.1f}m)', fontsize=10, fontweight='bold', color='red', ha='center')
        
        barrier_width = max(dist_total * 0.015, 1.0)
        ax.bar(x_bar, y_barrier - g_barrier, width=barrier_width, bottom=g_barrier, color='gray', alpha=0.8, align='center')
        ax.text(x_bar, y_barrier + 0.3, f'가설방음판넬 (H={h_bar}m)', fontsize=10, fontweight='bold', color='darkslategray', ha='center')
        
        ax.scatter([x_rcv], [y_rcv_abs], color='blue', s=100, zorder=5)
        ax.text(x_rcv, y_rcv_abs + 0.3, f'{selected_facility} O (Z={y_rcv_abs:.1f}m)', fontsize=10, fontweight='bold', color='blue', ha='center')
        
        ax.plot([x_src, x_bar, x_rcv], [y_src, y_barrier, y_rcv_abs], color='orange', linestyle='--', linewidth=2.5, label='회절 경로 A+B')
        ax.plot([x_src, x_rcv], [y_src, y_rcv_abs], color='forestgreen', linestyle=':', linewidth=2.0, label='직선거리 D')
        
        mid_A_x = (x_src + x_bar) / 2
        mid_A_y = (y_src + y_barrier) / 2
        ax.text(mid_A_x - dist_total * 0.02, mid_A_y + 0.35, f'A: {dist_A:.2f}m', fontsize=9, fontweight='bold', color='darkorange', bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7, edgecolor='orange'))

        mid_B_x = (x_bar + x_rcv) / 2
        mid_B_y = (y_barrier + y_rcv_abs) / 2
        ax.text(mid_B_x + dist_total * 0.02, mid_B_y + 0.35, f'B: {dist_B:.2f}m', fontsize=9, fontweight='bold', color='darkorange', bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7, edgecolor='orange'))

        mid_D_x = x_rcv / 2
        mid_D_y = (y_src + y_rcv_abs) / 2
        ax.text(mid_D_x, mid_D_y - 0.45, f'직선거리 D: {dist_D:.2f}m', fontsize=9, fontweight='bold', color='forestgreen', bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7, edgecolor='forestgreen'))

        ax.set_xlim(-dist_total*0.05, dist_total*1.05)
        ax.set_ylim(min(g_source, g_barrier, g_rcv) - 2.0, max(y_barrier, y_src, y_rcv_abs) * 1.4)
        ax.set_xlabel('수평 거리 (m)', fontsize=11)
        ax.set_ylabel('고도 (m)', fontsize=11)
        ax.grid(True, linestyle=':', alpha=0.6)
        ax.legend(loc='upper right')
        
        st.pyplot(fig)
else:
    st.warning("⚠️ 유효한 정온시설 데이터가 없습니다.")

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #BFBFBF; font-size: 14px;"
    " padding: 5px;'><b>제작자 :</b> (주)내경엔지니어링 박은정 과장</div>"
    "<div style='text-align: center; color: #BFBFBF; font-size: 14px;"
    " padding-bottom: 10px;'>문의사항은 <b>eunjeong0901@naver.com</b> 로 바랍니다.🦖</div>",
    unsafe_allow_html=True,
)
