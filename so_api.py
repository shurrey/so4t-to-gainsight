from typing import List
from dotenv import load_dotenv
import os
import requests

from insided_api import InsidedAPI

class StackOverflowAPI:

    def __init__(self):

        load_dotenv(".env", override=True)

        self.pat = os.getenv("SO4T_PAT")
        self.uri = os.getenv("SO4T_URI")
        self.default_user = os.getenv("INSIDED_DEFAULT_USER")
        self.default_email = os.getenv("INSIDED_DEFAULT_EMAIL")

        self.user_mapping = {}

        self.insided = InsidedAPI()

        self.headers = {
            "accept" : "application/json",
            "Authorization" : f"Bearer {self.pat}"
        }

    def migrate_all_users(self):

        page = 1
        total_pages = 1

        while page <= total_pages:

            r = requests.get(f"{self.uri}/users?pagesize=100&page={page}", headers=self.headers)

            response = r.json()

            total_pages = response["totalPages"]

            if total_pages == 1:
                total_pages = 0
            
            for user in response["items"]:

                so_id = user["id"]
                email_address = user["email"]

                if so_id == -1:
                    self.user_mapping[so_id] = self.default_user
                else:
                    insided_id = self.insided.create_user(email_address)

                    self.user_mapping[so_id] = insided_id

            page += 1

        return self.user_mapping



    def migrate_all_tags(self):
        page = 1
        total_pages = 1

        while page <= total_pages:

            r = requests.get(f"{self.uri}/tags?pagesize=100&page={page}", headers=self.headers)

            response = r.json()

            total_pages = response["totalPages"]

            if total_pages == 1:
                total_pages = 0
            
            for tag in response["items"]:

                tag_name = tag["name"]
                
                self.insided.create_tag(tag_name)

            page += 1

    def migrate_all_questions(self):
        total_pages = 1
        page=1

        while page <= total_pages:

            r = requests.get(f"{self.uri}/questions?order=asc&sort=creation&pagesize=100&page={page}", headers=self.headers)

            response=r.json()

            items = response["items"]

            total_pages = response["totalPages"]

            if total_pages == 1:
                total_pages = 0

            for item in items:
                question_id = item["id"]

                tags=[]
                for tag in item["tags"]:
                    tags.append(tag["name"])
                
                if item["owner"] is not None:
                    author_id=item["owner"]["id"]
                else:
                    author_id=-1

                title=item["title"]
                body=item["body"]

                insided_id = int(self.default_user)

                try:
                    insided_id = self.user_mapping[author_id]
                except KeyError as ke:
                    pass

                post_id = self.insided.create_post(title, body, insided_id, tags)

                self.get_question_comments(question_id, post_id)

                self.get_answers(question_id, post_id)
            

            page += 1

    def get_question_comments(self, question_id, post_id):
        r = requests.get(f"{self.uri}/questions/{question_id}/comments", headers=self.headers)

        response=r.json()

        for item in response:
            author_id = item["ownerUserId"]
            body = item["body"]

            insided_id = "646"

            try:
                insided_id = self.user_mapping[author_id]
            except KeyError as ke:
                pass

            reply_id = self.insided.reply_to_conversation(post_id, insided_id, body)

    def get_answers(self, question_id, post_id):
        total_pages = 1
        page=1

        while page <= total_pages: 
        
            r = requests.get(f"{self.uri}/questions/{question_id}/answers?order=asc&sort=creation&pagesize=100&page={page}", headers=self.headers)

            response=r.json()

            total_pages = response["totalPages"]

            if total_pages == 1:
                total_pages = 0

            for item in response["items"]:

                answer_id = item["id"]

                if item["owner"] is not None:
                    author_id = item["owner"]["id"]
                else:
                    author_id = -1

                body = item["body"]

                is_accepted = item["isAccepted"]

                comment_count = item["commentCount"]

                insided_id = "646"

                try:
                    insided_id = self.user_mapping[author_id]
                except KeyError as ke:
                    pass

                reply_id = self.insided.reply_to_conversation(post_id, insided_id, body)

                if is_accepted:
                    self.insided.mark_answer_correct(reply_id, insided_id)

                if comment_count > 0:
                    self.get_answer_comments(question_id, answer_id, post_id)
    
    def get_answer_comments(self, question_id, answer_id, post_id):
        r = requests.get(f"{self.uri}/questions/{question_id}/answers/{answer_id}/comments", headers=self.headers)

        response=r.json()

        for item in response:
            author_id = item["ownerUserId"]
            body = item["body"]

            insided_id = "646"

            try:
                insided_id = self.user_mapping[author_id]
            except KeyError as ke:
                pass

            reply_id = self.insided.reply_to_conversation(post_id, insided_id, body)