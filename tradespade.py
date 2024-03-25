import requests
import pandas as pd
from yahoo_fin import stock_info as si
from pandas_datareader import DataReader
import numpy as np
from nsetools import Nse
nse = Nse()
#from urllib.request import urlopen, Request
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import string
import preprocessor as p
import os
import time
from time import sleep
from bs4 import BeautifulSoup
import RiskyBusiness as rb
#from twitterscraper import query_tweets
from twitter_scraper import get_tweets
from tqdm.notebook import tqdm
from os import path
from datetime import datetime
from pathlib import Path
import emoji
import json
import csv

#from functools import lru_cache
now = datetime.now()
daily = now.strftime("%m/%d/%Y")
daily = daily.replace("/","_")
check = emoji.emojize(":heavy_check_mark:")
xmark = emoji.emojize(":x:")
bluecircle = emoji.emojize(":green_circle:")
red_circle = emoji.emojize(":red_circle:")

def gettickers():
    #ustickerkeys = si.tickers_sp500()
    #tickersdict = nse.get_stock_codes()
    reader = csv.reader(open('tickersdict.csv', 'r'))
    tickersdict = {}
    for row in reader:
        z, x = row
        tickersdict[z] = x

    tickerkeys = list(tickersdict.keys())
    tickervalues = list(tickersdict.values())
    #key_df = pd.DataFrame(tickerkeys)
    #key_df.to_csv("key_df.csv")

    stock_csv = str('company_08_18_2020.csv')
    stock_file = Path(stock_csv)
    if stock_file.is_file():
        print("Reading Stock Data")
        new_df = pd.read_csv(stock_csv)
    else:
        print("Getting Stock Data")
        recommendations = []
        try:
            for ticker in tqdm(tickerkeys):
                lhs_url = 'https://query2.finance.yahoo.com/v10/finance/quoteSummary/'
                rhs_url = '?formatted=true&crumb=swg7qs5y9UP&lang=en-US&region=US&' \
                          'modules=upgradeDowngradeHistory,recommendationTrend,' \
                          'financialData,earningsHistory,earningsTrend,industryTrend&' \
                          'corsDomain=finance.yahoo.com'

                urlrec =  lhs_url + ticker + rhs_url
                r = requests.get(urlrec)
                if not r.ok:
                    recommendation = 99
                try:
                    result = r.json()['quoteSummary']['result'][0]
                    recommendation =result['financialData']['recommendationMean']['fmt']
                except:
                    recommendation = 99

                recommendations.append(recommendation)
        except:
            print("Some issue")

        #def getrecommendations():
        data_tuples = list(zip(tickerkeys , recommendations))
        df = pd.DataFrame(data_tuples, columns = ['Company', 'Recommendations'], dtype= float)
        pd.set_option("display.max_rows", None, "display.max_columns", None)
        df['Recommendations'] = pd.to_numeric(df['Recommendations'])
        df = df[df.Recommendations != 99]
        df.sort_values(by=['Recommendations'],ascending = True)
        df = df.iloc[1:]
        #def segregate():
        buy_df = df[df.Recommendations <= 1.5]
        #hold_df = df[df.Recommendations >= 2.5 and df.Recommendations <= 3.5]
        sell_df = df[df.Recommendations >= 4.5]
        df_list = [buy_df, sell_df]
        new_df = pd.concat(df_list)
        new_df.reset_index(level=0, inplace=True)
        new_df.to_csv(stock_csv)


    newkeys =[]
    for index, rows in new_df.iterrows():
        newkeys.append(rows.Company)

    newdict = {}
    for k,v in tickersdict.items():
        for i in newkeys:
            if i==k:
                newdict[k] = v

    newvalues = list(newdict.values())
    newvalues1 = [" ".join([
                    words for words in sentence.split()
                    if '(' not in words and ')' not in words and not words.startswith('Limited')])
                    for sentence in newvalues]
    newvalues1 = [x.replace(' ', '_') for x in newvalues1]
    newvalues2 = ["#" + value for value in newvalues1]

    news_csv = str('news_08_18_2020.csv')
    news_file = Path(news_csv)
    if news_file.is_file():
        #os.path.isfile('./y')
        print("Reading News Data")
        scored_news = pd.read_csv(news_csv)

    else:
        print("Getting News for the date", daily)
        words_cleaned = [" ".join([
                        words for words in sentence.split()
                        if '(' not in words and ')' not in words and not words.startswith('Limited')])
                        for sentence in newvalues]

        words_cleaned = [x.replace(' ', '-') for x in words_cleaned]

        parsed_news = []
        for ticker in tqdm(words_cleaned):
            newsurl = 'https://www.livemint.com/Search/Link/Keyword/'+ticker
            page = ''
            header = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            while page == '':
                try:
                    page = requests.get(newsurl,headers = header)
                    break

                except:
                    print("Connection refused by the server..")
                    print("Let me sleep for 5 seconds")
                    print("ZZzzzz...")
                    time.sleep(5)
                    print("Was a nice sleep, now let me continue...")
                    continue
            soup = BeautifulSoup(page.content, 'html.parser')

            for x in soup.findAll('h2' ,class_='headline'):
            #if y in soup.findAll(data-updatedlongtime>="01 Jan 2020"):
                text = x.get_text().lstrip()
                parsed_news.append([ticker, text])

                columns = ['ticker', 'headline']
                scored_news = pd.DataFrame(parsed_news, columns=columns)
        scored_news['ticker'] = scored_news['ticker'].str.replace('-','_')
        scored_news['ticker'] = ('#' + scored_news['ticker'])
        scored_news = scored_news.groupby(['ticker'], as_index = False).agg({'headline': ''.join}, Inplace=True)

        #NewsFeed Sentiment
        vader = SentimentIntensityAnalyzer()
        scores = scored_news['headline'].apply(vader.polarity_scores).tolist()
        scores_df = pd.DataFrame(scores)
        scored_news = scored_news.join(scores_df, rsuffix='_right')
        scored_news.to_csv(news_csv)


    # TWITTER
    tweets_csv = str('tweets_08_18_2020.csv')
    tweet_file = Path(tweets_csv)
    if tweet_file.is_file():
        all_tweets_df = pd.read_csv(tweets_csv)

    else:
        print("Getting Twitter data for the date : ", daily)
        all_tweets_df = pd.DataFrame()
        #twitvals = newvalues2
        #twitvals = [x.replace('#', ' ') for x in newvalues2]
        for word in tqdm(newvalues2):
          tweets = get_tweets(word, pages = 1)
          try:
            for tweet in tweets:
              _ = pd.DataFrame({'ticker' : word,
                                'headline' : [tweet['text']],
                              })
              all_tweets_df = all_tweets_df.append(_, ignore_index = True)
          except Exception as e:
            print(word, ':', e)
            continue

        all_tweets_df = all_tweets_df.groupby(['ticker'], as_index = False).agg({'headline': ''.join}, Inplace=True)

        vader = SentimentIntensityAnalyzer()
        #Twitter Sentiment
        scoretweets = all_tweets_df['headline'].apply(vader.polarity_scores).tolist()
        scoretweets_df = pd.DataFrame(scoretweets)
        all_tweets_df = all_tweets_df.join(scoretweets_df, rsuffix='_right')
        all_tweets_df.to_csv(tweets_csv)



#def finalscore():
    #FINALSCORE
    #all_tweets_df, scored_news = mining()
    dfinal = scored_news.merge(all_tweets_df, on="ticker", how = 'right').fillna(0)
    sum_column = (dfinal["compound_x"] + dfinal["compound_y"])/2
    dfinal["compound_z"] = sum_column
    qdata = dfinal[['ticker', 'compound_z']].copy()

    #PRINTING
    vader_Buy=[]
    vader_Sell=[]
    r1 = []
    for i in range(len(qdata)):
        if qdata['compound_z'].values[i] > 0.20:
            r1 = "Trade Call for {row} is Buy.".format(row=qdata['ticker'].iloc[i])
            vader_Buy.append(qdata['ticker'].iloc[i])
    #vader_Buy = [e[1:] for e in vaderBuy]
    for i in range(len(qdata)):
        if qdata['compound_z'].values[i] < -0.20:
            r2 = "Trade Call for {row} is Buy.".format(row=qdata['ticker'].iloc[i])
            vader_Sell.append(qdata['ticker'].iloc[i])

    blue_diamond = emoji.emojize(":small_blue_diamond:")
    orange_diamond = emoji.emojize(":small_orange_diamond:")
    BuyList= []
    for bu in vader_Buy:
        BuyString = bu.replace("#", bluecircle+" ")
        BuyList.append(BuyString)

    SellList= []
    for se in vader_Sell:
        SellString = se.replace("#", red_circle+" ")
        SellList.append(SellString)

    Buy = '\n'
    Sell = '\n'
    Buy = (Buy.join(BuyList))
    Sell = (Sell.join(SellList))
    print(Buy)
    print(Sell)



#def messenger():
    #Buy,Sell = finalscore()
    b = 'BUY : \n'
    s = 'SELL : \n'
    x = b + Buy + "\n\n" + s + Sell
    print("Success")
    return x
"""def test():
    hbostr = ' Date :  '
    hbo = 'Hello, Stranger'
    hbp = (hbostr.join(hbo))
    b = 'Buy These Stocks : '
    s = 'Sell These Stocks : '
    x = 'HOlaaa' + hbp + "\n" + b + "\t" + s
    return hbo"""

if __name__ == "__main__":
    gettickers()
