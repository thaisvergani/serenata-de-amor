from django.shortcuts import render

from jarbas.chamber_of_deputies.models import Reimbursement, Tweet
import datetime
import os
import pandas as pd
import json
from django.http import JsonResponse, HttpResponse

import twitter


def dataviz_dashboard(request):
    # GET https://api.twitter.com/1.1/statuses/show.json?id=210462857140252672
    tweets = Tweet.objects.all().values()
    tweets_df = pd.DataFrame(list(tweets))
    tweet_reimbursements_list = tweets_df['reimbursement_id'].tolist()
    subquota_number = 13

    tweet_reimbursements = Reimbursement.objects.filter(
        year__gt=2015,
        issue_date__gt=datetime.date(2015, 1, 1),
        id__in=tweet_reimbursements_list,
        subquota_number=subquota_number
    )

    df_tweet = pd.DataFrame(list(tweet_reimbursements.values('congressperson_id',
                                                             'congressperson_name',
                                                             'congressperson_document',
                                                             'party',
                                                             'state'
                                                             )))
    df_tweet = df_tweet.drop_duplicates()
    df_tweet = df_tweet.to_dict('records')
    return render(request=request,
                  template_name="dashboard.html",
                  context={'congressperson_list': df_tweet}
                  )


def get_twitter_data():
    api_url = 'https://api.twitter.com/1.1/statuses/user_timeline.json'
    consumer_key = '7VaADONcHBiai9TS8YJ05mcTe'
    consumer_secret = 'C58ej1UQF5tg0hd7y54m31CuOUMMFuQoIiGfxc6VnGvNgeJYj6'
    access_token = '1030805473426063361-jlNN17oS2osQshKmp94GsrPeNJpwGw'
    access_token_secret = 'Lm7Nmw49oAYPd4ZqActTOpapmC6MTiQP4EElT583sMYMB'

    kwargs = dict(
        screen_name='RosieDaSerenata',
        count=200,  # this is the maximum suported by Twitter API
        include_rts=False,
        exclude_replies=True
    )

    api = twitter.Api(consumer_key='7VaADONcHBiai9TS8YJ05mcTe',
                      consumer_secret='C58ej1UQF5tg0hd7y54m31CuOUMMFuQoIiGfxc6VnGvNgeJYj6',
                      access_token_key='1030805473426063361-jlNN17oS2osQshKmp94GsrPeNJpwGw',
                      access_token_secret='Lm7Nmw49oAYPd4ZqActTOpapmC6MTiQP4EElT583sMYMB',
                      sleep_on_rate_limit=True)
    tweets = api.GetUserTimeline(
        screen_name='RosieDaSerenata',
        count=200,  # this is the maximum suported by Twitter API
        include_rts=False,
        exclude_replies=True)

    tweets = [t.AsDict() for t in tweets]

    df_tweets = pd.DataFrame(tweets)
    return df_tweets


def meals_chart(request):
    return render(request=request,
                  template_name="meals_chart.html",
                  )


def meals_chart_data(request):
    tweets = Tweet.objects.all().values()
    tweets_df = pd.DataFrame(list(tweets))
    tweet_reimbursements_list = tweets_df['reimbursement_id'].tolist()
    subquota_number = 13

    tweet_reimbursements = Reimbursement.objects.filter(id__in=tweet_reimbursements_list,
                                                        subquota_number=subquota_number)

    df = pd.DataFrame(list(tweet_reimbursements.values('document_id',
                                                       'year',
                                                       'total_value',
                                                       'total_net_value',
                                                       'congressperson_id',
                                                       'suspicions',
                                                       'issue_date',
                                                       'month',
                                                       'document_value',
                                                       'subquota_number',
                                                       )))

    print(df)
    df = df.fillna(0)
    df['issue_date'] = pd.to_datetime(df.issue_date)
    df['issue_date'] = df['issue_date'].dt.strftime('%m/%d/%Y')
    df = df.sort_values(['issue_date'])

    tweet_reimbursements = df.to_dict(orient='records')

    # return JsonResponse([
    #     {"year": "2005", "value": 771900},
    #     {"year": "2006", "value": 771500},
    #     {"year": "2007", "value": 770500},
    #     {"year": "2008", "value": 770400},
    #     {"year": "2009", "value": 771000},
    #     {"year": "2010", "value": 772400},
    #     {"year": "2011", "value": 774100},
    #     {"year": "2012", "value": 776700},
    #     {"year": "2013", "value": 777100},
    #     {"year": "2014", "value": 779200},
    #     {"year": "2015", "value": 782300}
    # ],
    #     safe=False)

    return JsonResponse(tweet_reimbursements,
                        safe=False)
    #
    # context={'max_reimbursement': float(df['total_net_value'].max()),
    #                        'min_date': tweet_reimbursements[0]['year'],
    #                        'max_date': tweet_reimbursements[-1]['year'],
    #                        'tweet_reimbursements':  df.to_json(orient='records')})

    min_year = df['year'].min()

    congresspeople = set(df['congressperson_id'].tolist())

    reimbursements = Reimbursement.objects.filter(
        subquota_number=subquota_number,
        congressperson_id__in=congresspeople
    )

    reimbursements_df = pd.DataFrame(list(reimbursements.values('document_id',
                                                                'year',
                                                                'total_value',
                                                                'total_net_value',
                                                                'congressperson_id')))

    return render(request=request,
                  template_name="dashboard.html",
                  )

    data = pd.DataFrame()
    current_path = os.getcwd()
    # years = [year for year in range(2008, 2020)]
    # for year in years:
    #     print(year)
    #     temp = pd.read_csv(f'{current_path}/serenata-data/reimbursements-{year}.csv', low_memory=False)
    #     data = pd.concat([data, temp])
    # del (temp)


def tweet_chart(request):
    tweets = Tweet.objects.all().values()
    all_tweets_df = pd.DataFrame(list(tweets))
    congressperson_id = 171620
    tweet_reimbursements_list = all_tweets_df['reimbursement_id'].tolist()
    subquota_number = 13

    # somente os reembolsos com tweet
    tweets_reimbursements = Reimbursement.objects.filter(
        year__gt=2015,
        congressperson_id=congressperson_id,
        issue_date__gt=datetime.date(2015, 1, 1),
        id__in=tweet_reimbursements_list,  # filtra se está na listagem de tweets
        subquota_number=subquota_number
    )

    df_tweets_reimbursements = pd.DataFrame(list(tweets_reimbursements.values(
        'id',
        'congressperson_id',
        'year',
        'month',
        'issue_date',
    )))

    df_tweets_reimbursements = pd.merge(df_tweets_reimbursements,
                                        all_tweets_df,
                                        left_on='id',
                                        right_on='reimbursement_id',
                                        how='left')

    df_tweet_data = get_twitter_data()
    df_tweets_reimbursements = pd.merge(df_tweets_reimbursements,
                                        df_tweet_data,
                                        left_on='status',
                                        right_on='id',
                                        how='left')

    # todos reembolsos do parlamentar
    reimbursements = Reimbursement.objects.filter(
        subquota_number=subquota_number,
        congressperson_id=congressperson_id
    )

    df_all_reimbursements = pd.DataFrame(list(reimbursements.values('id',
                                                                    'document_id',
                                                                    'congressperson_id',
                                                                    'congressperson_name',
                                                                    'year',
                                                                    'month',
                                                                    'total_net_value',
                                                                    'suspicions',
                                                                    'issue_date',
                                                                    )))

    df_all_reimbursements = df_all_reimbursements.fillna(0)
    df_all_reimbursements['reimbursement'] = df_all_reimbursements['id']
    df_all_reimbursements['issue_date'] = pd.to_datetime(df_all_reimbursements.issue_date)
    df_all_reimbursements['value'] = df_all_reimbursements['total_net_value'].astype(float)
    df_all_reimbursements = df_all_reimbursements[['reimbursement',
                                                   'value',
                                                   'issue_date',
                                                   'congressperson_name',
                                                   'congressperson_id']]

    tweetdates = df_tweets_reimbursements['issue_date'].tolist()
    tweetdates.sort()
    len_tweets = len(tweetdates)
    means = pd.DataFrame(columns=["initial_date", "final_date", "mean"])

    df_tweets_reimbursements=df_tweets_reimbursements.sort_values(by='issue_date')
    row_iterator = df_tweets_reimbursements.iterrows()

    for  index, (i, data) in enumerate(row_iterator):

        start_date = data.issue_date
        print(index)
        if index + 1 == len_tweets:
            final_date = datetime.date.today()
        else:
            final_date = tweetdates[index + 1]
        delta = final_date - start_date

        period = df_all_reimbursements[
            (df_all_reimbursements['issue_date'] > start_date) & (df_all_reimbursements['issue_date'] < final_date)
            ]
        mean_per_day = period['value'].sum() / delta.days
        mean = period['value'].mean()
        means = means.append(pd.DataFrame(
            [[congressperson_id, start_date, final_date, mean_per_day, mean, int(data.status)]],
            columns=["congressperson_id", "initial_date", "final_date", "mean_per_day", "mean", "tweet_id"],
        ), sort=True )

    means = pd.merge(means,
                     df_tweet_data,
                     left_on='tweet_id',
                     right_on='id',
                     how='left')
    print(means[['initial_date', 'final_date']])

    means['initial_date'] = means['initial_date'].apply(lambda x: x.strftime('%m/%d/%Y'))
    means['final_date'] = means['final_date'].apply(lambda x: x.strftime('%m/%d/%Y'))
    means = means.fillna(0)
    d = [
        {'congressperson_id': str(congressperson_id),
         'values': means[means['congressperson_id'] == congressperson_id].to_dict('records')}
        for congressperson_id in means['congressperson_id'].unique()
    ]

    print(json.dumps(d))
    print(d)
    return HttpResponse(
        json.dumps(d)
    )


def beckup_all_reibursements(self):
    df_reimb = 0
    df_reimb = df_reimb.fillna(0)

    df_reimb = df_reimb.sort_values(by='issue_date', ascending=True)
    df_reimb['issue_date'] = df_reimb['issue_date'].dt.strftime('%m/%d/%Y')
    df_reimb['status'] = df_reimb['status'].astype(str)

    tweets = df_reimb[df_reimb['status'] != 0]

    tweet_reimbursements = df_reimb.to_dict(orient='index')
    d = [
        {'congressperson_id': str(congressperson_id),
         'values': df_reimb[df_reimb['congressperson_id'] == congressperson_id].to_dict('records')}
        for congressperson_id in df_reimb['congressperson_id'].unique()
    ]

