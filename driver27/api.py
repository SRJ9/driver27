from django.core.exceptions import ValidationError as DjangoValidationError
from django_countries.serializer_fields import CountryField
from rest_framework import routers, serializers, viewsets, authentication, permissions, status
from rest_framework.compat import set_rollback
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.views import exception_handler as rest_exception_handler

from .models import Competition, Contender, Driver, Race, Result, Season, Seat, Team, GrandPrix, Circuit


# based on:
# https://github.com/tomchristie/django-rest-framework/pull/3149/commits/413fe93dbfda41e3b7890ea9550d60bca3315761
# https://github.com/RockHoward/django-rest-framework
def custom_exception_handler(exc, context):
    response = rest_exception_handler(exc, context)
    if isinstance(exc, DjangoValidationError):
        data = {'detail': exc.messages}
        set_rollback()
        return Response(data, status=status.HTTP_400_BAD_REQUEST)
    return response


class DR27Serializer(object):
    def __init__(self, *args, **kwargs):
        self.exclude_fields = kwargs.pop('exclude_fields', None)
        super(DR27Serializer, self).__init__(*args, **kwargs)

    def get_field_names(self, declared_fields, info):
        fields = super(DR27Serializer, self).get_field_names(declared_fields, info)
        if getattr(self, 'exclude_fields', None):
            fields = tuple([x for x in fields if x not in self.exclude_fields])
        return fields


class DR27ViewSet(viewsets.ModelViewSet):
    authentication_classes = (authentication.SessionAuthentication, authentication.BasicAuthentication)
    permission_classes = (permissions.IsAuthenticated,)

    def get_exception_handler(self):
        return custom_exception_handler


class GrandPrixSerializer(DR27Serializer, serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    country = CountryField()

    class Meta:
        model = GrandPrix
        fields = ('url', 'id', 'country', 'name', 'first_held', 'default_circuit', 'competitions',)


class CircuitSerializer(DR27Serializer, serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    country = CountryField()

    class Meta:
        model = Circuit
        fields = ('url', 'id', 'country', 'name', 'city', 'opened_in',)


class SeasonSerializer(DR27Serializer, serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    competition_details = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField(read_only=True)
    races = serializers.HyperlinkedRelatedField(view_name='race-detail',
                                                many=True,
                                                read_only=True)

    def get_competition_details(self, obj):
        return CompetitionSerializer(instance=obj.competition, many=False,
                                     context=self.context, exclude_fields=['seasons', ]).data

    def get_slug(self, obj):
        return '-'.join((obj.competition.slug, str(obj.year)))

    class Meta:
        model = Season
        fields = ('url', 'id', 'year', 'rounds', 'slug', 'punctuation', 'competition',
                  'competition_details', 'races',)
        read_only_fields = ('competition_details', 'races',)


class CompetitionSerializer(DR27Serializer, serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    # https://github.com/SmileyChris/django-countries/issues/106
    country = CountryField()
    seasons = SeasonSerializer(many=True, exclude_fields=['competition', 'competition_details', 'races'])

    class Meta:
        model = Competition
        fields = ('url', 'id', 'name', 'full_name', 'country', 'slug', 'seasons')


class DriverSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    country = CountryField()

    class Meta:
        model = Driver
        fields = ('url', 'id', 'last_name', 'first_name', 'year_of_birth', 'country', 'competitions')
        read_only_fields = ('competitions',)


class NestedDriverSerializer(DriverSerializer):
    class Meta:
        model = Driver
        fields = ('url', 'last_name', 'first_name', 'year_of_birth', 'country')


class TeamSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    country = CountryField()

    class Meta:
        model = Team
        fields = ('url', 'id', 'name', 'full_name', 'competitions', 'country')


class NestedTeamSerializer(TeamSerializer):
    class Meta:
        model = Team
        fields = ('url', 'name', 'full_name', 'country')


#
#


class ContenderSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    driver = NestedDriverSerializer(many=False)
    teams = NestedTeamSerializer(many=True)

    # competition = CompetitionSerializer(many=False)

    class Meta:
        model = Contender
        fields = ('url', 'id', 'driver', 'competition', 'teams')


#
class NestedContenderSerializer(ContenderSerializer):
    driver = NestedDriverSerializer(many=False)

    class Meta:
        model = Contender
        fields = ('url', 'driver')


class SeatSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    team_details = serializers.SerializerMethodField()
    contender_details = serializers.SerializerMethodField()

    def get_team_details(self, obj):
        return TeamSerializer(instance=obj.team, many=False,
                              context=self.context).data

    def get_contender_details(self, obj):
        return ContenderSerializer(instance=obj.contender, many=False,
                                   context=self.context).data

    class Meta:
        model = Seat
        fields = ('url', 'id', 'team', 'team_details', 'contender', 'contender_details', 'current', 'seasons')


class SeatRecapSerializer(serializers.ModelSerializer):
    contender = serializers.SerializerMethodField()
    team = serializers.SerializerMethodField()

    def get_contender(self, obj):
        contender = obj.contender
        return {
            'id': contender.id,
            'driver': {
                'id': contender.driver.id,
                'first_name': contender.driver.first_name,
                'last_name': contender.driver.last_name
            }
        }

    def get_team(self, obj):
        team = obj.team
        return {
            'id': team.id,
            'name': team.name
        }

    class Meta:
        model = Seat
        fields = ('contender',
                  'team')


class ResultSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    seat_details = serializers.SerializerMethodField()

    def get_seat_details(self, obj):
        return SeatRecapSerializer(instance=obj.seat,
                                   many=False,
                                   context=self.context).data

    class Meta:
        model = Result
        fields = ('url',
                  'id',
                  'race',
                  'seat',
                  'seat_details',
                  'qualifying',
                  'finish',
                  'fastest_lap',
                  'wildcard',
                  'retired',
                  'comment')


class RaceSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    grand_prix_details = serializers.SerializerMethodField()
    circuit_details = serializers.SerializerMethodField()

    def get_grand_prix_details(self, obj):
        return GrandPrixSerializer(instance=obj.grand_prix,
                                   many=False,
                                   context=self.context,
                                   exclude_fields=['competitions', ]).data

    def get_circuit_details(self, obj):
        return CircuitSerializer(instance=obj.circuit,
                                 many=False,
                                 context=self.context).data

    class Meta:
        model = Race
        fields = ('url', 'id', 'season', 'round', 'grand_prix', 'grand_prix_details',
                  'circuit', 'circuit_details', 'date', 'alter_punctuation')


# # ViewSets define the view behavior.
class RaceViewSet(DR27ViewSet):
    queryset = Race.objects.all()
    serializer_class = RaceSerializer

    @detail_route(methods=['get'])
    def results(self, request, pk=None):
        race = self.get_object()
        self.queryset = race.results.all()
        serializer = ResultSerializer(instance=self.queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def seats(self, request, pk=None):
        race = self.get_object()
        self.queryset = Seat.objects.filter(results__race=race)
        serializer = SeatSerializer(instance=self.queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @detail_route(methods=['get'], url_path='not-start-seats')
    def no_start_seats(self, request, pk=None):
        race = self.get_object()
        self.queryset = Seat.objects.filter(seasons=race.season).exclude(results__race=race)
        serializer = SeatSerializer(instance=self.queryset, many=True, context={'request': request})
        return Response(serializer.data)


# ViewSets define the view behavior.
class SeasonViewSet(DR27ViewSet):
    queryset = Season.objects.all()
    serializer_class = SeasonSerializer

    @detail_route(methods=['get'])
    def races(self, request, pk=None):
        season = self.get_object()
        self.queryset = season.races.all()
        serializer = RaceSerializer(instance=self.queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @detail_route(methods=['get'])
    def seats(self, request, pk=None):
        season = self.get_object()
        self.queryset = season.seats.all()
        serializer = SeatSerializer(instance=self.queryset, many=True, context={'request': request})
        return Response(serializer.data)


# ViewSets define the view behavior.
class CircuitViewSet(DR27ViewSet):
    queryset = Circuit.objects.all()
    serializer_class = CircuitSerializer


# ViewSets define the view behavior.
class GrandPrixViewSet(DR27ViewSet):
    queryset = GrandPrix.objects.all()
    serializer_class = GrandPrixSerializer


# ViewSets define the view behavior.
class CompetitionViewSet(DR27ViewSet):
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer


# ViewSets define the view behavior.
class ResultViewSet(DR27ViewSet):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer


# ViewSets define the view behavior.
class ContenderViewSet(DR27ViewSet):
    queryset = Contender.objects.all()
    serializer_class = ContenderSerializer


# ViewSets define the view behavior.
class DriverViewSet(DR27ViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer


# ViewSets define the view behavior.
class TeamViewSet(DR27ViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer


# ViewSets define the view behavior.
class SeatViewSet(DR27ViewSet):
    queryset = Seat.objects.all()
    serializer_class = SeatSerializer


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'circuits', CircuitViewSet)
router.register(r'competitions', CompetitionViewSet)
router.register(r'contenders', ContenderViewSet)
router.register(r'drivers', DriverViewSet)
router.register(r'grands-prix', GrandPrixViewSet)
router.register(r'races', RaceViewSet)
router.register(r'results', ResultViewSet)
router.register(r'seasons', SeasonViewSet)
router.register(r'seats', SeatViewSet)
router.register(r'teams', TeamViewSet)
