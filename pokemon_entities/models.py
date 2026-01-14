from django.db import models  # noqa F401
from django.utils import timezone


class Pokemon(models.Model):
    title = models.CharField(max_length=200, verbose_name='Имя покемона')
    title_en = models.CharField(max_length=200, blank=True, verbose_name='Имя покемона на англ.')
    title_jp = models.CharField(max_length=200, blank=True, verbose_name='Имя покемона на японском.')
    description = models.TextField(blank=True, verbose_name='Описание покемона')
    photo = models.ImageField(
        null=True,
        blank=True,
        verbose_name='Фото покемона'
    )
    previous_evolution = models.ForeignKey(
        'self',
        verbose_name='Из кого эволюционировал',
        null=True,
        blank=True,
        related_name='next_evolutions',
        on_delete=models.SET_NULL
    )

    class Meta:
        verbose_name = 'Покемон'
        verbose_name_plural = 'Покемоны'

    def __str__(self):
        return self.title


class PokemonEntity(models.Model):
    pokemon = models.ForeignKey(Pokemon, on_delete=models.CASCADE,related_name='entities')
    latitude = models.FloatField(verbose_name='Широта')
    longitude = models.FloatField( verbose_name='Долгота')
    appeared_at = models.DateTimeField(verbose_name='Появился в')
    disappeared_at = models.DateTimeField(verbose_name='Исчез в')
    level = models.IntegerField(null=True, blank=True, verbose_name='Уровень')
    health = models.IntegerField(null=True, blank=True, verbose_name='Здоровье')
    strength = models.IntegerField(null=True, blank=True, verbose_name='Сила')
    defence = models.IntegerField(null=True, blank=True, verbose_name='Защита')
    stamina = models.IntegerField(null=True, blank=True, verbose_name='Выносливость')

    class Meta:
        verbose_name = 'Сущность Покемона'
        verbose_name_plural = 'Сущности Покемонов'
    
    def __str__(self):
        return f'{self.pokemon.title} (ур. {self.level})'