from .models import Dataset
from rest_framework.serializers import ModelSerializer


# Serializers define the API representation.
class DataSerializer(ModelSerializer):
    class Meta:
        model = Dataset
        fields = "__all__"
