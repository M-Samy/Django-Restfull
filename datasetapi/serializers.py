from rest_framework.serializers import ModelSerializer
from .models import Dataset


# Serializers define the API representation.
class DataSerializer(ModelSerializer):
    class Meta:
        model = Dataset
        fields = "__all__"
