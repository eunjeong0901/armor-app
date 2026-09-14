import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="공사장비 운용 시 소음·진동 영향 예측 프로그램", layout="wide"
)

# 세션 스테이트 초기화
if "sound_facilities" not in st.session_state:
    st.session_state.sound_facilities = []
if "vibration_facilities" not in st.session_state:
    st.session_state.vibration_facilities = []

# ==========================================
# 🛠️ 사이드바 (왼쪽 입력창 구성)
# ==========================================
st.sidebar.markdown(
    "🎯 **1단계 : 산정 항목 선택**\n\n어떤 항목을 산정하시겠습니까?"
)
calc_category = st.sidebar.radio(
    "산정 항목",
    ["🔊 소음 영향 예측", "📳 진동 영향 예측"],
    label_visibility="collapsed",
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "🛠️ **2단계 : 입력 방식 선택**\n\n입력 방식을 선택하세요"
)
input_mode = st.sidebar.radio(
    "입력 방식",
    ["🚜 정온시설 수동 입력", "📁 CSV 파일 업로드"],
    label_visibility="collapsed",
)

st.sidebar.markdown("---")

# 🔊 소음 선택 시 사이드바 구성
if calc_category == "🔊 소음 영향 예측":
    st.sidebar.markdown("🐋 **3단계 : 합성소음도(SPL₀) 입력**")
    spl0 = st.sidebar.number_input(
        "◎ 합성소음도[dB(A)]", value=80.0, step=0.1, format="%.1f"
    )
    base_dist_s = 15.0  # 소음 기준거리 15m

    st.sidebar.markdown("---")

    if input_mode == "🚜 정온시설 수동 입력":
        st.sidebar.markdown("📍 **4단계 : 정온시설 입력**")
        fac_name = st.sidebar.text_input(
            "◎ 정온시설 명칭", value="", placeholder="예 : A주택", key="s_name"
        )
        facility_categories = ["주거시설", "교육시설", "사육시설", "기타"]
        selected_fac_type = st.sidebar.selectbox(
            "◎ 시설구분", facility_categories, key="new_fac_type"
        )

        if selected_fac_type == "기타":
            custom_fac_type = st.sidebar.text_input(
                "기타 시설구분 직접 입력", value="상업시설", key="new_custom_type"
            )
            final_fac_type = custom_fac_type
        else:
            final_fac_type = selected_fac_type

        fac_distance = st.sidebar.number_input(
            "◎ 이격거리(m)", min_value=1.0, value=50.0, step=1.0, key="new_dist"
        )

        if selected_fac_type == "주거시설":
            auto_target = 65.0
        elif selected_fac_type == "교육시설":
            auto_target = 55.0
        elif selected_fac_type == "사육시설":
            auto_target = 60.0
        else:
            auto_target = 65.0

        if selected_fac_type == "기타":
            fac_target = st.sidebar.number_input(
                "소음목표기준 [dB(A)] (기타 직접 입력)",
                value=auto_target,
                step=0.5,
                format="%.1f",
                key="new_target_custom",
            )
        else:
            fac_target = auto_target
            st.sidebar.info(
                f"소음목표기준 [dB(A)]: **{fac_target:.1f}** (자동 적용)"
            )

        col_b1, col_b2 = st.sidebar.columns(2)
        with col_b1:
            if st.button("➕ 정온시설 추가", use_container_width=True):
                if fac_name.strip() == "":
                    st.sidebar.error("정온시설 명칭을 입력해주세요.")
                else:
                    st.session_state.sound_facilities.append({
                        "정온시설 명칭": fac_name,
                        "시설구분": final_fac_type,
                        "이격거리(m)": fac_distance,
                        "소음목표기준": fac_target,
                    })
                    st.rerun()
        with col_b2:
            if st.button("🗑️ 전체 초기화", use_container_width=True):
                st.session_state.sound_facilities = []
                st.rerun()

    else:
        st.sidebar.markdown("📁 **4단계 : CSV 파일 일괄 파일 일괄 업로드**")
        sample_df = pd.DataFrame({
            "정온시설 명칭": ["A주택", "B초등학교", "C농장", "D상가"],
            "시설구분": ["주거시설", "교육시설", "사육시설", "기타"],
            "이격거리(m)": [50.0, 35.0, 40.0, 60.0],
            "소음목표기준": [65.0, 55.0, 60.0, 70.0],
        })
        sample_csv = sample_df.to_csv(index=False).encode("utf-8-sig")

        st.sidebar.download_button(
            label="📥 샘플 CSV 파일 다운로드",
            data=sample_csv,
            file_name="소음영향_입력_샘플.csv",
            mime="text/csv",
            use_container_width=True,
        )

        uploaded_file = st.sidebar.file_uploader(
            "정온시설 목록 CSV 파일 업로드", type=["csv"], key="s_upload"
        )

        if uploaded_file is not None:
            try:
                df_uploaded = pd.read_csv(uploaded_file, encoding="utf-8-sig")
            except:
                uploaded_file.seek(0)
                df_uploaded = pd.read_csv(uploaded_file, encoding="cp949")

            required_cols = [
                "정온시설 명칭",
                "시설구분",
                "이격거리(m)",
                "소음목표기준",
            ]
            if all(col in df_uploaded.columns for col in required_cols):
                if st.sidebar.button(
                    "📂 업로드 데이터 적용하기", use_container_width=True
                ):
                    st.session_state.sound_facilities = []
                    for _, row in df_uploaded.iterrows():
                        f_type = str(row["시설구분"]).strip()
                        f_dist = float(row["이격거리(m)"])

                        if f_type == "주거시설":
                            f_target = 65.0
                        elif f_type == "교육시설":
                            f_target = 55.0
                        elif f_type == "사육시설":
                            f_target = 60.0
                        else:
                            val = row["소음목표기준"]
                            f_target = float(val) if pd.notna(val) else 65.0

                        st.session_state.sound_facilities.append({
                            "정온시설 명칭": str(row["정온시설 명칭"]),
                            "시설구분": f_type,
                            "이격거리(m)": f_dist,
                            "소음목표기준": f_target,
                        })
                    st.sidebar.success("데이터가 성공적으로 불러와졌습니다!")
                    st.rerun()
            else:
                st.sidebar.error("CSV 파일 양식이 올바르지 않습니다.")

        if st.sidebar.button("🗑️ 전체 초기화", use_container_width=True):
            st.session_state.sound_facilities = []
            st.rerun()

# 📳 진동 선택 시 사이드바 구성
else:
    st.sidebar.markdown("🐋 **3단계 : 합성진동레벨(VL₀) 입력**")
    vl0 = st.sidebar.number_input(
        "◎ 합성진동레벨[dB(V)]", value=65.0, step=0.1, format="%.1f"
    )
    base_dist_v = 7.5  # 진동 기준거리 7.5m

    st.sidebar.markdown("---")

    if input_mode == "🚜 정온시설 수동 입력":
        st.sidebar.markdown("📍 **4단계 : 정온시설 입력**")
        v_fac_name = st.sidebar.text_input(
            "◎ 정온시설 명칭", value="", placeholder="예 : A주택", key="v_name"
        )
        v_facility_categories = ["주거시설", "교육시설", "사육시설", "기타"]
        v_selected_fac_type = st.sidebar.selectbox(
            "◎ 시설구분", v_facility_categories, key="v_fac_type"
        )

        if v_selected_fac_type == "기타":
            v_custom_fac_type = st.sidebar.text_input(
                "기타 시설구분 직접 입력",
                value="상업시설",
                key="v_custom_type",
            )
            v_final_fac_type = v_custom_fac_type
        else:
            v_final_fac_type = v_selected_fac_type

        v_fac_distance = st.sidebar.number_input(
            "◎ 이격거리(m)", min_value=1.0, value=30.0, step=1.0, key="v_dist"
        )

        if v_selected_fac_type == "주거시설":
            v_auto_target = 65.0
        elif v_selected_fac_type == "교육시설":
            v_auto_target = 65.0
        else:
            v_auto_target = 57.0

        if v_selected_fac_type == "기타":
            v_fac_target = st.sidebar.number_input(
                "진동목표기준 [dB(V)] (기타 직접 입력)",
                value=v_auto_target,
                step=0.5,
                format="%.1f",
                key="v_target_custom",
            )
        else:
            v_fac_target = v_auto_target
            st.sidebar.info(
                f"진동목표기준 [dB(V)]: **{v_fac_target:.1f}** (자동 적용)"
            )

        col_vb1, col_vb2 = st.sidebar.columns(2)
        with col_vb1:
            if st.button("➕ 정온시설 추가", use_container_width=True, key="v_add"):
                if v_fac_name.strip() == "":
                    st.sidebar.error("정온시설 명칭을 입력해주세요.")
                else:
                    st.session_state.vibration_facilities.append({
                        "정온시설 명칭": v_fac_name,
                        "시설구분": v_final_fac_type,
                        "이격거리(m)": v_fac_distance,
                        "진동목표기준": v_fac_target,
                    })
                    st.rerun()
        with col_vb2:
            if st.button(
                "🗑️ 전체 초기화", use_container_width=True, key="v_reset"
            ):
                st.session_state.vibration_facilities = []
                st.rerun()

    else:
        st.sidebar.markdown(" 📁 **4단계 : CSV 파일 일괄 업로드**")
        v_sample_df = pd.DataFrame({
            "정온시설 명칭": ["A주택", "B초등학교", "C농장"],
            "시설구분": ["주거시설", "교육시설", "사육시설"],
            "이격거리(m)": [30.0, 20.0, 50.0],
            "진동목표기준": [65.0, 65.0, 57.0],
        })
        v_sample_csv = v_sample_df.to_csv(index=False).encode("utf-8-sig")

        st.sidebar.download_button(
            label="📥 샘플 CSV 파일 다운로드",
            data=v_sample_csv,
            file_name="진동영향_입력_샘플.csv",
            mime="text/csv",
            use_container_width=True,
            key="v_down",
        )

        v_uploaded_file = st.sidebar.file_uploader(
            "정온시설 목록 CSV 파일 업로드", type=["csv"], key="v_file_up"
        )

        if v_uploaded_file is not None:
            try:
                v_df_uploaded = pd.read_csv(
                    v_uploaded_file, encoding="utf-8-sig"
                )
            except:
                v_uploaded_file.seek(0)
                v_df_uploaded = pd.read_csv(
                    v_uploaded_file, encoding="cp949"
                )

            v_required_cols = [
                "정온시설 명칭",
                "시설구분",
                "이격거리(m)",
                "진동목표기준",
            ]
            if all(col in v_df_uploaded.columns for col in v_required_cols):
                if st.sidebar.button(
                    "📂 업로드 데이터 적용하기",
                    use_container_width=True,
                    key="v_apply",
                ):
                    st.session_state.vibration_facilities = []
                    for _, row in v_df_uploaded.iterrows():
                        f_type = str(row["시설구분"]).strip()
                        f_dist = float(row["이격거리(m)"])

                        if f_type == "주거시설":
                            f_target = 65.0
                        elif f_type == "상업/공공시설":
                            f_target = 70.0
                        else:
                            val = row["진동목표기준"]
                            f_target = float(val) if pd.notna(val) else 65.0

                        st.session_state.vibration_facilities.append({
                            "정온시설 명칭": str(row["정온시설 명칭"]),
                            "시설구분": f_type,
                            "이격거리(m)": f_dist,
                            "진동목표기준": f_target,
                        })
                    st.sidebar.success("데이터가 성공적으로 불러와졌습니다!")
                    st.rerun()
            else:
                st.sidebar.error("CSV 파일 양식이 올바르지 않습니다.")

        if st.sidebar.button(
            "🗑️ 전체 초기화", use_container_width=True, key="v_reset_all"
        ):
            st.session_state.vibration_facilities = []
            st.rerun()


# ==========================================
# 🖥️ 메인 화면 (오른쪽 결과창 구성)
# ==========================================
st.title("🏗️ 공사장비 운용 시 소음·진동 영향 예측 프로그램")
st.markdown(
    "거리감쇠식을 바탕으로 정온시설별 예측값 및 만족 여부를 산정합니다."
)
st.markdown("---")

# 🔊 소음 결과 화면 출력
if calc_category == "🔊 소음 영향 예측":
    st.subheader("🔊 정온시설별 소음 영향 예측 결과")
    st.markdown(f"◎ 현재 적용된 **합성소음도(SPL₀)** : **{spl0:.1f} dB(A)**")
    st.markdown(
        "◎ 소음 거리감쇠 공식 : $SPL = SPL_0 - 20 · Log(r / r_0)$"
    )
    st.markdown(f"- SPL : 점음원 거리감쇠식으로 예측한 소음도[dB(A)]")
    st.markdown(f"- SPL$_0$ : 소음원으로부터 기준지점(r$_0$=15m)에서의 소음도[dB(A)]")
    st.markdown(f"- r : 소음원에서 정온시설까지의 거리(m)")
    st.markdown(f"- r$_0$ : 소음원에서 기준지점까지의 거리(15m)")

    if len(st.session_state.sound_facilities) == 0:
        st.info("👈 왼쪽 사이드바에서 산정 항목을 고르신 후 정온시설 정보를 추가해주세요.")
    else:
        sound_results = []
        for idx, row in enumerate(st.session_state.sound_facilities):
            name = row["정온시설 명칭"]
            category = row["시설구분"]
            r = row["이격거리(m)"]
            target = row["소음목표기준"]

            if r > 0:
                pred = spl0 - 20 * np.log10(r / base_dist_s)
                status = "✅ 만족" if pred <= target else "❌ 초과"
            else:
                pred = 0.0
                status = "거리 오류"

            sound_results.append({
                "No": idx + 1,
                "정온시설 명칭": name,
                "시설구분": category,
                "이격거리(m)": r,
                "소음목표기준": target,
                "예측소음도(SPL)[dB(A)]": round(pred, 1),
                "만족여부": status,
            })

        res_df = pd.DataFrame(sound_results)
        st.markdown("### 📊 최종 결과값 (출력창)")
        st.dataframe(res_df, use_container_width=True, hide_index=True)

        csv_data = res_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="📥 최종 결과 파일로 다운로드 (CSV)",
            data=csv_data,
            file_name="소음영향예측결과.csv",
            mime="text/csv",
            use_container_width=True,
        )

        st.markdown("---")
        st.markdown("### 🛠️ 등록된 정온시설 수정 및 관리")

        selected_edit_idx = st.selectbox(
            "수정 또는 삭제할 정온시설 선택",
            options=range(len(st.session_state.sound_facilities)),
            format_func=lambda x: (
                f"{x+1}. {st.session_state.sound_facilities[x]['정온시설 명칭']}"
                f" ({st.session_state.sound_facilities[x]['시설구분']})"
            ),
        )

        current_item = st.session_state.sound_facilities[selected_edit_idx]

        with st.form("edit_form"):
            st.markdown(f"**[{current_item['정온시설 명칭']}] 정보 수정**")
            e_name = st.text_input(
                "정온시설 명칭 수정", value=current_item["정온시설 명칭"]
            )
            base_types = ["주거시설", "교육시설", "사육시설", "기타"]
            initial_type = current_item["시설구분"]
            default_type_idx = (
                base_types.index(initial_type)
                if initial_type in base_types
                else 3
            )
            e_type_select = st.selectbox(
                "시설구분 수정", base_types, index=default_type_idx
            )

            if e_type_select == "기타":
                e_custom_type = st.text_input(
                    "기타 시설구분 직접 입력",
                    value=(
                        initial_type
                        if initial_type not in base_types
                        else "상업시설"
                    ),
                )
                e_final_type = e_custom_type
                e_target = st.number_input(
                    "소음목표기준 [dB(A)] 수정",
                    value=float(current_item["소음목표기준"]),
                    step=0.5,
                    format="%.1f",
                )
            else:
                e_final_type = e_type_select
                if e_type_select == "주거시설":
                    e_target = 65.0
                elif e_type_select == "교육시설":
                    e_target = 55.0
                elif e_type_select == "사육시설":
                    e_target = 60.0
                st.info(f"연동된 소음목표기준: **{e_target:.1f} dB(A)**")

            e_dist = st.number_input(
                "이격거리 (m) 수정",
                min_value=1.0,
                value=float(current_item["이격거리(m)"]),
                step=1.0,
            )

            col_e1, col_e2 = st.columns(2)
            with col_e1:
                submit_update = st.form_submit_button(
                    "💾 수정 사항 저장", use_container_width=True
                )
            with col_e2:
                submit_delete = st.form_submit_button(
                    "🗑️ 해당 정온시설 삭제", use_container_width=True
                )

            if submit_update:
                st.session_state.sound_facilities[selected_edit_idx] = {
                    "정온시설 명칭": e_name,
                    "시설구분": e_final_type,
                    "이격거리(m)": e_dist,
                    "소음목표기준": e_target,
                }
                st.success("성공적으로 수정되었습니다!")
                st.rerun()

            if submit_delete:
                st.session_state.sound_facilities.pop(selected_edit_idx)
                st.warning("해당 정온시설이 삭제되었습니다.")
                st.rerun()

# 📳 진동 결과 화면 출력
else:
    st.subheader("📳 정온시설별 진동 영향 예측 결과")
    st.markdown(
        f"◎ 현재 적용된 **합성진동레벨(VL₀)** : **{vl0:.1f} dB(V)**"
    )
    # 진동 거리감쇠식 수정 반영 ($VL = VL_0 - 20 · n · Log(r / r_0)$)
    st.markdown(
        "◎ 진동 거리감쇠 공식 : $VL = VL_0 - 20 · Log(r / r_0)^n$"
    )
    st.markdown(f"- VL : 진동원 거리감쇠식으로 예측한 진동레벨[dB(V)]")
    st.markdown(f"- VL$_0$ : 진동원으로부터 기준지점(r$_0$=7.5m)에서의 진동레벨[dB(V)]")
    st.markdown(f"- r : 진동원에서 정온시설까지의 거리(m)")
    st.markdown(f"- r$_0$ : 진동원에서 기준지점까지의 거리(7.5m)")
    st.markdown(f"- n : 기하감쇠정수(0.35∼1.8) → 건설장비 평균 0.81 적용")

    if len(st.session_state.vibration_facilities) == 0:
        st.info("👈 왼쪽 사이드바에서 산정 항목을 고르신 후 정온시설 정보를 추가해주세요.")
    else:
        v_results = []
        n_factor = 0.81  # 건설장비 평균 기하감쇠정수
        for idx, row in enumerate(st.session_state.vibration_facilities):
            name = row["정온시설 명칭"]
            category = row["시설구분"]
            r = row["이격거리(m)"]
            target = row["진동목표기준"]

            if r > 0:
                # 수정된 공식 반영: VL = VL0 - 20 * n * log10(r / 7.5)
                pred_v = vl0 - 20 * n_factor * np.log10(r / base_dist_v)
                v_status = "✅ 만족" if pred_v <= target else "❌ 초과"
            else:
                pred_v = 0.0
                v_status = "거리 오류"

            v_results.append({
                "No": idx + 1,
                "정온시설 명칭": name,
                "시설구분": category,
                "이격거리(m)": r,
                "진동목표기준": target,
                "예측진동레벨(VL)[dB(V)]": round(pred_v, 1),
                "만족여부": v_status,
            })

        v_res_df = pd.DataFrame(v_results)
        st.markdown("### 📊 진동 최종 결과값 (출력창)")
        st.dataframe(v_res_df, use_container_width=True, hide_index=True)

        v_csv_data = v_res_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label="📥 진동 결과 파일로 다운로드 (CSV)",
            data=v_csv_data,
            file_name="진동영향예측결과.csv",
            mime="text/csv",
            use_container_width=True,
        )

        st.markdown("---")
        st.markdown("### 🛠️ 등록된 진동 정온시설 수정 및 관리")

        v_edit_idx = st.selectbox(
            "수정 또는 삭제할 진동 정온시설 선택",
            options=range(len(st.session_state.vibration_facilities)),
            format_func=lambda x: (
                f"{x+1}. {st.session_state.vibration_facilities[x]['정온시설 명칭']}"
                f" ({st.session_state.vibration_facilities[x]['시설구분']})"
            ),
            key="v_edit_select",
        )

        v_current_item = st.session_state.vibration_facilities[v_edit_idx]

        with st.form("v_edit_form"):
            st.markdown(f"**[{v_current_item['정온시설 명칭']}] 정보 수정**")
            ve_name = st.text_input(
                "정온시설 명칭 수정", value=v_current_item["정온시설 명칭"]
            )
            v_base_types = ["주거시설", "교육시설", "사육시설", "기타"]
            v_init_type = v_current_item["시설구분"]
            v_default_idx = (
                v_base_types.index(v_init_type)
                if v_init_type in v_base_types
                else 2
            )
            ve_type_select = st.selectbox(
                "시설구분 수정", v_base_types, index=v_default_idx
            )

            if ve_type_select == "기타":
                ve_custom_type = st.text_input(
                    "기타 시설구분 직접 입력",
                    value=(
                        v_init_type
                        if v_init_type not in v_base_types
                        else "상업시설"
                    ),
                )
                ve_final_type = ve_custom_type
                ve_target = st.number_input(
                    "진동목표기준 [dB(V)] 수정",
                    value=float(v_current_item["진동목표기준"]),
                    step=0.5,
                    format="%.1f",
                )
            else:
                ve_final_type = ve_type_select
                if ve_type_select == "주거시설":
                    ve_target = 65.0
                elif ve_type_select == "교육시설":
                    ve_target = 65.0
                elif ve_type_select == "사육시설":
                    ve_target = 57.0
                st.info(f"연동된 진동목표기준: **{ve_target:.1f} dB(V)**")

            ve_dist = st.number_input(
                "이격거리 (m) 수정",
                min_value=1.0,
                value=float(v_current_item["이격거리(m)"]),
                step=1.0,
            )

            col_ve1, col_ve2 = st.columns(2)
            with col_ve1:
                ve_submit_update = st.form_submit_button(
                    "💾 수정 사항 저장", use_container_width=True
                )
            with col_ve2:
                ve_submit_delete = st.form_submit_button(
                    "🗑️ 해당 정온시설 삭제", use_container_width=True
                )

            if ve_submit_update:
                st.session_state.vibration_facilities[v_edit_idx] = {
                    "정온시설 명칭": ve_name,
                    "시설구분": ve_final_type,
                    "이격거리(m)": ve_dist,
                    "진동목표기준": ve_target,
                }
                st.success("성공적으로 수정되었습니다!")
                st.rerun()

            if ve_submit_delete:
                st.session_state.vibration_facilities.pop(v_edit_idx)
                st.warning("해당 정온시설이 삭제되었습니다.")
                st.rerun()

# 📌 푸터 추가
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #ffffff; font-size: 14px;"
    " padding: 10px;'><b>제작자 :</b> (주)내경엔지니어링 박은정 과장</div>",
    unsafe_allow_html=True,
)
