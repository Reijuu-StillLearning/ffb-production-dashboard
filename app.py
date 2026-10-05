import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Konfigurasi
st.set_page_config(page_title="Dashboard Produksi FFB", layout="wide")
st.title("Dashboard Produksi Tandan Buah Segar (FFB) Kelapa Sawit")

# 1. Load Data
@st.cache_data
def load_data():
    df = pd.read_csv("data/palm_ffb.csv")
    # Format CSV: DD.MM.YYYY
    df['Date'] = pd.to_datetime(df['Date'], format='%d.%m.%Y')
    return df

df = load_data()

# 2. Sidebar Filter
st.sidebar.header("Filter Konfigurasi")
min_date = df['Date'].min()
max_date = df['Date'].max()

start_date = st.sidebar.date_input("Tanggal Mulai", min_date)
end_date = st.sidebar.date_input("Tanggal Akhir", max_date)

# Tambahkan validasi simpel
if start_date > end_date:
    st.sidebar.error("Tanggal Mulai tidak boleh melebihi Tanggal Akhir!")

# Filter dataset
mask = (df['Date'] >= pd.to_datetime(start_date)) & (df['Date'] <= pd.to_datetime(end_date))
df_filtered = df.loc[mask]

# 3. KPI Cards
st.subheader("Highlight Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Avg Hasil FFB", f"{df_filtered['FFB_Yield'].mean():.2f} Ton/Ha")
col2.metric("Avg Kelembapan Tanah", f"{df_filtered['SoilMoisture'].mean():.1f} mm") 
col3.metric("Avg Curah Hujan", f"{df_filtered['Precipitation'].mean():.1f} mm")
col4.metric("Total HA Dipanen", f"{df_filtered['HA_Harvested'].sum():,.0f} Ha")

st.markdown("---")


# 4. Time-Series Chart
st.subheader("Tren Produksi & Cuaca (Deret Waktu)")

# skeleton dual-axis
fig_line = make_subplots(specs=[[{"secondary_y": True}]])

# FFB Yield
fig_line.add_trace(
    go.Scatter(x=df_filtered['Date'], y=df_filtered['FFB_Yield'], 
               name="FFB Yield", mode='lines+markers', line=dict(color='#2ca02c')),
    secondary_y=False,
)

# Curah Hujan
fig_line.add_trace(
    go.Scatter(x=df_filtered['Date'], y=df_filtered['Precipitation'], 
               name="Curah Hujan", mode='lines', line=dict(color='#1f77b4', dash='dot')),
    secondary_y=True,
)

# Konfigurasi Layout
fig_line.update_layout(
    title_text="Overlay FFB Yield vs Precipitation",
    hovermode="x unified"
)
fig_line.update_yaxes(title_text="FFB Yield (Ton/Ha)", secondary_y=False)
fig_line.update_yaxes(title_text="Curah Hujan (mm)", showgrid=False, secondary_y=True)

st.plotly_chart(fig_line, use_container_width=True)

# 5. Data Analysis (Heatmap & Scatter Plot)
st.markdown("---")
st.subheader("Analisis Data Eksplorasi (Exploratory Data Analysis)")

col_eda1, col_eda2 = st.columns(2)

with col_eda1:
    # Peta panas korelasi
    st.markdown("**Korelasi Heatmap**")
    # Hanya mengambil kolom numerik untuk korelasi
    df_num = df_filtered.select_dtypes(include='number')
    corr_matrix = df_num.corr()
    
    fig_corr = px.imshow(corr_matrix, text_auto=".2f", aspect="auto", 
                         color_continuous_scale='RdBu_r', origin='lower')
    st.plotly_chart(fig_corr, use_container_width=True)

with col_eda2:
    # Analisis diagram sebar
    st.markdown("**Analisis Scatter Plot**")
    # X dan Y axis bisa diatur dinamis via selectbox
    var_x = st.selectbox("Pilih Variabel X:", df_num.columns, index=1)
    var_y = st.selectbox("Pilih Variabel Y:", df_num.columns, index=7) # Default ke FFB_Yield
    
    fig_scatter = px.scatter(df_filtered, x=var_x, y=var_y, trendline="ols",
                             title=f"Hubungan {var_x} vs {var_y}", opacity=0.7)
    st.plotly_chart(fig_scatter, use_container_width=True)