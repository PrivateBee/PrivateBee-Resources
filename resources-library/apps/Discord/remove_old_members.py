import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from github import Github, Auth

from github_error_codes import GithubInviteCode

def remove_old_members():
    load_dotenv()

    TOKEN = os.getenv('GITHUB_TOKEN')
    ORG_NAME = os.getenv('ORG_NAME')

    if not TOKEN:
        print("Erreur: GITHUB_TOKEN manquant dans le .env")
        return GithubInviteCode.CONFIG_MISSING_TOKEN

    if not ORG_NAME:
        print("Erreur: ORG_NAME manquant dans le .env")
        return GithubInviteCode.CONFIG_MISSING_ORG

    auth = Auth.Token(TOKEN)
    g = Github(auth=auth)
    org = g.get_organization(ORG_NAME)

    LIMIT = timedelta(days=365*3)
    now = datetime.now()

    for member in org.get_members():
        print(f"Vérification de {member.login}...")
        print(f"Date de d'ajout à l'organisation: {member.created_at}")
        print(f"Date actuelle: {now}")
        # print(f"Durée depuis l'ajout: {now - member.created_at}")
        # membership = org.get_membership(member)
        # join_date = membership.created_at

        # if now - join_date > LIMIT:
        #     print(f"Suppression de {member.login} (rejoint le {join_date})")
        #     org.remove_from_members(member)

if __name__ == "__main__":
    remove_old_members()