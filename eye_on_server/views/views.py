from django.utils import timezone
from eye_on_server.models import SeverInfo

from .data_process import *
from .send_dingtalk import send_alert_to_dingtalk

from .chart import Chart


# Create your views here.
def cpu_percent_line(request, data):
    chart = Chart()
    cpu_data_line = chart.line_chart('cpu_avg', 'cpu平均使用率', timezone.now(), SeverInfo.cpu_percent)
    print('cpu_data_line', cpu_data_line)
    return render(request, 'monitor/cpu_m.html', locals())


def disk_percent_line(request, data):
    chart = Chart()
    disk_data_line = chart.line_chart('disk_avg', 'cpu平均使用率', timezone.now(), SeverInfo.disk_percent)

    return render(request, 'monitor/disk_m.html', locals())


def memory_percent_line(request, data):
    chart = Chart()
    memory_data_line = chart.line_chart('memory_avg', 'cpu平均使用率', timezone.now(), SeverInfo.memory_percent)

    return render(request, 'monitor/memory_m.html', locals())

def server(request):
    return render(request,'ServerList.html')
def home(request):
    infos = SeverInfo.objects.all().order_by('time')
    context = {'infos': infos}
    return render(request, "base.html", context=context)
