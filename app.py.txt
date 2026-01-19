import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# --- 页面配置 ---
st.set_page_config(page_title="极简仓管 Pro", layout="wide", initial_sidebar_state="expanded")

# --- 自定义样式 ---
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    .low-stock-row { background-color: #ffcccc !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 数据初始化 (实际应用建议连接数据库) ---
if 'inventory' not in st.session_state:
    # 预设一些演示数据
    st.session_state.inventory = pd.DataFrame([
        {"SKU": "A001", "描述": "轴承", "数量": 50, "单位": "个", "阈值": 100, "位置": "A区-01", "供应商": "工厂A"},
        {"SKU": "B002", "描述": "传感器", "数量": 150, "单位": "组", "阈值": 50, "位置": "B区-05", "供应商": "代理商B"}
    ])
if 'history' not in st.session_state:
    st.session_state.history = pd.DataFrame(columns=["时间", "SKU", "类型", "数量", "操作员"])

# --- 权限管理逻辑 ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def login():
    st.title("?? 仓库管理系统登录")
    user = st.text_input("用户名")
    pwd = st.text_input("密码", type="password")
    if st.button("进入系统"):
        if user == "admin" and pwd == "123456":
            st.session_state.authenticated = True
            st.session_state.role = "管理员"
            st.rerun()
        elif user == "staff":
            st.session_state.authenticated = True
            st.session_state.role = "员工"
            st.rerun()
        else:
            st.error("用户名或密码错误")

if not st.session_state.authenticated:
    login()
    st.stop()

# --- 侧边栏导航 ---
st.sidebar.title(f"?? {st.session_state.role}")
menu = st.sidebar.radio("功能菜单", ["?? 库存看板", "?? 入库登记", "?? 出库登记", "?? 历史记录"])
if st.sidebar.button("退出登录"):
    st.session_state.authenticated = False
    st.rerun()

# --- 功能模块：库存看板 ---
if menu == "?? 库存看板":
    st.header("实时库存概览")
    
    # 统计指标
    low_stock_df = st.session_state.inventory[st.session_state.inventory['数量'] < st.session_state.inventory['阈值']]
    c1, c2, c3 = st.columns(3)
    c1.metric("总SKU种类", len(st.session_state.inventory))
    c2.metric("库存预警数量", len(low_stock_df), delta=-len(low_stock_df), delta_color="inverse")
    c3.metric("最后更新", datetime.now().strftime("%H:%M"))

    # 库存表格显示
    def color_low_stock(row):
        return ['background-color: #ffdbdb' if row['数量'] < row['阈值'] else '' for _ in row]
    
    st.subheader("库存明细表")
    st.dataframe(st.session_state.inventory.style.apply(color_low_stock, axis=1), use_container_width=True)

    # 导出功能 (仅限管理员)
    if st.session_state.role == "管理员":
        csv = st.session_state.inventory.to_csv(index=False).encode('utf-8-sig')
        st.download_button("?? 导出库存为 Excel/CSV", data=csv, file_name="inventory.csv", mime="text/csv")

# --- 功能模块：入库登记 ---
elif menu == "?? 入库登记":
    st.header("新货入库录入")
    st.info("?? 手机端：点击SKU框可唤起扫码枪/摄像头。")
    
    with st.form("in_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            sku = st.text_input("?? SKU码（支持扫码输入）")
            desc = st.text_input("货物描述")
            qty = st.number_input("入库数量", min_value=1)
        with col2:
            loc = st.text_input("存放位置")
            threshold = st.number_input("设置预警阈值", min_value=0, value=20)
            photo = st.file_uploader("?? 拍照或选择照片", type=['png', 'jpg', 'jpeg'])
        
        if st.form_submit_button("确认入库"):
            # 简单逻辑：如果SKU存在则累加，不存在则新建
            if sku in st.session_state.inventory['SKU'].values:
                st.session_state.inventory.loc[st.session_state.inventory['SKU'] == sku, '数量'] += qty
            else:
                new_item = {"SKU": sku, "描述": desc, "数量": qty, "单位": "个", "阈值": threshold, "位置": loc, "供应商": "新录入"}
                st.session_state.inventory = pd.concat([st.session_state.inventory, pd.DataFrame([new_item])], ignore_index=True)
            
            # 记录历史
            new_log = {"时间": datetime.now(), "SKU": sku, "类型": "入库", "数量": qty, "操作员": st.session_state.role}
            st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([new_log])], ignore_index=True)
            st.success(f"? SKU {sku} 入库成功！")

# --- 功能模块：出库登记 ---
elif menu == "?? 出库登记":
    st.header("货物出库")
    sku_to_out = st.selectbox("选择要出库的SKU", st.session_state.inventory['SKU'].tolist())
    current_qty = st.session_state.inventory.loc[st.session_state.inventory['SKU'] == sku_to_out, '数量'].values[0]
    
    st.write(f"当前剩余数量: **{current_qty}**")
    out_qty = st.number_input("本次领用数量", min_value=1, max_value=int(current_qty))
    
    if st.button("确认出库"):
        st.session_state.inventory.loc[st.session_state.inventory['SKU'] == sku_to_out, '数量'] -= out_qty
        new_log = {"时间": datetime.now(), "SKU": sku_to_out, "类型": "出库", "数量": -out_qty, "操作员": st.session_state.role}
        st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([new_log])], ignore_index=True)
        st.success("? 出库成功！")
        st.rerun()

# --- 功能模块：历史记录 ---
elif menu == "?? 历史记录":
    st.header("操作流水记录")
    st.table(st.session_state.history.sort_values("时间", ascending=False))