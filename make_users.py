import os
import csv
import time
from pathlib import Path

from dotenv import load_dotenv
import pymongo

def import_users(file: str) -> list[str]:
    emails = []

    if Path(f"{ file }").is_file():
        with open(file) as input:
            rows = csv.DictReader(input)
            for row in rows:
                emails.append(row["email"])
    else:
        exit("Error: Input file doesn't exist")

    return emails

class User:
    username: str
    password: str

    def __init__(self, email: str) -> None:
        username = self.generate_username(email)

        self.username = username
        self.password = self.generate_password(username)
        
    @staticmethod
    def generate_username(email: str) -> str:
        # ab2-username@domain.ac.uk -> ab2username
        return email.split("@")[0].lower().replace("-", "").replace(".", "")

    @staticmethod
    def generate_password(username: str) -> str:
        # ab2username -> Ab2usernamE11+$++
        return f"{ username[0].upper() }{ username[1:-1].lower() }{ username[-1].upper() }{ len(username) }+$++"

if __name__ == "__main__":
    load_dotenv()
    from argparse import ArgumentParser

    parser = ArgumentParser(description="bulk create MongoDB databases and users")
    parser.add_argument("file", type=str, help="csv file to load users from")
    parser.add_argument(
        "--output",
        "-o",
        action="store_true",
        help="save csv output for successful and unsuccessful user creations",
    )
    parser.add_argument(
        "--debug",
        "-v",
        action="store_true",
        help="print debug messages to the terminal",
    )
    args = parser.parse_args()

    def debug(message: str):
        if args.debug:
            print(message)


    emails = import_users(args.file)
    users = []

    if(len(emails) < 1):
        exit("Error: Input file is empty")

    for email in emails:
        users.append(User(email))

    try:
        client = pymongo.MongoClient(username=os.getenv("MONGO_USER"), password=os.getenv("MONGO_PASSWORD"))
    
    except pymongo.errors.ConnectionFailure as e:
        exit(f"Error: Couldn't establish MongoDB connection - { e.message }")

    except Exception as e:
        exit(f"Error: MongoDB exception - { e.message }")

    successful = []
    unsuccessful = []

    for user in users:
        try:
            result = client.admin.command(
                "createUser",
                user.username,
                pwd=user.password,
                roles = [
                    "changeOwnPassword",
                    { "role": "readWrite", "db": user.username }
                ],
            )

            successful.append(user)

        except Exception as e:
            unsuccessful.append((user.username, e))

    debug(f"Run finished: { len(successful) } users added.")

    if len(unsuccessful) > 0 and args.debug:
        debug(
            f"\nThere was a problem adding { len(unsuccessful) } user(s):"
        )

        for username, error in unsuccessful:
            debug(f"{ username } - { error }")

    if args.output:
        t = int(time.time())

        if not os.path.exists("output"):
            os.makedirs("output")

        with open(f"output/{ t }_successful.csv", "w") as output:
            writer = csv.writer(output)
            writer.writerow(["username", "password"])
            for user in successful:
                writer.writerow([user.username, user.password])

        with open(f"output/{ t }_unsuccessful.csv", "w") as output:
            writer = csv.writer(output)
            writer.writerow(["username", "error"])
            for username, error in unsuccessful:
                writer.writerow([username, error])

