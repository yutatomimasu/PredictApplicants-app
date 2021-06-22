import os
import csv

from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import UploadFileForm
from .models import predict_data

UPLOAD_DIR = os.path.dirname(os.path.abspath(__file__)) + '/uploads/'


# Create your views here.
def handle_upload_file(f):
    path = os.path.join(UPLOAD_DIR, f.name)
    with open(path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def upload(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_upload_file(request.FILES['file'])
            path = os.path.join(UPLOAD_DIR, request.FILES['file'].name)
            predict_data(path)
            return redirect('myapp:upload_complete')
    else:
        form = UploadFileForm()
    return render(request, 'myapp/upload.html', {'form': form})


def upload_complete(request):
    return render(request, 'myapp/upload_complete.html')


def csv_export(request):
    with open(UPLOAD_DIR + 'result.csv', 'rb') as f:
        data = f.read()
    response = HttpResponse(data, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="result.csv"'
    return response


def index_template(request):
    return render(request, 'index.html')
