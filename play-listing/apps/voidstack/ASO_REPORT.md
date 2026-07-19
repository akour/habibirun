# Void Stack ASO candidate

Status: approved direction, validated candidate, **not yet published to Google Play**.

## Scope

- Package: `com.oneapps.voidstack`
- 20 existing locales preserved
- ASO-focused titles and short descriptions prepared for every locale
- Full descriptions substantially repaired or rewritten in English, Hindi, Indonesian, Japanese, Korean, Thai, Simplified Chinese and Traditional Chinese
- Turkish copy typo corrected
- Google Play limits validated: title 30, short description 80, full description 4000 characters

## English comparison

| Field | Current | Proposed |
|---|---|---|
| Title | Void Stack: Space Stacker | Void Stack: Space Stack Game |
| Short description | Relax by stacking cosmic blocks. Build towers, explore planets & reach Infinity. | Relaxing stacking game: build a space tower, play offline and explore planets. |

## Search direction

Primary concepts: stacking game, block game, relaxing game, offline game and space game.

Supporting concepts: tower building, timing, planets and endless progression.

## Publication safety

The candidate is stored in `listings.json`. The workflow's `validate` action is safe and read-only. The `publish` action remains a separate manual choice and commits the listing changes to Google Play.
