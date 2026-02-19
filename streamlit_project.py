import warnings #Nicht entfernen (frag' nicht warum)
import sys #Selbe Story
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pandas import isna

import streamlit_analysis as sta
import numpy as np
import html

#Design/Layout Basics
st.set_page_config(
    page_title="DAX App",
    layout="wide"
)

# Lädt Daten in session state und dann in Variable
@st.cache_data
def load_data():
    return pd.read_csv("DAXDataStreamlit.csv")

data = load_data()

#####################################################################################################
#Sidebar
st.sidebar.header("Sidebar")
st.sidebar.write("Hier kannst du die zu analysierenden Aktien auswählen:")

selected_stocks = st.sidebar.pills("Auswahl", data.iloc[:,1].drop_duplicates(), selection_mode='multi')

#Erstellt Arbeitskopie der Daten
filtered_data = data
#Entfernt Zeitzone durch String-Konversion und Slicing nach den ersten 11 Zeichen
filtered_data['Date'] = filtered_data['Date'].astype(str).str[:10] 
#Transformiert zu maschinen-freundlichem Datetime-Format
filtered_data['Date'] = pd.to_datetime(filtered_data['Date'], errors='coerce')

#Extrahiert erstes/letztes Datum für Zeit-Slider
first_date = filtered_data['Date'].min().to_pydatetime()
last_date = filtered_data['Date'].max().to_pydatetime()

#Erzeugt Dataframe, der nur Zeilen der ausgewählten Aktien beinhaltet (Angenommen zweite Spalte enthält die Namen d. Aktien)
stock_filtered_data = filtered_data[data.iloc[:, 1].isin(selected_stocks)]


#################################################################################################################
#Popover für Zeit-Einstellungen
with st.popover("Zeit-Einstellungen"):
    date_range = (first_date, last_date)
    if selected_stocks:
        #Erzeugt einen Slider für den Zeitrahmen
        selected_date_range = st.slider(
            "Wähle den Zeitraum aus:",
            min_value=first_date,
            max_value=last_date,
            value=date_range,  # Setzt den Zeitrahmen standardmäßig auf den vollständigen Zeitraum
            format="YYYY-MM-DD",
            step=pd.Timedelta(weeks=1).to_pytimedelta()  # Ensure the slider moves in one-week steps
        )

with st.popover("Metrik-Auswahl"):
    metric = st.selectbox("Wähle die darzustellende Metrik", ["Open", "High", "Low", "Close", "Volume"], index=3)

if selected_stocks:
    # Adapt the used date range based on slider selection
    stock_filtered_data = stock_filtered_data[
        (stock_filtered_data['Date'] >= selected_date_range[0]) &
        (stock_filtered_data['Date'] <= selected_date_range[1])
    ]

######################################################################################################
# Graph/Hauptteil
st.header("Projekt DAX-Analyse")
"Mit dieser App kannst du die letzten **sechs Monate** des DAX analysieren. :chart:"


col1_graph, col2_tools = st.columns([2, 1])


with col1_graph:
    st.write("") # Für die Optik
    if selected_stocks:
        fig, ax = plt.subplots(figsize=(10, 6))

        #Gruppiert nach Datum und plotted jede gewählte Aktie
        for stock in selected_stocks:
            stock_data = stock_filtered_data[stock_filtered_data.iloc[:, 1] == stock]
            ax.plot(stock_data.iloc[:, 2], stock_data.loc[:, metric], label=stock)  # Assuming last column is the stock price

        #Graph Konfiguration
        ax.xaxis.set_major_locator(mdates.MonthLocator())  # Show ticks at the start of each month
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))  # Format ticks as 'Year-Month'
        plt.xticks(rotation=45)  # Rotiert x-Achsen Labels für Lesbarkeit
        ax.set_title("Aktienpreise im Zeitverlauf")
        ax.set_xlabel("Datum")
        ax.set_ylabel("Preis [€]")
        ax.legend()
        ax.grid(True)
        plt.tight_layout()
        
        #Zeigt den Graphen für die ausgewählten Aktien
        st.pyplot(fig)

    else:
        st.write("Wähle Aktien aus der Sidebar aus um Analysen durchzuführen!")
    
    if st.toggle("Dataframe anzeigen:"):
        st.dataframe(stock_filtered_data)

############################################# TABS ######################################################
with col2_tools:
    st.header("Analyse-Tools")
    a, b, c = st.tabs(["Averages", "Volatility", "Insights"])


############################################# TAB a (Averages)
    with a:
        a_metric = st.selectbox("Wähle die Aktien-Kursart (Metrik):", ["Open", "Close", "High", "Low"], index=1)
        st.markdown(f'<h4 style="color:#0b3d91;">Durchschnittl. {a_metric}-Preis:</h3>', unsafe_allow_html=True)
        #st.subheader(f"Durchschnittl. {a_metric}-Preis:")
        avg = sta.average_price(stock_filtered_data, a_metric)
        if avg == {}:
            st.write("Keine Aktie in Sidebar ausgewählt!")
        else:
            for name, value in avg.items():
                st.write(f"{name}:  {value:.3f}€")


############################################# TAB b (Volatility)
    with b:
        st.write(f"Einblick in Volatilität des Aktienpreises (Metrik: {a_metric})")
        stock_statistik = st.selectbox("Statistische Berechnungsart auswählen:", ["Standardabweichung", "Durchschnittliche Schwankungsbreite"], index=0)
        statistik_calc = sta.volatility(stock_filtered_data, stock_statistik, a_metric)
        if statistik_calc == {}:
            st.write("Keine Aktie in Sidebar ausgewählt!")
        else:
            for name, value in statistik_calc.items():
                st.write(f"{name}:  {value:.3f}€")


############################################# TAB c (Insights ROI)
    with c:
        st.write("Einblick,  \n wie sich verschiedene Branchen und Sektoren verhalten (ROI)")
        industrie_sectors = data.iloc[:, 8].dropna().astype(str)
        unique_ind_sector = sorted(industrie_sectors.unique())

        st.markdown(f'<h4 style="color:#0b3d91;">Durchschnittlicher ROI über volle Zeitspanne</h3>', unsafe_allow_html=True)

        result_placeholder = st.empty()

        with st.expander("Auswahl Industriesektoren"):
            if not unique_ind_sector:
                st.write("Auswahl treffen")
            else:
                pill_pallet = st.pills("Auswahl", unique_ind_sector, selection_mode='single')
                pill_result = sta.insights(data, pill_pallet)

        if isna(pill_pallet):
            result_placeholder.write("Bitte Industriesektor wählen")
        else:
            result_placeholder.markdown(f"{pill_pallet}: <span style='color:#000000'><strong>{pill_result:.3f}€</span>",
                                        unsafe_allow_html=True)

