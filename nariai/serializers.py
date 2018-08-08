import json

from rest_framework import serializers
from .models import Group, Politician, Membership

#===SERIALIZER CUSTOM FIELDS===

#paverčia politiko bio laikomą json'u į python dict'ą
class BioField(serializers.Field):
    def to_representation(self, value):
        return json.loads(value)

#paverčia projektą į paprastą dictą
class ProjectField(serializers.RelatedField):
    def to_representation(self, value):
        return dict(code=value.code, title=value.title, date_start=value.date_start)


#===SERIALIZERS===

#narystės serializeris, rodomas prie PoliticianFullSerializer
class MembershipSerializer(serializers.ModelSerializer):
    group = serializers.StringRelatedField(read_only = True) #grupės pavadinimas
    grouptype = serializers.SerializerMethodField() #grupės tipas
    id = serializers.SerializerMethodField() #grupės, ne membership, id

    get_grouptype = lambda self, obj: obj.group.get_grouptype_display()
    get_id = lambda self, obj: obj.group.id

    class Meta:
        model = Membership
        exclude = ('member',)


#sutrauktas politiko serializeris, naudojamas su politikų sąrašais ir prie projektų
class PoliticianSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Politician
        fields = ('id', 'name','photo','meetings_total','meetings_attended','attendance', 'effectiveness','activity','area','party','description')


#prie PoliticianSummarySerializer prideda visą bio, nario grupes ir inicijuotus projektus
class PoliticianFullSerializer(PoliticianSummarySerializer):
    bio = BioField(read_only = True)
    groups = serializers.SerializerMethodField()
    projects = ProjectField(read_only = True, many = True)

    def get_groups(self, obj):
        queryset = Membership.objects.filter(member = obj)
        return MembershipSerializer(queryset, many = True).data

    class Meta:
        model = Politician
        fields = '__all__'


#serializuoja grupę
class GroupSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()
    grouptype = serializers.SerializerMethodField()

    def get_members(self, obj):
        queryset = obj.politician_set.all()
        return PoliticianSummarySerializer(queryset, many = True).data

    get_grouptype = lambda self, obj: obj.get_grouptype_display()

    class Meta:
        model = Group
        fields = '__all__'


