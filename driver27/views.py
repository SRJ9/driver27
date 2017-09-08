# -*- coding: utf-8 -*-
from django.db.models import Count
from django.http import Http404
from django.shortcuts import render
from django.utils.translation import ugettext as _

from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect
try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse

from .models import Competition, Season, Race, RankModel, Driver, Team, get_tuples_from_results
from .records import get_record_config, get_record_label_dict
from .punctuation import get_punctuation_config, get_punctuation_label_dict
from . import LIMIT_POSITION_LIST
from .common import get_season_or_competition, split_season_and_competition
from django.shortcuts import render, get_object_or_404


def competition_view(request, competition_slug):
    competition_obj = get_object_or_404(Competition, slug=competition_slug)
    title = '{competition}'.format(competition=competition_obj)
    context = {'competition': competition_obj, 'title': title}
    tpl = 'driver27/competition/competition-view.html'
    return render(request, tpl, context)


def global_view(request):
    title = _('Global view')
    context = {'title': title}
    tpl = 'driver27/global/global-view.html'
    return render(request, tpl, context)

def global_tpl(request):
    seasons = Season.objects.order_by('year', 'competition')
    context = {'seasons': seasons}
    tpl = 'driver27/global/_season_list.html'
    return render(request, tpl, context)


def season_view(request, competition_slug, year):
    season = get_object_or_404(Season, competition__slug=competition_slug, year=year)
    title = '{competition}/{year:d}'.format(competition=season.competition, year=season.year)
    context = {'season': season, 'title': title}
    tpl = 'driver27/season/season-view.html'
    return render(request, tpl, context)


def _rank_view(request, competition_slug, year, rank_model='driver', by_season=False):
    season_or_competition = get_season_or_competition(competition_slug, year)
    season, competition = split_season_and_competition(season_or_competition)
    by_season = request.POST.get('by_season', by_season)
    scoring_code = request.POST.get('scoring', None)

    punctuation_selector = get_punctuation_label_dict()
    if rank_model == 'driver':
        rank_title = _('DRIVERS')
    elif rank_model == 'team':
        rank_title = _('TEAMS')
    else:
        raise Http404(_('Impossible rank'))

    tpl = 'driver27/' + rank_model + '/' + rank_model + '-list.html'
    title = u'{season_or_competition} [{title}]'.format(season_or_competition=season_or_competition,
                                                        title=rank_title)

    context = {
        'season': season,
        'competition': competition,
        'title': title,
        'scoring_list': punctuation_selector,
        'scoring_code': scoring_code,
        'by_season': by_season}

    return render(request, tpl, context)


def driver_comeback_view(request, competition_slug=None, year=None):
    season_or_competition = get_season_or_competition(competition_slug, year)
    season, competition = split_season_and_competition(season_or_competition)

    # rank = season_or_competition.comeback_rank()
    rank_title = _('DRIVERS Comeback')

    title = u'{season_or_competition} [{title}]'.format(season_or_competition=season_or_competition,
                                                        title=rank_title)

    context = {
        # 'rank': rank,
        'season': season,
        'competition': competition,
        'title': title
    }

    tpl = 'driver27/driver/driver-comeback.html'

    return render(request, tpl, context)


def driver_rank_view(request, competition_slug=None, year=None):
    return _rank_view(request, competition_slug, year, rank_model='driver')


def driver_rank_seasons_view(request, competition_slug=None, year=None):
    return _rank_view(request, competition_slug, year, rank_model='driver', by_season=True)


def common_olympic_view(request, tpl, olympic_method, rank_title, competition_slug=None, year=None):
    season_or_competition = get_season_or_competition(competition_slug, year)
    season, competition = split_season_and_competition(season_or_competition)
    # rank = getattr(season_or_competition, olympic_method)()

    title = u'{season_or_competition} [{title}]'.format(season_or_competition=season_or_competition,
                                                        title=rank_title)

    context = {
        # 'rank': rank,
        'season': season,
        'competition': competition,
        'title': title,
        'olympic': True
    }
    return render(request, tpl, context)

def driver_olympic_view(request, competition_slug=None, year=None):
    return common_olympic_view(request, 'driver27/driver/driver-list.html', 'olympic_rank',
                               _('DRIVERS rank by olympic mode'), competition_slug=competition_slug, year=year)


def team_olympic_view(request, competition_slug=None, year=None):
    return common_olympic_view(request, 'driver27/team/team-list.html', 'team_olympic_rank',
                               _('TEAMS rank by olympic mode'), competition_slug=competition_slug, year=year)

def driver_season_pos_view(request, competition_slug, year):
    season = get_object_or_404(Season, competition__slug=competition_slug, year=year)
    rank = season.get_positions_draw()
    rank_title = 'POSITION draw'
    title = u'{season} [{title}]'.format(season=season,
                                         title=rank_title)
    context = {
        # 'rank': rank,
        'season': season,
        'title': title,
        'positions': list(season.past_races.values_list('round', flat=True)),
        'olympic': True}
    return render(request, 'driver27/driver/driver-list.html', context)

def team_rank_view(request, competition_slug=None, year=None):
    return _rank_view(request, competition_slug, year, rank_model='team')


def team_rank_seasons_view(request, competition_slug=None, year=None):
    return _rank_view(request, competition_slug, year, rank_model='team', by_season=True)


def race_list(request, competition_slug, year):
    season = get_object_or_404(Season, competition__slug=competition_slug, year=year)
    races = season.races.all()
    title = _('%(season)s [RACES]') % {'season': season}
    context = {'races': races, 'season': season, 'title': title}
    tpl = 'driver27/race/race-list.html'
    return render(request, tpl, context)


def race_view(request, competition_slug, year, race_id=None):
    race = get_object_or_404(Race, season__competition__slug=competition_slug, season__year=year, pk=race_id)
    results = race.results.all() \
        .annotate(null_position=Count('finish')).order_by('-null_position', 'finish', 'qualifying')
    title = _('Results of %(race)s') % {'race': race}
    context = {'race': race, 'season': race.season, 'title': title, 'results': results}
    tpl = 'driver27/race/race-view.html'
    return render(request, tpl, context)


def get_safe_record_config(record):
    record_config = get_record_config(record)
    if record_config:
        return record_config
    else:
        raise Http404(_('Record does not exist'))


def get_record_common_context(request, competition_slug, year, record=None):
    season_or_competition = get_season_or_competition(competition_slug, year)
    season, competition = split_season_and_competition(season_or_competition)

    context = {
        'season_or_competition': season_or_competition,
        'season': season,
        'competition': competition,
        'record': record,
    }
    if record:
        record_config = get_safe_record_config(record)
        record_label = record_config.get('label')
        title = _('%(record_label)s Record, %(season_or_competition)s') \
                % {'record_label': record_label, 'season_or_competition': season_or_competition}
        context['record_filter'] = record_config.get('filter')
    else:
        title = _('Select a %(season_or_competition)s record') % {'season_or_competition': season_or_competition}

    context['title'] = title
    context['record_codes'] = get_record_label_dict()
    return context


def driver_record_view(request, competition_slug=None, year=None, record=None):
    context = get_record_common_context(request, competition_slug, year, record)
    rank = None
    season_or_competition = context.get('season_or_competition')
    if record:
        rank = None
        # rank = season_or_competition.stats_rank(**context.get('record_filter')) if 'record_filter' in context else None
    context.pop('record_filter', None)
    context['rank'] = rank
    tpl = 'driver27/driver/driver-record.html'
    return render(request, tpl, context)


def common_record_seasons_view(request, tpl, season_rank_method, competition_slug=None, year=None, record=None):
    context = get_record_common_context(request, competition_slug, year, record)
    rank = None
    season_or_competition = context.get('season_or_competition')
    if record:
        # rank = getattr(season_or_competition, season_rank_method)(**context.get('record_filter')) \
        #     if 'record_filter' in context else None
        rank = None
    context.pop('record_filter', None)
    context['rank'] = rank
    context['rank_opt'] = 'seasons'
    return render(request, tpl, context)


def driver_record_seasons_view(request, competition_slug=None, year=None, record=None):
    return common_record_seasons_view(request, 'driver27/driver/driver-record.html', 'seasons_rank',
                                      competition_slug=competition_slug, year=year, record=record)


def team_record_seasons_view(request, competition_slug=None, year=None, record=None):
    return common_record_seasons_view(request, 'driver27/team/team-record.html', 'seasons_team_rank',
                                      competition_slug=competition_slug, year=year, record=record)


def driver_active_streak_view(request, competition_slug=None, year=None, record=None):
    return driver_streak_view(request, competition_slug=competition_slug, year=year, record=record, only_actives=True)


def driver_top_streak_view(request, competition_slug=None, year=None, record=None):
    return driver_streak_view(request, competition_slug=competition_slug, year=year, record=record, max_streak=True)


def driver_top_streak_active_view(request, competition_slug=None, year=None, record=None):
    return driver_streak_view(request, competition_slug=competition_slug, year=year, record=record,
                              only_actives=True, max_streak=True)


def team_top_streak_view(request, competition_slug=None, year=None, record=None):
    return team_streak_view(request, competition_slug=competition_slug, year=year, record=record, max_streak=True)


def get_streak_value_for_selector(only_actives=False, max_streak=False):
    if not only_actives:
        if max_streak:
            streak_value = 'streak_top'
        else:
            streak_value = 'streak'
    else:
        if max_streak:
            streak_value = 'streak_top_actives'
        else:
            streak_value = 'streak_actives'
    return streak_value


def common_streak_view(request, streak_method, tpl, competition_slug=None, year=None, record=None, only_actives=False,
                       max_streak=False,
                       ):
    context = get_record_common_context(request, competition_slug, year, record)
    rank = None
    season_or_competition = context.get('season_or_competition')
    if record:
        # rank = getattr(season_or_competition, streak_method)(only_actives=only_actives, max_streak=max_streak,
        #                                                      **context.get('record_filter')) \
        #     if 'record_filter' in context else None
        rank = None
    context.pop('record_filter', None)
    context['rank'] = rank
    context['rank_opt'] = get_streak_value_for_selector(only_actives=only_actives, max_streak=max_streak)
    return render(request, tpl, context)


def driver_streak_view(request, competition_slug=None, year=None, record=None, only_actives=False, max_streak=False):
    return common_streak_view(request, 'streak_rank', 'driver27/driver/driver-record.html',
                              competition_slug=competition_slug, year=year, record=record, only_actives=only_actives,
                              max_streak=max_streak)


def team_streak_view(request, competition_slug=None, year=None, record=None, only_actives=False, max_streak=False):
    return common_streak_view(request, 'streak_team_rank', 'driver27/team/team-record.html',
                              competition_slug=competition_slug, year=year, record=record, only_actives=only_actives,
                              max_streak=max_streak)


def team_record_doubles_view(request, competition_slug=None, year=None, record=None):
    return _team_record_view(request, competition_slug, year, record=record, rank_type='DOUBLES')


def team_record_races_view(request, competition_slug=None, year=None, record=None):
    return _team_record_view(request, competition_slug, year, record=record, rank_type='RACES')


def team_record_view(request, competition_slug=None, year=None, record=None):
    return _team_record_view(request, competition_slug, year, record=record, rank_type='STATS')


def _team_record_view(request, competition_slug, year, rank_type, record=None):
    context = get_record_common_context(request, competition_slug, year, record)

    rank = None
    season_or_competition = context.get('season_or_competition')
    if record:
        # rank = season_or_competition.get_team_rank(rank_type, **context.get('record_filter')) if 'record_filter' in context else None
        rank = None
    context['rank'] = rank
    context['rank_opt'] = rank_type
    context['doubles_record_codes'] = [double_code for double_code, double_label in get_record_label_dict(doubles=True)]
    tpl = 'driver27/team/team-record.html'
    return render(request, tpl, context)


def driver_profile_view(request, driver_id):
    driver = get_object_or_404(Driver, pk=driver_id)
    by_season = driver.get_stats_by_season(append_points=True)
    by_competition = driver.get_stats_by_competition(append_points=True)
    context = {
        'driver': driver,
        'by_season': by_season,
        'by_competition': by_competition,
        'results': get_tuples_from_results(driver.get_results()),
        'stats': driver.get_stats_list(append_points=True),
        'title': 'Profile of {driver}'.format(driver=driver)
    }
    tpl = 'driver27/driver/driver-profile.html'
    return render(request, tpl, context)


def team_profile_view(request, team_id):
    team = get_object_or_404(Team, pk=team_id)
    by_season = team.get_stats_by_season(append_points=True)
    by_competition = team.get_stats_by_competition(append_points=True)
    context = {
        'team': team,
        'by_season': by_season,
        'by_competition': by_competition,
        'stats': team.get_stats_list(append_points=True),
        'title': 'Profile of {team}'.format(team=team)
    }
    tpl = 'driver27/team/team-profile.html'
    return render(request, tpl, context)


def _get_reverse_record_url(request):
    competition_slug = request.POST.get('competition', None)
    year = request.POST.get('year', None)
    record = request.POST.get('record', '')

    request_args = [competition_slug, year, record]
    reverse_args = [arg for arg in request_args if arg]

    if competition_slug and year:
        base_reverse_url = 'dr27-season'
    elif competition_slug:
        base_reverse_url = 'dr27-competition'
    else:
        base_reverse_url = 'dr27-global'

    return base_reverse_url, reverse_args


@require_http_methods(["POST"])
def team_record_redirect_view(request):
    base_reverse_url, reverse_args = _get_reverse_record_url(request)
    rank_opt = request.POST.get('rank_opt')
    if not rank_opt:
        rank_opt = 'stats'

    reverse_url_dict = \
        {
            'streak': 'streak',
            'streak_top': 'top-streak',
            'doubles': 'record-doubles',
            'races': 'record-races',
            'stats': 'record'
        }

    if not (request.POST.get('competition') and request.POST.get('year')):
        reverse_url_dict['seasons'] = 'seasons'

    reverse_url = reverse_url_dict.get(rank_opt, 'stats')

    return redirect(reverse('-'.join([base_reverse_url, 'team', reverse_url]), args=reverse_args))


@require_http_methods(["POST"])
def driver_record_redirect_view(request):
    base_reverse_url, reverse_args = _get_reverse_record_url(request)
    rank_opt = request.POST.get('rank_opt')
    if not rank_opt:
        rank_opt = 'stats'

    reverse_url_dict = \
        {
            'streak': 'streak',
            'streak_top': 'top-streak',
            'streak_actives': 'active-streak',
            'streak_top_actives': 'active-top-streak',
        }

    if not (request.POST.get('competition') and request.POST.get('year')):
        reverse_url_dict['seasons'] = 'seasons'

    reverse_url = reverse_url_dict.get(rank_opt, 'record')

    return redirect(reverse('-'.join([base_reverse_url, 'driver', reverse_url]), args=reverse_args))
