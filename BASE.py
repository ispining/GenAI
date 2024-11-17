import json
import requests, texts
import requests
import mimetypes
import os


# Replace with your actual image path and API key
IMG_PATH_2 = 'path_to_your_image.jpg'
GOOGLE_API_KEY = 'YOUR_GOOGLE_API_KEY'
BASE_URL = 'https://generativelanguage.googleapis.com'


os.chdir("/home/promiteus/Desktop/GenAI/")


class GenAI:
    def __init__(self, system_instruction: str):
        self.system_instruction = system_instruction
        self.history = []
    
    def get_params(self):
        api_key = "AIzaSyCSIYOP-4VqmsUzOR0Hoel_D2Nf14yC0Eg"

        return {
            'key': api_key,
        }

    def add_to_history(self, role: str, prompt: str):
        self.history.append({
            'role': role,
            'parts': [{'text': prompt}],
        })

    def add_media_to_history(self, role: str, mime_type: str, file_uri: str, caption: str = None):
        self.history.append({
            'role': role,
            'parts': [{'text': caption},
                      {"file_data": {"mime_type": mime_type,"file_uri": file_uri}}],
        })

    def add_document_to_history(self, role: str, mime_type: str, file_uri: str, caption: str = None):
        self.history.append({
            'role': role,
            'parts': [{'text': caption},
                      {"file_data": {"mime_type": mime_type, "file_uri": file_uri}}],
        })

    def generate_content(self, user_prompt: str):

        self.add_to_history('user', user_prompt)

        json_data = {
            'safetySettings': [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_CIVIC_INTEGRITY", "threshold": "BLOCK_NONE"}
            ],
            'contents': self.history
            }
    
        if self.system_instruction:
            json_data['system_instruction'] = {
                'parts': [{
                    'text': self.system_instruction,
                }],
            }

        response = requests.post(
            'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent',
            params=self.get_params(),
            headers={'Content-Type': 'application/json'},
            json=json_data)
        
        r = response.json()
        
        try:    
            r = r['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            print(r)

        self.add_to_history('model', r)
        
        return r

    def generate_content_from_image(self, image_path: str, user_prompt: str):
        IMG_PATH_2 = image_path
        DISPLAY_NAME = 'UPLOADED FILE'

        # Get MIME type of the image
        mime_type, _ = mimetypes.guess_type(IMG_PATH_2)
        if mime_type is None:
            mime_type = 'application/octet-stream'

        # Get the size of the image in bytes
        num_bytes = os.path.getsize(IMG_PATH_2)

        # Initial resumable request defining metadata
        url = f"https://generativelanguage.googleapis.com/upload/v1beta/files"
        headers = {
            "X-Goog-Upload-Protocol": "resumable",
            "X-Goog-Upload-Command": "start",
            "X-Goog-Upload-Header-Content-Length": str(num_bytes),
            "X-Goog-Upload-Header-Content-Type": mime_type,
            "Content-Type": "application/json"
        }
        payload = {
            "file": {
                "display_name": DISPLAY_NAME
            }
        }

        response = requests.post(url, headers=headers, json=payload, params=self.get_params())

        # Get the upload URL from response headers
        upload_url = response.headers.get('X-Goog-Upload-URL')
        if not upload_url:
            pass
        headers = {
            "Content-Length": str(num_bytes),
            "X-Goog-Upload-Offset": "0",
            "X-Goog-Upload-Command": "upload, finalize"
        }

        with open(IMG_PATH_2, 'rb') as f:
            data = f.read()

        response = requests.post(upload_url, headers=headers, data=data)
        file_info = response.json()

        file_uri = file_info.get('file', {}).get('uri')

        self.add_media_to_history('user', mime_type, file_uri, user_prompt)

        json_data = {
            'safetySettings': [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_CIVIC_INTEGRITY", "threshold": "BLOCK_NONE"}
            ],
            'contents': self.history
        }

        if self.system_instruction:
            json_data['system_instruction'] = {
                'parts': [{
                    'text': self.system_instruction,
                }],
            }

        response = requests.post(
            'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent',
            params=self.get_params(),
            headers={'Content-Type': 'application/json'},
            json=json_data)

        r = response.json()

        try:
            r = r['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            print(r)

        self.add_to_history('model', r)

        return r



# ai = GenAI(system_instruction=texts.dgpt)

# print('[MODEL] '+ai.generate_content(input('[USER] ')))
