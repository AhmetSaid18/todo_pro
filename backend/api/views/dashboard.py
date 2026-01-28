from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q
from django.utils import timezone
from api.models import Project, Task, ShootingDay
from api.serializers.project import ProjectSerializer
from api.serializers.task import TaskSerializer

class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        agency = request.user.current_agency
        if not agency:
            return Response({"error": "No active agency found for user"}, status=400)

        # 1. Project Stats
        active_projects = Project.objects.filter(
            agency=agency,
            status__in=['standard_planning', 'active_production', 'post_production', 'review_client']
        )
        
        # 2. Task Stats
        tasks = Task.objects.filter(agency=agency)
        pending_tasks = tasks.exclude(status='done')
        completed_tasks_count = tasks.filter(status='done').count()
        urgent_tasks_count = pending_tasks.filter(priority='critical').count()

        # 3. Financial Stats (Simplified for now: sum of project budgets)
        # Note: In a real system you'd use a real Finance/Transaction model
        current_month = timezone.now().month
        current_year = timezone.now().year
        
        monthly_revenue = Project.objects.filter(
            agency=agency,
            created_at__month=current_month,
            created_at__year=current_year
        ).aggregate(total=Sum('budget_estimated'))['total'] or 0

        # 4. Recent Projects (for the list)
        recent_projects = active_projects.order_by('-updated_at')[:5]
        recent_projects_serializer = ProjectSerializer(recent_projects, many=True)

        # 5. Today's Schedule (ShootingDays or Tasks due today)
        today = timezone.now().date()
        today_shooting = ShootingDay.objects.filter(
            agency=agency,
            date=today
        ).select_related('project', 'main_location')
        
        schedule = []
        for shoot in today_shooting:
            schedule.append({
                'type': 'shooting',
                'time': shoot.call_time.strftime('%H:%M'),
                'title': f"{shoot.project.title} - Set/Çekim",
                'location': shoot.main_location.name if shoot.main_location else "Belirtilmedi",
                'color': 'blue'
            })

        # Also add tasks due today
        today_tasks = tasks.filter(due_date__date=today)
        for task in today_tasks:
            schedule.append({
                'type': 'task',
                'time': task.due_date.strftime('%H:%M') if task.due_date else '--:--',
                'title': task.title,
                'location': task.project.title,
                'color': 'purple'
            })
            
        # Sort schedule by time
        schedule.sort(key=lambda x: x['time'])

        return Response({
            'stats': {
                'active_projects': {
                    'value': active_projects.count(),
                    'trend': '+2 bu hafta' # Static trend for now or calculate
                },
                'pending_tasks': {
                    'value': pending_tasks.count(),
                    'trend': f'{urgent_tasks_count} acil'
                },
                'completed_tasks': {
                    'value': completed_tasks_count,
                    'trend': '%12 artış'
                },
                'monthly_revenue': {
                    'value': f'₺{int(monthly_revenue/1000)}K' if monthly_revenue >= 1000 else f'₺{monthly_revenue}',
                    'trend': '+%8.2'
                }
            },
            'recent_projects': recent_projects_serializer.data,
            'schedule': schedule
        })
