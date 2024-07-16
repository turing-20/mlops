from celery import shared_task
from .models import Deployment


@shared_task
def schedule_deployments():
    deployments = Deployment.objects.filter(status='queued').order_by('-priority')
    for deployment in deployments:
        cluster = deployment.cluster
        if (cluster.available_ram >= deployment.required_ram and
                cluster.available_cpu >= deployment.required_cpu and
                cluster.available_gpu >= deployment.required_gpu):

            cluster.available_ram -= deployment.required_ram
            cluster.available_cpu -= deployment.required_cpu
            cluster.available_gpu -= deployment.required_gpu
            cluster.save()

            deployment.status = 'running'
            deployment.save()
        else:
            # Queue deployment if resources are unavailable
            deployment.status = 'queued'
            deployment.save()



