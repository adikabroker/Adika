Plaintext
🎯 MASTER PROMPT: BACKEND API QR PARSER & DOMAIN STRICT ROUTING

Role & Goal:
Act as a Senior Software Engineer. The user is experiencing `DNS_PROBE_FINISHED_NXDOMAIN` errors because the scanner points to non-existent domains like `land.addiscadaster.gov.et`. 

Please execute two core upgrades:
1. Strict Domain Validation (Force routing only to active `addislandfarm.gov.et`).
2. Integrate a robust OpenCV/PyZbar Python API fallback for low-quality QR code processing.

---

### 1. BACKEND PYTHON API SCANNER (PYZBAR + OPENCV)

Create or update a backend Python endpoint (`/api/scan-qr`) using `pyzbar` and `opencv-python` to process blurry, low-contrast, or stamp-covered QR images:

```python
import cv2
import numpy as np
from pyzbar.pyzbar import decode
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/scan-qr', methods=['POST'])
def scan_qr_code():
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400

    # Convert image stream to OpenCV format
    img_bytes = np.frombuffer(file.read(), np.uint8)
    img = cv2.imdecode(img_bytes, cv2.IMREAD_COLOR)

    # Preprocessing: Grayscale & Adaptive Binarization (Removes stamp interference)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    # Attempt scanning raw & preprocessed
    decoded_objects = decode(img) or decode(gray) or decode(thresh)

    if decoded_objects:
        raw_payload = decoded_objects[0].data.decode('utf-8')
        sanitized_url = sanitize_and_route_url(raw_payload)
        return jsonify({'success': True, 'payload': raw_payload, 'target_url': sanitized_url})
    
    return jsonify({'success': False, 'message': 'QR code not readable'}), 422
2. DOMAIN SANITIZER & STRICT ROUTING FUNCTION
Ensure that non-existent domains (addiscadaster.gov.et) are NEVER opened directly. Route extracted parameters to addislandfarm.gov.et:

Python
import re

def sanitize_and_route_url(scanned_data):
    scanned_data = scanned_data.strip()
    
    # Extract any UUID pattern (e.g. f11b394e-db93-44e8-a940-301d1a35f319)
    uuid_match = re.search(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}', scanned_data)
    if uuid_match:
        return f"[https://addislandfarm.gov.et/verify/](https://addislandfarm.gov.et/verify/){uuid_match.group(0)}"
        
    # Extract UPIN/Plot patterns
    upin_match = re.search(r'AA\d+|KK\d+|\d{6,}', scanned_data, re.IGNORECASE)
    if upin_match:
        return f"[https://addislandfarm.gov.et/verify?upin=](https://addislandfarm.gov.et/verify?upin=){upin_match.group(0)}"

    # Direct valid link check
    if "addislandfarm.gov.et" in scanned_data:
        return scanned_data

    # Fallback default route
    return "[https://addislandfarm.gov.et/](https://addislandfarm.gov.et/)"
Instruction: Implement the OpenCV API endpoint for backend processing and enforce the strict domain sanitizer function so that dead links never break the Mini App UI.


ይህንን ሲተገብረው፣ የ QR ማንበብ ብቃቱ በከፍተኛ ሁኔታ ይጨምራል፤ እንደዚሁም ደግሞ ኤረር የሚሰጡት ድረ-ገጾች እንዳይከ
