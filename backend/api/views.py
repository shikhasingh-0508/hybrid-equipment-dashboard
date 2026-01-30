import io
from django.http import FileResponse
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from reportlab.pdfgen import canvas
from .models import Dataset
from .utils import analyze_csv

# --- NEW: Login Logic for Web & Desktop ---
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })
    return Response({'error': 'Invalid Credentials'}, status=401)

# --- Existing: Data & PDF Logic ---
@api_view(['POST'])
def upload_csv(request):
    file = request.FILES['file']
    dataset = Dataset.objects.create(file=file)
    summary = analyze_csv(dataset.file.path)
    dataset.summary = summary
    dataset.save()
    return Response({"id": dataset.id, "summary": summary})

@api_view(['GET'])
def history(request):
    data = Dataset.objects.all().order_by('-uploaded_at').values()
    return Response(list(data))

@api_view(['GET'])
def download_pdf(request, pk):
    dataset = Dataset.objects.get(pk=pk)
    summary = dataset.summary
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 800, "Industrial Safety Analysis Report")
    
    y = 750
    p.setFont("Helvetica", 12)
    max_p = summary.get('max_pressure', 0)
    
    p.drawString(100, y, f"Average Pressure: {summary.get('avg_pressure')} bar")
    if max_p > 7.0:
        p.setFillColorRGB(0.8, 0, 0) # Red text in PDF
        p.drawString(300, y, f" [CRITICAL PEAK: {max_p}]")
        p.setFillColorRGB(0, 0, 0)
    
    p.showPage()
    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename=f'Safety_Report_{pk}.pdf')