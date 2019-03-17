
from django.shortcuts import render


def dataviz_dashboard(request):

    return render(request=request,
           template_name="dashboard.html",
           )
