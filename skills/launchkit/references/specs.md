# Asset specs: every slot, every dimension

Console requirements drift. Specs below were verified mid-2026 against Apple's
App Store Connect screenshot specification and Google's Play Console graphic
assets help. Both consoles reject off-by-one uploads, so verify before uploading:

```bash
sips -g pixelWidth -g pixelHeight -g hasAlpha file.png
```

## Contents

- [The slot-label rule](#the-slot-label-rule)
- [App Store screenshots](#app-store-screenshots)
- [App Store icon](#app-store-icon)
- [Google Play screenshots](#google-play-screenshots)
- [Google Play graphics](#google-play-graphics)
- [Social banners](#social-banners)
- [Product Hunt](#product-hunt)
- [Format rules that cause rejections](#format-rules-that-cause-rejections)

## The slot-label rule

**Render at the size the console's upload box asks for, not the newest size
Apple supports.**

An existing app record can present an **iPhone 6.5" Display** box that accepts
only 1242×2688 or 1284×2778. A valid 6.9" image (1290×2796 or 1320×2868)
uploaded there fails with "The dimensions of one or more screenshots are wrong",
and the error lists the sizes it *does* want — read that list rather than
re-rendering even larger.

Records created at different times expose different slots. Check the label
before generating anything; it decides your render dimensions. When you cannot
see the console, ask the user to read the slot label to you.

## App Store screenshots

Apple requires only the largest display class per device family and scales down
for smaller devices. One iPhone set plus one iPad set covers everything.

| Class | Status | Accepted portrait px | Native capture device |
|---|---|---|---|
| iPhone 6.9" | Required (or supply 6.5") | 1320×2868, 1290×2796, 1260×2736 | iPhone 17 / 16 Pro Max → 1320×2868 |
| iPhone 6.5" | Legacy alternative | 1284×2778, 1242×2688 | iPhone 14 Plus → 1284×2778 |
| iPad 13" | Required if iPad supported | 2064×2752, 2048×2732 | iPad Pro 13-inch (M4/M5) → 2064×2752 |
| Smaller classes | Optional | auto-scaled | skip unless layout differs |

Landscape = the same numbers swapped. Count: 1–10 per class per localisation.

**Capture native, compose native, upload native.** Each class lists several
accepted sizes and it is tempting to standardise on a smaller one. Don't —
anything but the native size means resampling every shot, softening UI text.

## App Store icon

One 1024×1024 PNG, **no alpha channel, no pre-rounded corners** — Apple applies
the mask, and an alpha channel is a binary rejection. For Expo, set
`"icon": "./assets/icon.png"` in the app config; the build writes the asset
catalog. The store icon comes from the binary, so there is normally nothing to
upload in App Store Connect.

## Google Play screenshots

| Asset | Spec |
|---|---|
| Phone | Min 2, max 8. Each side 320–3840px. **Longest side ≤ 2× shortest.** ≤8MB each |
| Promotion eligibility | ≥4 shots at ≥1080px, 16:9 or 9:16 |
| 7" / 10" tablet | Up to 8 each, optional to publish |

**The 2:1 trap.** Modern Android phones are ~20:9, so a raw capture is e.g.
1080×2400 — and 2400 > 2×1080, so Play rejects it. Every Android phone
screenshot needs a pad or crop step. Standardise on **1080×1920**. Google does
not auto-scale between device types the way Apple does; each set is used as-is.

## Google Play graphics

| Asset | Spec | Notes |
|---|---|---|
| Feature graphic | **1024×500**, no alpha | Required to publish, and required for a promo video to display. Design it as a banner: it crops behind the play button in some placements, so keep key content centred |
| App icon | **512×512**, 32-bit PNG, alpha allowed, ≤1024KB | Google applies a 30%-radius corner mask and its own shadow — upload a full square, don't pre-round, keep content out of the corners |

## Social banners

| Surface | Size |
|---|---|
| X / Twitter header | 1500×500 |
| LinkedIn company cover | 1128×191 |
| LinkedIn personal cover | 1584×396 |
| Open Graph / link preview | 1200×630 |

LinkedIn covers are extreme letterboxes and both crop responsively — keep the
logo and any words in the middle third, well inside the vertical bounds.

## Product Hunt

| Asset | Size |
|---|---|
| Gallery image | 1270×760 |
| Thumbnail / logo | 240×240 |

## Format rules that cause rejections

- **Flatten everything destined for a screenshot slot.** RGB, no alpha. Both
  stores reject transparency in screenshots; Apple rejects it in the icon.
- **Screenshots must show the app in use** — not splash screens, not login
  walls, and never a feature absent from the submitted build (App Review 2.3.x;
  Play "misleading assets").
- **Device frames are allowed**, and Apple publishes official bezels. Don't show
  Android hardware in App Store shots or iPhones in Play shots.
- **Captions may not exaggerate.** Superlatives and unverifiable claims count as
  misleading metadata.
- **Regulated content** (cannabis, gambling, alcohol): captions must match
  in-app disclaimers exactly, state what the app does *not* do, and never frame
  a feature as a medical or safety tool. Reviewers diff store copy against
  in-app copy.

## App preview videos (optional, lowest ROI for a v1)

iOS: up to 3 per class, 15–30s, ≤500MB, H.264. The 6.9" class takes 886×1920
portrait, iPad 13" takes 1200×1600 — **not** the screenshot dimensions, so a
screen recording needs resizing. Capture with
`xcrun simctl io booted recordVideo out.mov`; no hands or devices in frame.

Google Play takes a **YouTube URL** instead (a video, not a playlist): public or
unlisted, embedding on, monetisation off, not age-restricted, and it only
displays if a feature graphic exists. Only the first ~30s autoplay, so
front-load. Ship screenshots first.
