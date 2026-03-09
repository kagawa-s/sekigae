import streamlit as st
import pandas as pd
import random
import os
import requests
from PIL import Image, ImageDraw, ImageFont
import io

# --- 1. 日本語フォントをサーバーに用意する関数 ---
def get_japanese_font(size=24):
    font_path = "NotoSansJP-Regular.otf"
    
    # フォントがなければダウンロード
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
    
    # 画像サイズ
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
    draw.text((img_w//2 - 120, 20), "新しい座席表", fill="black", font=font_title)

    # 座席の描画（2列配置）
    for i, name in enumerate(names):
        col = i % 2
        row = i // 2
        x = 100 + col * 350
        y = 100 + row * 60
        draw.rectangle([x, y, x+300, y+50], outline="blue", width=2)
        # 文字化け対策済みのフォントで描画
        draw.text((x+10, y+10), f"{i+1}: {name}", fill="black", font=font_name)
    
    return image

# --- 3. メイン画面 ---
def main():
    st.title("席替えツール (画像保存対応)")
    st.write("ExcelまたはCSVをアップロードしてください。")

    # ↓ ここを修正しました（file_file_uploader → file_uploader）
    uploaded_file = st.file_uploader("ファイルを選択", type=['xlsx', 'csv'])

    if uploaded_file:
        # ファイル読み込み
        try:
            if uploaded_file.name.endswith('.xlsx'):
                df = pd.read_excel(uploaded_file, header=None)
            else:
                df = pd.read_csv(uploaded_file, header=None)
            
            # 1列目のデータをリスト化（空欄は除外）
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
                    label="座席表を画像としてダウンロード",
                    data=byte_im,
                    file_name="sekigae_result.png",
                    mime="image/png"
                )
        except Exception as e:
            st.error(f"ファイルの読み込みに失敗しました: {e}")

if __name__ == "__main__":
    main()
