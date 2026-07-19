#!/usr/bin/env python3
import argparse, json, os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APPS = {
    "habibirun": {"package": "com.oneapps.habibirun", "locales": ROOT / "locales"},
    "voidstack": {"package": "com.oneapps.voidstack", "locales": ROOT / "apps" / "voidstack" / "listings.json"},
    "voiddash": {"package": "com.oneapps.voiddash002", "locales": ROOT / "apps" / "voiddash" / "locales"},
}

def load_listings(source):
    listings = {}
    if source.is_file():
        candidates = [
            (locale, data, source)
            for locale, data in json.loads(source.read_text(encoding="utf-8")).items()
        ]
    else:
        candidates = [
            (path.stem, json.loads(path.read_text(encoding="utf-8")), path)
            for path in sorted(source.glob("*.json"))
        ]
    for locale, data, path in candidates:
        required = ("title", "shortDescription", "fullDescription")
        missing = [key for key in required if not data.get(key)]
        if missing:
            raise SystemExit(f"{path}: missing {', '.join(missing)}")
        limits = {"title": 30, "shortDescription": 80, "fullDescription": 4000}
        for key, limit in limits.items():
            if len(data[key]) > limit:
                raise SystemExit(f"{path}: {key} is {len(data[key])}/{limit} characters")
        listings[locale] = data
    if not listings:
        raise SystemExit(f"No locale listings found in {source}")
    return listings

def service():
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    raw = os.environ.get("PLAY_SERVICE_ACCOUNT_JSON")
    if not raw:
        raise SystemExit("PLAY_SERVICE_ACCOUNT_JSON is not available")
    credentials = service_account.Credentials.from_service_account_info(
        json.loads(raw), scopes=["https://www.googleapis.com/auth/androidpublisher"]
    )
    return build("androidpublisher", "v3", credentials=credentials, cache_discovery=False)

def read_listings(api, package_name):
    edit = api.edits().insert(packageName=package_name, body={}).execute()
    edit_id = edit["id"]
    try:
        result = api.edits().listings().list(
            packageName=package_name, editId=edit_id
        ).execute()
        return result.get("listings", [])
    finally:
        api.edits().delete(packageName=package_name, editId=edit_id).execute()

def api_check(api, package_name):
    listings = read_listings(api, package_name)
    languages = [item.get("language") for item in listings]
    print(f"API access verified for {package_name}. Existing locales: {languages}")

def export_listings(api, app_name, package_name):
    listings = read_listings(api, package_name)
    output_dir = Path("listing-export") / app_name
    output_dir.mkdir(parents=True, exist_ok=True)
    for item in listings:
        locale = item["language"]
        data = {
            "title": item.get("title", ""),
            "shortDescription": item.get("shortDescription", ""),
            "fullDescription": item.get("fullDescription", ""),
            "video": item.get("video", ""),
        }
        (output_dir / f"{locale}.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    summary = {
        "app": app_name,
        "package": package_name,
        "locales": sorted(item["language"] for item in listings),
        "count": len(listings),
    }
    (output_dir / "_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Exported {len(listings)} existing listings for {package_name}")

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
    parser.add_argument("action", choices=("validate", "api-check", "export", "publish"))
    args = parser.parse_args()
    config = APPS[args.app]
    package_name = config["package"]

    if args.action == "api-check":
        api_check(service(), package_name)
        return
    if args.action == "export":
        export_listings(service(), args.app, package_name)
        return

    listings = load_listings(config["locales"])
    print(f"Validated {len(listings)} locale files for {package_name}")
    if args.action == "validate":
        return
    publish(service(), package_name, listings)

if __name__ == "__main__":
    main()
