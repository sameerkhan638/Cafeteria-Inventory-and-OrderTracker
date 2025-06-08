import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
import os

st.set_page_config(page_title="Cafeteria Tracker", layout="centered", page_icon="🍽️")

DATA_FILE = "cafeteria_data.json"

# Dummy login data
USERS = {
    "student": "pass123",
    "staff": "admin@123"
}

def login(username, password):
    return USERS.get(username) == password

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(st.session_state.inventory, f)

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            st.session_state.inventory = json.load(f)
    else:
        st.session_state.inventory = {
            'Sandwich': {'price': 50, 'quantity': 10, 'orders': 0},
            'Burger': {'price': 80, 'quantity': 5, 'orders': 0},
            'Juice': {'price': 30, 'quantity': 20, 'orders': 0},
        }
        save_data()

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Cafeteria Login")
    user = st.text_input("Username")
    pw = st.text_input("Password", type="password")
    if st.button("Login"):
        if login(user, pw):
            st.session_state.logged_in = True
            st.session_state.user = user
            load_data()
            st.success("Login successful!")
            st.experimental_rerun()
        else:
            st.error("Invalid credentials")
    st.stop()

# Theme toggle (simple)
mode = st.sidebar.checkbox("🌗 Dark Mode")
if mode:
    st.markdown("""
        <style>
        body {
            background-color: #1e1e1e;
            color: #e0e0e0;
        }
        h1, h2, h3, h4, h5 {
            color: #feca57;
        }
        </style>
    """, unsafe_allow_html=True)

st.markdown("""
    <style>
    .title {
        text-align: center;
        font-size: 3em;
        color: #ff4b4b;
        font-weight: bold;
        font-family: 'Trebuchet MS', sans-serif;
        margin-bottom: 20px;
    }
    .menu-box {
        background-color: #fefae0;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    }
    .btn-style {
        background-color: #f94144;
        color: white;
        font-size: 1.1em;
        padding: 10px;
        border-radius: 8px;
        border: none;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🍽️ College Cafeteria Dashboard</div>', unsafe_allow_html=True)

# Load or initialize inventory
if 'inventory' not in st.session_state:
    load_data()

inventory = st.session_state.inventory

st.sidebar.image("https://img.freepik.com/free-vector/restaurant-menu-template_23-2147503760.jpg", use_column_width=True)
menu = ["➕ Add Item", "🛒 Place Order", "📊 Popularity Report", "📤 Export Data"]
choice = st.sidebar.radio("📌 Menu", menu)

def show_item_card(item, info):
    st.markdown(f"""
    <div style="border:1px solid #ddd; border-radius:12px; padding:15px; margin-bottom:10px; box-shadow: 2px 2px 6px #ccc;">
        <h4 style="margin:0; color:#f94144;">{item}</h4>
        <p><b>Ordered:</b> {info['orders']} times<br>
        <b>Remaining:</b> {info['quantity']}<br>
        <b>Price:</b> ₹{info['price']}</p>
    </div>
    """, unsafe_allow_html=True)

with st.container():
    if choice == "➕ Add Item":
        if st.session_state.user != "staff":
            st.warning("Only staff can add or update items.")
        else:
            st.subheader("Add or Update Food Item")
            name = st.text_input("🍱 Enter item name")
            col1, col2 = st.columns(2)
            with col1:
                price = st.number_input("💰 Price (₹)", min_value=1)
            with col2:
                qty = st.number_input("📦 Quantity", min_value=1, step=1)
            if st.button("Add / Update"):
                if name.strip():
                    if name in inventory:
                        inventory[name]['quantity'] += qty
                        st.success(f"✅ Updated stock of {name}.")
                    else:
                        inventory[name] = {'price': price, 'quantity': qty, 'orders': 0}
                        st.success(f"🍽️ Added new item: {name}")
                    save_data()
                else:
                    st.error("❗ Item name cannot be empty")

    elif choice == "🛒 Place Order":
        st.subheader("🛍️ Select Items to Order")
        st.markdown("<small style='color: gray;'>Only items in stock are listed.</small>", unsafe_allow_html=True)
        order = {}
        for item, details in inventory.items():
            if details['quantity'] == 0:
                continue
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{item}** — ₹{details['price']} | In Stock: {details['quantity']}")
            with col2:
                qty = st.number_input("", key=item, min_value=0, max_value=details['quantity'], step=1, label_visibility="collapsed")
                if qty > 0:
                    order[item] = qty
        if st.button("Submit Order ✅"):
            total = 0
            for item, qty in order.items():
                if inventory[item]['quantity'] >= qty:
                    total += inventory[item]['price'] * qty
                    inventory[item]['quantity'] -= qty
                    inventory[item]['orders'] += qty
                else:
                    st.warning(f"⚠️ Not enough stock for {item}.")
            if total > 0:
                st.success(f"🎉 Order Successful! Total Bill: ₹{total}")
                save_data()
            else:
                st.info("📝 Please select at least one item to place an order.")

    elif choice == "📊 Popularity Report":
        st.subheader("📈 Popular Items Summary")
        sorted_items = sorted(inventory.items(), key=lambda x: x[1]['orders'], reverse=True)
        if all(info['orders'] == 0 for _, info in sorted_items):
            st.info("No orders yet. Once students place orders, popularity will be shown here.")
        else:
            df = pd.DataFrame([{
                'Item': item,
                'Orders': info['orders']
            } for item, info in sorted_items if info['orders'] > 0])
            chart_type = st.selectbox("Select chart type", ["Bar Chart", "Pie Chart"])
            if chart_type == "Bar Chart":
                st.bar_chart(df.set_index('Item'))
            else:
                fig, ax = plt.subplots()
                ax.pie(df['Orders'], labels=df['Item'], autopct='%1.1f%%', startangle=90)
                ax.axis('equal')
                st.pyplot(fig)
            st.write("---")
            for item, info in sorted_items:
                if info['orders'] > 0:
                    show_item_card(item, info)

    elif choice == "📤 Export Data":
        st.subheader("📦 Export Inventory and Orders")
        export_df = pd.DataFrame([{
            "Item": item,
            "Price": info['price'],
            "Quantity": info['quantity'],
            "Orders": info['orders']
        } for item, info in inventory.items()])

        csv = export_df.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Download as CSV", data=csv, file_name="cafeteria_data.csv", mime="text/csv")


