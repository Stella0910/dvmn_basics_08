import os
from dotenv import load_dotenv
import requests
from geopy import distance
import json
import folium


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def get_coffee_distance(coffee):
    return coffee['distance']


def main():
    load_dotenv()
    apikey = os.getenv("APIKEY_YANDEX_GEOCODER")

    address_user = input("Где вы находитесь? ")
    coords_longitude = float(fetch_coordinates(apikey, address_user)[0])
    coords_latitude = float(fetch_coordinates(apikey, address_user)[1])

    m = folium.Map([coords_latitude, coords_longitude], zoom_start=12)

    folium.Marker(location=[coords_latitude, coords_longitude],
                  tooltip="Click me!",
                  popup="Here you are!",
                  icon=folium.Icon(color="red", icon='user')).add_to(m)

    with open("coffee.json", "r", encoding="CP1251") as file:
        file_content = file.read()
    content = json.loads(file_content)

    intermediate_list_of_coffees = []
    for coffee in content:
        intermediate_list_of_coffees.append({
            'title': coffee['Name'],
            'distance': distance.distance(
                (coords_latitude,
                 coords_longitude),
                (coffee['geoData']['coordinates'][1],
                 coffee['geoData']['coordinates'][0])).km,
            'latitude': coffee['geoData']['coordinates'][1],
            'longitude': coffee['geoData']['coordinates'][0]
        })

    five_coffees = sorted(intermediate_list_of_coffees,
                          key=get_coffee_distance)[:5]

    for coffee in five_coffees:
        folium.Marker(
            location=[coffee['latitude'], coffee['longitude']],
            tooltip="Click me!",
            popup=coffee['title'],
            icon=folium.Icon(color="blue", icon="fa-mug-hot", prefix='fa'),
        ).add_to(m)

    m.save("index.html")


if __name__ == '__main__':
    main()
