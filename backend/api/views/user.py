from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from api.models import User, AgencyMembership
from api.serializers.user import UserSerializer, AgencyMembershipSerializer
from django.db.models import Q, Count

class UserViewSet(viewsets.ModelViewSet):
    """
    👥 KULLANICI & EKİP YÖNETİMİ
    
    Features:
    - Kullanıcı profilleri
    - Agency membership yönetimi
    - Ekip listesi
    - Müsaitlik durumları
    - Performance tracking
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Sadece aynı agency'deki kullanıcıları göster"""
        if not self.request.user.current_agency:
            return User.objects.none()
        
        # Aynı agency'deki tüm members
        return User.objects.filter(
            memberships__agency=self.request.user.current_agency,
            memberships__is_active=True
        ).distinct()

    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        👤 Kendi Profilim
        Kullanıcının kendi bilgileri
        """
        serializer = self.get_serializer(request.user)
        
        # Extra info
        membership = AgencyMembership.objects.filter(
            user=request.user,
            agency=request.user.current_agency
        ).first()
        
        extra = {
            'current_agency': {
                'id': request.user.current_agency.id,
                'name': request.user.current_agency.name,
                'plan': request.user.current_agency.plan
            } if request.user.current_agency else None,
            'role': membership.role.name if membership and membership.role else None,
            'is_owner': membership.is_owner if membership else False,
        }
        
        return Response({
            **serializer.data,
            **extra
        })

    @action(detail=False, methods=['get'])
    def team(self, request):
        """
        👥 Ekip Listesi
        Agency'deki tüm aktif kullanıcılar
        """
        team_members = self.get_queryset().select_related(
            'current_agency'
        ).prefetch_related('memberships')
        
        result = []
        for user in team_members:
            membership = user.memberships.filter(
                agency=request.user.current_agency
            ).first()
            
            result.append({
                'id': user.id,
                'name': user.get_full_name() or user.email,
                'email': user.email,
                'avatar': user.avatar.url if user.avatar else None,
                'phone': user.phone,
                'role': membership.role.name if membership and membership.role else 'Member',
                'is_owner': membership.is_owner if membership else False,
                'joined_at': membership.joined_at if membership else None
            })
        
        return Response({
            'count': len(result),
            'team_members': result
        })

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """
        📊 Kullanıcı İstatistikleri
        - Kaç proje
        - Kaç görev tamamladı
        - Ekipman kullanımı
        - Performance
        """
        user = self.get_object()
        
        # Task stats
        from api.models import Task
        tasks = Task.objects.filter(
            assigned_to=user,
            agency=request.user.current_agency
        )
        
        task_stats = {
            'total': tasks.count(),
            'completed': tasks.filter(status='done').count(),
            'in_progress': tasks.filter(status='in_progress').count(),
            'pending': tasks.filter(status__in=['not_started', 'in_review', 'revision_needed']).count()
        }
        
        # Completion rate
        completion_rate = (
            (task_stats['completed'] / task_stats['total']) * 100
            if task_stats['total'] > 0 else 0
        )
        
        # Projects involved
        from api.models import Project
        projects = Project.objects.filter(
            Q(team_members=user) | Q(created_by=user),
            agency=request.user.current_agency
        ).distinct()
        
        project_stats = {
            'total': projects.count(),
            'as_team_member': projects.filter(team_members=user).count(),
            'as_creator': projects.filter(created_by=user).count()
        }
        
        # Equipment usage
        from api.models import EquipmentReservation
        equipment_usage = EquipmentReservation.objects.filter(
            reserved_by=user,
            agency=request.user.current_agency
        ).count()
        
        return Response({
            'user': {
                'id': user.id,
                'name': user.get_full_name(),
                'email': user.email
            },
            'tasks': task_stats,
            'completion_rate': round(completion_rate, 1),
            'projects': project_stats,
            'equipment_reservations': equipment_usage
        })

    @action(detail=False, methods=['get'])
    def available(self, request):
        """
        ✅ Müsait Ekip Üyeleri
        Şu an aktif görevde olmayan kullanıcılar
        """
        from api.models import Task
        
        # Aktif görevi olmayanlar
        active_task_users = Task.objects.filter(
            agency=request.user.current_agency,
            status__in=['in_progress', 'in_review']
        ).values_list('assigned_to_id', flat=True)
        
        available_users = self.get_queryset().exclude(
            id__in=active_task_users
        )
        
        serializer = self.get_serializer(available_users, many=True)
        return Response({
            'count': available_users.count(),
            'available_users': serializer.data
        })

    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        🔍 Kullanıcı Ara
        ?q=ahmet
        """
        query = request.query_params.get('q', '').strip()
        if not query:
            return Response({'error': 'q parametresi gerekli'}, status=400)
        
        users = self.get_queryset().filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )
        
        serializer = self.get_serializer(users, many=True)
        return Response({
            'query': query,
            'count': users.count(),
            'users': serializer.data
        })

    @action(detail=True, methods=['post'])
    def update_role(self, request, pk=None):
        """
        🔑 Rol Değiştir (Owner/Admin only)
        """
        user = self.get_object()
        new_role_id = request.data.get('role_id')
        
        if not new_role_id:
            return Response({'error': 'role_id gerekli'}, status=400)
        
        # Permission check: Sadece owner değiştirebilir
        requester_membership = AgencyMembership.objects.filter(
            user=request.user,
            agency=request.user.current_agency
        ).first()
        
        if not requester_membership or not requester_membership.is_owner:
            return Response({'error': 'Sadece owner rol değiştirebilir'}, status=403)
        
        # Rol değiştir
        from api.models import AgencyRole
        try:
            new_role = AgencyRole.objects.get(
                id=new_role_id,
                agency=request.user.current_agency
            )
            
            membership = AgencyMembership.objects.get(
                user=user,
                agency=request.user.current_agency
            )
            membership.role = new_role
            membership.save()
            
            return Response({
                'message': f'{user.get_full_name()} rolü {new_role.name} olarak değiştirildi',
                'role': new_role.name
            })
        except AgencyRole.DoesNotExist:
            return Response({'error': 'Rol bulunamadı'}, status=404)
        except AgencyMembership.DoesNotExist:
            return Response({'error': 'Kullanıcı bu agency\'de değil'}, status=404)

    @action(detail=False, methods=['post'])
    def invite(self, request):
        """
        📧 Davet Gönder
        - E-posta ile kullanıcı davet et
        - Eğer kullanıcı zaten varsa agency'ye ekle
        - Yoksa hesap oluştur ve davet gönder
        """
        email = request.data.get('email')
        role_id = request.data.get('role_id')
        
        if not email:
            return Response({'error': 'email gerekli'}, status=400)
            
        agency = request.user.current_agency
        
        # 1. Kullanıcı var mı bak
        user = User.objects.filter(email=email).first()
        
        if not user:
            # 2. Kullanıcı yoksa oluştur (temporary password)
            import uuid
            temp_password = uuid.uuid4().hex[:12]
            user = User.objects.create_user(
                email=email,
                username=email,
                password=temp_password,
                first_name=request.data.get('first_name', ''),
                last_name=request.data.get('last_name', '')
            )
            created = True
        else:
            created = False
            
        # 3. Agency'ye ekle
        from api.models import AgencyRole
        role = None
        if role_id:
            role = AgencyRole.objects.filter(id=role_id, agency=agency).first()
            
        if not role:
            # Default role (Staff/Member)
            role = AgencyRole.objects.get_or_create(name='Member', agency=agency)[0]
            
        membership, m_created = AgencyMembership.objects.get_or_create(
            user=user,
            agency=agency,
            defaults={'role': role}
        )
        
        if not m_created:
            return Response({'message': f'{email} zaten bu ekipte.'}, status=200)

        return Response({
            'message': f'{email} başarıyla davet edildi.',
            'created_new_user': created,
            'user_id': user.id
        }, status=status.HTTP_201_CREATED)
