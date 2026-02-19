import pandas as pd
import numpy as np

def average_price(dataframe, selected_metric):
    results = {}
    
    # Stellt sicher, dass die Spalte mit Aktiennamen existiert und
    # nur einzigartige Werte hat
    stock_names = dataframe.iloc[:, 1].unique()  # Vorausgesetzt Aktiennamen sind in der zweiten Spalte
    for stock in stock_names:
        # Filtert die Zeile nach den selektierten Aktien
        selected_stock_data = dataframe[dataframe.iloc[:, 1] == stock]
        # Berechnet den Durchschnitt für die aktuelle Aktie
        avg = selected_stock_data[selected_metric].mean()
        # Speichert das Ergebnis im "results" dictionary
        results[stock] = avg
   
    return results

###################################################################

def volatility(dataframe, selected_avg, selected_metric):
    results = {}
    stock_names = dataframe.iloc[:, 1].unique()  # Vorausgesetzt Aktiennamen sind in der zweiten Spalte
    for stock in stock_names:
        # Filtert Zeilen nach gewählten Aktien
        selected_stock_data = dataframe[dataframe.iloc[:, 1] == stock].copy()

        if selected_avg == "Standardabweichung":
            # Berechnet Standardabweichung für die Spalte m. d. gewählten Metrik
            avg = selected_stock_data[selected_metric].std()
            results[stock] = avg

        elif selected_avg == "Durchschnittliche Schwankungsbreite":
            # Prüft, ob die notwendige Spalte tatsächlich existiert
            if "High" in selected_stock_data.columns and "Low" in selected_stock_data.columns and "Close" in selected_stock_data.columns:
                # Berechne die "True Range" (TR)
                selected_stock_data["Previous Close"] = selected_stock_data["Close"].shift(1)
                selected_stock_data["TR"] = np.maximum(
                    selected_stock_data["High"] - selected_stock_data["Low"],
                    np.maximum(
                        abs(selected_stock_data["High"] - selected_stock_data["Previous Close"]),
                        abs(selected_stock_data["Low"] - selected_stock_data["Previous Close"])
                    )
                )

                # Entfernt Zeilen mit NaN (erste Spalte nach Shift)
                selected_stock_data.dropna(subset=["TR"], inplace=True)

                # Berechne ATR mit den verfügbaren Zeilen
                atr_period = len(selected_stock_data)  # Um immer die volle Zeitspanne zu nutzen
                if atr_period > 1:  # Stellt sicher, dass genug Zeilen f. d. Berechnung vorhanden sind
                    selected_stock_data["ATR"] = selected_stock_data["TR"].rolling(window=atr_period).mean()
                    results[stock] = selected_stock_data["ATR"].iloc[-1]  # Extrahiert den letzten ATR-Wert
                else:
                    results[stock] = np.nan  # Nicht genug Daten für ATR
            else:
                results[stock] = np.nan  # Notwendige Spalten fehlen

    return results

########################################################################

def insights(dataframe, sector):
    sector_data = dataframe[dataframe.iloc[:, -2] == sector]
    stock_names = sector_data.iloc[:, 1].unique()
    sector_return = 0
    for i in stock_names:
        stock_data = sector_data[sector_data.iloc[:, 1] == i]
        roi = stock_data["Close"].iloc[-1] - stock_data["Close"].iloc[0]
        sector_return += roi
    return sector_return/len(stock_names) if len(stock_names) > 0 else 0

