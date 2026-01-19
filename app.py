# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
from datetime import datetime

# --- 强制设置页面编码和配置 ---
st.set_page_config(page_title="仓库管理系统", layout="wide")

# --- 初始化数据 ---
if 'inventory' not in st.session_state:
    st.session_state.inventory = pd.DataFrame([
        {"SKU": "A001", "描述": "示例货物", "数量": 10, "单位": "个", "阈值": 5, "位置": "A-01"}
    ])

# --- 简单的登录界面 ---
if 'login' not in st.session_state:
    st.session_state.login = False

if not st.session_state.login:
    st.title("📦 仓库管理系统登录")
    user = st.text_input("用户名 (admin)")
    pwd = st.text_input("密码 (123)", type="password")
    if st.button("登录"):
        if user == "admin" and pwd == "123":
            st.session_state.login = True
            st.rerun()
        else:
            st.error("用户名或密码错误")
    st.stop()

# --- 主界面 ---
st.title("🚀 极简仓管 Pro")
st.sidebar.success(f"当前用户: admin")
menu = st.sidebar.selectbox("功能菜单", ["库存查询", "入库登记", "出库登记"])

if menu == "库存查询":
    st.subheader("当前库存清单")
    # 增加低库存预警显示逻辑
    def highlight_low(row):
        return ['background-color: #ffcccc' if row['数量'] < row['阈值'] else '' for _ in row]
    st.dataframe(st.session_state.inventory.style.apply(highlight_low, axis=1))

elif menu == "入库登记":
    st.subheader("货物入库")
    with st.form("in_form"):
        sku = st.text_input("SKU码 (支持扫码枪)")
        qty = st.number_input("数量", min_value=1)
        if st.form_submit_button("确认入库"):
            st.success(f"SKU {sku} 已成功入库 {qty} 个")

elif menu == "出库登记":
    st.subheader("货物出库")
    st.info("请选择对应的SKU进行操作")
