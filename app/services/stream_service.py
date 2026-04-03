# app/services/stream_service.py

import requests
from typing import Optional, Dict, Any


class StreamService:
    """Service for handling stream-related operations"""

    @staticmethod
    def fetch_cookies(cookie_url: str) -> Optional[Dict[str, Any]]:
        """Fetch cookies from external URL"""
        try:
            response = requests.get(cookie_url, timeout=10)
            return response.json()
        except:
            return None

    @staticmethod
    def build_clearkey_license_url(key_id: str, key: str) -> str:
        """Build ClearKey license data URL"""
        import base64
        import json

        # Convert hex to base64url
        def hex_to_base64url(hex_string: str) -> str:
            bytes_data = bytes.fromhex(hex_string)
            b64 = base64.b64encode(bytes_data).decode('utf-8')
            return b64.replace('+', '-').replace('/', '_').rstrip('=')

        license_data = {
            "keys": [{
                "kty": "oct",
                "kid": hex_to_base64url(key_id),
                "k": hex_to_base64url(key)
            }],
            "type": "temporary"
        }

        json_str = json.dumps(license_data)
        b64_license = base64.b64encode(json_str.encode()).decode()
        
        return f"data:application/json;base64,{b64_license}"

    @staticmethod
    def get_stream_headers() -> Dict[str, str]:
        """Get common headers for stream requests"""
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://www.jio.com/",
            "Origin": "https://www.jio.com"
        }