#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 12 20:40:35 2022

@author: goncalodelacerda
"""
import pandas as pd
from collections import Counter
import csv
import re

#imports both csvs as dataframes. 
speeches = pd.read_csv("speeches.csv", sep='|')
fx = pd.read_csv("fx.csv", skiprows=3, header = 1)

#removes rows from fx where there isnt a value on the US dollar column. Renames columns.
fx = fx[fx["[US dollar ]"] != "-"]
fx = fx.rename(columns={r"Period\Unit:": "date"}, index={"ONE":"Row_1"})
fx = fx.rename(columns={"[US dollar ]": "exchange_rate"}, index={"ONE":"Row_1"})

#removes rows from speeches where there are null values in any cell.
speeches = speeches.dropna(how="any",axis=0)

#merge both dataframes where there are common dates. Then remove any cells with null values.
fx_speeches = pd.merge(speeches, fx, how="left", on=["date"])
fx_speeches = fx_speeches.dropna(how="any",axis=0)

#convert exchange from string to float
fx_speeches["exchange_rate"] = pd.to_numeric(fx_speeches["exchange_rate"], downcast ="float")

#create a new dataframe by assigning new variable to our original combined dataframe, which is the exchange return.
fx_speeches_return = fx_speeches.assign(exchange_return = (fx_speeches["exchange_rate"] - fx_speeches["exchange_rate"].shift()) / fx_speeches["exchange_rate"].shift() * 100)

#create new dataframes with calculated bad news or good news. Finalises by removing any new null cells.
fx_speeches_return_good_news = fx_speeches_return.assign(good_news = fx_speeches_return["exchange_return"].apply(lambda x: '1' if x > 0.5 else '0'))
fx_speeches_return_good_bad_news = fx_speeches_return_good_news.assign(bad_news = fx_speeches_return["exchange_return"].apply(lambda x: '1' if x < -0.5 else '0'))
df = fx_speeches_return_good_bad_news.dropna(how="any",axis=0)
 
#creates new dataframes and includes only the rows where good_news = 1 and bad_news = 1. Then lowers all letters and removes articles and connectors.

df_goodnews_1 = df[df.good_news == "1"]
df_goodnews_1["title"] = df_goodnews_1["title"].str.lower()
df_goodnews_1["title"] = df_goodnews_1["title"].str.replace("( a | an | and | the | from | on | at | to | it | of | for | for | as | in | la | - )", " ")

df_badnews_1 = df[df.bad_news == "1"]
df_badnews_1["title"] = df_badnews_1["title"].str.lower()
df_badnews_1["title"] = df_badnews_1["title"].str.replace("( a | an | and | the | from | on | at | to | it | of | for | for | as | in | la | - )", " ")


#create 2 lists with the 20 most common word each. Turn them into dataframes, and then turn them into csvs.

commonwords_goodnews_list = (Counter(" ".join(df_goodnews_1["title"].str.lower().str.replace("( a | an | and | the | from | on | at | to | it | of | for | for | as | in | la | - |the)", " ")).split()).most_common(20))
commonwords_goodnews_df = pd.DataFrame(commonwords_goodnews_list)
commonwords_goodnews_df.to_csv("Good News: Most Common 20 words", index=False, header=True)

commonwords_badnews_list = (Counter(" ".join(df_badnews_1["title"].str.lower().str.replace("( a | an | and | the | from | on | at | to | it | of | for | for | as | in | la | - |the)", " ")).split()).most_common(20))
commonwords_badnews_df = pd.DataFrame(commonwords_badnews_list)
commonwords_badnews_df.to_csv("Bad News: Most Common 20 words", index=False, header=True)
