import streamlit as st
import pandas as pd
import random
import os
import requests
from PIL import Image, ImageDraw, ImageFont
import io
import time

# 1. 日本語フォントをネットから取得する（文字化け対策）
def get_japanese_font(size=24):
    font_path = "NotoSansJP-Regular.otf"
    if not os.path.exists(font_path):
        # Google提供の日本語フォント（これなら漢字も化けません）
        url = "https://github.com/googlefonts/noto-cjk/raw/main/Sans/SubsetOTF/JP/NotoSansJP-Regular.otf"
        try:
            response = requests.get(url)
            with open(font_path, "wb") as f:
                f.write(response.content)
        except:
            return ImageFont.load_default()
    return ImageFont.truetype(font_path, size)

# 2. 座席表の描画
def create_chart(names):
    # 画像の土台を作成
    img_w, img_h = 800, 600
    image = Image.new("RGB", (img_w, img_h), (245, 245, 245)) # 薄いグレー
    draw = ImageDraw.Draw(image)
    
    font_title = get_japanese_font(36)
    font_text = get_japanese_font(20)

    # タイトル
    draw.text((250, 30), "決定した座席表", fill=(50, 50, 50), font=font_title)

    # 座席の配置
    for i, name in enumerate(names):
        col = i % 2
        row = i // 2
        x = 80 + col * 380
        y = 100 + row * 60
        # 枠線
        draw.rectangle([x, y, x+300, y+50], outline=(0, 100, 200), width=2, fill="white")
        # 名前
        draw.text((x+15, y+10), f"{i+1}: {name}", fill="black", font=font_text)
    
    return image

# 3. メイン画面
def main():
    st.set_page_config(page_title="席替えツール", layout="centered")
    st.title("🪑 席替え自動生成ツール")
    
    uploaded_file = st.file_uploader("名簿（Excel/CSV）をアップロードしてください", type=['xlsx', 'csv'])

    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.xlsx'):
                df = pd.read_excel(uploaded_file, header=None)
            else:
                df = pd.read_csv(uploaded_file, header=None)
            
            names = df[0].dropna().tolist()
            st.success(f"{len(names)} 名の名簿を読み込みました。")

            if st.button("席替えを開始する（演出あり）"):
                # 演出用プレースホルダー
                status = st.empty()
                for i in range(5):
                    status.info(f"座席をシャッフル中... {'.' * (i % 4 + 1)}")
                    time.sleep(0.3)
                
                random.shuffle(names)
                status.success("席替えが完了しました！")
                
                # 画像生成
                chart_img = create_chart(names)
                st.image(chart_img)

                # ダウンロード準備
                buf = io.BytesIO()
                chart_img.save(buf, format="PNG")
                
                st.download_button(
                    label="座席表を画像(PNG)で保存",
                    data=buf.getvalue(),
                    file_name="seating_chart.png",
                    mime="image/png"
                )
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    main()
