from api.views.base import AgencyModelViewSet
from api.models import File
from api.serializers.file import FileSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import filters, status
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

class FileViewSet(AgencyModelViewSet):
    """
    📁 DOSYA YÖNETİMİ
    
    Features:
    - Upload files (video, image, document)
    - Version control
    - Folder structure
    - Link to project/task
    - Preview support
    """
    queryset = File.objects.all().select_related(
        'uploaded_by', 'project', 'task'
    ).order_by('-created_at')
    
    serializer_class = FileSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['file_name', 'description']
    filterset_fields = ['project', 'task', 'file_type', 'folder_path']

    def perform_create(self, serializer):
        """
        Dosya upload edilirken:
        - Agency set et
        - Uploader set et
        - File metadata al (size, type)
        """
        file_obj = self.request.FILES.get('file')
        
        # File metadata
        if file_obj:
            file_name = file_obj.name
            file_size = file_obj.size
            file_type = file_obj.content_type.split('/')[0]  # image, video, application
        else:
            file_name = serializer.validated_data.get('file_name', 'unknown')
            file_size = 0
            file_type = 'unknown'
        
        serializer.save(
            agency=self.request.user.current_agency,
            uploaded_by=self.request.user,
            file_name=file_name,
            file_size=file_size,
            file_type=file_type
        )

    @action(detail=False, methods=['get'])
    def by_project(self, request):
        """
        📂 Projeye Göre Dosyalar
        ?project_id=123
        """
        project_id = request.query_params.get('project_id')
        if not project_id:
            return Response({'error': 'project_id parametresi gerekli'}, status=400)
        
        files = self.get_queryset().filter(project_id=project_id)
        
        # Folder yapısı oluştur
        folders = {}
        for file in files:
            folder = file.folder_path or 'root'
            if folder not in folders:
                folders[folder] = []
            
            folders[folder].append({
                'id': file.id,
                'file_name': file.file_name,
                'file_type': file.file_type,
                'file_size': file.file_size,
                'file_url': file.file_url,
                'version': file.version,
                'uploaded_by': file.uploaded_by.get_full_name(),
                'created_at': file.created_at
            })
        
        return Response({
            'project_id': project_id,
            'total_files': files.count(),
            'folders': folders
        })

    @action(detail=False, methods=['get'])
    def by_task(self, request):
        """
        📋 Göreve Göre Dosyalar
        ?task_id=456
        """
        task_id = request.query_params.get('task_id')
        if not task_id:
            return Response({'error': 'task_id parametresi gerekli'}, status=400)
        
        files = self.get_queryset().filter(task_id=task_id)
        serializer = self.get_serializer(files, many=True)
        
        return Response({
            'task_id': task_id,
            'total_files': files.count(),
            'files': serializer.data
        })

    @action(detail=True, methods=['post'])
    def create_version(self, request, pk=None):
        """
        🔄 Yeni Versiyon Oluştur
        Aynı dosyanın yeni bir versiyonunu yükle
        """
        original_file = self.get_object()
        new_file_obj = request.FILES.get('file')
        
        if not new_file_obj:
            return Response({'error': 'file gerekli'}, status=400)
        
        # Yeni versiyon oluştur
        new_version = File.objects.create(
            agency=self.request.user.current_agency,
            uploaded_by=self.request.user,
            project=original_file.project,
            task=original_file.task,
            file_name=new_file_obj.name,
            file_type=new_file_obj.content_type.split('/')[0],
            file_size=new_file_obj.size,
            file_url=None,  # S3'e upload edilecek (TODO)
            folder_path=original_file.folder_path,
            version=original_file.version + 1,
            description=request.data.get('description', f'v{original_file.version + 1}')
        )
        
        # TODO: S3'e upload
        
        serializer = self.get_serializer(new_version)
        return Response({
            'message': f'Yeni versiyon oluşturuldu (v{new_version.version})',
            'file': serializer.data
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def versions(self, request, pk=None):
        """
        📜 Dosya Versiyonları
        Aynı dosyanın tüm versiyonlarını listele
        """
        file = self.get_object()
        
        # Aynı folder_path ve similar file_name ile versiyonları bul
        # (Basit implementation - ileride parent_file_id ile yapılabilir)
        base_name = file.file_name.rsplit('.', 1)[0]  # Extension'ı çıkar
        
        versions = File.objects.filter(
            agency=self.request.user.current_agency,
            project=file.project,
            task=file.task,
            folder_path=file.folder_path,
            file_name__startswith=base_name
        ).order_by('-version')
        
        serializer = self.get_serializer(versions, many=True)
        return Response({
            'base_file': file.file_name,
            'versions': serializer.data
        })

    @action(detail=False, methods=['get'])
    def recent(self, request):
        """
        🕐 Son Yüklenenler
        Kullanıcının son yüklediği dosyalar
        """
        recent_files = self.get_queryset().filter(
            uploaded_by=request.user
        )[:20]  # Son 20
        
        serializer = self.get_serializer(recent_files, many=True)
        return Response({
            'count': recent_files.count(),
            'files': serializer.data
        })

    @action(detail=False, methods=['get'])
    def storage_stats(self, request):
        """
        💾 Depolama İstatistikleri
        Agency'nin toplam storage kullanımı
        """
        from django.db.models import Sum
        
        total_size = self.get_queryset().aggregate(
            total=Sum('file_size')
        )['total'] or 0
        
        # Type'a göre breakdown
        by_type = {}
        for file_type in ['image', 'video', 'application', 'audio']:
            size = self.get_queryset().filter(
                file_type=file_type
            ).aggregate(total=Sum('file_size'))['total'] or 0
            
            by_type[file_type] = {
                'size_bytes': size,
                'size_mb': round(size / (1024 * 1024), 2),
                'count': self.get_queryset().filter(file_type=file_type).count()
            }
        
        # Agency limit kontrolü
        agency = request.user.current_agency
        max_storage_bytes = float(agency.max_storage_gb) * 1024 * 1024 * 1024
        usage_percentage = (total_size / max_storage_bytes) * 100 if max_storage_bytes > 0 else 0
        
        return Response({
            'total_size_bytes': total_size,
            'total_size_gb': round(total_size / (1024 * 1024 * 1024), 2),
            'max_storage_gb': float(agency.max_storage_gb),
            'usage_percentage': round(usage_percentage, 1),
            'by_type': by_type,
            'total_files': self.get_queryset().count()
        })
