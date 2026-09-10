# Store listing copy

Everything a console will ask you to type, in one file per product, so nobody
writes copy inside a console text box at submission time.

## Contents

- [File conventions](#file-conventions)
- [The consistency triangle](#the-consistency-triangle)
- [iOS App Store fields](#ios-app-store-fields)
- [Google Play fields](#google-play-fields)
- [App Review notes](#app-review-notes)
- [What can change without a review](#what-can-change-without-a-review)
- [Voice and localisation](#voice-and-localisation)

## File conventions

One `STORE-LISTING-COPY.md` per product. For each field:

- A bold label carrying the store's limit, then the **live character count**:
  `**Subtitle (max 30)** (28/30)`
- The value inside a fenced code block, so it pastes clean with no Markdown
  artefacts and no smart-quote substitution.

````markdown
**App Name (max 30)** (17/30)

```
Bola: Taxi y Moto
```
````

Counts are the point: a description that silently truncates at 4000 characters,
or a 31-character name the console refuses, is discovered at the worst moment.
Count them for real rather than estimating, and re-count after every edit.

Organise by product → store → locale:

```
# <Product>
## iOS App Store / English (en)
## iOS App Store / Spanish (es)
## Google Play / English (en)
## Google Play / Spanish (es)
## App Review Notes (shared)
## Age Rating (shared)
## Privacy Labels (shared)
```

Mark anything you could not determine as an explicit placeholder —
`[SUPPORT NAME / EMAIL / PHONE]` — so it is greppable. Never invent a support
contact, a privacy-policy URL, or a demo credential.

## The consistency triangle

The **description**, the **App Review notes**, and the **privacy declarations**
are read against each other by reviewers. When they disagree, the submission
stalls, and the disagreement is usually accidental: marketing copy says "send
money to friends", review notes say "we do not process payments".

So identify the product's boundaries — where money is handled, what data leaves
the device, what the product deliberately does not do — and state each one **the
same way in all three places**. Writing the boundary once, near the top of the
copy file, and reusing that exact sentence is a reliable way to keep them
aligned.

## iOS App Store fields

| Field | Limit | Notes |
|---|---|---|
| App Name | 30 | Must be unique across the entire App Store. A free bundle ID does not mean the name is free |
| Subtitle | 30 | Below the name in results. Concrete benefit, not a tagline |
| Promotional Text | 170 | The only field editable any time **without review** — use it for time-sensitive news |
| Keywords | 100 | Comma-separated, no spaces after commas (they cost characters). Don't repeat words already in the name/subtitle |
| Description | 4000 | Only the first ~3 lines show before "more" |
| What's New | 4000 | Per version, requires review |
| Support / Marketing URL | — | Support URL is required and must resolve |

Keywords: singular and plural are matched separately in some cases; prefer the
form users type. Don't waste characters on your own brand name (already
indexed), category names Apple derives, or competitor trademarks (rejection).

## Google Play fields

| Field | Limit | Notes |
|---|---|---|
| App name | 30 | |
| Short description | 80 | Shown first and expandable; carries a lot of weight |
| Full description | 4000 | Indexed for Play search, unlike iOS descriptions |
| Release notes | 500 | Per track, per locale |

Play indexes the full description, so natural repetition of the terms people
search for is genuinely useful — but keyword stuffing violates the metadata
policy. Write for a person, then check the important terms appear naturally.

## App Review notes

The most valuable paragraph in the whole kit. Structure it as:

```
WHAT THE APP DOES
<Two or three sentences a reviewer can verify against the running app.>

WHAT THE APP DOES NOT DO
- <Each boundary a reviewer might otherwise assume, stated as a negative.>
- <Especially: money handling, data sharing, regulated-sounding features.>

TEST ACCOUNT
<Working credentials, and how to bypass anything a reviewer cannot receive —
an SMS code, a physical device, a geofence. State it plainly.>

SPECIAL REQUIREMENTS
- <Permissions the app will ask for and why.>
- <Geographic restrictions, hardware needs, network assumptions.>

CONTACT
<Name / email / phone.>
```

Why the negatives matter: reviewers reject on ambiguity. A feature that *might*
be a payments product, a medical tool, or a way to buy a regulated good gets
scrutinised unless you close the question yourself. Say what it is not.

Test accounts must actually work at review time, and must survive whatever
cleanup you run before launch. If review access depends on a test bypass (a
fixed OTP, a seeded account), note that it must be removed before public
launch — and put that in the handoff, because forgetting is a security incident.

## What can change without a review

| Editable any time | Needs a new version + review |
|---|---|
| iOS Promotional Text | Description, keywords, subtitle |
| Pricing and availability | Screenshots and app previews |
| Privacy answers | What's New text |
| Review contact/notes (for next submission) | App name, age-rating answers |

Useful when a launch date slips: promotional text can carry the news while the
rest waits for review.

## Voice and localisation

State the voice explicitly at the top of the copy file — a sentence or two on
register and audience — so later edits stay consistent. List any terms that must
**not** be translated (brand names, local words the audience actually uses).

**Check the project's own conventions before writing.** Some projects forbid
particular characters or mandate a house style; look for a style doc, a
CLAUDE.md, or an existing copy file and follow it rather than defaulting to your
own habits. If a project bans a character, add a check that rejects it rather
than trusting yourself to notice.

Minimum viable localisation is re-rendering caption text per locale over the
same captures. Full localisation captures with the UI language switched. Keep
captions short and idiom-free so translation stays cheap.
