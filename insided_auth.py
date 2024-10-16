
from cachetools import TTLCache
import os
import requests

from dotenv import load_dotenv

class AuthController():
    target_url = ''
    def __init__(self):
        load_dotenv(".env", override=True)
        self.domain = os.getenv("INSIDED_URI")
        self.client_id = os.getenv("INSIDED_CLIENT_ID")
        self.client_secret = os.getenv("INSIDED_CLIENT_SECRET")

        print(f"client_id {self.client_id} client_secret {self.client_secret}")
        
        self.cache = None

    def getKey(self):
        return self.key

    def getSecret(self):
        return self.secret
    
    def insided_auth(self):
   
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
    
        body = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "write read"
        }

        response = requests.post(f"{self.domain}/oauth2/token", data=body, headers=headers)

        if response.ok:
            auth_json = response.json()
            return auth_json['access_token'], auth_json['expires_in']
        else:
            print(f"GDH_AUTH: error getting token {response.text}")
            return None,None


    def set_token(self):
        
        if self.cache is not None:
            try:
                token = self.cache['token']

                return
            
            except KeyError:

                pass

        token, expires_in = self.insided_auth()

        self.cache = TTLCache(maxsize=1, ttl=expires_in)
        self.cache['token'] = token
        
    def get_token(self):
        
        try:
            token = self.cache['token']
            return token
        except KeyError:
            print(f"GET TOKEN KeyError {KeyError.with_traceback()}")
            self.set_token()

            return self.cache['token']
        except TypeError:
            print(f"GET TOKEN TypeError")
            self.set_token()

            return self.cache['token']
        except Exception:
            print(f"GET TOKEN Exception {Exception.with_traceback()}")