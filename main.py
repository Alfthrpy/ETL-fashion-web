from utils.extract import scrape
from utils.transform import transform_data



def main():
    df = scrape()
    df_clean = transform_data(df,16000)

    df_clean.to_csv('clean.csv')


if __name__ == '__main__':
    main()