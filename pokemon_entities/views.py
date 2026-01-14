import folium
import json

from django.http import HttpResponseNotFound
from django.shortcuts import render
from pokemon_entities.models import Pokemon, PokemonEntity
from django.utils.timezone import localtime


MOSCOW_CENTER = [55.751244, 37.618423]
DEFAULT_IMAGE_URL = (
    'https://vignette.wikia.nocookie.net/pokemon/images/6/6e/%21.png/revision'
    '/latest/fixed-aspect-ratio-down/width/240/height/240?cb=20130525215832'
    '&fill=transparent'
)


def add_pokemon(folium_map, lat, lon, image_url=DEFAULT_IMAGE_URL):
    icon = folium.features.CustomIcon(
        image_url,
        icon_size=(50, 50),
    )
    folium.Marker(
        [lat, lon],
        # Warning! `tooltip` attribute is disabled intentionally
        # to fix strange folium cyrillic encoding bug
        icon=icon,
    ).add_to(folium_map)


def show_all_pokemons(request):
    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    now = localtime()
    pokemons = Pokemon.objects.all()
    entities = PokemonEntity.objects.select_related('pokemon').filter(
            appeared_at__lte=now,
            disappeared_at__gte=now,
    )
    for pokemon_entity in entities:
        if pokemon_entity.pokemon.photo:
            img_url = request.build_absolute_uri(
                pokemon_entity.pokemon.photo.url
            )
        else:
            img_url = DEFAULT_IMAGE_URL
        add_pokemon(
            folium_map, pokemon_entity.latitude,
            pokemon_entity.longitude,
            img_url
        )

    pokemons_on_page = []
    for pokemon in pokemons:
        if pokemon.photo:
            img_url = request.build_absolute_uri(pokemon.photo.url)
        else:
            img_url = DEFAULT_IMAGE_URL
        pokemons_on_page.append({
            'pokemon_id': pokemon.id,
            'img_url': img_url,
            'title_ru': pokemon.title,
        })

    return render(request, 'mainpage.html', context={
        'map': folium_map._repr_html_(),
        'pokemons': pokemons_on_page,
    })


def show_pokemon(request, pokemon_id):
    try:
        pokemon = Pokemon.objects.get(id=pokemon_id)
    except Pokemon.DoesNotExist:
        return HttpResponseNotFound('<h1>Такой покемон не найден</h1>')

    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    entities = pokemon.entities.all()
    for entity in entities:
        if pokemon.photo:
            img_url = request.build_absolute_uri(
                pokemon.photo.url
            )
        else:
            img_url = DEFAULT_IMAGE_URL
        add_pokemon(
            folium_map,
            entity.latitude,
            entity.longitude,
            img_url
        )

    previous_evolution = None
    if pokemon.previous_evolution:
        previous_pokemon = pokemon.previous_evolution
        previous_evolution = {
            'pokemon_id': previous_pokemon.id,
            'title_ru': previous_pokemon.title,
            'img_url': request.build_absolute_uri(previous_pokemon.photo.url)
                if previous_pokemon.photo else DEFAULT_IMAGE_URL
        }

    next_evolution = None
    next_pokemon = pokemon.next_evolutions.all()
    if next_pokemon.exists():
        next_pokemon = next_pokemon.first()
        next_evolution = {
            'pokemon_id': next_pokemon.id,
            'title_ru': next_pokemon.title,
            'img_url': request.build_absolute_uri(next_pokemon.photo.url)
                if next_pokemon.photo else DEFAULT_IMAGE_URL,
        }

    pokemon_data = {
        'id': pokemon.id,
        'title_ru': pokemon.title,
        'title_en': pokemon.title_en,
        'title_jp': pokemon.title_jp,
        'description': pokemon.description,
        'img_url': request.build_absolute_uri(pokemon.photo.url)
            if pokemon.photo else DEFAULT_IMAGE_URL,
        'previous_evolution': previous_evolution,
        'next_evolution': next_evolution,
        'entities': []
    }

    for entity in entities:
        pokemon_data['entities'].append({
            'level': entity.level,
            'lat': entity.latitude,
            'lon': entity.longitude,
        })

    return render(request, 'pokemon.html', context={
        'map': folium_map._repr_html_(),
        'pokemon': pokemon_data
    })
