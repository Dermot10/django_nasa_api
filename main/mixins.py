from django.conf import settings
from django.shortcuts import redirect
from urllib.parse import urlencode
import requests
import json
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()


# use to append url parameters to redirecitng users
# takes keywords and creates parameters for url
def RedirectParams(**kwargs):
    """Accept keyword parameters from POST request and append to url"""
    url = kwargs.get("url")
    params = kwargs.get("params")
    response = redirect(url)
    if params:
        query_string = urlencode(params)
        response['Location'] += '?' + query_string
    print("response---->", response)
    return response


class APIMixin:
    def __init__(self, *args, **kwargs):
        # class deals with what to do after posted request, it will decide what data to return using API
        # then returned data is rendered in the views file
        self.category = kwargs.get("category")
        self.category_dict = {
            'apod': f'planetary/apod?api_key={settings.API_KEY}',
            'mars': f'mars-photos/api/v1/rovers/curiosity/photos?sol=1000&api_key={settings.API_KEY}',
            'epic': f'EPIC/api/natural/images?api_key={settings.API_KEY}',
            'robotics': f'robotics&api_key={settings.API_KEY}',
            'it-software': f'it/software&api_key={settings.API_KEY}',
            'aerospace': f'aerospace&api_key={settings.API_KEY}',
            'propulsion': f'propulsion&api_key={settings.API_KEY}'
        }
        self.process_functions = {
            'mars': self.process_mars,
            'apod': self.process_apod,
            'epic': self.process_epic,
            'robotics': self.process_robotics,
            'it-software': self.process_it_software,
            'aerospace': self.process_aerospace,
            'propulsion': self.process_propulsion
        }

    def send_full_request(self):
        """API request to retrieve non patent related data"""
        url = f'https://api.nasa.gov/{self.category_dict[self.category]}'
        print("full url:", url)
        res = requests.get(url)
        return res

    def send_patent_request(self):
        """API request to retrieve patent data"""
        url = f'https://api.nasa.gov/techtransfer/patent/?{self.category_dict[self.category]}'
        print("full url:", url)
        res = requests.get(url)
        print(self.category)
        return res

    def process_mars(self, data):
        return {
            # first element is list in list look for key
            "image": data['photos'][0]["img_src"],
            "text": "Image data gathered by NASA's Curiosity, Opportunity, and Spirit rovers on Mars."
        }

    def process_apod(self, data):
        return {
            "image": data["url"],
            "text": data["explanation"]
        }

    def process_epic(self, data):
        image_id = data[0]["image"]
        date = data[0]["date"].split(" ")[0].split("-")
        new_url = f'https://api.nasa.gov/EPIC/archive/natural/{date[0]}/{date[1]}/{date[2]}/png/{image_id}.png?api_key={settings.API_KEY}'
        return {
            "image": new_url,
            "text": "Imagery collected by DSCOVR's Earth Polychromatic Imaging Camera (EPIC) instrument. Uniquely positioned at the Earth-Sun Lagrange point, EPIC provides full disc imagery of the Earth and captures unique perspectives of certain astronomical events such as lunar transits using a 2048x2048 pixel CCD (Charge Coupled Device) detector coupled to a 30-cm aperture Cassegrain telescope."
        }

    def process_robotics(self, data):
        data = self.parse_html(data)
        return {
            "title": data[0],
            "text": data[1]
        }

    def process_it_software(self, data):
        data = self.parse_html(data)
        return {
            "title": data[0],
            "text": data[1]
        }

    def process_aerospace(self, data):
        data = self.parse_html(data)
        return {
            "title": data[0],
            "text": data[1]
        }

    def process_propulsion(self, data):
        data = self.parse_html(data)
        return {
            "title": data[0],
            "text": data[1]
        }

    def parse_html(self, data):
        """Helper function to parse html out of API response"""
        raw_title = data["results"][0][2]
        raw_text = data["results"][0][3]

        soup = BeautifulSoup(raw_title, 'html.parser')
        title = soup.get_text()

        soup = BeautifulSoup(raw_text, 'html.parser')
        text = soup.get_text()

        return [title, text]

    def get_result_data(self):
        res = self.send_full_request()

        if res.status_code == 200 and self.category in self.process_functions:
            return self.process_functions[self.category](res.json())

        return None

    def get_patent_data(self):
        res = self.send_patent_request()

        if res.status_code == 200 and self.category in self.process_functions:
            return self.process_functions[self.category](res.json())

        return None
