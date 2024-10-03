import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
 
all_df = pd.read_csv("dashboard/all_data.csv")
all_df.reset_index(inplace=True)

def get_data_per_jam(tanggal, cuaca=None):
    
    filtered_df = all_df[all_df['dteday'] == tanggal]
    if cuaca:
        filtered_df = filtered_df[filtered_df['weathersit'].isin(cuaca)]
    hours_full_range = pd.DataFrame({'hr': np.arange(24)})
    hourly_rentals = filtered_df.groupby('hr')['cnt'].sum().reset_index()
    hourly_rentals = hours_full_range.merge(hourly_rentals, on='hr', how='left').fillna(0)
    hourly_rentals = hourly_rentals.sort_values(by='hr')
    
    # Visualisasi data
    plt.figure(figsize=(30, 10))
    fig, ax = plt.subplots()
    sns.barplot(data=hourly_rentals, x='hr', y='cnt', ax=ax)
    
    for p in ax.patches:
        ax.annotate(format(p.get_height(), '.0f'), 
                    (p.get_x() + p.get_width() / 2., p.get_height()), 
                    ha='center', va='center', 
                    xytext=(0, 9), 
                    textcoords='offset points')

    plt.title('Sewa Sepeda Berdasarkan Jam Hari')
    plt.xlabel('Jam')
    plt.ylabel('Total Sewa')
    ax.set_xticks(np.arange(24))
    ax.set_xticklabels(np.arange(24))
    st.pyplot(fig)

def get_registered(df):
    return df['registered'].sum()

def get_casual(df):
    return df['casual'].sum()

def get_count(df):
    return df['cnt'].sum()

st.title('Bike Sharing Analysis')

# Mengonversi 'dteday' menjadi format datetime
all_df['dteday'] = pd.to_datetime(all_df['dteday'])

min_date = all_df["dteday"].min()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://files.klob.id/public/mig01/l32ovhf5/channels4_profile.jpg")
    st.text("David Samuel Sitorus \nm014b4ky1018")
    
    
col1, col2, col3 = st.columns(3)
total_registered = get_registered(all_df)
total_casual = get_casual(all_df)
total_count = get_count(all_df)

with col1:
    st.subheader("Total Registered Customer")
    st.info(total_registered, icon="🌟")
with col2:
    st.subheader("Total Casual Customer")
    st.info(total_casual, icon="🔰")
with col3:
    st.subheader("Total Customer")
    st.info(total_count, icon="👥")

## Info


tab1, tab2, tab3 = st.tabs(["Info", "Data Total Sewa per Jam", "Skor RFM"])

with tab1:
    
    st.header('Tabel Data Penyewaan Sepeda')
    st.write(f'Total rows: {len(all_df)}')

    # Mapping label kolom
    column_mapping = {
        'instant': 'Record Index',
        'dteday': 'Date',
        'season': 'Season (1: Spring, 2: Summer, 3: Fall, 4: Winter)',
        'yr': 'Year (0: 2011, 1: 2012)',
        'mnth': 'Month (1 to 12)',
        'hr': 'Hour (0 to 23)',
        'holiday': 'Holiday (1: Yes, 0: No)',
        'weekday': 'Weekday',
        'workingday': 'Working Day (1: Yes, 0: No)',
        'weathersit': 'Weather Situation (1-4)',
        'temp': 'Normalized Temperature (C)',
        'atemp': 'Normalized Feeling Temperature (C)',
        'hum': 'Normalized Humidity',
        'windspeed': 'Normalized Wind Speed',
        'casual': 'Casual Users',
        'registered': 'Registered Users',
        'cnt': 'Total Rentals'
    }

    start_row, end_row = st.slider(
        'Select range of rows to display',
        0, len(all_df), (0, 10)
    )

    filtered_df = all_df.iloc[start_row:end_row]
    renamed_df = filtered_df.rename(columns=column_mapping)

    st.dataframe(renamed_df)
    
## Data per jam 

with tab2:
    st.header('Data Total Sewa per Jam')
    
    tanggal = st.date_input(label='Tanggal yang Ingin Dicari', value = min_date)   
    weather_mapping = {
        1: 'Clear',
        2: 'Mist',
        3: 'Light Rain',
        4: 'Heavy Rain'
    }
    cuaca_options = [1, 2, 3, 4]  # Corresponds to Clear, Mist, Light Rain, Heavy Rain
    selected_cuaca = st.multiselect(
        'Pilih Cuaca',
        options=cuaca_options,
        format_func=lambda x: weather_mapping[x]
    )
    get_data_per_jam(str(tanggal), selected_cuaca)




## RFM

with tab3:
    st.header('Skor RFM')

    # Menghitung RFM

    # Ambil tanggal terakhir dalam dataset untuk perhitungan Recency
    today = all_df['dteday'].max()

    rfm = pd.DataFrame()
    rfm['Recency'] = (today - all_df['dteday']).dt.days  # Menghitung Recency
    rfm['Frequency'] = all_df['cnt']  # Menghitung Frequency
    rfm['Monetary'] = all_df['cnt'] * 1  # Mengasumsikan $1 per sewa

    # Menampilkan ringkasan RFM
    print(rfm.describe())

    # Mengelompokkan pengguna berdasarkan RFM
    rfm['R_Score'] = pd.qcut(rfm['Recency'], 4, labels=False)  # Semakin rendah semakin baik
    rfm['F_Score'] = pd.qcut(rfm['Frequency'], 4, labels=False)  # Semakin tinggi semakin baik
    rfm['M_Score'] = pd.qcut(rfm['Monetary'], 4, labels=False)  # Semakin tinggi semakin baik

    # Membuat skor gabungan
    rfm['RFM_Score'] = rfm['R_Score'] + rfm['F_Score'] + rfm['M_Score']
    print(rfm[['Recency', 'Frequency', 'Monetary', 'RFM_Score']])

    # Membuat hitungan setiap skor RFM
    rfm_score_counts = rfm['RFM_Score'].value_counts().sort_index()

    # Membuat plot
    plt.figure(figsize=(12, 6))
    fig, ax = plt.subplots()
    sns.barplot(x=rfm_score_counts.index, y=rfm_score_counts.values)

    # Menambahkan angka di atas setiap bar
    for p in ax.patches:
        ax.annotate(format(p.get_height(), '.0f'), 
                    (p.get_x() + p.get_width() / 2., p.get_height()), 
                    ha = 'center', va = 'center', 
                    xytext = (0, 9), 
                    textcoords = 'offset points')
        

    plt.title('Distribusi Skor RFM')
    plt.xlabel('Skor RFM')
    plt.ylabel('Jumlah Pengguna')
    plt.xticks(rotation=0)
    st.pyplot(fig)
    
    with st.expander("Penjelasan"):
        st.write(
            """Dari grafik tersebut, kita dapat melihat bahwa sebagian besar 
            pelanggan memiliki skor RFM di kisaran 2 hingga 7, dengan puncak 
            pada skor 7 yang mencapai 2880 pengguna.
            """
        )

