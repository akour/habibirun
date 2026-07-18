# Google Play listing automation

Package: `com.oneapps.habibirun`

The manual **Google Play Store Listing** workflow supports:

- `validate`: checks locale JSON and Play character limits without credentials.
- `api-check`: opens a temporary Google Play edit, reads listings, and discards it. It does not change the store.
- `publish`: creates or updates all localized listings and commits the edit.

Publishing is intentionally manual. Do not use `publish` while another release or store-listing edit is under review.

The repository secret `PLAY_SERVICE_ACCOUNT_JSON` must contain the complete JSON service-account key. Never commit that key.
