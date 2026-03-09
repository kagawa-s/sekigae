import streamlit as st
import pandas as pd
import random
import re
from PIL import Image, ImageDraw, ImageFont
import io
import os
import time
from math import ceil
import os
import requests
from PIL import ImageFont

def get_japanese_font():
    # フォントの保存パス
    font_path = "NotoSansJP-Regular.ttf"
    
    # フォントがなければダウンロード
    if not os.path.exists(font_path):
        url = "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/Japanese/NotoSansCJKjp-Regular.otf"
        response = requests.get(url)
        with open(font_path, "wb") as f:
            f.write(response.content)
    
    return font_path

# 画像生成している部分で、このフォントを指定する
font_file = get_japanese_font()
# 例: font = ImageFont.truetype(font_file, 20)

# --- ページ設定 ---
st.set_page_config(page_title="席替えやります", layout="wide")

# デザインCSS（横幅を150pxで固定し、間隔を詰める）
st.markdown("""
    <style>
    .stApp { background-color: #F1F5F9; }
    
    .block-container {
        padding-top: 4rem !important; 
        padding-left: 0.5rem !important; /* 余白を微減 */
        padding-right: 0.5rem !important;
        max-width: none !important; 
    }
    
    .kyotaku {
        background-color: #334155; color: white;
        text-align: center; padding: 12px; font-weight: bold;
        border-radius: 4px; margin: 0 auto 40px auto; width: 220px;
        letter-spacing: 0.6em; font-size: 1rem;
    }

    [data-testid="stHorizontalBlock"] {
        width: max-content !important;
        margin: 0 auto !important;
        min-width: 100%;
        display: flex;
        justify-content: center;
        gap: 0 !important; /* カラム間の隙間をゼロに */
    }
    
    .stButton > button {
        border-radius: 8px !important;
        white-space: pre !important;
        transition: all 0.2s ease;
        text-align: center !important; /* センタリング */
    }

    /* 座席ボタン：150px固定 & センタリング */
    [data-testid="column"] .stButton > button {
        height: 100px !important; 
        width: 150px !important;  
        min-width: 150px !important;
        max-width: 150px !important;
        font-size: 0.95rem !important;
        font-weight: bold !important;
        background-color: white;
        color: #1E293B;
        border: 1px solid #CBD5E1;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 0 auto !important;
    }

    section[data-testid="stSidebar"] .stButton > button {
        height: 80px !important;
        width: 100% !important;
        max-width: none !important;
        font-size: 1.1rem !important;
        margin-bottom: 15px !important;
        border: 2px solid #3B82F6 !important;
    }
    
    section[data-testid="stSidebar"] .stButton:nth-of-type(1) > button {
        background-color: #3B82F6 !important;
        color: white !important;
    }
    
    section[data-testid="stSidebar"] .stButton:nth-of-type(2) > button {
        background-color: white !important;
        color: #B45309 !important;
        border-color: #F59E0B !important;
    }

    .fixed-seat .stButton > button {
        border: 3px solid #F59E0B !important;
        background-color: #FFFBEB !important;
        color: #B45309 !important;
    }
    .selected-btn .stButton > button {
        background-color: #EFF6FF !important;
        border: 3px solid #3B82F6 !important;
        color: #1D4ED8 !important;
    }

    /* 【修正】席の間隔を狭める（160px -> 155px） */
    [data-testid="column"] {
        width: 155px !important;
        flex: 0 0 155px !important;
        padding: 2px !important; /* パディングを削って間隔を詰める */
    }
    </style>
    """, unsafe_allow_html=True)

# --- ロジック関数 ---

def get_output_name(full_name, all_full_names):
    name_str = str(full_name).strip()
    parts = re.split(r'[ 　]', name_str)
    last_name = parts[0]
    all_last_names = [re.split(r'[ 　]', str(n).strip())[0] for n in all_full_names]
    if all_last_names.count(last_name) > 1:
        first_name = parts[1] if len(parts) > 1 else ""
        return f"{last_name}{first_name[0]}" if first_name else last_name
    return last_name

def shuffle_seats(seats):
    movable_indices = [i for i, s in enumerate(seats) if not s.get('fixed', False)]
    movable_contents = [seats[i] for i in movable_indices]
    random.shuffle(movable_contents)
    new_seats = list(seats)
    for i, content_idx in enumerate(movable_indices):
        new_seats[content_idx] = movable_contents[i]
    return new_seats

def main_logic_get_layout(num_students, num_cols):
    base_rows = num_students // num_cols
    remainder = num_students % num_cols
    col_counts = [base_rows + (1 if (num_cols - 1 - i) < remainder else 0) for i in range(num_cols)]
    layout = []
    for c in range(num_cols):
        target_col = (num_cols - 1) - c
        for r in range(col_counts[c]):
            layout.append((r, target_col))
    return layout

def get_japanese_font(size):
    font_paths = ["C:\\Windows\\Fonts\\msgothic.ttc", "/System/Library/Fonts/Hiragino Sans GB.ttc", "/usr/share/fonts/truetype/fonts-japanese-gothic.ttf"]
    for path in font_paths:
        if os.path.exists(path): return ImageFont.truetype(path, size)
    return ImageFont.load_default()

def create_png(seats, num_cols):
    W, H = 2400, 1800
    img = Image.new("RGB", (W, H), "#F8F9FA")
    draw = ImageDraw.Draw(img)
    f_t = get_japanese_font(70); f_n = get_japanese_font(45); f_s = get_japanese_font(25); f_p = get_japanese_font(30)
    draw.rectangle([W//2-200, 50, W//2+200, 150], fill="#334155")
    draw.text((W//2, 100), "教 卓", fill="white", font=f_t, anchor="mm")
    l_map = main_logic_get_layout(len(seats), num_cols)
    num_rows = max(r for r, c in l_map) + 1
    cw, ch = (W - 200) // num_cols, (H - 300) // num_rows
    all_full_names = [s['name'] for s in seats]
    for i, seat in enumerate(seats):
        r, c = l_map[i]
        x1, y1 = 100 + c*cw + 20, 250 + r*ch + 20
        x2, y2 = x1 + cw - 40, y1 + ch - 40
        bg_color, line_color = ("#FFFBEB", "#F59E0B") if seat.get('fixed') else ("white", "#CBD5E1")
        draw.rounded_rectangle([x1, y1, x2, y2], radius=20, fill=bg_color, outline=line_color, width=3)
        mid_x, mid_y = x1 + (x2-x1)//2, y1 + (y2-y1)//2
        if seat.get('fixed'): draw.text((mid_x, y1 + 40), "📌", fill="#F59E0B", font=f_p, anchor="mm")
        draw.text((mid_x, mid_y - 10), f"No.{seat['no']}", fill="#64748B", font=f_s, anchor="mm")
        display_name = get_output_name(seat['name'], all_full_names)
        draw.text((mid_x, mid_y + 40), display_name, fill="#1E293B", font=f_n, anchor="mm")
    buf = io.BytesIO(); img.save(buf, format="PNG"); return buf.getvalue()

def main():
    if 'seats' not in st.session_state: st.session_state.seats = []
    if 'swap_idx' not in st.session_state: st.session_state.swap_idx = None
    if 'is_shuffling' not in st.session_state: st.session_state.is_shuffling = False

    with st.sidebar:
        st.title("🏫 席替えやります")
        file = st.file_uploader("名簿(Excel/CSV)", type=["xlsx", "xls", "csv"])
        num_cols = st.number_input("横の列数", 3, 12, 6)
        
        if file and not st.session_state.seats:
            df = pd.read_excel(file, header=None) if not file.name.endswith('.csv') else pd.read_csv(file, header=None)
            names = df[df.columns[df.notna().any()][0]].dropna().astype(str).tolist()
            if st.button("座席を生成"):
                st.session_state.seats = [{"no": i+1, "name": n, "fixed": False} for i, n in enumerate(names)]
                st.rerun()

        if st.session_state.seats:
            st.divider()
            mode = st.radio("操作モード", ["席を入れ替える", "ピンで固定する"])
            if st.button("🎲 席替え実行", disabled=st.session_state.is_shuffling):
                st.session_state.is_shuffling = True
                st.rerun()
            if st.button("🔄 ピンをすべて抜く"):
                for s in st.session_state.seats: s['fixed'] = False
                st.rerun()
            st.divider()
            st.download_button("📥 画像を保存する", data=create_png(st.session_state.seats, num_cols), file_name="seat.png")

    if st.session_state.seats:
        if st.session_state.is_shuffling:
            placeholder = st.empty()
            total_duration = 10.0
            start_time = time.time()
            
            while True:
                elapsed = time.time() - start_time
                remaining = total_duration - elapsed
                if remaining <= 0: break
                
                if remaining > 3.0:
                    wait_time = 0.05
                else:
                    wait_time = 0.05 + (0.55 * (1 - (remaining / 3.0)))
                
                temp_seats = shuffle_seats(st.session_state.seats)
                with placeholder.container():
                    st.markdown(f'<div style="text-align:center; font-size:2.5rem; font-weight:bold; color:#3B82F6; margin-bottom:10px;">席替え中... <span style="color:#EF4444; font-size:3.5rem;">{int(remaining)+1}</span></div>', unsafe_allow_html=True)
                    st.markdown('<div class="kyotaku">教 卓</div>', unsafe_allow_html=True)
                    l_map = main_logic_get_layout(len(temp_seats), num_cols)
                    max_rows = max(r for r, c in l_map) + 1
                    for r in range(max_rows):
                        cols_ui = st.columns(num_cols)
                        for c in range(num_cols):
                            idx = next((i for i, pos in enumerate(l_map) if pos == (r, c)), None)
                            if idx is not None:
                                seat = temp_seats[idx]
                                container_cls = "fixed-seat" if seat.get('fixed') else ""
                                with cols_ui[c]:
                                    st.markdown(f'<div class="{container_cls}">', unsafe_allow_html=True)
                                    label = f"{'📌' if seat.get('fixed') else ' '}\nNo.{seat['no']}\n{seat['name']}"
                                    st.button(label, key=f"shuf_{elapsed}_{idx}", disabled=True)
                                    st.markdown('</div>', unsafe_allow_html=True)
                time.sleep(wait_time)
            
            st.session_state.seats = shuffle_seats(st.session_state.seats)
            st.session_state.is_shuffling = False
            st.rerun()

        else:
            st.markdown('<div class="kyotaku">教 卓</div>', unsafe_allow_html=True)
            l_map = main_logic_get_layout(len(st.session_state.seats), num_cols)
            max_rows = max(r for r, c in l_map) + 1
            for r in range(max_rows):
                cols_ui = st.columns(num_cols)
                for c in range(num_cols):
                    idx = next((i for i, pos in enumerate(l_map) if pos == (r, c)), None)
                    if idx is not None:
                        seat = st.session_state.seats[idx]
                        container_cls = "fixed-seat" if seat.get('fixed') else ("selected-btn" if st.session_state.swap_idx == idx else "")
                        with cols_ui[c]:
                            st.markdown(f'<div class="{container_cls}">', unsafe_allow_html=True)
                            label = f"{'📌' if seat.get('fixed') else ' '}\nNo.{seat['no']}\n{seat['name']}"
                            if st.button(label, key=f"btn_{idx}"):
                                if mode == "ピンで固定する":
                                    st.session_state.seats[idx]['fixed'] = not st.session_state.seats[idx]['fixed']
                                    st.session_state.swap_idx = None
                                else:
                                    if st.session_state.swap_idx is None: st.session_state.swap_idx = idx
                                    else:
                                        i1, i2 = st.session_state.swap_idx, idx
                                        st.session_state.seats[i1], st.session_state.seats[i2] = st.session_state.seats[i2], st.session_state.seats[i1]
                                        st.session_state.swap_idx = None
                                st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":

    main()
