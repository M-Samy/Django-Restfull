from rest_framework.serializers import ModelSerializer, SerializerMethodField
from .models import Dataset


# Serializers define the API representation.
class DataSerializer(ModelSerializer):
    cpi=SerializerMethodField()
    class Meta:
        model = Dataset
        fields = "__all__"

    def get_cpi(self, obj):
        try:
            return obj.spend / obj.installs
        except Exception as e:
            raise Http404('Failed to calculate cpi due to {}'.format(e.__doc__))
