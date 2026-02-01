import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ページ設定（未使用UI①）
st.set_page_config(page_title="都道府県別人口動態",
                layout="wide")

st.title("都道府県別人口動態")
st.caption("出典：e-Stat 人口推計（表番号 25-01）")

# CSV読み込み
csv_file = "2501stjin.csv"

if not os.path.exists(csv_file):
    st.error(f"{csv_file} が見つかりません。パスを確認してください。")
else:
    df = pd.read_csv(csv_file, encoding="cp932")
    df.columns = df.columns.str.strip()
    df = df[df["都道府県名"] != "合計"]
    df["都道府県名"] = df["都道府県名"].astype(str).str.strip()
    
    # サイドバー
    with st.sidebar:
        st.header("抽出条件")

        # 都道府県選択
        prefectures = st.multiselect("都道府県を選択（複数可）",
                                sorted(df["都道府県名"].unique()),default=["東京都", "大阪府"])

        # 人口種別選択（未使用UI②）
        population_col = st.select_slider("人口区分を選択",
                                        options=[
                                            "2025年人口（男）",
                                            "2025年人口（女）",
                                            "2025年人口（計）",
                                            "2025年世帯数",
                                            "2024年転入者数（国内）",
                                            "2024年転入者数（国外）",
                                            "2024年転入者数（計）",
                                            "2024年出生者数",
                                            "2024年転出者数（国内）",
                                            "2024年転出者数（国外）",
                                            "2024年転出者数（計）",
                                            "2024年死亡者数"
                                        ],
                                        value="2025年人口（計）")

    # データ抽出
    filtered_df = df[df["都道府県名"].isin(prefectures)].copy()

    if filtered_df.empty:
        st.warning("条件に一致するデータがありません")
    else:
        # 数値化
        filtered_df[population_col] = pd.to_numeric(
            filtered_df[population_col], errors="coerce")

        # 並び替え（人口順）
        filtered_df_sorted = filtered_df.sort_values(population_col, ascending=False)


        # 単位の自動切り替え
        if "2025年世帯数" in population_col:
            unit = "世帯数（世帯）"
        else:
            unit = "人口（人）"


        # タブ表示（未使用UI③）
        tab1, tab2, tab3 = st.tabs(["📊横棒グラフ", "📈縦棒グラフ", "📋データと解説"])

        # 横棒グラフ（人口順）
        with tab1:
            st.subheader(f"都道府県別 {population_col}（人口順）")
            fig1 = px.bar(filtered_df_sorted,
                x=population_col,
                y="都道府県名",
                orientation="h",
                labels={population_col: f"{unit}", "都道府県名": "都道府県"},
                text=population_col)
            fig1.update_traces(texttemplate="%{text:,}", textposition="outside")
            fig1.update_layout(yaxis={"categoryorder": "total ascending"}, margin=dict(l=100, r=40, t=40, b=40))
            st.plotly_chart(fig1, use_container_width=True)
            st.write("※「k」は1,000（千）を表し、「M」は1,000,000（百万）を表す")

        # 縦棒グラフ（人口順）
        with tab2:
            st.subheader(f"都道府県別 {population_col}（人口順）")
            fig2 = px.bar(filtered_df_sorted,
                x="都道府県名",
                y=population_col,
                labels={population_col: f"{unit}", "都道府県名": "都道府県"},
                text=population_col)
            fig2.update_traces(texttemplate="%{text:,}", textposition="outside")
            fig2.update_layout(xaxis_tickangle=-45, margin=dict(l=40, r=40, t=40, b=150))
            st.plotly_chart(fig2, use_container_width=True)
            st.write("※「k」は1,000（千）を表し、「M」は1,000,000（百万）を表す")



        # データ表と簡単解説
        with tab3:
            st.subheader("データ一覧")
            st.dataframe(filtered_df_sorted.reset_index(drop=True))

            st.markdown("---")
            st.subheader("簡単な解説")
            max_pop = filtered_df_sorted[population_col].max()
            min_pop = filtered_df_sorted[population_col].min()
            max_pref = filtered_df_sorted.loc[filtered_df_sorted[population_col] == max_pop, "都道府県名"].values[0]
            min_pref = filtered_df_sorted.loc[filtered_df_sorted[population_col] == min_pop, "都道府県名"].values[0]
            st.write(f"- 選択した都道府県の中で人口が最も多いのは **{max_pref}**（{max_pop:,}人）")
            st.write(f"- 選択した都道府県の中で人口が最も少ないのは **{min_pref}**（{min_pop:,}人）")
            st.write("- グラフを見ると、人口の多い都道府県と少ない都道府県の差が一目で分かる。")