from django.shortcuts import render, reverse, redirect
from django.conf import settings

from .mixins import (
    RedirectParams,
    APIMixin
)


# basic view for selecting query
# request is passed automatically to all views

def check_categories():
    """Helper method to differentiate between POST keywords"""
    categories = {"apod": "apod", "mars": "mars", "epic": "epic"}
    return categories


def check_patents():
    """Helper method to differentiate between POST keywords"""
    patents = {"robotics": "robotics",
               "it-software": "it-software", "aerospace": "aerospace", "propulsion": "propulsion"}
    return patents


def index(request):
    """Home Page"""
    if request.method == "POST":
        # get category keyword from the posted request
        category = request.POST.get("category", None)
        if category:
            if category in check_categories():
                # if successful in getting posted data it will redirect user
                # redirect takes keyword arguments to complete query string
                return RedirectParams(url='main:results', params={"category": category})
            elif category in check_patents():
                return RedirectParams(url='main:patents', params={"category": category})
    return render(request, 'main/index.html', {})

# basic view for rendering results


def results(request):
    """Results Page"""
    # get data posted to server
    category = request.GET.get('category', None)

    if category:
        results = APIMixin(category=category).get_result_data()
        print(results)

        if results:
            context = {
                "results": results,
                "category": category
            }
            return render(request, 'main/results.html', context)

    return redirect(reverse('main:home'))


def patents(request):
    """Patents Page"""
    category = request.GET.get('category', None)

    if category:
        results = APIMixin(category=category).get_patent_data()
        print(results)

        if results:
            context = {
                "results": results,
                "category": category
            }
            return render(request, 'main/patents.html', context)

    return redirect(reverse('main:home'))
