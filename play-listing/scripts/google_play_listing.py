#!/usr/bin/env python3
import argparse, json, os
from pathlib import Path

PACKAGE_NAME = "com.oneapps.habibirun"
LOCALES_DIR = Path(__file__).resolve().parents[1] / "locales"

def load_listings():
    listings = {}
    for path in sorted(LOCALES_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        locale = path.stem
        required = ("title", "shortDescription", "fullDescription")
        missing = [key for key in required if not data.get(key)]
        if missing:
            raise SystemExit(f"{path}: missing {', '.join(missing)}")
        limits = {"title": 30, "shortDescription": 80, "fullDescription": 4000}
        for key, limit in limits.items():
            length = len(data[key])
            if length > limit:
                raise SystemExit(f"{path}: {key} is {length}/{limit} characters")
        listings[locale] = data
    if not listings:
        raise SystemExit("No locale files found")
    return listings

def service():
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    raw = os.environ.get("PLAY_SERVICE_ACCOUNT_JSON")
    if not raw:
        raise SystemExit("PLAY_SERVICE_ACCOUNT_JSON is not available")
    info = json.loads(raw)
    credentials = service_account.Credentials.from_service_account_info(
        info, scopes=["https://www.googleapis.com/auth/androidpublisher"]
    )
    return build("androidpublisher", "v3", credentials=credentials, cache_discovery=False)

def api_check(api):
    edit = api.edits().insert(packageName=PACKAGE_NAME, body={}).execute()
    edit_id = edit["id"]
    try:
        result = api.edits().listings().list(
            packageName=PACKAGE_NAME, editId=edit_id
        ).execute()
        languages = [item.get("language") for item in result.get("listings", [])]
        print(f"API access verified for {PACKAGE_NAME}. Existing locales: {languages}")
    finally:
        api.edits().delete(packageName=PACKAGE_NAME, editId=edit_id).execute()

def publish(api, listings):
    edit = api.edits().insert(packageName=PACKAGE_NAME, body={}).execute()
    edit_id = edit["id"]
    for locale, body in listings.items():
        api.edits().listings().update(
            packageName=PACKAGE_NAME, editId=edit_id, language=locale, body=body
        ).execute()
        print(f"Prepared {locale}")
    api.edits().commit(packageName=PACKAGE_NAME, editId=edit_id).execute()
    print(f"Committed {len(listings)} localized listings to Google Play")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("validate", "api-check", "publish"))
    args = parser.parse_args()
    listings = load_listings()
    print(f"Validated {len(listings)} locale files")
    if args.action == "validate":
        return
    api = service()
    if args.action == "api-check":
        api_check(api)
    else:
        publish(api, listings)

if __name__ == "__main__":
    main()
