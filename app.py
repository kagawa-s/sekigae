import streamlit as st
import pandas as pd
import random
import os
import requests
from PIL import Image, ImageDraw, ImageFont
import io

# --- 1. フォント取得（文字化け対策） ---
def get_japanese_font(size=24):
    font_path = "NotoSansJP-Regular.otf"
    if not os.path.exists(font_path):
        url = "https://github.com/googlefonts/noto-cjk/raw/main/Sans/SubsetOTF/JP/NotoSansJP-Regular.otf"
        try:
            r = requests.get(url)
            with open(font_path, "wb") as f:
                f.write(r.content)
        except:
            return ImageFont.load_default()
    return ImageFont.truetype(font_path, size)

# --- 2. A4サイズ画像生成 ---
def create_a4_chart(seating_dict, num_cols):
    # A4比率（300dpi相当）
    width, height = 2480, 3508
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    
    font_title = get_japanese_font(120)
    font_name = get_japanese_font(60)

    draw.text((width//2 - 300, 200), "座席配置図", fill="black", font=font_title)

    # レイアウト計算
    margin = 200
    cell_w = (width - margin * 2) // num_cols
    cell_h = 200
    
    for idx, name in seating_dict.items():
        r = idx // num_cols
        c = idx % num_cols
        x = margin + c * cell_w
        y = 500 + r * (cell_h + 50)
        
        draw.rectangle([x, y, x + cell_w - 40, y + cell_h], outline="blue", width=5)
        draw.text((x + 20, y + 60), f"{idx+1}: {name}", fill="black", font=font_name)
    
    return image

# --- 3. メインアプリ ---
def main():
    st.set_page_config(page_title="席替えシステム", layout="wide")
    st.title("🪑 席替え詳細設定システム")

    # セッション状態の初期化
    if 'names' not in st.session_state:
        st.session_state.names = []
    if 'fixed' not in st.session_state:
        st.session_state.fixed = {} # {index: name}

    # サイドバー：設定
    st.sidebar.header("基本設定")
    num_cols = st.sidebar.number_input("列数を指定", min_value=1, max_value=10, value=4)
    uploaded_file = st.sidebar.file_uploader("名簿アップロード", type=['xlsx', 'csv'])

    if uploaded_file:
        df = pd.read_excel(uploaded_file, header=None) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file, header=None)
        st.session_state.names = df[0].dropna().tolist()

    if st.session_state.names:
        st.subheader("座席の固定・入れ替え設定")
        
        # 現在の座席リスト（固定を考慮）
        current_seats = list(st.session_state.names)
        
        cols = st.columns(num_cols)
        for i, name in enumerate(current_seats):
            with cols[i % num_cols]:
                is_fixed = st.checkbox(f"固定 ({i+1})", key=f"fix_{i}")
                if is_fixed:
                    st.session_state.fixed[i] = name
                elif i in st.session_state.fixed:
                    del st.session_state.fixed[i]
                st.write(f"**{name}**")

        if st.button("席替え実行！"):
            # シャッフル（固定以外）
            fixed_indices = st.session_state.fixed.keys()
            flexible_names = [n for i, n in enumerate(current_seats) if i not in fixed_indices]
            random.shuffle(flexible_names)
            
            result = {}
            flex_idx = 0
            for i in range(len(current_seats)):
                if i in st.session_state.fixed:
                    result[i] = st.session_state.fixed[i]
                else:
                    result[i] = flexible_names[flex_idx]
                    flex_idx += 1
            
            st.session_state.result = result
            st.success("シャッフル完了")

        if 'result' in st.session_state:
            chart_img = create_a4_chart(st.session_state.result, num_cols)
            st.image(chart_img, use_container_width=True)

            # A4画像ダウンロード
            buf = io.BytesIO()
            chart_img.save(buf, format="PNG")
            st.download_button("A4サイズ画像を保存", buf.getvalue(), "seat_a4.png", "image/png")

if __name__ == "__main__":
    main()
