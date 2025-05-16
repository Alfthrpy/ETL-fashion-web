import pandas as pd
import re

def transform_data(data: pd.DataFrame, exchange_rate: int) -> pd.DataFrame:
    '''Membersihkan data dan mentransformasikannya'''

    try:
        # Hapus duplikat
        data.drop_duplicates(inplace=True)

        # Dirty pattern
        dirty_pattern = {
            "Title": ['Unknown Product'],
            "Rating": ['⭐ Invalid Rating / 5', 'Not Rated'],
            "Price": ["Price Unavailable", None]
        }

        for key, value in dirty_pattern.items():
            if key in data.columns:
                data[key] = data[key].apply(lambda x: None if x in value else x)

        # Drop missing values
        data.dropna(inplace=True)

        # Transformasi kolom 'Price'
        if 'Price' in data.columns:
            data['Price_in_dolar'] = data['Price'].apply(
                lambda x: float(re.search(r"[\d.]+", x).group()) if pd.notnull(x) and re.search(r"[\d.]+", x) else 0
            )
            data['Price_in_rupiah'] = data['Price_in_dolar'] * exchange_rate
            data.drop(['Price'], axis=1, inplace=True)

        # Transformasi kolom 'Rating'
        if 'Rating' in data.columns:
            data['Rating'] = data['Rating'].apply(
                lambda x: float(x.split()[1]) if isinstance(x, str) and len(x.split()) >= 2 and x.split()[1].replace('.', '', 1).isdigit() else None
            )

        # Transformasi kolom 'Colors'
        if 'Colors' in data.columns:
            data['Colors'] = data['Colors'].apply(
                lambda x: int(x.split()[0]) if isinstance(x, str) and x.split()[0].isdigit() else None
            )

        # Transformasi kolom 'Timestamp'
        if 'Timestamp' in data.columns:
            data['Timestamp'] = pd.to_datetime(data['Timestamp'], errors='coerce')

        return data

    except Exception as e:
        print(f"Terjadi error saat transformasi data: {e}")
        return None
