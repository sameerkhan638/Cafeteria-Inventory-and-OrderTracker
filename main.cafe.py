import streamlit as st

# Initialize session state if not already done
if 'inventory' not in st.session_state:
    st.session_state.inventory = {
        'Sandwich': {'price': 50, 'quantity': 10, 'orders': 0},
        'Burger': {'price': 80, 'quantity': 5, 'orders': 0},
        'Juice': {'price': 30, 'quantity': 20, 'orders': 0},
    }

inventory = st.session_state.inventory

st.title("🍽️ College Cafeteria Inventory & Order Tracker")

menu = ["Add Item", "Place Order", "Popularity Report"]
choice = st.sidebar.selectbox("Choose Option", menu)

if choice == "Add Item":
    st.header("➕ Add New Food Item")
    name = st.text_input("Enter food item name")
    price = st.number_input("Enter price", min_value=1)
    qty = st.number_input("Enter quantity", min_value=1, step=1)
    if st.button("Add / Update Item"):
        if name:
            if name in inventory:
                inventory[name]['quantity'] += qty
                st.success(f"Updated quantity of {name}.")
            else:
                inventory[name] = {'price': price, 'quantity': qty, 'orders': 0}
                st.success(f"Added new item: {name}")
        else:
            st.error("Item name cannot be empty")

elif choice == "Place Order":
    st.header("🛒 Place Your Order")
    order = {}
    for item, details in inventory.items():
        st.subheader(f"{item} (₹{details['price']})")
        qty = st.number_input(f"Quantity for {item}", min_value=0, max_value=details['quantity'], step=1, key=item)
        if qty > 0:
            order[item] = qty

    if st.button("Submit Order"):
        total = 0
        for item, qty in order.items():
            if inventory[item]['quantity'] >= qty:
                total += inventory[item]['price'] * qty
                inventory[item]['quantity'] -= qty
                inventory[item]['orders'] += qty
            else:
                st.warning(f"Not enough stock for {item}.")
        st.success(f"Order placed! Total Bill: ₹{total}")

elif choice == "Popularity Report":
    st.header("📊 Popularity Summary")
    sorted_items = sorted(inventory.items(), key=lambda x: x[1]['orders'], reverse=True)
    for item, info in sorted_items:
        st.write(f"**{item}** — Ordered: {info['orders']} times, Remaining: {info['quantity']}, Price: ₹{info['price']}")