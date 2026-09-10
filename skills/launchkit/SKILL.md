---
name: launchkit
description: "Build a complete, ready-to-upload launch kit for an app or product: store screenshots at exact slot dimensions, app icons, Play feature graphics, social banners (X, LinkedIn), Product Hunt assets, and every field of store listing copy with character counts, App Review notes, and privacy/data-safety answers. Use this whenever the user is preparing a launch or a store submission, mentions a launch kit, store screenshots, App Store or Google Play listing assets, a feature graphic, store listing copy, review notes, privacy labels or data safety answers, social/launch banners, or Product Hunt assets, or asks to 'get the store assets together', 'make the screenshots for the listing', 'prep the launch', or 'we're submitting tomorrow, what do I need'. Use it even when they name only one piece (just screenshots, just the copy) because the pieces have to agree with each other."
license: Complete terms in LICENSE.txt
metadata:
  publisher: Peppi Labs
  publisher-url: https://www.peppilabs.net
  copyright: "© 2026 Peppi Labs. All rights reserved."
  version: "1.0.0"
---

# Launch Kit

A launch kit is a folder someone drags into store consoles **without making a
single decision**. Every image is already the exact size its slot wants, already
flat and opaque, already numbered in upload order. Every text field is already
inside a code block with its character count against the store's limit. A README
maps each file to the console screen it belongs on.

That is the bar. If the person uploading has to crop something, pick between two
files, or ask "does this go in the 6.5 or the 6.9 slot", the kit is not finished.

## Why the details matter here

Store consoles reject on exact pixel dimensions and on alpha channels. App
reviewers cross-check the screenshots against the running app, and the listing
description against the review notes against the privacy labels. So the failure
modes are not "it looks a bit off" — they are a rejected upload or a rejected
submission, days after you thought you were done.

Three failures that have actually happened and cost rebuild cycles:

- A perfectly valid 6.9" screenshot (1320×2868) uploaded to a record whose
  console showed an **iPhone 6.5" Display** slot. Rejected: "the dimensions of
  one or more screenshots are wrong." Newer is not safer. **Read the slot label.**
- Capture scripts written into a scratch directory. The kit shipped, the
  scratchpad was cleaned, and the screenshots became unregenerable — so the next
  release shipped stale shots of screens that had changed.
- An app whose in-app theme colour had drifted from its icon and website, caught
  only when the screenshots were laid next to the store icon.

## Phase 1 — Scope the kit before generating anything

Answer these first; they determine every dimension you will render at.

1. **Which surfaces?** Per app: App Store, Google Play, or both. Plus social and
   Product Hunt if this is a public launch. Multi-app products (a rider app and
   a driver app) get one subfolder each — they are separate listings with
   separate copy.
2. **Read the actual slot labels in the consoles.** Ask the user to look, or look
   yourself if you have console access. Do not infer from the app's age. This is
   the single highest-cost mistake in the whole process.
3. **Does it support tablets?** `supportsTablet: true` in an Expo config, or an
   iPad target, obliges iPad screenshots at submission. Either produce them or
   turn tablet support off before submitting.
4. **What login does a reviewer need?** Screenshots need populated screens, and
   App Review needs working credentials. If neither exists yet, that is a
   blocker to surface now, not after you have built half the kit.
5. **Is the app on-brand with itself?** Compare the in-app theme colour to the
   icon and the marketing site. Screenshots are where drift becomes visible to
   everyone at once, and fixing it after capture means recapturing.

Read `references/specs.md` for every dimension and which console slot it feeds.

## Phase 2 — Capture real screens, running the real product

**Drive one real end-to-end flow and shoot at each state.** Not mockups, not
seeded lorem, not empty states with placeholder rows. Reviewers compare
screenshots against the app they are running, and "shows features that don't
exist in the submitted build" is a rejection. Real data is also simply more
persuasive: a real name, a real route, a real balance.

This means the screens need content before you shoot. Seed a real account and
perform the actual flow.

Capture from the device class that matches the slot natively, so the raw file is
already the right size and needs no resampling:

```bash
bash scripts/shoot_ios.sh --device "iPhone 17 Pro Max" --bundle com.example.app --out raw/iphone-6.9
```

That script boots the simulator, waits for it to actually finish booting
(shooting early gets you the springboard), pins the status bar to 9:41 with full
battery and signal, and captures on each press of Enter so you can navigate
between shots. Run `--help` for the options.

For Expo apps, capture a **release** build, not a dev build — dev builds leak the
dev-menu bubble and `__DEV__` warnings into your shots. A store build is an
`.ipa` and cannot install to a simulator, so make a simulator build
(`"ios": { "simulator": true }` in an `eas.json` profile) or run
`npx expo run:ios --configuration Release`.

Android has no `adb` on every machine and its own trap: a raw Pixel capture is
1080×2400, and Play rejects anything whose longest side exceeds twice its
shortest. Standardise on 1080×1920 and let `compose.py` pad rather than distort.

### Choosing the shots

Five to eight images that tell one story in order. iOS search shows the first ~3
and Play the first ~4, so the story has to land before anyone taps.

1. **Hero** — the one differentiating thing, mid-use, with real data. Never the
   login, splash, or an empty state.
2. **The next step** — what happens after the hero action.
3. **The payoff** — the thing the user actually came for.
4. A secondary feature, still with real data in it.
5. Trust: verification, privacy stance, reviews.
6–8. Optional: personalisation, platform extras, a closing brand card.

Write down what each numbered shot shows. That list goes in the README, and it
is what makes the kit regenerable by someone who wasn't there.

## Phase 3 — Compose to exact dimensions

```bash
python3 scripts/compose.py --in raw/iphone-6.9 --out kit/app-store-iphone \
  --size 1320x2868 --captions captions.json --bg "#044ED7" --fg "#FFFFFF"
```

`compose.py` adds the caption bar, scales the shot beneath it, flattens to
opaque RGB, and asserts the result is exactly the target size before writing. It
refuses to silently rescale — a wrong input size means the wrong simulator was
booted, and you want to hear about that immediately.

Captions are optional; raw screenshots are acceptable to both stores. Framed and
captioned sets convert better, but **a correct raw set beats a missing fancy
set.** Keep caption text factual and descriptive — Apple treats superlatives and
exaggerated claims as misleading metadata.

Social and Product Hunt banners:

```bash
python3 scripts/banners.py --out kit/social --logo assets/logo.png \
  --headline "Find your lost items" --bg "#044ED7"
```

## Phase 4 — Write the copy, then verify the whole kit

Store copy lives in one Markdown file per product, every field in a code block
with a live character count against the store's limit — `(28/30)` — so nothing
gets truncated at paste time. Read `references/listing-copy.md` for the field
list and templates, and `references/privacy.md` for the privacy labels and Play
Data safety answers.

**The consistency triangle.** The description, the App Review notes, and the
privacy declarations must tell the same story, because reviewers read them
against each other. Wherever the product has a boundary that a reviewer might
mistake — where money is handled, what data leaves the device, what the app
deliberately does *not* do — state it the same way in all three. Writing "what
the app does NOT do" explicitly in the review notes is the single highest-value
paragraph in the kit.

Then verify, before anyone opens a console:

```bash
python3 scripts/verify_kit.py kit/ --manifest kit/manifest.json
```

It checks every expected file exists, is exactly its slot's dimensions, is
opaque where the slot demands opacity, and is under any size ceiling. A loud
failure costs seconds; a silent rescale costs a rebuild cycle.

## Phase 5 — Write the README and make it regenerable

Copy `assets/README-TEMPLATE.txt` into the kit root and fill it in. It must say,
for every file: the exact pixel size, and the console screen it goes on. It must
also record what each numbered shot shows, when the kit was captured and against
what environment, and the reviewer sign-in.

**Keep the generation scripts with the kit, not in a scratch directory.** The
most common way a kit dies is that it cannot be regenerated: screens change,
nobody can rebuild the shots, and the listing ships stale. Stale screenshots are
worse than none.

## The output shape

```
launch-kit/
├── README.txt                        the map: file -> console slot
├── <app>/                            one folder per app/listing
│   ├── app-store-iphone/01..05.png   exact slot size, opaque
│   ├── app-store-ipad/01..05.png     if tablets are supported
│   ├── app-store-icon-1024.png       1024x1024, NO alpha
│   ├── play-store-phone/01..05.png   1080x1920
│   ├── play-store-feature.png        1024x500, required to publish
│   └── play-store-icon-512.png       512x512, alpha allowed
├── social/
│   ├── x-banner.png                  1500x500
│   ├── linkedin-company.png          1128x191
│   └── linkedin-personal.png         1584x396
├── product-hunt/
│   ├── gallery.png                   1270x760
│   └── thumbnail.png                 240x240
└── STORE-LISTING-COPY.md             every field, with character counts
```

Numeric filenames matter: they are the upload order, and they encode the story.

## Reference index

| Read | When |
|---|---|
| `references/specs.md` | Any dimension question; the full slot table for both stores, social, and Product Hunt |
| `references/listing-copy.md` | Writing any store text: names, subtitles, descriptions, keywords, release notes, review notes |
| `references/privacy.md` | iOS privacy labels, Play Data safety, age rating, and the declarations people get wrong |
| `scripts/shoot_ios.sh` | Capturing from the iOS Simulator |
| `scripts/compose.py` | Captioning, padding, flattening, exact-size enforcement |
| `scripts/banners.py` | Social and Product Hunt graphics |
| `scripts/verify_kit.py` | Before handing the kit over — always |
| `assets/README-TEMPLATE.txt` | The kit's own README |

## Working style

- **Surface blockers early.** Missing demo account, no tablet screenshots, brand
  drift, a payment flow that needs IAP — these are cheaper to raise in Phase 1
  than to discover at review.
- **Never invent facts about the product.** Screenshots and copy are claims a
  reviewer will check. If you do not know whether something is true, ask.
- **Check the project's own conventions** before writing copy. Some projects ban
  particular characters or mandate a voice; look for a house style doc and follow
  it rather than defaulting to your own.
- **Localisation**: the cheap version re-renders caption text per locale over the
  same captures. Budget captions for translation from the start — keep them
  short and idiom-free.
