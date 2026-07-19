#!/usr/bin/env python3
import argparse, json, os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APPS = {
    "habibirun": {
        "package": "com.oneapps.habibirun",
        "locales": ROOT / "locales",
    },
    "voidstack": {
        "package": "com.oneapps.voidstack",
        "locales": ROOT / "apps" / "voidstack" / "locales",
    },
    "voiddash": {
        "package": "com.oneapps.voiddash002",
        "locales": ROOT / "apps" / "voiddash" / "locales",
    },
}

def load_listings(locales_dir):
    listings = {}
    for path in sorted(locales_dir.glob("*.json")):
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
        raise SystemExit(f"No locale files found in {locales_dir}")
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

def api_check(api, package_name):
    edit = api.edits().insert(packageName=package_name, body={}).execute()
    edit_id = edit["id"]
    try:
        result = api.edits().listings().list(
            packageName=package_name, editId=edit_id
        ).execute()
        languages = [item.get("language") for item in result.get("listings", [])]
        print(f"API access verified for {package_name}. Existing locales: {languages}")
    finally:
        api.edits().delete(packageName=package_name, editId=edit_id).execute()

def publish(api, package_name, listings):
    edit = api.edits().insert(packageName=package_name, body={}).execute()
    edit_id = edit["id"]
    for locale, body in listings.items():
        api.edits().listings().update(
            packageName=package_name, editId=edit_id, language=locale, body=body
        ).execute()
        print(f"Prepared {locale}")
    api.edits().commit(packageName=package_name, editId=edit_id).execute()
    print(f"Committed {len(listings)} localized listings for {package_name}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("app", choices=tuple(APPS))
    parser.add_argument("action", choices=("validate", "api-check", "publish"))
    args = parser.parse_args()

    config = APPS[args.app]
    package_name = config["package"]

    if args.action == "api-check":
        api_check(service(), package_name)
        return

    listings = load_listings(config["locales"])
    print(f"Validated {len(listings)} locale files for {package_name}")
    if args.action == "validate":
        return
    publish(service(), package_name, listings)

if __name__ == "__main__":
    main()
