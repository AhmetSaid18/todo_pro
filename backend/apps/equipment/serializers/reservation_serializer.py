from rest_framework import serializers
from apps.core.serializers import AgencyModelSerializer
from apps.equipment.models import EquipmentReservation
from django.db.models import Q

class EquipmentReservationSerializer(AgencyModelSerializer):
    """
    Rezervasyon işlemi.
    Critical: Overlap Check (Çakışma Kontrolü) burada yapılır.
    """
    class Meta:
        model = EquipmentReservation
        fields = '__all__'
        read_only_fields = ['reserved_by', 'agency', 'status']

    def validate(self, data):
        """
        ÇAKIŞMA KONTROLÜ
        """
        equipment = data['equipment']
        start = data['start_date']
        end = data['end_date']

        conflicts = EquipmentReservation.objects.filter(
            agency=equipment.agency,
            equipment=equipment,
            status__in=['approved', 'active'],
        ).filter(
            Q(start_date__lt=end) & Q(end_date__gt=start)
        )

        if self.instance:
             conflicts = conflicts.exclude(id=self.instance.id)

        if conflicts.exists():
            conflict_names = ", ".join([str(c.project or "Bireysel") for c in conflicts])
            raise serializers.ValidationError(f"Bu tarihlerde ekipman dolu! (Çakışan: {conflict_names})")

        return data
