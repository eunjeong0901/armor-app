import streamlit as st
import numpy as np
import pandas as pd

st.set_page_config(page_title="공사장비 운용 시 합성소음도 산정 프로그램", layout="wide")

st.title("🏗️ 공사장비 운용 시 합성소음도 산정 프로그램")
st.markdown("공사 장비 제원(CSV 업로드 또는 수동 선택)을 통해 환경영향평가 실무 공식에 따른 합성소음도를 산정합니다.")

# 📋 표준 장비 소음도 데이터베이스 (제공된 전체 표 완벽 반영 - 15m 평균 소음도 기준)
NOISE_DB = [
    # 굴착기
    {"기계": "굴착기", "동력": "75미만", "가동상태": "작업", "대당소음도(15m)": 67.5},
    {"기계": "굴착기", "동력": "75~140", "가동상태": "작업", "대당소음도(15m)": 71.7},
    {"기계": "굴착기", "동력": "140~280", "가동상태": "작업", "대당소음도(15m)": 73.4},
    {"기계": "굴착기", "동력": "280이상", "가동상태": "작업", "대당소음도(15m)": 76.5},
    # 불도저
    {"기계": "불도저", "동력": "70미만", "가동상태": "작업", "대당소음도(15m)": 72.6},
    {"기계": "불도저", "동력": "70~140", "가동상태": "작업", "대당소음도(15m)": 73.1},
    {"기계": "불도저", "동력": "140이상", "가동상태": "작업", "대당소음도(15m)": 75.8},
    # 로우더 / 그레이더
    {"기계": "로우더", "동력": "140이상", "가동상태": "작업", "대당소음도(15m)": 75.6},
    {"기계": "그레이더", "동력": "120~170", "가동상태": "작업", "대당소음도(15m)": 72.7},
    # 롤러류
    {"기계": "탠덤롤러", "동력": "75이상", "가동상태": "작업", "대당소음도(15m)": 70.6},
    {"기계": "진동롤러", "동력": "75이상", "가동상태": "무진동작업", "대당소음도(15m)": 72.5},
    {"기계": "진동롤러", "동력": "75이상", "가동상태": "진동작업", "대당소음도(15m)": 74.8},
    {"기계": "타이어롤러", "동력": "75이상", "가동상태": "작업", "대당소음도(15m)": 62.7},
    {"기계": "탬핑롤러", "동력": "75이상", "가동상태": "무진동작업", "대당소음도(15m)": 74.5},
    {"기계": "탬핑롤러", "동력": "75이상", "가동상태": "진동작업", "대당소음도(15m)": 77.4},
    # 다짐기 / 트랙터
    {"기계": "법면다짐기", "동력": "180", "가동상태": "작업", "대당소음도(15m)": 72.2},
    # 어스오거 / 항타기
    {"기계": "어스오거", "동력": "-", "가동상태": "작업", "대당소음도(15m)": 76.6},
    {"기계": "어스오거", "동력": "-", "가동상태": "항타", "대당소음도(15m)": 78.2},
    {"기계": "항타기", "동력": "-", "가동상태": "작업", "대당소음도(15m)": 89.2},
    {"기계": "진동항타기", "동력": "-", "가동상태": "작업", "대당소음도(15m)": 81.9},
    # 드릴 / 착암기
    {"기계": "크롤라드릴", "동력": "-", "가동상태": "작업", "대당소음도(15m)": 80.9},
    {"기계": "착암기", "동력": "-", "가동상태": "작업", "대당소음도(15m)": 86.8},
    # 콘크리트 관련 장비
    {"기계": "콘크리트펌프카", "동력": "305~340", "가동상태": "작업", "대당소음도(15m)": 73.5},
    {"기계": "콘크리트믹서", "동력": "320", "가동상태": "작업", "대당소음도(15m)": 62.5},
    {"기계": "콘크리트플랜트", "동력": "250", "가동상태": "작업", "대당소음도(15m)": 0.0},
    {"기계": "크리트바이브레이터", "동력": "-", "가동상태": "작업", "대당소음도(15m)": 68.3},
    {"기계": "콘크리트피니셔", "동력": "-", "가동상태": "작업", "대당소음도(15m)": 76.9},
    {"기계": "아스팔트피니셔", "동력": "-", "가동상태": "작업", "대당소음도(15m)": 76.5},
    # 브레이커류
    {"기계": "브레이커", "동력": "500kg미만", "가동상태": "작업", "대당소음도(15m)": 82.9},
    {"기계": "브레이커", "동력": "500kg이상", "가동상태": "작업", "대당소음도(15m)": 88.7},
    {"기계": "핸드브레이커", "동력": "-", "가동상태": "작업", "대당소음도(15m)": 0.0},
    # 발전기 / 압쇄기 / 압축기 / 크레인
    {"기계": "발전기", "동력": "75미만", "가동상태": "개방", "대당소음도(15m)": 69.1},
    {"기계": "발전기", "동력": "75미만", "가동상태": "폐쇄", "대당소음도(15m)": 66.8},
    {"기계": "발전기", "동력": "75이상", "가동상태": "개방", "대당소음도(15m)": 72.8},
    {"기계": "소형발전기", "동력": "75미만", "가동상태": "작업", "대당소음도(15m)": 69.9},
    {"기계": "압쇄기", "동력": "75미만", "가동상태": "작업", "대당소음도(15m)": 62.6},
    {"기계": "압쇄기", "동력": "75~140", "가동상태": "작업", "대당소음도(15m)": 65.9},
    {"기계": "압축기", "동력": "10~30㎥/분", "가동상태": "작업", "대당소음도(15m)": 73.1},
    {"기계": "크레인", "동력": "-", "가동상태": "작업", "대당소음도(15m)": 70.1},
    # 기타 장비
    {"기계": "고압살수차량", "동력": "-", "가동상태": "작업", "대당소음도(15m)": 70.3},
    {"기계": "지게차", "동력": "-", "가동상태": "작업", "대당소음도(15m)": 74.7},
    {"기계": "덤프트럭", "동력": "-", "가동상태": "작업", "대당소음도(15m)": 74.9},
]

df_db = pd.DataFrame(NOISE_DB)

# 세션 스테이트로 수동 입력 목록 관리
if "manual_equipment_list" not in st.session_state:
    st.session_state.manual_equipment_list = []

# 사이드바 설정: 입력 방식 선택
st.sidebar.header("🛠️  입력 방식 선택")
input_mode = st.sidebar.radio("방식을 선택하세요", ["📁 CSV 파일 업로드", "✍️ 장비 수동 입력"])

input_df = None

if input_mode == "📁 CSV 파일 업로드":
    st.sidebar.markdown("---")
    st.sidebar.subheader("CSV 파일 업로드")
    st.sidebar.text("필수 컬럼: 장비명, 대수, 대당소음도(15m)")
    uploaded_file = st.sidebar.file_uploader("CSV 파일 선택", type=["csv"])
    
    sample_data = pd.DataFrame([
        {"장비명": "굴착기", "대수": 1, "대당소음도(15m)": 73.4},
        {"장비명": "콘크리트펌프카", "대수": 1, "대당소음도(15m)": 73.5}
    ])
    sample_csv = sample_data.to_csv(index=False).encode('utf-8-sig')
    st.sidebar.download_button("📥 입력용 샘플 CSV 다운로드", sample_csv, "sample_equipment_list.csv", "mime/csv")

    if uploaded_file is not None:
        try:
            try:
                input_df = pd.read_csv(uploaded_file, encoding='utf-8')
            except UnicodeDecodeError:
                uploaded_file.seek(0)
                input_df = pd.read_csv(uploaded_file, encoding='cp949')
        except Exception as e:
            st.error(f"파일 읽기 오류: {e}")

else:  # 수동 입력 모드
    st.sidebar.markdown("---")
    st.sidebar.subheader("✍️ 장비별 제원 선택 입력")
    
    available_machines = df_db["기계"].unique().tolist()
    selected_machine = st.sidebar.selectbox("◎ 장비", available_machines)
    
    filtered_powers = df_db[df_db["기계"] == selected_machine]["동력"].unique().tolist()
    selected_power = st.sidebar.selectbox("◎ 동력(HP)", filtered_powers)
    
    filtered_states = df_db[(df_db["기계"] == selected_machine) & (df_db["동력"] == selected_power)]["가동상태"].unique().tolist()
    selected_state = st.sidebar.selectbox("◎ 가동상태", filtered_states)
    
    matched_row = df_db[(df_db["기계"] == selected_machine) & (df_db["동력"] == selected_power) & (df_db["가동상태"] == selected_state)]
    default_noise = float(matched_row["대당소음도(15m)"].values[0]) if not matched_row.empty else 75.0
    
    st.sidebar.info(f"🔊 **연동된 대당소음도(15m)**: **{default_noise:.1f} dB(A)**")
    
    eq_count = st.sidebar.number_input("투입 대수 [대]", min_value=1, value=1, step=1)
    
    col_s1, col_s2 = st.sidebar.columns(2)
    with col_s1:
        if st.button("➕ 목록에 추가", use_container_width=True):
            eq_name_full = f"{selected_machine} ({selected_power}, {selected_state})"
            st.session_state.manual_equipment_list.append({
                "장비명": eq_name_full,
                "대수": eq_count,
                "대당소음도(15m)": default_noise
            })
            st.rerun()
    with col_s2:
        if st.button("🗑️ 목록 초기화", use_container_width=True):
            st.session_state.manual_equipment_list = []
            st.rerun()
            
    if len(st.session_state.manual_equipment_list) > 0:
        input_df = pd.DataFrame(st.session_state.manual_equipment_list)

# 메인 화면 구성 (전체 너비 활용)
if input_df is None or len(input_df) == 0:
    st.info("👋 **안내**: 왼쪽 사이드바에서 **[CSV 파일 업로드]** 또는 **[장비 수동 입력]**을 통해 공사 장비 정보를 추가해 주세요.")
else:
    try:
        required_columns = ["장비명", "대수", "대당소음도(15m)"]
        if not all(col in input_df.columns for col in required_columns):
            st.error("🚨 필수 컬럼(`장비명`, `대수`, `대당소음도(15m)`)이 누락되었습니다.")
        else:
            df = input_df.copy()
            df["수음점도달소음도"] = df["대당소음도(15m)"]

            # 합성소음도 산출공식(L0) 적용
            spl_values = df["수음점도달소음도"].values
            counts = df["대수"].values
            
            energy_terms = counts * (10 ** (0.1 * spl_values))
            total_energy_sum = np.sum(energy_terms)
            total_synthesized_noise = 10 * np.log10(total_energy_sum) if total_energy_sum > 0 else 0.0

            st.subheader("📊 장비 소음 산정 내역")
            
            html_code = """
            <style>
                .noise-table {
                    width: 100%;
                    border-collapse: collapse;
                    font-family: inherit;
                    font-size: 14px;
                    color: #fafafa;
                    background-color: #0e1117;
                    margin-bottom: 1rem;
                }
                .noise-table th, .noise-table td {
                    border: 1px solid #303030;
                    padding: 10px 12px;
                    text-align: center;
                }
                .noise-table th {
                    background-color: #262730;
                    font-weight: 600;
                }
                .noise-table td {
                    background-color: #0e1117;
                }
            </style>
            <table class="noise-table">
                <thead>
                    <tr>
                        <th>장비명</th>
                        <th>대수 [대]</th>
                        <th>대당소음도(15m) [dB(A)]</th>
                        <th>최종 합성소음도 (L₀) [dB(A)]</th>
                    </tr>
                </thead>
                <tbody>
            """

            num_rows = len(df)
            for i, row in df.iterrows():
                name = row["장비명"]
                count = int(row["대수"])
                spl_15m = row["대당소음도(15m)"]
                
                html_code += "<tr>"
                html_code += f"<td>{name}</td>"
                html_code += f"<td>{count}대</td>"
                html_code += f"<td>{spl_15m:.1f}</td>"
                
                if i == 0:
                    html_code += f'<td rowspan="{num_rows}" style="vertical-align: middle; font-weight: bold; font-size: 16px; color: #ff4b4b;">{total_synthesized_noise:.1f}</td>'
                
                html_code += "</tr>"

            html_code += """
                </tbody>
            </table>
            """
            
            st.markdown(html_code, unsafe_allow_html=True)
            
            # 📌 산정 공식 명시
            st.markdown("---")
            st.markdown("### 📐 적용된 산정 공식")
            st.markdown(
                """
                <div style="background-color: #1e2530; padding: 18px 22px; border-radius: 8px; border-left: 5px solid #ff4b4b; font-size: 16px; line-height: 1.9; color: #fafafa;">
                    <b>■ 합성소음도 산출공식</b><br>
                    &nbsp;&nbsp;&nbsp;&nbsp;<b>L₀ = 10 · log ( A · 10<sup>SPL₁/10</sup> + B · 10<sup>SPL₂/10</sup> + …… + N · 10<sup>SPLₙ/10</sup> )</b><br><br>
                    <b>여기서,</b> &nbsp; <b>L₀</b> : 합성음 소음도 (dB(A))<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>A, B, ……, N</b> : 각 장비의 투입대수<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>SPL₁,₂,……,ₙ</b> : 각 장비별 발생소음도 (dB(A))
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown("---")
            
            # 다운로드 버튼
            download_df = df[["장비명", "대수", "대당소음도(15m)"]].copy()
            download_df["최종합성소음도(L0)"] = round(total_synthesized_noise, 1)
            csv_result = download_df.to_csv(index=False).encode('utf-8-sig')
            
            st.download_button(
                label="📥 최종 산정 결과 보고서 다운로드 (CSV)",
                data=csv_result,
                file_name="noise_prediction_result.csv",
                mime="text/csv",
            )

    except Exception as e:
        st.error(f"🚨 처리 중 오류가 발생했습니다: {e}")

# 📌 제작자 정보 푸터 추가 (텍스트 색상 흰색 처리)
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #ffffff; font-size: 14px; padding: 10px;'>"
    "<b>제작자:</b> (주)내경엔지니어링 박은정 과장"
    "</div>",
    unsafe_allow_html=True
)