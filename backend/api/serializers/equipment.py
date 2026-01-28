from rest_framework import serializers
from api.serializers.base import AgencyModelSerializer
from api.models import Equipment, EquipmentCategory, EquipmentReservation
from django.db.models import Q

class CategorySerializer(AgencyModelSerializer):
    class Meta:
        model = EquipmentCategory
        fields = '__all__'

class EquipmentSerializer(AgencyModelSerializer):
    # ... (Aynı kalacak)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Equipment
        fields = '__all__'
        read_only_fields = ['created_by', 'agency', 'qr_code']

class EquipmentReservationSerializer(AgencyModelSerializer):
    """
    Çakışma Kontrolü & Waitlist Logic
    """
    class Meta:
        model = EquipmentReservation
        fields = '__all__'
        read_only_fields = ['reserved_by', 'agency', 'status']

    def validate(self, data):
        """
        ÇAKIŞMA KONTROLÜ
        Eğer çakışma varsa ve kullanıcı waitlist istemediyse hata dön.
        Waitlist istediyse kabul et ama status 'waitlist' olacak (View tarafında set edilir).
        """
        equipment = data['equipment']
        start = data['start_date']
        end = data['end_date']

        # Çakışan rezervasyonlar (Onaylı veya Aktif)
        conflicts = EquipmentReservation.objects.filter(
            agency=equipment.agency,
            equipment=equipment,
            status__in=['approved', 'active'],
        ).filter(Q(start_date__lt=end) & Q(end_date__gt=start))

        if self.instance:
             conflicts = conflicts.exclude(id=self.instance.id)

        if conflicts.exists():
            # Kullanıcı "Evet, sıraya al" dediyse (waitlist=True) hata fırlatma
            request = self.context.get('request')
            is_waitlist = request.data.get('waitlist') if request else False
            
            # String 'true' gelebilir, onu handle et
            if str(is_waitlist).lower() == 'true':
                 return data # Validasyondan geçir, create'de waitlist yapacağız

            conflict_names = ", ".join([str(c.project or "Bireysel") for c in conflicts])
            raise serializers.ValidationError({
                "code": "conflict",
                "message": f"Bu tarihlerde ({conflict_names}) tarafından dolu.",
                "can_waitlist": True
            })

        return data
    
    def create(self, validated_data):
        request = self.context.get('request')
        is_waitlist = request.data.get('waitlist') if request else False
        
        if str(is_waitlist).lower() == 'true':
            validated_data['status'] = 'waitlist'
            
        return super().create(validated_data)
