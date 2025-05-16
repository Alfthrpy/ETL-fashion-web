from utils.extract import scrape
from utils.transform import transform_data
from utils.load import save_to_csv,save_to_spreadsheet,save_to_postgres



def main():
    df = scrape()
    df_clean = transform_data(df,16000)
    save_to_csv(df_clean,'products.csv','D:/CODING/PYTHON/SUBMISSION PROCESSING DATA')
    save_to_spreadsheet(df_clean,"1TKH2hZ5Z_vEOHCi-FL0bRPCpClMcXYVE4c9BZNowFW0",'google-sheets-api.json','Sheet1!A2:H')

    db_url = 'postgresql+psycopg2://developer:password@localhost:5432/fashiondb'
    save_to_postgres(df_clean,db_url)


if __name__ == '__main__':
    main()