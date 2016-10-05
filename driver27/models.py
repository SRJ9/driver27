from __future__ import unicode_literals

import datetime
from django.db import models
from django.core.exceptions import ValidationError
import punctuation
from slugify import slugify

try:
    from django_countries.fields import CountryField
except ImportError:
    raise ImportError(
        'You are using the `driver27` app which requires the `django-countries` module.'
        'Be sure to add `django_countries` to your INSTALLED_APPS for `driver27` to work properly.'
    )

def get_season_points(season, enrolled_driver, rounds=None):
    if not isinstance(season, Season) or not isinstance(enrolled_driver, DriverCompetition):
        return None
    results = Result.objects.filter(race__season=season, contender__enrolled=enrolled_driver).order_by('race__round')
    points_list = [result.points for result in results.all() if result.points is not None]
    return sum(points_list)

class Driver(models.Model):
    last_name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=25)
    year_of_birth = models.IntegerField()
    country = CountryField()
    competitions = models.ManyToManyField('Competition', through='DriverCompetition')

    def save(self, *args, **kwargs):
        if self.year_of_birth < 1900 or self.year_of_birth > 2099:
            raise ValidationError('Year_of_birth must be between 1900 and 2099')
        super(Driver, self).save(*args, **kwargs)

    def __unicode__(self):
        return ', '.join((self.last_name, self.first_name))

    class Meta:
        unique_together = ('last_name', 'first_name')

class DriverCompetitionTeam(models.Model):
    team = models.ForeignKey('Team', related_name='partners')
    enrolled = models.ForeignKey('DriverCompetition', related_name='squad')
    current = models.BooleanField(default=False)
    seasons = models.ManyToManyField('Season', blank=True, default=None)

    def __unicode__(self):
        return '%s %s %s' % (self.enrolled.driver, 'in', self.team)

    class Meta:
        unique_together = [('team', 'enrolled'), ('enrolled', 'current')]
        ordering = ['enrolled__driver__last_name', 'team']

class DriverCompetition(models.Model):
    driver = models.ForeignKey(Driver, related_name='career')
    competition = models.ForeignKey('Competition', related_name='career')
    teams = models.ManyToManyField('Team', through='DriverCompetitionTeam')

    @property
    def teams_verbose(self):
        teams = self.teams
        if teams.count():
            return ', '.join([team.name for team in teams.all()])
        else:
            return None

    def __unicode__(self):
        return '%s %s %s' % (self.driver, 'in', self.competition)

    class Meta:
        unique_together = ('driver', 'competition')


class Team(models.Model):
    name = models.CharField(max_length=75, verbose_name='team')
    full_name = models.CharField(max_length=200)
    competitions = models.ManyToManyField('Competition', related_name='teams')
    country = CountryField()

    def __unicode__(self):
        return self.name

class Competition(models.Model):
    name = models.CharField(max_length=30, verbose_name='competition')
    full_name = models.CharField(max_length=100)
    country = CountryField(null=True, blank=True, default=None)
    slug = models.SlugField(null=True, blank=True, default=None)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Competition, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name

class Circuit(models.Model):
    name = models.CharField(max_length=30, verbose_name='circuit')
    city = models.CharField(max_length=100, null=True, blank=True)
    country = CountryField()
    opened_in = models.IntegerField()

    # @todo Add Clockwise and length
    def __unicode__(self):
        # @todo Add country name in __unicode__
        return self.name

class GrandPrix(models.Model):
    name = models.CharField(max_length=30, verbose_name='grand prix')
    country = CountryField(null=True, blank=True, default=None)
    first_held = models.IntegerField(null=True, blank=True)
    default_circuit = models.ForeignKey(Circuit, related_name='default_to_grands_prix', null=True, blank=True, default=None)
    competitions = models.ManyToManyField('Competition', related_name='grands_prix', default=None)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'grands prix'


class Season(models.Model):
    year = models.IntegerField()
    competition = models.ForeignKey(Competition, related_name='seasons')
    rounds = models.IntegerField(blank=True, null=True, default=None)
    teams = models.ManyToManyField(Team, related_name='seasons', through='TeamSeasonRel')
    punctuation = models.CharField(max_length=20, null=True, default=None)

    def get_scoring(self):
        for scoring in punctuation.DRIVER27_PUNCTUATION:
            if scoring['code'] == self.punctuation:
                return scoring
        return None

    def __unicode__(self):
        return '/'.join((self.competition.name, str(self.year)))

    class Meta:
        unique_together = ('year', 'competition')

class Race(models.Model):
    ALTER_PUNCTUATION = (
        ('double', 'Double'),
        ('half', 'Half')
    )
    season = models.ForeignKey(Season, related_name='races')
    round = models.IntegerField()
    grand_prix = models.ForeignKey(GrandPrix, related_name='races', blank=True, null=True, default=None)
    circuit = models.ForeignKey(Circuit, related_name='races', blank=True, null=True, default=None)
    date = models.DateField(blank=True, null=True, default=None)
    alter_punctuation = models.CharField(choices=ALTER_PUNCTUATION, null=True, blank=True, default=None, max_length=6)


    def __unicode__(self):
        race_str = str(self.season) + '-'+str(self.round)
        if self.grand_prix:
            race_str += '.' + str(self.grand_prix)
        return race_str

    class Meta:
        unique_together = ('season', 'round')

class TeamSeasonRel(models.Model):
    season = models.ForeignKey('Season')
    team = models.ForeignKey('Team')
    sponsor_name = models.CharField(max_length=75, null=True, blank=True, default=None)

    def save(self, *args, **kwargs):
        if self.season.competition not in self.team.competitions.all():
            raise ValidationError('Team ' + str(self.team) + ' doesn\'t participate in '+str(self.season.competition))
        super(TeamSeasonRel, self).save(*args, **kwargs)

    class Meta:
        unique_together = ('season', 'team')

class Result(models.Model):
    race = models.ForeignKey(Race, related_name='results')
    contender = models.ForeignKey(DriverCompetitionTeam, related_name='results')
    qualifying = models.IntegerField(blank=True, null=True, default=None)
    finish = models.IntegerField(blank=True, null=True, default=None)
    fastest_lap = models.BooleanField(default=False)
    retired = models.BooleanField(default=False)
    comment = models.CharField(max_length=250, blank=True, null=True, default=None)

    @property
    def points(self):
        race = self.race
        scoring = self.race.season.get_scoring()
        points = 0
        if scoring:
            if 'fastest_lap' in scoring and self.fastest_lap:
                points += scoring['fastest_lap']

            points_factor = {'double': 2, 'half': 0.5}
            factor = points_factor[race.alter_punctuation] if race.alter_punctuation in points_factor else 1
            points_scoring = sorted(scoring['finish'], reverse=True)
            if self.finish:
                scoring_len = len(points_scoring)
                if self.finish <= scoring_len:
                    points += points_scoring[self.finish-1]*factor
        return points if points > 0 else None


    class Meta:
        unique_together = ('race', 'contender')

