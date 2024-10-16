from dotenv import load_dotenv
import json
import os
import requests
import uuid

from insided_auth import AuthController

class InsidedAPI:

    def __init__(self):
        load_dotenv(".env", override=True)
        self.domain = os.getenv("INSIDED_URI")
        self.category_id = os.getenv("INSIDED_CATEGORY_ID")
        self.default_user = os.getenv("INSIDED_DEFAULT_USER")
        self.roles = [
            "roles.registered",
            "box_engineering",
            "boxers"
        ]

        self.user_mapping = {}

        self.auth = AuthController()

    def set_user_mapping(self, user_mapping):
        self.user_mapping = user_mapping

    def create_post(self, title, body, author_id, tags):
        
        url = f"{self.domain}/v2/questions/ask?authorId={author_id}"
        token = self.auth.get_token()
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        payload = {
            "title": title,
            "content": body,
            "categoryId": self.category_id,   
            "tags": tags
        }

        response = requests.post(url, data=json.dumps(payload), headers=headers)
        
        if response.ok:
            
            location = response.headers['Location']
            conversation_id = location.split('/')[3]

            return conversation_id
        else:
            print(f"CREATE POST: Error {response.status_code} response body: {response.text} payload: {payload} url: {url}")
            return "UNKNOWN"
        
    def reply_to_conversation(self, conversation_id, author_id, body):
        url = f"{self.domain}/v2/questions/{conversation_id}/reply?authorId={author_id}"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.auth.get_token()}"
        }

        payload = {
            "content": body
        }

        r = requests.post(url, data=json.dumps(payload), headers=headers)

        if r.ok:
            location = r.headers['Location']
            reply_id = location.split('/')[5]

            return reply_id

        else:
            print(f"Error replying to question {r.status_code} response body: {r.text} payload: {payload} url: {url}")
            return None
        
    def create_user(self,email_address):
        url = f"{self.domain}/user/register"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.auth.get_token()}"
        }

        payload = { "data" : {
                "email" : email_address,
                "username" : email_address,
                "password" : str(uuid.uuid4()),
                "user_role" : self.roles
            }
        }

        r = requests.post(url, data=json.dumps(payload), headers=headers)

        user_id = -1

        print(f"status code {r.status_code}")

        if r.ok:
            response = r.json()
            
            user_id = response["user"]["userid"]
        elif r.status_code == 400:
            response = r.json()

            if "email" in response["errors"]:
                if response["errors"]["email"][0] == "E-mail address already exists":
                    user_id = self.get_user_by_email(email_address)
            else:
                print(f"error is 400 {r.content}")
        else:
            print(f"Error {r.status_code} response body: {r.text}")
            return None
        
        print(f"Insided User {user_id} Email {email_address}")
        return user_id

    def create_tag(self, tag_name):
        url = f"{self.domain}/v2/tags/create?authorId={self.default_user}"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.auth.get_token()}"
        }

        payload = {
            "name" : tag_name
        }

        r = requests.post(url, data=json.dumps(payload), headers=headers)

        if r.ok:
            pass
        else:
            print(f"Error {r.status_code} response body: {r.text}")
            return None

    def mark_answer_correct(self, reply_id, author_id):
        url = f"{self.domain}/v2/questions/replies/{reply_id}/answer?authorId={self.default_user}"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.auth.get_token()}"
        }

        r = requests.post(url, headers=headers)

        if r.ok:
            pass
        else:
            print(f"Error marking answer correct {r.status_code} response body: {r.text} reply_id {reply_id} author_id {author_id}")
            return None
        
    def get_user_by_email(self, email_address):
        url = f"{self.domain}/user/email/{email_address}"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.auth.get_token()}"
        }

        r = requests.get(url, headers=headers)

        if r.ok:
            response = r.json()

            user_id = response["userid"]
            print(f"found user {user_id}")
            return user_id
        else:
            print(f"Error {r.status_code} response body: {r.text}")
            return None