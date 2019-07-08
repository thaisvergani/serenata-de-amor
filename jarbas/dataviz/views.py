from decimal import Decimal

from django.shortcuts import render

from jarbas.chamber_of_deputies.models import Reimbursement, Tweet, SocialMedia
import datetime
import os

import json
import requests
from django.http import JsonResponse, HttpResponse
import pandas as pd
import numpy as np
from scipy import stats
import twitter


def refund_chart(request):
    df_tweets = pd.DataFrame(list(Tweet.objects.all().values('id',
                                                             'reimbursement',
                                                             'status'
                                                             )))

    reimbursements = Reimbursement.objects.filter(
        id__in=df_tweets['reimbursement'].tolist(),
        year__gte=2014,
        subquota_number = 13
    )

    df_tweeted_reimbursements = pd.DataFrame(list(reimbursements.values('id',
                                                                        'congressperson_name',
                                                                        'party',
                                                                        'total_value',
                                                                        'suspicions',
                                                                        'total_net_value'
                                                                        )))
    df_tweeted_reimbursements['reimbursement_id'] = df_tweeted_reimbursements['id']
    df_tweeted_reimbursements['suspicions'] = df_tweeted_reimbursements['suspicions'].apply(
        lambda x: get_suspicion_description(x))

    df_tweeted_reimbursements = pd.merge(
        df_tweeted_reimbursements,
        df_tweets,
        left_on='reimbursement_id',
        right_on='reimbursement',
        how='left')

    df_api_twitter = get_twitter_data(df_tweeted_reimbursements['status'].astype(str).tolist())
    df_api_twitter = df_api_twitter[['created_at', 'favorite_count', 'id', 'id_str', 'retweet_count']]

    df_tweeted_reimbursements = pd.merge(df_tweeted_reimbursements,
                                         df_api_twitter,
                                         left_on='status',
                                         right_on='id',
                                         how='left')
    df_tweeted_reimbursements['created_at'] = pd.to_datetime(
        df_tweeted_reimbursements['created_at'])
    df_tweeted_reimbursements = df_tweeted_reimbursements[df_tweeted_reimbursements['created_at'] > '2014-01-01 ']

    df_tweeted_reimbursements['status'] = df_tweeted_reimbursements['status'].astype(str)
    df_tweeted_reimbursements = df_tweeted_reimbursements.fillna(0)
    d = df_tweeted_reimbursements.to_dict('records')
    # from IPython import embed; embed()
    # first_tweet = df_tweeted_reimbursements['issue_date'].min()
    # refunds = Reimbursement.objects.filter(
    #     issue_date__gte=first_tweet,
    #     total_value__gt=0,
    # )
    # refunds_tweeted = Reimbursement.objects.filter(
    #     id__in=df_tweets['reimbursement'].tolist(),
    #     issue_date__gte=first_tweet,
    #     total_value__gt=0,
    # )

    return HttpResponse(
        json.dumps(d, cls=DatavizEncoder)
    )


def dataviz_dashboard(request):
    # GET https://api.twitter.com/1.1/statuses/show.json?id=210462857140252672

    deputados = "https://dadosabertos.camara.leg.br/api/v2/deputados"
    page = 1
    congressperson_list = []
    while True:
        response = requests.get(url=deputados,
                                params={'itens': 500,
                                        'pagina': page},
                                timeout=10).json()
        congressperson_page = response.get('dados', [])
        if congressperson_page == []:
            break
        congressperson_list.extend(congressperson_page)
        page = page + 1
    # from IPython import embed; embed()
    legislaturas_url = "https://dadosabertos.camara.leg.br/api/v2/legislaturas"
    response = requests.get(url=legislaturas_url,
                            params={'itens': 5,
                                    'pagina': 1,
                                    'ordem': 'DESC'},
                            timeout=10).json()

    legislaturas = response.get('dados', [])
    legislaturas = pd.DataFrame(legislaturas)
    legislaturas['dataFim'] = pd.to_datetime(legislaturas.dataFim)
    legislaturas['dataInicio'] = pd.to_datetime(legislaturas.dataInicio)

    return render(request=request,
                  template_name="dashboard.html",
                  context={'congressperson_list': congressperson_list,
                           'legislaturas': legislaturas,
                           'years': range(2017,2020)}
                  )


def get_congressperson_reimbursements(congressperson_id, subquota_number, year=None):
    reimbursements = Reimbursement.objects.filter(
        subquota_number=subquota_number,
        congressperson_id=congressperson_id
    )

    if year:
        reimbursements = reimbursements.filter(year=year)
    df_all_reimbursements = pd.DataFrame(list(reimbursements.values('id',
                                                                    'document_id',
                                                                    'congressperson_id',
                                                                    'congressperson_name',
                                                                    'year',
                                                                    'month',
                                                                    'total_net_value',
                                                                    'suspicions',
                                                                    'receipt_url',
                                                                    'issue_date',
                                                                    )))
    if df_all_reimbursements.empty:
        return df_all_reimbursements

    df_all_reimbursements = df_all_reimbursements.fillna(0)
    df_all_reimbursements['reimbursement_id'] = df_all_reimbursements['id']
    df_all_reimbursements['issue_date'] = pd.to_datetime(df_all_reimbursements.issue_date)
    df_all_reimbursements['value'] = df_all_reimbursements['total_net_value'].astype(float)
    df_all_reimbursements = df_all_reimbursements[['reimbursement_id',
                                                   'value',
                                                   'issue_date',
                                                   'suspicions',
                                                   'receipt_url',
                                                   'document_id',
                                                   'congressperson_name',
                                                   'congressperson_id']]
    # # remove outliers
    # df_all_reimbursements = outliers(df_all_reimbursements)

    return df_all_reimbursements


def outliers(df, level=10):
    # calc Z-score
    df['score_z'] = stats.zscore(df.value)

    # print outliers
    print(df[df['score_z'] > level])
    # remove outliers
    df = df[df['score_z'] < level]

    return df


def get_twitter_data(status_ids):
    api = twitter.Api(consumer_key='7VaADONcHBiai9TS8YJ05mcTe',
                      consumer_secret='C58ej1UQF5tg0hd7y54m31CuOUMMFuQoIiGfxc6VnGvNgeJYj6',
                      access_token_key='1030805473426063361-jlNN17oS2osQshKmp94GsrPeNJpwGw',
                      access_token_secret='Lm7Nmw49oAYPd4ZqActTOpapmC6MTiQP4EElT583sMYMB',
                      sleep_on_rate_limit=True)

    # tweets = api.GetUserTimeline(
    #     screen_name='RosieDaSerenata',
    #     count=200,  # this is the maximum suported by Twitter API
    #     include_rts=False,
    #     exclude_replies=True)
    tweets = api.GetStatuses(trim_user=True, include_entities=False, status_ids=status_ids)

    variables = ['created_at', 'favorite_count', 'id', 'id_str', 'retweet_count']
    df_tweets = pd.DataFrame([[getattr(i, j) for j in variables] for i in tweets], columns=variables)
    return df_tweets


def tweet_chart(request):
    congressperson_id = request.GET.get('congressperson_id')
    year = request.GET.get('year')
    year = 2019
    subquota_number = 13

    df_all_reimbursements = get_congressperson_reimbursements(
        congressperson_id,
        subquota_number
    )
    if df_all_reimbursements.empty:
        return HttpResponse(
            json.dumps({'msg': 'Nenhum reembolso encontrado para o parlamentar'}, cls=DatavizEncoder)
        )

    tweets = Tweet.objects.filter(
        reimbursement__in=df_all_reimbursements['reimbursement_id'].tolist()
    ).values()
    df_tweets = pd.DataFrame(list(tweets))

    if not df_tweets.empty:
        df_api_twitter = get_twitter_data(df_tweets['status'].tolist())

        df_tweets = pd.merge(df_tweets,
                             df_all_reimbursements,
                             left_on='reimbursement_id',
                             right_on='reimbursement_id',
                             how='left')
        df_tweets = pd.merge(df_tweets,
                             df_api_twitter,
                             left_on='status',
                             right_on='id',
                             how='outer')
        df_tweets['created_at'] = pd.to_datetime(df_api_twitter['created_at'])
        df_tweets['suspicions'] = df_tweets['suspicions'].apply(lambda x: get_suspicion_description(x))
        df_tweets['status'] = df_tweets['status'].astype(str)

    # period_ini = df_all_reimbursements['issue_date'].min()
    # period_end = df_all_reimbursements['issue_date'].max()
    #
    # periods = pd.date_range(period_ini, period_end, freq='MS').tolist()

    df_all_reimbursements = df_all_reimbursements.set_index('issue_date')
    periods = df_all_reimbursements.groupby(pd.Grouper(freq="Q"))
    means = periods['value'].mean()
    means = means.to_frame().reset_index()
    means = means.fillna(0)
    means['issue_date'] = means['issue_date'].apply(lambda x: x.strftime('%m/%d/%Y'))
    df_all_reimbursements = df_all_reimbursements.reset_index()
    # for index, (i, data) in enumerate(row_iterator):
    #
    #     start_date = data.issue_date
    #
    #     if index + 1 == len_tweets:
    #         final_date = datetime.date.today()
    #     else:
    #         final_date = tweetdates[index + 1]
    #     delta = final_date - start_date
    #
    #     period = df_all_reimbursements[
    #         (df_all_reimbursements['issue_date'] > start_date) & (df_all_reimbursements['issue_date'] < final_date)
    #         ]
    #     mean_per_day = period['value'].sum() / delta.days
    #     mean = period['value'].mean()
    #
    #     suspicions = list(data.suspicions.keys())[0] if data.suspicions else ''
    #     suspicions = get_suspicion_description(suspicions)
    #
    #     means = means.append(pd.DataFrame(
    #         [[congressperson_id, start_date, final_date, mean_per_day, mean, str(data.status),
    #           "https://twitter.com/RosieDaSerenata/status/" + str(data.status),
    #           float(data.total_net_value),suspicions , data.reimbursement_id]],
    #         columns=["congressperson_id", "initial_date", "final_date", "mean_per_day", "mean", "tweet_id",  "tweet_url",
    #                  "total_net_value", "suspicions", 'reimbursement'],
    #     ), sort=True)
    # means['initial_date'] = means['initial_date'].apply(lambda x: x.strftime('%m/%d/%Y'))
    # means['final_date'] = means['final_date'].apply(lambda x: x.strftime('%m/%d/%Y'))
    df_all_reimbursements['issue_date'] = df_all_reimbursements['issue_date'].apply(lambda x: x.strftime('%m/%d/%Y'))
    d = [{
        'means': means.to_dict('records'),
        'reimbursements': df_all_reimbursements.to_dict('records'),
        'tweets': df_tweets.to_dict('records')}]

    return HttpResponse(
        json.dumps(d, cls=DatavizEncoder)
    )


class DatavizEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)

        if isinstance(obj, datetime.datetime):
            return obj.strftime('%m/%d/%Y')

        return json.JSONEncoder.default(self, obj)


def get_suspicion_description(s):
    if not s:
        return ''
    s = list(s.keys())[0]
    SUSPICIONS = (
        'meal_price_outlier',
        'over_monthly_subquota_limit',
        'suspicious_traveled_speed_day',
        'invalid_cnpj_cpf',
        'election_expenses',
        'irregular_companies_classifier'
    )

    HUMAN_NAMES = (
        'Preço de refeição muito incomum',
        'Extrapolou limita da (sub)quota',
        'Muitas despesas em diferentes cidades no mesmo dia',
        'CPF ou CNPJ inválidos',
        'Gasto com campanha eleitoral',
        'CNPJ irregular'
    )

    MAP = dict(zip(SUSPICIONS, HUMAN_NAMES))
    return MAP.get(s, '')


def get_congress_person_data(request):
    congressperson_id = request.GET.get('congressperson_id')
    try:
        social_media = SocialMedia.objects.get(
            congressperson_id=congressperson_id
        )
    except SocialMedia.DoesNotExist:
        social_media = None

    dados_abertos_api = "https://dadosabertos.camara.leg.br/api/v2/deputados/" + congressperson_id
    # todo: define url to external api

    response = requests.get(dados_abertos_api, timeout=10)
    response = response.json()

    c_info = {
        'congressperson_name': response.get('dados').get('ultimoStatus').get('nomeEleitoral'),
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
