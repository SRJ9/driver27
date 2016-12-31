from .models import Competition, Race, Result, Season, Seat
from rest_framework import routers, serializers, viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from django_countries.serializer_fields import CountryField


class SeatSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Seat
        fields = ('team_id', 'contender_id', 'current', 'seasons')


# ViewSets define the view behavior.
class SeatViewSet(viewsets.ModelViewSet):
    queryset = Seat.objects.all()
    serializer_class = SeatSerializer


class ResultSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Result
        fields = ('race', 'seats', 'qualifying', 'finish', 'fastest_lap', 'wildcard',
                  'retired', 'comment')


# ViewSets define the view behavior.
class ResultViewSet(viewsets.ModelViewSet):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer


class RaceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Race
        fields = ('season', 'round', 'round', 'date', 'alter_punctuation',)


# ViewSets define the view behavior.
class RaceViewSet(viewsets.ModelViewSet):
    queryset = Race.objects.all()
    serializer_class = RaceSerializer

    @detail_route(methods=['get'])
    def results(self, request, pk=None):
        race = self.get_object()
        self.queryset = race.results.all()
        serializer = ResultSerializer(instance=self.queryset, many=True, context={'request': request})
        return Response(serializer.data)


class SeasonSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Season
        fields = ('year', 'competition', 'rounds', 'punctuation', 'races')


# ViewSets define the view behavior.
class SeasonViewSet(viewsets.ModelViewSet):
    queryset = Season.objects.all()
    serializer_class = SeasonSerializer

    @detail_route(methods=['get'])
    def races(self, request, pk=None):
        season = self.get_object()
        self.queryset = season.races.all()
        serializer = RaceSerializer(instance=self.queryset, many=True, context={'request': request})
        return Response(serializer.data)


class CompetitionSerializer(serializers.HyperlinkedModelSerializer):
    # https://github.com/SmileyChris/django-countries/issues/106
    country = CountryField()

    class Meta:
        model = Competition
        fields = ('name', 'full_name', 'country', 'slug')


# ViewSets define the view behavior.
class CompetitionViewSet(viewsets.ModelViewSet):
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'competitions', CompetitionViewSet)
router.register(r'races', RaceViewSet)
router.register(r'results', ResultViewSet)
router.register(r'seasons', SeasonViewSet)
router.register(r'seats', SeatViewSet)
