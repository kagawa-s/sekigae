import streamlit as st
import pandas as pd
import random
import os
import requests
from PIL import Image, ImageDraw, ImageFont
import io

# --- 1. 日本語フォントをサーバーに用意する関数 ---
def get_japanese_font(size=24):
    # サーバー上の保存先
    font_path = "NotoSansJP-Regular.otf"
    
    # フォントがなければGoogleからダウンロード（初回のみ）
    if not os.path.exists(font_path):
        url = "https://github.com/googlefonts/noto-cjk/raw/main/Sans/SubsetOTF/JP/NotoSansJP-Regular.otf"
        try:
            response = requests.get(url)
            with open(font_path, "wb") as f:
                f.write(response.content)
        except Exception as e:
            st.error(f"フォントのダウンロードに失敗しました: {e}")
            return ImageFont.load_default()
            
    return ImageFont.truetype(font_path, size)

# --- 2. 席替えロジック & 画像生成 ---
def create_seating_chart(names):
    random.shuffle(names)
    
    # 画像サイズ（適宜調整してください）
    img_w, img_h = 800, 600
    image = Image.new("RGB", (img_w, img_h), "white")
    draw = ImageDraw.Draw(image)
    
    # フォント読み込み
    try:
        font_title = get_japanese_font(40)
        font_name = get_japanese_font(24)
    except:
        font_title = font_name = ImageFont.load_default()

    # タイトル描画
    draw.text((img_w//2 - 100, 20), "新しい座席表", fill="black", font=font_title)

    # 座席の描画（簡易的な2列配置の例）
    for i, name in enumerate(names):
        col = i % 2
        row = i // 2
        x = 100 + col * 350
        y = 100 + row * 60
        draw.rectangle([x, y, x+300, y+50], outline="blue", width=2)
        draw.text((x+10, y+10), f"{i+1}: {name}", fill="black", font=font_name)
    
    return image

# --- 3. メイン画面 ---
def main():
    st.title("席替えツール (画像保存対応)")
    st.write("ExcelまたはCSVをアップロードしてください。")

    uploaded_file = st.file_file_uploader("ファイルを選択", type=['xlsx', 'csv'])

    if uploaded_file:
        # ファイル読み込み
        if uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file, header=None)
        else:
            df = pd.read_csv(uploaded_file, header=None)
        
        names = df[0].dropna().tolist()

        if st.button("席替え実行！"):
            # 席替えと画像生成
            chart_img = create_seating_chart(names)
            
            # 画面に表示
            st.image(chart_img, caption="生成された座席表")

            # ダウンロード用バッファ
            buf = io.BytesIO()
            chart_img.save(buf, format="PNG")
            byte_im = buf.getvalue()

            st.download_button(
                label="画像をダウンロード",
                data=byte_im,
                file_name="sekigae_result.png",
                mime="image/png"
            )

if __name__ == "__main__":
    main()
