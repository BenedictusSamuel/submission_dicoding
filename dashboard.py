import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set(style="whitegrid", palette="pastel")

def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "payment_value": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "revenue"
    }, inplace=True)
    
    return daily_orders_df

def create_rfm_df(df):
    rfm_df = df.groupby(by="customer_id", as_index=False).agg({
        "order_purchase_timestamp": "max", 
        "order_id": "nunique",
        "payment_value": "sum"
    })
    rfm_df.columns = ["customer_id", "max_order_timestamp", "frequency", "monetary"]
    
    rfm_df["max_order_timestamp"] = rfm_df["max_order_timestamp"].dt.date
    recent_date = df["order_purchase_timestamp"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    
    return rfm_df

data = pd.read_csv('final_merged_data.csv')
data['order_purchase_timestamp'] = pd.to_datetime(data['order_purchase_timestamp'])

min_date = data["order_purchase_timestamp"].min()
max_date = data["order_purchase_timestamp"].max()

with st.sidebar:
    st.image("samlogo.png")
    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value=min_date,
        max_value=max_date, value=[min_date, max_date]
    )

main_df = data[(data["order_purchase_timestamp"] >= str(start_date)) & 
               (data["order_purchase_timestamp"] <= str(end_date))]

daily_orders_df = create_daily_orders_df(main_df)
rfm_df = create_rfm_df(main_df)

st.title('✨ Selamat Datang ✨')

st.subheader("📊 Daily Orders and Revenue")
col1, col2 = st.columns(2)
with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total Orders", total_orders)

with col2:
    total_revenue = format_currency(daily_orders_df.revenue.sum(), "USD", locale='en_US')
    st.metric("Total Revenue", total_revenue)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(daily_orders_df["order_purchase_timestamp"], daily_orders_df["order_count"],
        marker='o', linewidth=2, color="#90CAF9")
ax.set_title("Daily Orders", fontsize=15)
ax.set_xlabel("Date", fontsize=12)
ax.set_ylabel("Order Count", fontsize=12)
sns.despine()
st.pyplot(fig)

st.subheader("💬 Customer Satisfaction Ratings")
review_scores = main_df['review_score'].value_counts().sort_values(ascending=False)
most_common_score = review_scores.idxmax()

plt.figure(figsize=(10, 5))
sns.barplot(
    x=review_scores.index,
    y=review_scores.values,
    order=review_scores.index,
    palette=["#4CAF50" if score == most_common_score else "#D3D3D3" for score in review_scores.index],
)
plt.title("Customer Satisfaction Ratings", fontsize=15)
plt.xlabel("Rating", fontsize=12)
plt.ylabel("Count", fontsize=12)
sns.despine()
st.pyplot(plt.gcf())  

st.subheader("🛍️ Top 10 Produk dengan Penjualan Terbanyak")

product_sales = main_df.groupby('product_category_name_english').agg({
    'order_id': 'count'
}).reset_index().sort_values(by='order_id', ascending=False)

plt.figure(figsize=(10, 6))
sns.barplot(y=product_sales['product_category_name_english'].head(10), x=product_sales['order_id'].head(10), palette='Blues_d')
plt.title('Top 10 Produk dengan Penjualan Terbanyak', fontsize=15)
plt.xlabel('Jumlah Penjualan', fontsize=12)
plt.ylabel('Nama Produk', fontsize=12)
sns.despine()
st.pyplot(plt.gcf())

st.subheader("🏙️ Top 10 Kota dengan Jumlah Pelanggan Terbanyak")
city_customers = main_df['customer_city'].value_counts().reset_index()
city_customers.columns = ['customer_city', 'customer_count']

plt.figure(figsize=(10, 6))
sns.barplot(y=city_customers['customer_city'].head(10), x=city_customers['customer_count'].head(10), color='#1E88E5')
plt.title('Top 10 Kota dengan Jumlah Pelanggan Terbanyak', fontsize=15)
plt.xlabel('Jumlah Pelanggan', fontsize=12)
plt.ylabel('Kota', fontsize=12)
sns.despine()
st.pyplot(plt.gcf())

st.subheader("🌍 Top 10 Negara Bagian dengan Jumlah Pelanggan Terbanyak")
state_customers = main_df['customer_state'].value_counts().reset_index()
state_customers.columns = ['customer_state', 'customer_count']

plt.figure(figsize=(10, 6))
sns.barplot(y=state_customers['customer_state'].head(10), x=state_customers['customer_count'].head(10), color='#66BB6A')
plt.title('Top 10 Negara Bagian dengan Jumlah Pelanggan Terbanyak', fontsize=15)
plt.xlabel('Jumlah Pelanggan', fontsize=12)
plt.ylabel('Negara Bagian', fontsize=12)
sns.despine()
st.pyplot(plt.gcf())

st.subheader("📈 RFM Analysis")

col1, col2, col3 = st.columns(3)
with col1:
    avg_recency = round(rfm_df.recency.mean(), 1)
    st.metric("Average Recency (days)", avg_recency)

with col2:
    avg_frequency = round(rfm_df.frequency.mean(), 2)
    st.metric("Average Frequency", avg_frequency)

with col3:
    avg_monetary = format_currency(rfm_df.monetary.mean(), "USD", locale='en_US')
    st.metric("Average Monetary", avg_monetary)

# --- Footer with Copyright ---
st.markdown("""
    ---
    © 2024 Benedictus Samuel - [benedictussamuel1@gmail.com](mailto:benedictussamuel1@gmail.com)
""")

st.caption('Data visualized for E-Commerce')
