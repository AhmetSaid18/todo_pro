from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from api.models import User, Agency, AgencyMembership, AgencyRole
from api.serializers.user import UserSerializer

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    👤 KAYIT OL
    
    Yeni kullanıcı + agency oluştur
    """
    email = request.data.get('email')
    password = request.data.get('password')
    first_name = request.data.get('first_name', '')
    last_name = request.data.get('last_name', '')
    agency_name = request.data.get('agency_name')
    
    # Validation
    if not email or not password:
        return Response({'error': 'Email ve şifre gerekli'}, status=400)
    
    if not agency_name:
        return Response({'error': 'Ajans adı gerekli'}, status=400)
    
    if User.objects.filter(email=email).exists():
        return Response({'error': 'Bu email zaten kayıtlı'}, status=400)
    
    # Username oluştur (email'den)
    username = email.split('@')[0]
    base_username = username
    counter = 1
    while User.objects.filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1
    
    # Agency oluştur
    agency_slug = agency_name.lower().replace(' ', '-')
    base_slug = agency_slug
    counter = 1
    while Agency.objects.filter(slug=agency_slug).exists():
        agency_slug = f"{base_slug}-{counter}"
        counter += 1
    
    agency = Agency.objects.create(
        name=agency_name,
        slug=agency_slug,
        plan='free',
        is_active=True
    )
    
    # User oluştur
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        current_agency=agency
    )
    
    # Default owner rolü oluştur
    owner_role = AgencyRole.objects.create(
        agency=agency,
        name='Owner',
        can_manage_projects=True,
        can_manage_team=True,
        can_manage_equipment=True,
        can_view_finance=True
    )
    
    # Membership oluştur
    AgencyMembership.objects.create(
        user=user,
        agency=agency,
        role=owner_role,
        is_owner=True,
        is_active=True
    )
    
    # JWT token oluştur
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'message': 'Kayıt başarılı',
        'user': UserSerializer(user).data,
        'agency': {
            'id': agency.id,
            'name': agency.name,
            'slug': agency.slug,
            'plan': agency.plan
        },
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    🔐 GİRİŞ YAP
    
    Email + şifre ile login
    """
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response({'error': 'Email ve şifre gerekli'}, status=400)
    
    # Email ile kullanıcıyı bul
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'Geçersiz email veya şifre'}, status=401)
    
    # Şifre kontrolü
    if not user.check_password(password):
        return Response({'error': 'Geçersiz email veya şifre'}, status=401)
    
    # Aktif mi?
    if not user.is_active:
        return Response({'error': 'Hesap devre dışı'}, status=403)
    
    # JWT token oluştur
    refresh = RefreshToken.for_user(user)
    
    # Agency bilgisi
    agency_data = None
    if user.current_agency:
        membership = AgencyMembership.objects.filter(
            user=user,
            agency=user.current_agency
        ).first()
        
        agency_data = {
            'id': user.current_agency.id,
            'name': user.current_agency.name,
            'slug': user.current_agency.slug,
            'plan': user.current_agency.plan,
            'role': membership.role.name if membership and membership.role else 'Member',
            'is_owner': membership.is_owner if membership else False
        }
    
    return Response({
        'message': 'Giriş başarılı',
        'user': UserSerializer(user).data,
        'agency': agency_data,
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    """
    🚪 ÇIKIŞ YAP
    
    Token'ı blacklist'e ekle (optional)
    """
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        return Response({'message': 'Çıkış başarılı'})
    except Exception as e:
        return Response({'error': str(e)}, status=400)


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    """
    🔄 TOKEN YENİLE
    
    Refresh token ile yeni access token al
    """
    refresh = request.data.get('refresh')
    
    if not refresh:
        return Response({'error': 'Refresh token gerekli'}, status=400)
    
    try:
        refresh_token = RefreshToken(refresh)
        return Response({
            'access': str(refresh_token.access_token),
        })
    except Exception as e:
        return Response({'error': 'Geçersiz refresh token'}, status=401)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def switch_agency(request):
    """
    🔄 AGENCY DEĞİŞTİR
    
    Kullanıcı birden fazla agency'e üyeyse geçiş yapabilir
    """
    agency_id = request.data.get('agency_id')
    
    if not agency_id:
        return Response({'error': 'agency_id gerekli'}, status=400)
    
    # Kullanıcı bu agency'nin üyesi mi?
    try:
        membership = AgencyMembership.objects.get(
            user=request.user,
            agency_id=agency_id,
            is_active=True
        )
        
        # Current agency'i değiştir
        request.user.current_agency = membership.agency
        request.user.save()
        
        return Response({
            'message': 'Agency değiştirildi',
            'agency': {
                'id': membership.agency.id,
                'name': membership.agency.name,
                'slug': membership.agency.slug,
                'role': membership.role.name if membership.role else 'Member',
                'is_owner': membership.is_owner
            }
        })
    except AgencyMembership.DoesNotExist:
        return Response({'error': 'Bu agency\'ye erişim yetkiniz yok'}, status=403)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_agencies(request):
    """
    📋 BENİM AGENCY'LERİM
    
    Kullanıcının üye olduğu tüm agency'ler
    """
    memberships = AgencyMembership.objects.filter(
        user=request.user,
        is_active=True
    ).select_related('agency', 'role')
    
    agencies = []
    for membership in memberships:
        agencies.append({
            'id': membership.agency.id,
            'name': membership.agency.name,
            'slug': membership.agency.slug,
            'plan': membership.agency.plan,
            'role': membership.role.name if membership.role else 'Member',
            'is_owner': membership.is_owner,
            'is_current': membership.agency == request.user.current_agency,
            'joined_at': membership.joined_at
        })
    
    return Response({
        'count': len(agencies),
        'agencies': agencies
    })
