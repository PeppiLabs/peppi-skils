# Privacy labels, data safety, and age ratings

Both stores make you declare what you collect. These declarations are checked
against your description, your review notes, and sometimes against the binary
itself. Getting them wrong is a policy problem in its own right — over-declaring
as much as under-declaring.

## Contents

- [Work from the code, not from memory](#work-from-the-code-not-from-memory)
- [iOS App Privacy](#ios-app-privacy)
- [Google Play Data safety](#google-play-data-safety)
- [The answers people get wrong](#the-answers-people-get-wrong)
- [Play App content declarations](#play-app-content-declarations)
- [Age ratings](#age-ratings)
- [Account deletion](#account-deletion)

## Work from the code, not from memory

Before filling anything in, enumerate what the app actually touches:

- Permission strings in the app config (`NSCameraUsageDescription`,
  `NSLocationWhenInUseUsageDescription`, Android `permissions`) — each one
  implies a data type, and an unused permission is worth deleting rather than
  declaring.
- Every field the client sends to the API, and every third-party SDK linked in
  (analytics, crash reporting, payments, maps, push).
- What the backend stores and for how long.

An SDK you added and forgot collects data on your behalf and you are
responsible for declaring it. Conversely, do not declare crash/diagnostics data
if no crash SDK is installed.

## iOS App Privacy

Declared per data type with three questions: is it **linked to the user**, is it
**used to track** them, and what is the **purpose**. Tabulate it:

| Data type (Apple category) | Linked to user | Used to track | Purpose |
|---|---|---|---|
| Email Address (Contact Info) | Yes | No | App Functionality: account and sign-in |
| Name (Contact Info) | Yes | No | App Functionality: shown to <whom, why> |
| Photos (User Content) | Yes | No | App Functionality: <what the photo is for> |
| Precise Location (Location) | Yes | No | App Functionality: <only during what> |
| Payment Info (Financial Info) | Yes | No | App Functionality: handled by <processor> |
| Crash Data (Diagnostics) | No | No | App Functionality: stability |

"**Tracking**" has a narrow, specific meaning: linking this data with data from
other companies' apps or websites for advertising or measurement, or sharing it
with a data broker. Using data inside your own app is not tracking. Most apps
without ad SDKs answer **Tracking: None** — and if you do track, you need the
App Tracking Transparency prompt.

## Google Play Data safety

Per data type: **collected**, **shared**, purpose, whether it is required or
optional, plus two global questions — encrypted in transit, and whether users
can request deletion.

```
- <Category> > <Type> - Collected: Yes. Shared: No. Purpose: <...>. Optional/Required.
```

Processing by service providers acting on your behalf (a payment processor, a
transcription service, an SMS gateway) is disclosed but is not "sharing with
third parties" in Play's sense. Say so explicitly in the copy file so the next
person doesn't re-litigate it.

## The answers people get wrong

- **"Shared" means leaving your app's control — including to another user.** If
  one user sees another user's name, photo, or live location, that is sharing.
  Say yes. This is the most commonly missed answer.
- **Precise location must be declared even if used only in the foreground.**
  There is no "only while in use" escape on the data-safety form; that is a
  *permission* question, not a data-safety one.
- **Optional data must be marked optional.** If a user can complete the core
  flow without ever granting the mic, the recording is optional. Marking it
  required is a false declaration.
- **Do not declare data you do not collect.** Diagnostics and crash logs are the
  usual over-declaration, added reflexively without a crash SDK present.
- **Deletion must mean deletion.** An endpoint that deactivates but retains does
  not satisfy the answer.
- **Payment data**: if a processor collects the card and you only store a token,
  say exactly that. Do not claim you collect card numbers, and do not claim you
  collect nothing.

## Play App content declarations

Beyond data safety, Play asks for:

| Item | Notes |
|---|---|
| Privacy policy | A URL that resolves and actually covers the app |
| App access | If anything is behind a login, provide working credentials **and** instructions, including any review bypass |
| Ads | Whether the app contains ads — separate from whether you track |
| Content rating | IARC questionnaire; answer truthfully, it is easy to over-rate by accident |
| Target audience | Age bands. Anything including children triggers Families policy |
| Financial features | Answer carefully — "the app moves money" and "the app charges for itself" are different claims |
| Government apps | Yes only if you are a government entity |
| Health | Includes fitness and wellbeing claims |

## Age ratings

**Apple**, as of 2026: tiers are **4+, 9+, 13+, 16+, 18+** (12+ and 17+ were
retired; the updated questionnaire has been mandatory since January 2026, and
apps that never answered it are blocked from submitting updates).

**Play / IARC**: a questionnaire per territory producing ESRB/PEGI equivalents.

Two things that surprise people: user-to-user communication as *core
functionality* (a chat between a buyer and a seller) does not by itself raise
the tier the way an open social feed does — but enabling "Unrestricted Web
Access" does. Answer for what the app actually exposes.

## Account deletion

Apple requires apps offering account creation to offer **in-app account
deletion** (5.1.1(v)) — not a support email, not a web form buried elsewhere.
Verify the path exists in the build you are submitting, and write the exact
navigation into the review notes: `Profile → Delete account`. Play's data-safety
form asks the equivalent question.

This is a routine rejection cause and it is cheap to check before submitting.
