import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="공사장비 환경영향 예측 프로그램", layout="wide"
)

st.title("🏗️ 공사장비 운용 시 소음·진동 영향 예측 프로그램")
st.markdown(
    "합성공식에 따라 공사장비의 합성소음도 및 합성진동레벨을"
    " 산정합니다."
)

# 📋 표준 장비 소음도 데이터베이스 (15m 기준)
NOISE_DB = [
    {"기계": "굴착기", "동력": "75미만", "가동상태": "작업", "대당소음도(15m)": 67.5},
    {"기계": "굴착기", "동력": "75~140", "가동상태": "작업", "대당소음도(15m)": 71.7},
    {
        "기계": "굴착기",
        "동력": "140~280",
        "가동상태": "작업",
        "대당소음도(15m)": 73.4,
    },
    {"기계": "굴착기", "동력": "280이상", "가동상태": "작업", "대당소음도(15m)": 76.5},
    {"기계": "불도저", "동력": "70미만", "가동상태": "작업", "대당소음도(15m)": 72.6},
    {"기계": "불도저", "동력": "70~140", "가동상태": "작업", "대당소음도(15m)": 73.1},
    {"기계": "불도저", "동력": "140이상", "가동상태": "작업", "대당소음도(15m)": 75.8},
    {"기계": "로우더", "동력": "140이상", "가동상태": "작업", "대당소음도(15m)": 75.6},
    {
        "기계": "그레이더",
        "동력": "120~170",
        "가동상태": "작업",
        "대당소음도(15m)": 72.7,
    },
    {
        "기계": "탠덤롤러",
        "동력": "75이상",
        "가동상태": "작업",
        "대당소음도(15m)": 70.6,
    },
    {
        "기계": "진동롤러",
        "동력": "75이상",
        "가동상태": "무진동작업",
        "대당소음도(15m)": 72.5,
    },
    {
        "기계": "진동롤러",
        "동력": "75이상",
        "가동상태": "진동작업",
        "대당소음도(15m)": 74.8,
    },
    {
        "기계": "타이어롤러",
        "동력": "75이상",
        "가동상태": "작업",
        "대당소음도(15m)": 62.7,
    },
    {
        "기계": "탬핑롤러",
        "동력": "75이상",
        "가동상태": "무진동작업",
        "대당소음도(15m)": 74.5,
    },
    {
        "기계": "탬핑롤러",
        "동력": "75이상",
        "가동상태": "진동작업",
        "대당소음도(15m)": 77.4,
    },
    {
        "기계": "법면다짐기",
        "동력": "180",
        "가동상태": "작업",
        "대당소음도(15m)": 72.2,
    },
    {"기계": "어스오거", "동력": "-", "가동상태": "작업", "대당소음도(15m)": 76.6},
    {"기계": "어스오거", "동력": "-", "가동상태": "항타", "대당소음도(15m)": 78.2},
    {"기계": "항타기", "동력": "-", "가동상태": "작업", "대당소음도(15m)": 89.2},
    {
        "기계": "진동항타기",
        "동력": "-",
        "가동상태": "작업",
        "대당소음도(15m)": 81.9,
    },
    {
        "기계": "크롤라드릴",
        "동력": "-",
        "가동상태": "작업",
        "대당소음도(15m)": 80.9,
    },
    {"기계": "착암기", "동력": "-", "가동상태": "작업", "대당소음도(15m)": 86.8},
    {
        "기계": "콘크리트펌프카",
        "동력": "305~340",
        "가동상태": "작업",
        "대당소음도(15m)": 73.5,
    },
    {
        "기계": "콘크리트믹서",
        "동력": "320",
        "가동상태": "작업",
        "대당소음도(15m)": 62.5,
    },
    {
        "기계": "콘크리트플랜트",
        "동력": "250",
        "가동상태": "작업",
        "대당소음도(15m)": 0.0,
    },
    {
        "기계": "크리트바이브레이터",
        "동력": "-",
        "가동상태": "작업",
        "대당소음도(15m)": 68.3,
    },
    {
        "기계": "콘크리트피니셔",
        "동력": "-",
        "가동상태": "작업",
        "대당소음도(15m)": 76.9,
    },
    {
        "기계": "아스팔트피니셔",
        "동력": "-",
        "가동상태": "작업",
        "대당소음도(15m)": 76.5,
    },
    {
        "기계": "브레이커",
        "동력": "500kg미만",
        "가동상태": "작업",
        "대당소음도(15m)": 82.9,
    },
    {
        "기계": "브레이커",
        "동력": "500kg이상",
        "가동상태": "작업",
        "대당소음도(15m)": 88.7,
    },
    {
        "기계": "핸드브레이커",
        "동력": "-",
        "가동상태": "작업",
        "대당소음도(15m)": 0.0,
    },
    {"기계": "발전기", "동력": "75미만", "가동상태": "개방", "대당소음도(15m)": 69.1},
    {"기계": "발전기", "동력": "75미만", "가동상태": "폐쇄", "대당소음도(15m)": 66.8},
    {"기계": "발전기", "동력": "75이상", "가동상태": "개방", "대당소음도(15m)": 72.8},
    {
        "기계": "소형발전기",
        "동력": "75미만",
        "가동상태": "작업",
        "대당소음도(15m)": 69.9,
    },
    {"기계": "압쇄기", "동력": "75미만", "가동상태": "작업", "대당소음도(15m)": 62.6},
    {"기계": "압쇄기", "동력": "75~140", "가동상태": "작업", "대당소음도(15m)": 65.9},
    {
        "기계": "압축기",
        "동력": "10~30㎥/분",
        "가동상태": "작업",
        "대당소음도(15m)": 73.1,
    },
    {"기계": "크레인", "동력": "-", "가동상태": "작업", "대당소음도(15m)": 70.1},
    {
        "기계": "고압살수차량",
        "동력": "-",
        "가동상태": "작업",
        "대당소음도(15m)": 70.3,
    },
    {"기계": "지게차", "동력": "-", "가동상태": "작업", "대당소음도(15m)": 74.7},
    {
        "기계": "덤프트럭",
        "동력": "-",
        "가동상태": "작업",
        "대당소음도(15m)": 74.9,
    },
]

# 📋 표준 장비 진동레벨 데이터베이스 (7.5m 기준)
VIBRATION_DB = [
    {
        "기계": "굴착기",
        "동력": "75미만",
        "가동상태": "작업",
        "대당진동레벨(7.5m)": 36.7,
    },
    {
        "기계": "굴착기",
        "동력": "140~280",
        "가동상태": "작업",
        "대당진동레벨(7.5m)": 39.9,
    },
    {
        "기계": "굴착기",
        "동력": "280이상",
        "가동상태": "작업",
        "대당진동레벨(7.5m)": 55.4,
    },
    {
        "기계": "로우더",
        "동력": "140이상",
        "가동상태": "주행",
        "대당진동레벨(7.5m)": 37.9,
    },
    {
        "기계": "그레이더",
        "동력": "120~170",
        "가동상태": "작업",
        "대당진동레벨(7.5m)": 36.6,
    },
    {
        "기계": "탠덤롤러",
        "동력": "75이상",
        "가동상태": "작업",
        "대당진동레벨(7.5m)": 34.6,
    },
    {
        "기계": "진동롤러",
        "동력": "75이상",
        "가동상태": "무진동작업",
        "대당진동레벨(7.5m)": 36.1,
    },
    {
        "기계": "진동롤러",
        "동력": "75이상",
        "가동상태": "진동작업",
        "대당진동레벨(7.5m)": 73.8,
    },
    {
        "기계": "타이어롤러",
        "동력": "75이상",
        "가동상태": "작업",
        "대당진동레벨(7.5m)": 26.3,
    },
    {
        "기계": "탬핑롤러",
        "동력": "75이상",
        "가동상태": "무진동작업",
        "대당진동레벨(7.5m)": 42.9,
    },
    {
        "기계": "탬핑롤러",
        "동력": "75이상",
        "가동상태": "진동작업",
        "대당진동레벨(7.5m)": 71.7,
    },
    {
        "기계": "법면다짐기",
        "동력": "180",
        "가동상태": "작업",
        "대당진동레벨(7.5m)": 66.5,
    },
    {
        "기계": "어스오거",
        "동력": "-",
        "가동상태": "작업",
        "대당진동레벨(7.5m)": 61.1,
    },
    {
        "기계": "어스오거",
        "동력": "-",
        "가동상태": "항타",
        "대당진동레벨(7.5m)": 54.7,
    },
    {
        "기계": "항타기",
        "동력": "-",
        "가동상태": "작업",
        "대당진동레벨(7.5m)": 73.9,
    },
    {
        "기계": "진동항타기",
        "동력": "-",
        "가동상태": "작업",
        "대당진동레벨(7.5m)": 67.9,
    },
    {
        "기계": "천공기",
        "동력": "-",
        "가동상태": "작업",
        "대당진동레벨(7.5m)": 48.7,
    },
    {
        "기계": "착암기",
        "동력": "-",
        "가동상태": "작업",
        "대당진동레벨(7.5m)": 44.6,
    },
    {
        "기계": "콘크리트펌프카",
        "동력": "305~340",
        "가동상태": "공회전",
        "대당진동레벨(7.5m)": 26.2,
    },
    {
        "기계": "콘크리트펌프카",
        "동력": "305~340",
        "가동상태": "작업",
        "대당진동레벨(7.5m)": 33.3,
    },
    {
        "기계": "콘크리트피니셔",
        "동력": "-",
        "가동상태": "작업",
        "대당진동레벨(7.5m)": 33.8,
    },
    {
        "기계": "아스팔트피니셔",
        "동력": "-",
        "가동상태": "작업",
        "대당진동레벨(7.5m)": 32.6,
    },
    {
        "기계": "브레이커",
        "동력": "500kg미만",
        "가동상태": "작업",
        "대당진동레벨(7.5m)": 57.9,
    },
    {
        "기계": "브레이커",
        "동력": "500kg이상",
        "가동상태": "작업",
        "대당진동레벨(7.5m)": 68.4,
    },
    {
        "기계": "크레인",
        "동력": "500kg미만",
        "가동상태": "작업",
        "대당진동레벨(7.5m)": 31.4,
    },
]

df_db = pd.DataFrame(NOISE_DB)
df_vib_db = pd.DataFrame(VIBRATION_DB)

# 세션 스테이트 관리 (타겟이 바뀌면 목록 초기화)
if "last_target" not in st.session_state:
    st.session_state.last_target = ""
if "equipment_list" not in st.session_state:
    st.session_state.equipment_list = []

# 사이드바 설정
st.sidebar.header("🎯 1단계: 산정 항목 선택")
calculation_target = st.sidebar.radio(
    "어떤 항목을 산정하시겠습니까?", ["🔊 합성소음도 산정", "📳 합성진동레벨 산정"]
)

# 산정 항목이 바뀌면 기존 입력 목록 초기화
if st.session_state.last_target != calculation_target:
    st.session_state.equipment_list = []
    st.session_state.last_target = calculation_target

st.sidebar.markdown("---")
st.sidebar.header("🛠️ 2단계: 입력 방식 선택")
input_mode = st.sidebar.radio(
    "입력 방식을 선택하세요", ["✍️ 장비 수동 선택 입력", "📁 CSV 파일 업로드"]
)

input_df = None

# 모드별 데이터베이스 소스 선택
current_db = (
    df_db if calculation_target == "🔊 합성소음도 산정" else df_vib_db
)

if input_mode == "📁 CSV 파일 업로드":
    st.sidebar.markdown("---")
    st.sidebar.subheader("CSV 파일 업로드")

    if calculation_target == "🔊 합성소음도 산정":
        st.sidebar.text("필수 컬럼: 장비명, 대수, 대당소음도(15m)")
        sample_data = pd.DataFrame([
            {"장비명": "굴착기", "대수": 1, "대당소음도(15m)": 73.4}
        ])
    else:
        st.sidebar.text("필수 컬럼: 장비명, 대수, 대당진동레벨(7.5m)")
        sample_data = pd.DataFrame([
            {"장비명": "굴착기", "대수": 1, "대당진동레벨(7.5m)": 39.9}
        ])

    sample_csv = sample_data.to_csv(index=False).encode("utf-8-sig")
    st.sidebar.download_button(
        "📥 입력용 샘플 CSV 다운로드",
        sample_csv,
        "sample_equipment_list.csv",
        "mime/csv",
    )

    uploaded_file = st.sidebar.file_uploader("CSV 파일 선택", type=["csv"])
    if uploaded_file is not None:
        try:
            try:
                input_df = pd.read_csv(uploaded_file, encoding="utf-8")
            except UnicodeDecodeError:
                uploaded_file.seek(0)
                input_df = pd.read_csv(uploaded_file, encoding="cp949")
        except Exception as e:
            st.error(f"파일 읽기 오류: {e}")

else:  # 수동 입력 모드
    st.sidebar.markdown("---")
    st.sidebar.subheader("✍️ 장비 제원 선택")

    available_machines = current_db["기계"].unique().tolist()
    selected_machine = st.sidebar.selectbox("◎ 장비명", available_machines)

    filtered_powers = current_db[current_db["기계"] == selected_machine][
        "동력"
    ].unique().tolist()
    selected_power = st.sidebar.selectbox("◎ 동력(HP)", filtered_powers)

    filtered_states = current_db[
        (current_db["기계"] == selected_machine)
        & (current_db["동력"] == selected_power)
    ]["가동상태"].unique().tolist()
    selected_state = st.sidebar.selectbox("◎ 가동상태", filtered_states)

    # 데이터베이스 매칭 값 가져오기
    matched_row = current_db[
        (current_db["기계"] == selected_machine)
        & (current_db["동력"] == selected_power)
        & (current_db["가동상태"] == selected_state)
    ]

    if calculation_target == "🔊 합성소음도 산정":
        default_val = (
            float(matched_row["대당소음도(15m)"].values[0])
            if not matched_row.empty
            else 75.0
        )
        st.sidebar.info(f"🔊 **대당소음도(15m)**: **{default_val:.1f} dB(A)**")
    else:
        default_val = (
            float(matched_row["대당진동레벨(7.5m)"].values[0])
            if not matched_row.empty
            else 50.0
        )
        st.sidebar.info(
            f"📳 **대당진동레벨(7.5m)**: **{default_val:.1f} dB(V)**"
        )

    eq_count = st.sidebar.number_input(
        "투입 대수 [대]", min_value=1, value=1, step=1
    )

    col_s1, col_s2 = st.sidebar.columns(2)
    with col_s1:
        if st.button("➕ 목록에 추가", use_container_width=True):
            eq_name_full = (
                f"{selected_machine} ({selected_power}, {selected_state})"
            )
            item_dict = {"장비명": eq_name_full, "대수": eq_count}
            if calculation_target == "🔊 합성소음도 산정":
                item_dict["대당소음도(15m)"] = default_val
            else:
                item_dict["대당진동레벨(7.5m)"] = default_val

            st.session_state.equipment_list.append(item_dict)
            st.rerun()

    with col_s2:
        if st.button("🗑️ 전체 초기화", use_container_width=True):
            st.session_state.equipment_list = []
            st.rerun()

    if len(st.session_state.equipment_list) > 0:
        input_df = pd.DataFrame(st.session_state.equipment_list)

# 메인 화면 구성
if input_df is None or len(input_df) == 0:
    st.info(
        "👈 왼쪽 사이드바에서 산정 항목을 고르신 후 장비를 추가해 주세요."
    )
else:
    try:
        df = input_df.copy()
        total_synthesized = 0.0

        if calculation_target == "🔊 합성소음도 산정":
            if "대당소음도(15m)" not in df.columns:
                st.error("🚨 필수 컬럼 `대당소음도(15m)`가 누락되었습니다.")
                st.stop()
            vals = df["대당소음도(15m)"].values
            counts = df["대수"].values
            energy = counts * (10 ** (0.1 * vals))
            sum_energy = np.sum(energy)
            total_synthesized = (
                10 * np.log10(sum_energy) if sum_energy > 0 else 0.0
            )
        else:
            if "대당진동레벨(7.5m)" not in df.columns:
                st.error("🚨 필수 컬럼 `대당진동레벨(7.5m)`가 누락되었습니다.")
                st.stop()
            vals = df["대당진동레벨(7.5m)"].values
            counts = df["대수"].values
            energy = counts * (10 ** (0.1 * vals))
            sum_energy = np.sum(energy)
            total_synthesized = (
                10 * np.log10(sum_energy) if sum_energy > 0 else 0.0
            )

        st.subheader("📊 장비 영향 예측 산정 내역")

        # HTML 테이블 동적 생성
        html_code = """
        <style>
            .res-table {
                width: 100%;
                border-collapse: collapse;
                font-family: inherit;
                font-size: 14px;
                color: #fafafa;
                background-color: #0e1117;
                margin-bottom: 1rem;
            }
            .res-table th, .res-table td {
                border: 1px solid #303030;
                padding: 10px 12px;
                text-align: center;
            }
            .res-table th {
                background-color: #262730;
                font-weight: 600;
            }
            .res-table td {
                background-color: #0e1117;
            }
        </style>
        <table class="res-table">
            <thead>
                <tr>
                    <th>장비명</th>
                    <th>대수 [대]</th>
        """

        if calculation_target == "🔊 합성소음도 산정":
            html_code += "<th>대당소음도(15m) [dB(A)]</th>"
            html_code += "<th>최종 합성소음도 (L₀) [dB(A)]</th>"
        else:
            html_code += "<th>대당진동레벨(7.5m) [dB(V)]</th>"
            html_code += "<th>최종 합성진동레벨 (7.5m) [dB(V)]</th>"

        html_code += "</tr></thead><tbody>"

        num_rows = len(df)
        for i, row in df.iterrows():
            name = row["장비명"]
            count = int(row["대수"])

            html_code += "<tr>"
            html_code += f"<td>{name}</td>"
            html_code += f"<td>{count}대</td>"

            if calculation_target == "🔊 합성소음도 산정":
                val_std = row["대당소음도(15m)"]
                html_code += f"<td>{val_std:.1f}</td>"
                if i == 0:
                    html_code += f'<td rowspan="{num_rows}" style="vertical-align: middle; font-weight: bold; font-size: 16px; color: #ff4b4b;">{total_synthesized:.1f}</td>'
            else:
                val_std = row["대당진동레벨(7.5m)"]
                html_code += f"<td>{val_std:.1f}</td>"
                if i == 0:
                    html_code += f'<td rowspan="{num_rows}" style="vertical-align: middle; font-weight: bold; font-size: 16px; color: #4b9fff;">{total_synthesized:.1f}</td>'

            html_code += "</tr>"

        html_code += "</tbody></table>"
        st.markdown(html_code, unsafe_allow_html=True)

        # 산정 공식 안내
        st.markdown("---")
        st.markdown("### 📐 적용된 산정 공식")
        if calculation_target == "🔊 합성소음도 산정":
            formula_title = "합성소음도 산출공식"
            formula_desc = "L₀ = 10 · log ( A · 10<sup>X₁/10</sup> + B · 10<sup>X₂/10</sup> + …… + N · 10<sup>Xₙ/10</sup> )"
            var_desc = "<b>L₀</b> : 합성소음도 [dB(A)]"
        else:
            formula_title = (
                "합성진동레벨 산출공식"
            )
            formula_desc = "V₀ = 10 · log ( A · 10<sup>X₁/10</sup> + B · 10<sup>X₂/10</sup> + …… + N · 10<sup>Xₙ/10</sup> )"
            var_desc = "<b>V₀</b> : 합성진동레벨 [dB(V)]"

        st.markdown(
            f"""
            <div style="background-color: #1e2530; padding: 18px 22px; border-radius: 8px; border-left: 5px solid #ff4b4b; font-size: 16px; line-height: 1.9; color: #fafafa;">
                <b>■ {formula_title}</b><br>
                &nbsp;&nbsp;&nbsp;&nbsp;<b>{formula_desc}</b><br><br>
                <b>여기서,</b> &nbsp; {var_desc}<br>
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>A, B, ……, N</b> : 각 장비의 투입대수<br>
                &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>X₁,₂,……,ₙ</b> : 각 장비별 개별 소음도
            </div
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # 결과 다운로드 버튼
        download_df = df[["장비명", "대수"]].copy()
        if calculation_target == "🔊 합성소음도 산정":
            download_df["대당소음도(15m)"] = df["대당소음도(15m)"]
            download_df["최종합성소음도(L0)"] = round(total_synthesized, 1)
        else:
            download_df["대당진동레벨(7.5m)"] = df["대당진동레벨(7.5m)"]
            download_df["최종합성진동레벨(7.5m)"] = round(
                total_synthesized, 1
            )

        csv_result = download_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="📥 최종 산정 결과 보고서 다운로드 (CSV)",
            data=csv_result,
            file_name="environmental_prediction_result.csv",
            mime="text/csv",
        )

    except Exception as e:
        st.error(f"🚨 처리 중 오류가 발생했습니다: {e}")

# 제작자 푸터
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #BFBFBF; font-size: 14px; padding: 10px;'>"
    "<b>제작자:</b> (주)내경엔지니어링 박은정 과장"
    "</div>",
    unsafe_allow_html=True,
)
