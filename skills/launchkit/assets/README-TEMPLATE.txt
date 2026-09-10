<PRODUCT> — LAUNCH KIT
=======================
Every image below is a flat, fully opaque PNG at the exact size its slot wants.
Nothing here needs a crop, a resize, or a decision at upload time: drag the
folder contents in, in numeric order.

Captured <DATE> from <WHAT WAS RUNNING — build number, environment, API> by
<WHAT FLOW WAS DRIVEN>. Every screen shows real data: <NAME THE REAL RECORDS —
the actual account, the actual item, the actual numbers>. No mockups, no lorem,
no placeholder rows.


<APP DISPLAY NAME>  (<bundle.id>)
---------------------------------
  <app>/app-store-iphone/01–0N.png   <W> × <H>
      → App Store Connect ▸ your version ▸ App Screenshots ▸ iPhone <CLASS> slot
  <app>/app-store-ipad/01–0N.png     <W> × <H>
      → same screen ▸ iPad <CLASS> slot         (only if the app supports iPad)
  <app>/app-store-icon-1024.png      1024 × 1024
      → normally unused; the store icon comes from the binary
  <app>/play-store-phone/01–0N.png   1080 × 1920
      → Play Console ▸ Store listing ▸ Graphics ▸ Phone screenshots
  <app>/play-store-feature.png       1024 × 500   → Play feature graphic (required, exact)
  <app>/play-store-icon-512.png       512 × 512   → Play app icon

  The <N>, in order, tell one story:
    01  <what this shot shows and why it leads>
    02  <the next step in the flow>
    03  <the payoff>
    04  <secondary feature, with real data>
    05  <trust / closing>


SOCIAL
------
  social/x-banner.png            1500 × 500   → X / Twitter header
  social/linkedin-company.png    1128 × 191   → LinkedIn company cover
  social/linkedin-personal.png   1584 × 396   → LinkedIn personal cover


PRODUCT HUNT
------------
  product-hunt/gallery.png       1270 × 760   → Gallery image
  product-hunt/thumbnail.png      240 × 240   → Thumbnail / logo


LISTING COPY
------------
Every text field for every app and store, in every locale, is in
  <PATH TO STORE-LISTING-COPY.md>
App Store captions stay factual and descriptive, with no superlatives, per
Apple's review rules.

Reviewer sign-in: <CREDENTIALS, and any bypass a reviewer needs — a fixed OTP,
a seeded account, a simulated location>.


VERIFYING
---------
  python3 <skill>/scripts/verify_kit.py <kit dir> --manifest <kit dir>/manifest.json

Checks every file exists at exactly its slot size, opaque where required, under
any size ceiling. Run it before opening a console.


REGENERATING
------------
Screens change, and stale screenshots are worse than none. To redo:
  bash   <skill>/scripts/shoot_ios.sh --device "<DEVICE>" --bundle <BUNDLE> --out raw/<class>
  python3 <skill>/scripts/compose.py --in raw/<class> --out <app>/app-store-iphone \
            --size <W>x<H> --captions captions.json --bg "<BRAND>" --expect-raw <W>x<H>
  python3 <skill>/scripts/banners.py --out social --logo <LOGO> --headline "<HEADLINE>"

Keep these commands and any captions.json here in the kit, not in a scratch
directory — a kit that cannot be regenerated ships stale at the next release.
See <PATH TO RELEASE-HANDOFF.md> for the submission pipeline.
