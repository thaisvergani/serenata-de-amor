from django.shortcuts import render

from jarbas.chamber_of_deputies.models import Reimbursement, SocialMedia, Tweet, ReimbursementSummary
from django.db.models import Q
import datetime
import os
import pandas as pd
from django.http import JsonResponse


def dataviz_dashboard(request):
    # GET https://api.twitter.com/1.1/statuses/show.json?id=210462857140252672

    return render(request=request,
                  template_name="dashboard.html",
                  )

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

    tweet_reimbursements_df = pd.DataFrame(list(tweet_reimbursements.values('document_id',
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

    print(tweet_reimbursements_df)
    tweet_reimbursements_df = tweet_reimbursements_df.fillna(0)
    tweet_reimbursements_df['issue_date'] = pd.to_datetime(tweet_reimbursements_df.issue_date)
    tweet_reimbursements_df['issue_date'] = tweet_reimbursements_df['issue_date'].dt.strftime('%m/%d/%Y')
    tweet_reimbursements_df = tweet_reimbursements_df.sort_values(['issue_date'])

    tweet_reimbursements = tweet_reimbursements_df.to_dict(orient='records')

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
    # context={'max_reimbursement': float(tweet_reimbursements_df['total_net_value'].max()),
    #                        'min_date': tweet_reimbursements[0]['year'],
    #                        'max_date': tweet_reimbursements[-1]['year'],
    #                        'tweet_reimbursements':  tweet_reimbursements_df.to_json(orient='records')})

    min_year = tweet_reimbursements_df['year'].min()

    congresspeople = set(tweet_reimbursements_df['congressperson_id'].tolist())

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
    tweets_df = pd.DataFrame(list(tweets))
    tweet_reimbursements_list = tweets_df['reimbursement_id'].tolist()
    subquota_number = 13


    tweet_reimbursements = Reimbursement.objects.filter(
                                                        issue_date__gt=datetime.date(2015, 1, 1),
        id__in=tweet_reimbursements_list,
        subquota_number=subquota_number,
    )

    tweet_reimbursements_df = pd.DataFrame(list(tweet_reimbursements.values('document_id',
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


    print(tweet_reimbursements_df)
    tweet_reimbursements_df = tweet_reimbursements_df.fillna(0)
    tweet_reimbursements_df['issue_date'] = pd.to_datetime(tweet_reimbursements_df.issue_date)
    tweet_reimbursements_df['issue_date'] = tweet_reimbursements_df['issue_date'].dt.strftime('%m/%d/%Y')
    tweet_reimbursements_df = tweet_reimbursements_df.sort_values(['issue_date'])

    tweet_reimbursements = tweet_reimbursements_df.to_dict(orient='records')

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
    # context={'max_reimbursement': float(tweet_reimbursements_df['total_net_value'].max()),
    #                        'min_date': tweet_reimbursements[0]['year'],
    #                        'max_date': tweet_reimbursements[-1]['year'],
    #                        'tweet_reimbursements':  tweet_reimbursements_df.to_json(orient='records')})

    min_year = tweet_reimbursements_df['year'].min()

    congresspeople = set(tweet_reimbursements_df['congressperson_id'].tolist())

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


def get_tweets_date():
    pass


def get_data_sample_from_all_years(current_path):
    data = pd.read_csv(f'{current_path}/sample_all_years_csv.csv')

    data = data[data['congressperson_id'].notnull()]
    data['numbers'] = data['numbers'].str.replace('nan', 'None').apply(eval)
    data['is_returned'] = data['numbers'].apply(lambda values: None in values)
    data['is_meal'] = data['subquota_description'] == 'Congressperson meal'
    return data


def get_meals_sample_from_all_years(current_path):
    data = pd.read_csv(f'{current_path}/meals_from_all_years_sample.csv')

    meals = data.query('is_meal')
    meals.to_csv('meals_from_all_years_sample.csv', index=False)

    """`suspicions` vem do banco de dados do Whistleblower, contendo todos os `document_id`s já tuitados pela @RosieDaSerenata."""

    suspicions = data[data['document_id'].isin(suspicions)]

    """A maior parte das devoluções são referentes a gastos de 2015-2017, o mandato atual."""

    return render(request=request,
                  template_name="dashboard.html",
                  context=data)
