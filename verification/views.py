from pprint import pprint
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from .forms import StaffLoginForm, ManualSearchForm
from .models import ScanLog
from course_registration.models import Registration
# from pyzbar.pyzbar import decode
from PIL import Image
import json
import uuid
import logging
def staff_login(request):
    if request.user.is_authenticated:
        return redirect('scanner')
    
    if request.method == 'POST':
        form = StaffLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('scanner')
    else:
        form = StaffLoginForm()
    
    return render(request, 'verification/login.html', {'form': form})

@login_required
def staff_logout(request):
    logout(request)
    return redirect('staff_login')

@login_required
def scanner(request):
    return render(request, 'verification/scanner.html')

@login_required
def manual_search(request):
    form = ManualSearchForm()
    if request.method == 'POST':
        form = ManualSearchForm(request.POST)
        if form.is_valid():
            try:
                registration = Registration.objects.get(
                    registration_id=form.cleaned_data['registration_id']
                )
                return redirect('verification_result', reg_id=registration.registration_id)
            except ObjectDoesNotExist:
                form.add_error('registration_id', 'Registration not found')
    
    return render(request, 'verification/manual_search.html', {'form': form})



# Set up logging
logger = logging.getLogger(__name__)

def validate_image_file(image_file):
    """Validate uploaded image file."""
    # Check file size (limit to 5MB)
    if image_file.size > 5 * 1024 * 1024:
        raise ValueError("File size too large. Maximum size is 5MB.")
    
    # Check file extension
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif'}
    file_extension = '.' + image_file.name.split('.')[-1].lower()
    if file_extension not in allowed_extensions:
        raise ValueError("Invalid file format. Supported formats: JPG, PNG, GIF")
    
    return True

# def read_qr_code(image_file):
#     """Read QR code from image file."""
#     try:
#         # Open image using PIL
#         image = Image.open(image_file)
        
#         # Convert to RGB if necessary
#         if image.mode != 'RGB':
#             image = image.convert('RGB')
        
#         # Decode QR code
#         decoded_objects = decode(image)
        
#         if not decoded_objects:
#             raise ValueError("No QR code found in image")
        
#         # Get the first QR code data
#         qr_data = decoded_objects[0].data.decode('utf-8')
#         return qr_data
        
#     except Exception as e:
#         logger.error(f"Error reading QR code: {str(e)}")
#         raise ValueError(f"Error reading QR code: {str(e)}")


import cv2
import numpy as np
from PIL import Image
import logging

logger = logging.getLogger(__name__)

def read_qr_code(image_file):
    """Read QR code from image file."""
    try:
        # Open image using PIL
        pil_image = Image.open(image_file)
        
        # Convert to RGB if necessary
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # Convert PIL image to OpenCV format
        opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
        
        # Initialize QR code detector
        qr_detector = cv2.QRCodeDetector()
        
        # Detect and decode QR code
        qr_data, bbox, _ = qr_detector.detectAndDecode(opencv_image)
        
        if not qr_data:
            raise ValueError("No QR code found in image")
        
        return qr_data
        
    except Exception as e:
        logger.error(f"Error reading QR code: {str(e)}")
        raise ValueError(f"Error reading QR code: {str(e)}")

def verify_qr(request):
    """Handle QR code verification from both camera and file upload."""
    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'Method not allowed'
        }, status=405)
    
    try:
        registration_id = None
        
        # Handle file upload
        if request.FILES and 'qr_image' in request.FILES:
            file = request.FILES['qr_image']
            try:
                # Validate file
                validate_image_file(file)
                
                # Read QR code
                qr_data = read_qr_code(file)
                print("---------------------qr_data----------------------")
                pprint(qr_data)
                
                try:
                    # First try parsing as JSON
                    data = json.loads(qr_data)
                    registration_id = data.get('registration_id')
                except json.JSONDecodeError:
                    # If not JSON, handle the tuple/string format
                    if isinstance(qr_data, tuple):
                        qr_data = ''.join(qr_data)
                    
                    # Look for registration ID in the text
                    for line in qr_data.split('\n'):
                        if 'Registration ID:' in line:
                            registration_id = line.replace('Registration ID:', '').strip()
                            break
                    
            except ValueError as e:
                return JsonResponse({
                    'status': 'error',
                    'message': str(e)
                }, status=400)
        
        if not registration_id:
            return JsonResponse({
                'status': 'error',
                'message': 'No registration ID provided'
            }, status=400)

        try:
            # Clean and validate registration ID format
            clean_registration_id = str(uuid.UUID(registration_id))
            
            # Get registration
            registration = Registration.objects.get(registration_id=clean_registration_id)
            print("---------------------registration-retrieved----------------------")
            print(registration)
            
            # Log successful scan
            ScanLog.objects.create(
                scanned_by=request.user,
                registration=registration,
                scan_status='valid'
            )
            
            # Safely construct response data
            try:
                response_data = {
                    'status': 'success',
                    'data': {
                        'full_name': str(registration.full_name),
                        'course': "UI/UX Design",
                        'preferred_schedule': str(registration.get_preferred_schedule_display()),
                        'registration_id': str(registration.registration_id)
                    }
                }
                return JsonResponse(response_data)
            except AttributeError as e:
                logger.error(f"Error formatting registration data: {str(e)}")
                return JsonResponse({
                    'status': 'error',
                    'message': 'Error formatting registration data'
                }, status=500)
                
        except ValueError:
            logger.warning(f"Invalid UUID format: {registration_id}")
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid registration ID format'
            }, status=400)
            
        except ObjectDoesNotExist:
            logger.warning(f"Registration not found: {registration_id}")
            ScanLog.objects.create(
                scanned_by=request.user,
                registration=None,
                scan_status='invalid',
                notes=f'Attempted registration ID: {registration_id}'
            )
            return JsonResponse({
                'status': 'error',
                'message': 'Registration not found'
            }, status=404)
            
    except Exception as e:
        logger.error(f"Unexpected error in verify_qr: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'An unexpected error occurred'
        }, status=500)

@login_required
def verification_result(request, reg_id):
    try:
        registration = Registration.objects.get(registration_id=reg_id)
        return render(request, 'verification/result.html', {'registration': registration})
    except ObjectDoesNotExist:
        return render(request, 'verification/result.html', {'error': 'Registration not found'})

@login_required
def dashboard(request):
    recent_scans = ScanLog.objects.select_related('registration', 'scanned_by').order_by('-scan_timestamp')[:50]
    return render(request, 'verification/dashboard.html', {'recent_scans': recent_scans})