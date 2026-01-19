import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# --- Ò³ÃæÅäÖÃ ---
st.set_page_config(page_title="¼«¼ò²Ö¹Ü Pro", layout="wide", initial_sidebar_state="expanded")

# --- ×Ô¶¨ÒåÑùÊ½ ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    .low-stock-row { background-color: #ffcccc !important; }
    </style>
    """, unsafe_allow_html=True)

# --- Êý¾Ý³õÊ¼»¯ (Êµ¼ÊÓ¦ÓÃ½¨ÒéÁ¬½ÓÊý¾Ý¿â) ---
if 'inventory' not in st.session_state:
    # Ô¤ÉèÒ»Ð©ÑÝÊ¾Êý¾Ý
    st.session_state.inventory = pd.DataFrame([
        {"SKU": "A001", "ÃèÊö": "Öá³Ð", "ÊýÁ¿": 50, "µ¥Î»": "¸ö", "ãÐÖµ": 100, "Î»ÖÃ": "AÇø-01", "¹©Ó¦ÉÌ": "¹¤³§A"},
        {"SKU": "B002", "ÃèÊö": "´«¸ÐÆ÷", "ÊýÁ¿": 150, "µ¥Î»": "×é", "ãÐÖµ": 50, "Î»ÖÃ": "BÇø-05", "¹©Ó¦ÉÌ": "´úÀíÉÌB"}
    ])
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=["Ê±¼ä", "SKU", "ÀàÐÍ", "ÊýÁ¿", "²Ù×÷Ô±"])

# --- È¨ÏÞ¹ÜÀíÂß¼­ ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def login():
    st.title("?? ²Ö¿â¹ÜÀíÏµÍ³µÇÂ¼")
    user = st.text_input("ÓÃ»§Ãû")
    pwd = st.text_input("ÃÜÂë", type="password")
    if st.button("½øÈëÏµÍ³"):
        if user == "admin" and pwd == "123456":
            st.session_state.authenticated = True
            st.session_state.role = "¹ÜÀíÔ±"
            st.rerun()
        elif user == "staff":
            st.session_state.authenticated = True
            st.session_state.role = "Ô±¹¤"
            st.rerun()
        else:
            st.error("ÓÃ»§Ãû»òÃÜÂë´íÎó")

if not st.session_state.authenticated:
    login()
    st.stop()

# --- ²à±ßÀ¸µ¼º½ ---
st.sidebar.title(f"?? {st.session_state.role}")
menu = st.sidebar.radio("¹¦ÄÜ²Ëµ¥", ["?? ¿â´æ¿´°å", "?? Èë¿âµÇ¼Ç", "?? ³ö¿âµÇ¼Ç", "?? ÀúÊ·¼ÇÂ¼"])
if st.sidebar.button("ÍË³öµÇÂ¼"):
    st.session_state.authenticated = False
    st.rerun()

# --- ¹¦ÄÜÄ£¿é£º¿â´æ¿´°å ---
if menu == "?? ¿â´æ¿´°å":
    st.header("ÊµÊ±¿â´æ¸ÅÀÀ")
    
    # Í³¼ÆÖ¸±ê
    low_stock_df = st.session_state.inventory[st.session_state.inventory['ÊýÁ¿'] < st.session_state.inventory['ãÐÖµ']]
    c1, c2, c3 = st.columns(3)
    c1.metric("×ÜSKUÖÖÀà", len(st.session_state.inventory))
    c2.metric("¿â´æÔ¤¾¯ÊýÁ¿", len(low_stock_df), delta=-len(low_stock_df), delta_color="inverse")
    c3.metric("×îºó¸üÐÂ", datetime.now().strftime("%H:%M"))

    # ¿â´æ±í¸ñÏÔÊ¾
    def color_low_stock(row):
        return ['background-color: #ffdbdb' if row['ÊýÁ¿'] < row['ãÐÖµ'] else '' for _ in row]
    
    st.subheader("¿â´æÃ÷Ï¸±í")
    st.dataframe(st.session_state.inventory.style.apply(color_low_stock, axis=1), use_container_width=True)

    # µ¼³ö¹¦ÄÜ (½öÏÞ¹ÜÀíÔ±)
    if st.session_state.role == "¹ÜÀíÔ±":
        csv = st.session_state.inventory.to_csv(index=False).encode('utf-8-sig')
        st.download_button("?? µ¼³ö¿â´æÎª Excel/CSV", data=csv, file_name="inventory.csv", mime="text/csv")

# --- ¹¦ÄÜÄ£¿é£ºÈë¿âµÇ¼Ç ---
elif menu == "?? Èë¿âµÇ¼Ç":
    st.header("ÐÂ»õÈë¿âÂ¼Èë")
    st.info("?? ÊÖ»ú¶Ë£ºµã»÷SKU¿ò¿É»½ÆðÉ¨ÂëÇ¹/ÉãÏñÍ·¡£")
    
    with st.form("in_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            sku = st.text_input("?? SKUÂë£¨Ö§³ÖÉ¨ÂëÊäÈë£©")
            desc = st.text_input("»õÎïÃèÊö")
            qty = st.number_input("Èë¿âÊýÁ¿", min_value=1)
        with col2:
            loc = st.text_input("´æ·ÅÎ»ÖÃ")
            threshold = st.number_input("ÉèÖÃÔ¤¾¯ãÐÖµ", min_value=0, value=20)
            photo = st.file_uploader("?? ÅÄÕÕ»òÑ¡ÔñÕÕÆ¬", type=['png', 'jpg', 'jpeg'])
        
        if st.form_submit_button("È·ÈÏÈë¿â"):
            # ¼òµ¥Âß¼­£ºÈç¹ûSKU´æÔÚÔòÀÛ¼Ó£¬²»´æÔÚÔòÐÂ½¨
            if sku in st.session_state.inventory['SKU'].values:
                st.session_state.inventory.loc[st.session_state.inventory['SKU'] == sku, 'ÊýÁ¿'] += qty
            else:
                new_item = {"SKU": sku, "ÃèÊö": desc, "ÊýÁ¿": qty, "µ¥Î»": "¸ö", "ãÐÖµ": threshold, "Î»ÖÃ": loc, "¹©Ó¦ÉÌ": "ÐÂÂ¼Èë"}
                st.session_state.inventory = pd.concat([st.session_state.inventory, pd.DataFrame([new_item])], ignore_index=True)
            
            # ¼ÇÂ¼ÀúÊ·
            new_log = {"Ê±¼ä": datetime.now(), "SKU": sku, "ÀàÐÍ": "Èë¿â", "ÊýÁ¿": qty, "²Ù×÷Ô±": st.session_state.role}
            st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([new_log])], ignore_index=True)
            st.success(f"? SKU {sku} Èë¿â³É¹¦£¡")

# --- ¹¦ÄÜÄ£¿é£º³ö¿âµÇ¼Ç ---
elif menu == "?? ³ö¿âµÇ¼Ç":
    st.header("»õÎï³ö¿â")
    sku_to_out = st.selectbox("Ñ¡ÔñÒª³ö¿âµÄSKU", st.session_state.inventory['SKU'].tolist())
    current_qty = st.session_state.inventory.loc[st.session_state.inventory['SKU'] == sku_to_out, 'ÊýÁ¿'].values[0]
    
    st.write(f"µ±Ç°Ê£ÓàÊýÁ¿: **{current_qty}**")
    out_qty = st.number_input("±¾´ÎÁìÓÃÊýÁ¿", min_value=1, max_value=int(current_qty))
    
    if st.button("È·ÈÏ³ö¿â"):
        st.session_state.inventory.loc[st.session_state.inventory['SKU'] == sku_to_out, 'ÊýÁ¿'] -= out_qty
        new_log = {"Ê±¼ä": datetime.now(), "SKU": sku_to_out, "ÀàÐÍ": "³ö¿â", "ÊýÁ¿": -out_qty, "²Ù×÷Ô±": st.session_state.role}
        st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([new_log])], ignore_index=True)
        st.success("? ³ö¿â³É¹¦£¡")
        st.rerun()

# --- ¹¦ÄÜÄ£¿é£ºÀúÊ·¼ÇÂ¼ ---
elif menu == "?? ÀúÊ·¼ÇÂ¼":
    st.header("²Ù×÷Á÷Ë®¼ÇÂ¼")
    st.table(st.session_state.history.sort_values("Ê±¼ä", ascending=False))
