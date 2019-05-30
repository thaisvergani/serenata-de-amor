from django.shortcuts import render

from jarbas.chamber_of_deputies.models import Reimbursement, Tweet, SocialMedia
import datetime
import os
import pandas as pd
import json
import requests
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


def tweet_chart(request):
    tweets = Tweet.objects.all().values()
    all_tweets_df = pd.DataFrame(list(tweets))
    congressperson_id = request.GET.get('congressperson_id')
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
        'total_net_value',
        'suspicions'
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
                                                   'suspicions',
                                                   'congressperson_name',
                                                   'congressperson_id']]

    tweetdates = df_tweets_reimbursements['issue_date'].tolist()
    tweetdates.sort()
    len_tweets = len(tweetdates)
    means = pd.DataFrame(columns=["initial_date", "final_date", "mean"])

    df_tweets_reimbursements = df_tweets_reimbursements.sort_values(by='issue_date')
    row_iterator = df_tweets_reimbursements.iterrows()

    for index, (i, data) in enumerate(row_iterator):

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
        # from IPython import embed; embed()
        means = means.append(pd.DataFrame(
            [[congressperson_id, start_date, final_date, mean_per_day, mean, int(data.status),
              float(data.total_net_value), list(data.suspicions.keys())]],
            columns=["congressperson_id", "initial_date", "final_date", "mean_per_day", "mean", "tweet_id",
                     "total_net_value", "suspicions"],
        ), sort=True)

    means = pd.merge(means,
                     df_tweet_data,
                     left_on='tweet_id',
                     right_on='id',
                     how='left')

    means['initial_date'] = means['initial_date'].apply(lambda x: x.strftime('%m/%d/%Y'))
    means['final_date'] = means['final_date'].apply(lambda x: x.strftime('%m/%d/%Y'))
    means = means.fillna(0)
    d = [
        {'congressperson_id': str(congressperson_id),
         'values': means[means['congressperson_id'] == congressperson_id].to_dict('records')}
        for congressperson_id in means['congressperson_id'].unique()
    ]

    return HttpResponse(
        json.dumps(d)
    )


def get_congress_person_data(request):
    congressperson_id = request.GET.get('congressperson_id')
    try:
        social_media = SocialMedia.objects.get(
            congressperson_id=congressperson_id
        )
    except SocialMedia.DoesNotExist:
        social_media = None

    # todo pode ser que nao tenha socialmedia

    dados_abertos_api = "https://dadosabertos.camara.leg.br/api/v2/deputados/" + congressperson_id
    # todo: define url to external api

    response = requests.get(dados_abertos_api, timeout=10)
    response = response.json()
    print(response)
    c_info = {
        'congressperson_name':  response.get('dados').get('ultimoStatus').get('nomeEleitoral'),
        'twitter_profile': 'https://twitter.com' + social_media.twitter_profile if social_media else '',
        'facebook_page': social_media.facebook_page if social_media else '',
        'image_url': response.get('dados').get('ultimoStatus').get('urlFoto'),
        'birthday': response.get('dados').get('dataNascimento'),
        'status': response.get('dados').get('ultimoStatus').get('situacao'),
        'scholarity': response.get('dados').get('escolaridade'),
        'party': response.get('dados').get('ultimoStatus').get('siglaPartido'),
        'uf': response.get('dados').get('ultimoStatus').get('siglaUf')
    }

    return render(request=request,
                  template_name="congressperson.html",
                  context=c_info
                  )
