"""Test file upload flow in Sky Survey API"""
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import json

API_BASE = "http://localhost:8000/api"

def check_server():
    try:
        urllib.request.urlopen("http://localhost:8000/health", timeout=3)
        print("Server is running! OK\n")
        return True
    except Exception as e:
        print("Server not running:", e)
        return False

def create_survey():
    req = urllib.request.Request(API_BASE + "/surveys?name=File+Test&description=File+upload+test", method="POST")
    resp = urllib.request.urlopen(req)
    r = ET.fromstring(resp.read().decode())
    sid = r.get("id")
    print(f"1. Created survey #{sid}")
    return sid

def add_question(survey_id, name, qtype, text, required="yes"):
    data = urllib.parse.urlencode({
        "name": name, "type": qtype, "text": text, "required": required
    }).encode()
    req = urllib.request.Request(
        API_BASE + f"/surveys/{survey_id}/questions",
        data=data, method="POST"
    )
    resp = urllib.request.urlopen(req)
    resp.read()
    print(f"2. Added question: {name} ({qtype})")

def submit_with_file(survey_id):
    """Submit multipart form with a file upload"""
    boundary = "----FormBoundary7MA4YWxkTrZu0gW"
    
    lines = []
    # Email
    lines.append("--" + boundary)
    lines.append('Content-Disposition: form-data; name="email_address"')
    lines.append("")
    lines.append("user@test.com")
    # Full name
    lines.append("--" + boundary)
    lines.append('Content-Disposition: form-data; name="full_name"')
    lines.append("")
    lines.append("John Doe")
    # File
    lines.append("--" + boundary)
    lines.append('Content-Disposition: form-data; name="my_resume"; filename="my_resume.pdf"')
    lines.append("Content-Type: application/pdf")
    lines.append("")
    lines.append("%PDF-1.4 fake content for testing")
    lines.append("--" + boundary + "--")
    
    body = "\r\n".join(lines).encode()
    
    req = urllib.request.Request(
        API_BASE + f"/surveys/{survey_id}/responses",
        data=body, method="POST"
    )
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    
    try:
        resp = urllib.request.urlopen(req)
        result = resp.read().decode()
        print("3. Response submitted! Status:", resp.status)
        
        root = ET.fromstring(result)
        rid_el = root.find("response_id")
        rid = rid_el.text if rid_el is not None else "?"
        print(f"   Response ID: {rid}")
        return rid
    except urllib.error.HTTPError as e:
        print("3. ERROR:", e.code, e.read().decode()[:300])
        return None

def get_responses(survey_id):
    req = urllib.request.Request(
        API_BASE + f"/surveys/{survey_id}/responses?page=1&pageSize=10"
    )
    resp = urllib.request.urlopen(req)
    body = resp.read().decode()
    print(f"4. Response XML (status {resp.status}):")
    print(body)
    print()
    
    # Check for certificates
    if "certificate" in body.lower():
        print("YES - Certificates are present in the response!")
        # Parse to extract details
        root = ET.fromstring(body)
        for child in root:
            certs = child.find("certificates")
            if certs is not None:
                for c in certs:
                    cid = c.get("id")
                    fname = c.get("filename") or c.text or ""
                    print(f"  Certificate #{cid}: {fname}")
    else:
        print("NO - No certificates found in the response")
        print("Available fields:", [c.tag for c in ET.fromstring(body)])

def test_certificate_download(cert_id):
    try:
        req = urllib.request.Request(
            API_BASE + f"/certificates/{cert_id}"
        )
        resp = urllib.request.urlopen(req)
        content = resp.read()
        print(f"5. Download certificate #{cert_id}:")
        print(f"   Status: {resp.status}")
        print(f"   Content-Type: {resp.headers.get('Content-Type')}")
        print(f"   File size: {len(content)} bytes")
        print("   Download works!")
    except urllib.error.HTTPError as e:
        print(f"5. Download error: {e.code} - {e.read().decode()[:100]}")


if __name__ == "__main__":
    if not check_server():
        exit(1)
    
    sid = create_survey()
    add_question(sid, "my_resume", "file", "Upload your resume")
    add_question(sid, "full_name", "short_text", "Your name")
    print()
    
    rid = submit_with_file(sid)
    print()
    
    if rid:
        get_responses(sid)
        print()
        test_certificate_download(rid)
