from rest_framework import serializers

class AgencyModelSerializer(serializers.ModelSerializer):
    """
    Otomatik olarak 'agency' alanını yöneten Base Serializer.
    Read: Agency bilgisini göstermez (zaten kullanıcının ajansı)
    Write: Agency bilgisini request.user.current_agency'den alır.
    """
    
    def create(self, validated_data):
        user = self.context['request'].user
        if not user.current_agency:
            raise serializers.ValidationError("Kullanıcının aktif bir ajansı yok!")
        
        validated_data['agency'] = user.current_agency
        return super().create(validated_data)
