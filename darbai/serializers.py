from rest_framework import serializers

from nariai.serializers import PoliticianSummarySerializer
from .models import Project, Vote, Link

#Viskas čia tiesiog paverčia modelių duomenis į JSON
#Verta kartu pažiūrėt ir į models.py

#===CUSTOM FIELDS

#naudojama VoteSerializer pateikti duomenis apie balsavusį politiką
class VoterField(serializers.RelatedField):
    def to_representation(self, value):
        return {'name': value.name, 
                'id': value.id, 
                'active': value.active
        }

#===SERIALIZERS===

#Pateikia paprastus duomenis apie projektą
class ProjectSerializer(serializers.ModelSerializer):
    initiators = serializers.SerializerMethodField()

    get_initiators = lambda self, obj: PoliticianSummarySerializer(obj.initiators, many=True).data
    
    class Meta:
        model = Project
        exclude = ('hidden',)

#Naudojama tik ProjectVoteSerializer pateikti balsų už projektą sąrašui
class VoteSerializer(serializers.ModelSerializer):
    voter = VoterField(read_only = True)

    class Meta:
        model = Vote
        fields = ('vote', 'voter','fraction')


class RecordSerializer(serializers.ModelSerializer):
    balsavimas_type = serializers.CharField(source="get_balsavimas_type_display")
    balsavimas_result = serializers.CharField(source="get_balsavimas_result_display")
    votes = serializers.SerializerMethodField()

    get_votes = lambda self, obj: VoteSerializer(obj.votes, many=True).data

    class Meta:
        model = Link
        exclude = ('funny', 'projects')


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link
        fields = ('href', 'level', 'extra', 'date', 'time')

#Pateikia praktiškai visus duomenis apie projektą
class ProjectVoteSerializer(serializers.ModelSerializer):
    votes = serializers.SerializerMethodField()
    initiators = serializers.SerializerMethodField()
    #votes_fraction = serializers.SerializerMethodField()
    related_projects = serializers.SerializerMethodField()
    schedule_entries = serializers.SerializerMethodField()

    get_initiators = lambda self, obj: PoliticianSummarySerializer(obj.initiators, many=True).data
    get_schedule_entries = lambda self, obj: ScheduleSerializer(obj.schedule_entries, many=True).data
    #get_votes_fraction = lambda self, obj: obj.votes_fraction()

    def get_votes(self, obj):
        queryset = Link.objects.filter(level='b', parent__projects=obj)
        return RecordSerializer(queryset, many=True).data

    def get_related_projects(self, obj):
        queryset = Project.objects.filter(metacode=obj.metacode).exclude(code=obj.code)
        return ProjectSerializer(queryset, many=True).data

    class Meta:
        model = Project
        exclude = ('hidden',)
