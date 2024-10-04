import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Membaca file CSV yang berisi data penyewaan sepeda
all_df = pd.read_csv("dashboard/all_data.csv")
all_df.reset_index(inplace=True)

# Mengonversi kolom 'dteday' menjadi format datetime
all_df['dteday'] = pd.to_datetime(all_df['dteday'])


# Fungsi untuk mendapatkan total sewa per jam pada tanggal tertentu dan kondisi cuaca tertentu
def get_data_per_jam(tanggal, cuaca=None):
    
    # Filter dataframe berdasarkan tanggal yang dipilih
    filtered_df = all_df[all_df['dteday'] == tanggal]
    
    # Jika pengguna memilih kondisi cuaca tertentu, filter berdasarkan cuaca
    if cuaca:
        filtered_df = filtered_df[filtered_df['weathersit'].isin(cuaca)]
    
    # Membuat range penuh dari jam 0 hingga 23
    hours_full_range = pd.DataFrame({'hr': np.arange(24)})
    
    # Mengelompokkan data berdasarkan jam dan menjumlahkan total sewa
    hourly_rentals = filtered_df.groupby('hr')['cnt'].sum().reset_index()
    
    # Melakukan join untuk memastikan setiap jam terwakili meskipun tidak ada sewa pada jam tersebut
    hourly_rentals = hours_full_range.merge(hourly_rentals, on='hr', how='left').fillna(0)
    hourly_rentals = hourly_rentals.sort_values(by='hr')
    
    # Visualisasi data dengan bar chart
    plt.figure(figsize=(30, 10))
    fig, ax = plt.subplots()
    sns.barplot(data=hourly_rentals, x='hr', y='cnt', ax=ax)
    
    # Menambahkan label pada setiap bar
    for p in ax.patches:
        ax.annotate(format(p.get_height(), '.0f'), 
                    (p.get_x() + p.get_width() / 2., p.get_height()), 
                    ha='center', va='center', 
                    xytext=(0, 9), 
                    textcoords='offset points')

    plt.title(f'Sewa Sepeda Berdasarkan Jam di Tanggal {str(tanggal)}')
    plt.xlabel('Jam')
    plt.ylabel('Total Sewa')
    ax.set_xticks(np.arange(24))
    ax.set_xticklabels(np.arange(24))
    
    # Menampilkan plot di Streamlit
    st.pyplot(fig)


# Fungsi untuk mendapatkan total pengguna terdaftar
def get_registered(df):
    return df['registered'].sum()

# Fungsi untuk mendapatkan total pengguna kasual
def get_casual(df):
    return df['casual'].sum()

# Fungsi untuk mendapatkan total sewa
def get_count(df):
    return df['cnt'].sum()

# Judul aplikasi di halaman utama
st.title('Bike Sharing Analysis')

# Mendapatkan tanggal minimum dan maksimum dari dataset
min_date = all_df["dteday"].min()
max_date = all_df["dteday"].max()

# Bagian sidebar, menampilkan logo dan informasi pengguna
with st.sidebar:
    st.image("https://files.klob.id/public/mig01/l32ovhf5/channels4_profile.jpg")
    st.text("David Samuel Sitorus \nm014b4ky1018")
    
# Menampilkan informasi total pengguna dan total sewa dalam kolom
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

# Tabs untuk menampilkan beberapa informasi berbeda dalam aplikasi
tab1, tab2, tab3, tab4 = st.tabs(["Info", "Data Total Sewa per Jam", "Skor RFM", "Korelasi Pelanggan dengan Cuaca"])

# Tab pertama: Menampilkan tabel data penyewaan sepeda
with tab1:
    
    st.header('Tabel Data Penyewaan Sepeda')
    st.write(f'Total rows: {len(all_df)}')

    # Mapping untuk penamaan label kolom agar lebih deskriptif
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

    # Filter data berdasarkan rentang tanggal
    start_date, end_date = st.date_input(label='Tanggal yang Ingin Dicari',
                                         min_value=min_date, 
                                         max_value=max_date,
                                         value=[min_date, max_date]
    )

    filtered_df = all_df[(all_df["dteday"] >= str(start_date)) & (all_df["dteday"] <= str(end_date))]
    renamed_df = filtered_df.rename(columns=column_mapping)
    
    # Menampilkan dataframe yang telah difilter
    st.dataframe(renamed_df)
    
# Tab kedua: Data total sewa per jam
with tab2:
    st.header('Data Total Sewa per Jam')
    
    st.subheader('Data Total Sewa per Jam Secara Keseluruhan')
    
    # Mengelompokkan data berdasarkan jam dan menjumlahkan total sewa
    hourly_rentals = all_df.groupby('hr')['cnt'].sum().reset_index()

    # Membuat figure dan axis untuk plotting
    plt.figure(figsize=(15, 10))
    fig, ax = plt.subplots()

    # Menggunakan seaborn lineplot untuk membuat grafik garis
    sns.lineplot(data=hourly_rentals, x='hr', y='cnt', ax=ax, marker='o')

    # Menambahkan label ke setiap titik di plot
    for x, y in zip(hourly_rentals['hr'], hourly_rentals['cnt']):
        ax.text(x, y + y * 0.05, f'{y:.0f}', ha='center', va='bottom', fontsize=10, rotation=90,
                bbox=dict(facecolor='white', edgecolor='none', boxstyle='round,pad=0.3'))

    # Menambahkan judul, label sumbu, dan menyesuaikan ticks
    ax.set_title('Sewa Sepeda Berdasarkan Jam Total', loc='left')
    ax.set_xlabel('Jam', fontsize=12)
    ax.set_ylabel('Total Sewa', fontsize=12)
    ax.set_xticks(hourly_rentals['hr'])
    ax.grid(True)

    # Menampilkan plot di Streamlit
    st.pyplot(fig)

    st.subheader('Data Total Sewa per Jam Sesuai Tanggal Filter')
    
    # Pengguna dapat memilih tanggal yang ingin dianalisis
    tanggal = st.date_input(label='Tanggal yang Ingin Dicari', value=min_date)   
    
    # Pilihan cuaca yang tersedia untuk filter
    weather_mapping = {
        1: 'Clear',
        2: 'Mist',
        3: 'Light Rain',
        4: 'Heavy Rain'
    }
    cuaca_options = [1, 2, 3, 4]  # Sesuai dengan cuaca Clear, Mist, Light Rain, Heavy Rain
    
    # Pengguna dapat memilih cuaca untuk memfilter data
    selected_cuaca = st.multiselect(
        'Pilih Cuaca untuk Filter Data',
        options=cuaca_options,
        format_func=lambda x: weather_mapping[x]
    )
    
    
    # Memanggil fungsi untuk menampilkan data sewa per jam berdasarkan filter yang dipilih
    get_data_per_jam(str(tanggal), selected_cuaca)

# Tab ketiga: Skor RFM (Recency, Frequency, Monetary)
with tab3:
    st.header('Skor RFM')

    # Fungsi untuk menghitung dan menampilkan skor RFM
    def rfm_scores():
        # Menggunakan tanggal terakhir dalam dataset sebagai acuan untuk menghitung Recency
        today = all_df['dteday'].max()

        # Menghitung metrik RFM
        rfm = pd.DataFrame()
        rfm['Recency'] = (today - all_df['dteday']).dt.days  # Menghitung Recency
        rfm['Frequency'] = all_df['cnt']  # Menghitung Frequency
        rfm['Monetary'] = all_df['cnt'] * 1  # Mengasumsikan $1 per sewa

        # Menampilkan ringkasan statistik RFM
        print(rfm.describe())

        # Mengelompokkan pengguna berdasarkan kuartil RFM
        rfm['R_Score'] = pd.qcut(rfm['Recency'], 4, labels=False)  # Semakin rendah semakin baik
        rfm['F_Score'] = pd.qcut(rfm['Frequency'], 4, labels=False)  # Semakin tinggi semakin baik
        rfm['M_Score'] = pd.qcut(rfm['Monetary'], 4, labels=False)  # Semakin tinggi semakin baik

        # Membuat skor gabungan RFM
        rfm['RFM_Score'] = rfm['R_Score'] + rfm['F_Score'] + rfm['M_Score']
        print(rfm[['Recency', 'Frequency', 'Monetary', 'RFM_Score']])

        # Hitung jumlah pengguna untuk setiap skor RFM
        rfm_score_counts = rfm['RFM_Score'].value_counts().sort_index()

        # Membuat plot untuk distribusi skor RFM
        plt.figure(figsize=(12, 6))
        fig, ax = plt.subplots()
        sns.barplot(x=rfm_score_counts.index, y=rfm_score_counts.values)

        # Menambahkan label pada setiap bar
        for p in ax.patches:
            ax.annotate(format(p.get_height(), '.0f'), 
                        (p.get_x() + p.get_width() / 2., p.get_height()), 
                        ha = 'center', va = 'center', 
                        xytext = (0, 9), 
                        textcoords = 'offset points')

        plt.title('Distribusi Skor RFM')
        plt.xlabel('Skor RFM')
        plt.ylabel('Jumlah Pelanggan')
        plt.xticks(rotation=0)
        
        # Menampilkan plot di Streamlit
        st.pyplot(fig)
    
    # Menampilkan grafik skor RFM
    rfm_scores()
    
    # Penjelasan terkait hasil analisis RFM
    with st.expander("Penjelasan"):
        st.write(
            """Dari grafik tersebut, kita dapat melihat bahwa sebagian besar 
            pelanggan memiliki skor RFM di kisaran 2 hingga 7, dengan puncak 
            pada skor 6 yang mencapai 2880 pelanggan.
            """
        )

# Tab keempat: Korelasi penyewaan sepeda dengan cuaca
with tab4:

    st.header('Korelasi Pelanggan Penyewaan Sepeda dengan Cuaca')
    
    # Fungsi untuk menampilkan total sewa berdasarkan kondisi cuaca
    def weather_group(filtered_df):

        # Mapping untuk kondisi cuaca
        weather_mapping = {
            1: 'Clear',
            2: 'Mist',
            3: 'Light Rain',
            4: 'Heavy Rain'
        }
        filtered_df['weather_condition'] = filtered_df['weathersit'].map(weather_mapping)

        # Mengelompokkan data berdasarkan kondisi cuaca dan menjumlahkan total sewa
        weather_grouped = filtered_df.groupby('weather_condition')['cnt'].sum().reset_index()

        # Fungsi untuk menambahkan label di atas setiap bar
        def addlabels(x, y):
            for i in range(len(x)):
                plt.text(i, y[i], f'{y[i]:,.0f}', ha='center', va='bottom', fontsize=10)

        # Membuat visualisasi bar chart untuk total sewa berdasarkan cuaca
        plt.figure(figsize=(10, 6))
        fig, ax = plt.subplots()
        sns.barplot(data=weather_grouped, x='weather_condition', y='cnt')
        addlabels(weather_grouped['weather_condition'], weather_grouped['cnt'])
        plt.title('Total Sewa Sepeda Berdasarkan Kondisi Cuaca')
        plt.xlabel('Kondisi Cuaca')
        plt.ylabel('Total Sewa')
        plt.xticks(rotation=45)
        
        # Menampilkan plot di Streamlit
        st.pyplot(fig)
    
    # Menambahkan filter tanggal menggunakan st.date_input
    start_date, end_date = st.date_input("Filter data dengan tanggal", min_value=min_date, 
                                            max_value=max_date,
                                            value=[min_date, max_date])

    # Filter data berdasarkan rentang tanggal yang dipilih
    filtered_df = all_df[(all_df['dteday'] >= pd.to_datetime(start_date)) & 
                        (all_df['dteday'] <= pd.to_datetime(end_date))]

    # Memanggil fungsi untuk menampilkan total sewa berdasarkan cuaca
    weather_group(filtered_df)

    # Penjelasan terkait hasil analisis cuaca
    with st.expander("Penjelasan"):
        st.write(
            """Berdasarkan bar chart di atas, berikut adalah beberapa kesimpulan terkait total sewa sepeda berdasarkan kondisi cuaca:

- Cuaca Cerah (Clear): Merupakan kondisi cuaca dengan jumlah sewa sepeda tertinggi, mencapai lebih dari 2,3 juta total sewa. Ini menunjukkan bahwa penyewaan sepeda paling populer ketika cuaca cerah, kemungkinan karena cuaca yang mendukung untuk aktivitas luar ruangan.

- Cuaca Berkabut (Mist): Meskipun jauh di bawah cuaca cerah, kondisi berkabut masih memiliki jumlah total sewa yang cukup tinggi, sekitar 795.952. Hal ini menunjukkan bahwa kabut ringan tidak secara signifikan menghambat penyewaan sepeda.

- Hujan Ringan (Light Rain): Penyewaan sepeda menurun cukup signifikan saat terjadi hujan ringan, dengan total sewa sekitar 158.331. Ini mengindikasikan bahwa pelanggan mungkin kurang tertarik menyewa sepeda dalam kondisi hujan, meskipun tidak terlalu lebat.

- Hujan Lebat (Heavy Rain): Jumlah sewa sepeda paling rendah terjadi saat hujan lebat, hanya sebanyak 223 total sewa. Ini menunjukkan bahwa hujan lebat hampir sepenuhnya menghentikan aktivitas penyewaan sepeda, mungkin karena faktor keselamatan dan kenyamanan.
            """
        )
