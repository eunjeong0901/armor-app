import math
import platform
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="가설방음판넬 저감효과 자동산정 프로그램", layout="wide")

st.title("🛡️ 가설방음판넬 소음 저감효과 상세 산정 프로그램")

# --- 운영체제별 한글 폰트 자동 설정 (리눅스 서버 및 윈도우 공통 대응) ---
if platform.system() == 'Windows':
    plt.rcParams['font.family'] = 'Malgun Gothic'
else:
    # Streamlit Cloud (Linux) 환경에서는 나눔고딕 사용
    plt.rcParams['font.family'] = 'NanumGothic'

plt.rcParams['axes.unicode_minus'] = False

# --- 사이드바 입력부 ---
with st.sidebar:
    st.header("1. 현장 조건 및 제원 입력")
    
    # 1) 메인 제원 (자주 변경하는 항목)
    source_noise = st.number_input("예측 소음도 [dB(A)]", value=52.3, step=0.1, format="%.1f")
    env_target = st.number_input("소음목표기준 [dB(A)]", value=65.0, step=1.0, format="%.0f")
    h_barrier_rel = st.number_input("가설방음판넬 높이 (m)", value=6.0, step=0.1, format="%.1f")
    
    st.markdown("---")
    st.subheader("2. 거리 및 지반 조건")
    dist_source_barrier = st.number_input("음원-가설방음판넬 수평거리 (m)", value=10.0, step=0.1, format="%.1f")
    dist_receiver_barrier = st.number_input("수음점-가설방음판넬 수평거리 (m)", value=30.0, step=0.1, format="%.1f")
    
    g_barrier = st.number_input("가설방음판넬 설치 지반고 (m)", value=0.0, step=0.1, format="%.1f")
    g_receiver = st.number_input("수음점 지반고 (m)", value=0.0, step=0.1, format="%.1f")
    
    st.markdown("---")
    
    # 2) 고정값 및 상세 제원 (평소에 잘 안 바꾸는 항목들)
    with st.expander("⚙️ 상세 제원 및 고정값 설정 (주파수·높이·TL 등)", expanded=False):
        freq = st.number_input("대표 주파수 (Hz)", value=500.0, step=1.0, format="%.0f")
        h_source_rel = st.number_input("음원 상대 높이 (m)", value=1.2, step=0.1, format="%.1f")
        h_receiver_rel = st.number_input("수음점 상대 높이 (m)", value=1.5, step=0.1, format="%.1f")
        tl_barrier = st.number_input("가설방음판넬 투과손실 (TL, dB)", value=15.0, step=1.0, format="%.0f")

# --- 최종 절대 좌표(고도) 산정 (음원 지반고는 0으로 고정) ---
g_source = 0.0
y_src = g_source + h_source_rel
y_barrier = g_barrier + h_barrier_rel
y_rcv = g_receiver + h_receiver_rel

# --- 2. 엑셀 수식 기반 정밀 연산부 ---
wavelength = 340.0 / freq if freq > 0 else 0.68

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

# [직접음 계산] (지반고 연동 절대고도 기준)
dist_A1 = math.sqrt(dist_source_barrier**2 + (y_barrier - y_src)**2)
dist_B1 = math.sqrt(dist_receiver_barrier**2 + (y_barrier - y_rcv)**2)
total_dist1 = dist_source_barrier + dist_receiver_barrier
dist_D1 = math.sqrt(total_dist1**2 + (y_rcv - y_src)**2)

delta_1 = (dist_A1 + dist_B1) - dist_D1
fresnel_N1 = (delta_1 * freq) / 170.0
delta_ld1 = round(get_diffraction_attenuation(fresnel_N1), 2)

# [반사음 계산]
y_source_ref = 2 * g_source - y_src
dist_A2 = math.sqrt(dist_source_barrier**2 + (y_barrier - y_source_ref)**2)
dist_B2 = math.sqrt(dist_receiver_barrier**2 + (y_barrier - y_rcv)**2)
dist_D2 = math.sqrt(total_dist1**2 + (y_rcv - y_source_ref)**2)

delta_2 = (dist_A2 + dist_B2) - dist_D2
fresnel_N2 = (delta_2 * freq) / 170.0
delta_ld2 = round(get_diffraction_attenuation(fresnel_N2), 2)

# [종합 회절감쇠치]
try:
    val_c23 = 10 ** (-delta_ld1 / 10.0)
    val_c36 = 10 ** (-delta_ld2 / 10.0)
    delta_ld_total = round(-10 * math.log10(val_c23 + val_c36), 2)
except:
    delta_ld_total = delta_ld1

# [삽입손실치 및 저감 후 소음도]
tl_energy = 10 ** (-tl_barrier / 10.0)
try:
    delta_li = round(-10 * math.log10(val_c23 + tl_energy), 1)
except:
    delta_li = round(min(delta_ld_total, tl_barrier), 1)

final_noise = round(source_noise - delta_li, 1)

# --- 3. 화면 출력 결과 리포트 ---
st.markdown("### 📊 가설방음판넬 저감효과 산정 결과")

col1, col2, col3, col4 = st.columns(4)
col1.metric("직접음 경로차 ($\delta_1$)", f"{delta_1:.2f} m")
col2.metric("직접음 프레넬 수 ($N_1$)", f"{fresnel_N1:.2f}")
col3.metric("직접음 회절감쇠치 ($\Delta L_{d1}$)", f"{delta_ld1:.2f} dB")
col4.metric("종합 회절감쇠치 ($\Delta L_d$)", f"{delta_ld_total:.2f} dB")

st.markdown("---")

res_col1, res_col2, res_col3 = st.columns(3)
res_col1.metric("최종 삽입손실치 ($\Delta Li$)", f"{delta_li:.1f} dB")
res_col2.metric("저감 후 예상 소음도", f"{final_noise:.1f} dB(A)")
res_col3.metric("환경목표기준 비교", f"{env_target:.0f} dB(A)")

if final_noise <= env_target:
    st.success(f"✅ 저감 후 소음도[{final_noise:.1f} dB(A)]가 소음목표기준[{env_target:.0f} dB(A)] 이내로 적합합니다.")
else:
    st.error(f"⚠️ 저감 후 소음도[{final_noise:.1f} dB(A)]가 소음목표기준[{env_target:.0f} dB(A)]을 초과합니다.")

# --- 4. 횡단면 배치도 시각화 ---
st.markdown("### 📐 소음원-가설방음판넬-수음점 횡단면도")

fig, ax = plt.subplots(figsize=(10, 5.2))

x_src = 0.0
x_bar = dist_source_barrier
x_rcv = dist_source_barrier + dist_receiver_barrier

max_x = x_rcv * 1.05

# 지형 시각화 (음원 지반고는 0.0 기준)
ax.plot([x_src, x_bar, x_rcv], [g_source, g_barrier, g_receiver], color='saddlebrown', linewidth=3, label='지형 단면 (Ground Profile)')

# 음원, 가설방음판넬, 수음점 위치 표시
ax.scatter([x_src], [y_src], color='red', s=120, zorder=5)
ax.text(x_src, y_src + 0.4, f'음원 (Z={y_src:.1f}m)', fontsize=10, fontweight='bold', color='red', ha='center')

barrier_width = max_x * 0.015
ax.bar(x_bar, y_barrier - g_barrier, width=barrier_width, bottom=g_barrier, color='gray', alpha=0.8, align='center')
ax.text(x_bar, y_barrier + 0.4, f'가설방음판넬 (Z={y_barrier:.1f}m)', fontsize=10, fontweight='bold', color='darkslategray', ha='center')

ax.scatter([x_rcv], [y_rcv], color='blue', s=120, zorder=5)
ax.text(x_rcv, y_rcv + 0.4, f'수음점 (Z={y_rcv:.1f}m)', fontsize=10, fontweight='bold', color='blue', ha='center')

# 회절 경로선 (A+B)
ax.plot([x_src, x_bar, x_rcv], [y_src, y_barrier, y_rcv], color='orange', linestyle='--', linewidth=2.5, label='회절 경로 A+B')

# 직선거리선 (D)
ax.plot([x_src, x_rcv], [y_src, y_rcv], color='forestgreen', linestyle=':', linewidth=2.0, label='직선거리 D')

# 회절 경로 구간 A, B 표시
mid_x_A = (x_src + x_bar) / 2
mid_y_A = (y_src + y_barrier) / 2
ax.text(mid_x_A - 1.5, mid_y_A, f'A = {dist_A1:.2f}m', fontsize=9, fontweight='bold', color='darkorange', ha='right')

mid_x_B = (x_bar + x_rcv) / 2
mid_y_B = (y_barrier + y_rcv) / 2
ax.text(mid_x_B, mid_y_B + 0.5, f'B = {dist_B1:.2f}m', fontsize=9, fontweight='bold', color='darkorange', ha='center')

# 직선거리 D 값 표시
mid_x_D = (x_src + x_rcv) / 2
mid_y_D = (y_src + y_rcv) / 2
ax.text(mid_x_D, mid_y_D - 0.7, f'D = {dist_D1:.2f}m', fontsize=10, fontweight='bold', color='forestgreen', ha='center')

ax.set_xlim(-5, max_x)
min_y = min(g_source, g_barrier, g_receiver) - 2
max_y = max(y_barrier, y_src, y_rcv) * 1.4
ax.set_ylim(min_y, max_y)

ax.set_xlabel('수평 거리 (m)', fontsize=11)
ax.set_ylabel('해발/기준 고도 (m)', fontsize=11)
ax.grid(True, linestyle=':', alpha=0.6)
ax.legend(loc='upper right', framealpha=0.9)

st.pyplot(fig)

# 상세 데이터 아코디언
with st.expander("🔍 엑셀 세부 파라미터 및 지반고 상세 보기"):
    st.write(f"- **음원 절대고도 (Z)**: {y_src:.2f} m (상대높이 {h_source_rel}m)")
    st.write(f"- **가설방음판넬 상단 절대고도 (Z)**: {y_barrier:.2f} m (지반고 {g_barrier}m + 판넬높이 {h_barrier_rel}m)")
    st.write(f"- **수음점 절대고도 (Z)**: {y_rcv:.2f} m (지반고 {g_receiver}m + 상대높이 {h_receiver_rel}m)")
    st.write(f"- **음원 ~ 가설방음판넬 상단 거리 (A)**: {dist_A1:.2f} m")
    st.write(f"- **수음점 ~ 가설방음판넬 상단 거리 (B)**: {dist_B1:.2f} m")
    st.write(f"- **음원 ~ 수음점 직선거리 (D)**: {dist_D1:.2f} m")
    st.write(f"- **최종 경로차 ($\delta_1 = A + B - D$)**: {delta_1:.2f} m (회절감쇠치: {delta_ld1:.2f} dB)")
    # 📌 푸터 추가
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #ffffff; font-size: 14px;"
    " padding: 10px;'><b>제작자 :</b> (주)내경엔지니어링 박은정 과장</div>",
    unsafe_allow_html=True,
)
