from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import viewsets, authentication, permissions, status, filters
from rest_framework.compat import set_rollback
from rest_framework.response import Response
from rest_framework.views import exception_handler as rest_exception_handler
from django_filters.rest_framework import DjangoFilterBackend
from collections import namedtuple



def get_dict_from_team_rank_entry(rank_entry):

    return {
        'points': rank_entry['points'],
        'team': rank_entry['team'].name,
        'positions_order': rank_entry['pos_str']
     }


def get_dict_from_races(races):
    return [
        {
            'id': race.pk,
            'name': u'{race}'.format(race=race),
            'alter_punctuation': race.alter_punctuation
        }
        for race in races
    ]


def get_dict_from_rank_entry(rank_entry):

    return {
        'points': rank_entry['points'],
        'driver': {
            'id': rank_entry['driver'].id,
            'last_name': rank_entry['driver'].last_name,
            'first_name': rank_entry['driver'].first_name,
            'country': rank_entry['driver'].country.code
        },
        'teams': rank_entry['teams'],
        'positions_order': rank_entry['pos_str']
     }


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
    # authentication_classes = (authentication.SessionAuthentication, authentication.BasicAuthentication)
    # permission_classes = (permissions.IsAuthenticated,)

    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)

    def get_exception_handler(self):
        return custom_exception_handler


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