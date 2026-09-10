#!/usr/bin/env bash
# Capture App Store screenshots from the iOS Simulator at native slot size.
#
# Why this exists: capturing on the device class that matches the console slot
# means the raw PNG is already an accepted dimension, so nothing gets resampled
# and UI text stays sharp. Everything else here guards a specific failure:
# booting is asynchronous (shoot too early and you get the springboard), and a
# real status bar leaks battery percentage and carrier name into your kit.
set -euo pipefail

DEVICE="iPhone 17 Pro Max"
BUNDLE=""
OUT="raw"
APP_PATH=""

usage() {
  cat <<'USAGE'
Usage: shoot_ios.sh [options]

  --device NAME    Simulator device name (default: "iPhone 17 Pro Max")
                   App Store slots and their native devices:
                     iPhone 6.9" (1320x2868)  -> iPhone 17 Pro Max / 16 Pro Max
                     iPhone 6.5" (1284x2778)  -> iPhone 14 Plus
                     iPad 13"    (2064x2752)  -> iPad Pro 13-inch (M4/M5)
  --bundle ID      Bundle id to launch (e.g. com.example.app)
  --app PATH       Optional .app to install first (from an EAS simulator build)
  --out DIR        Output directory for raw captures (default: raw)
  --list           List available simulator devices and exit
  --help           This message

Press Enter to capture each shot; type 'q' then Enter to finish.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --device) DEVICE="$2"; shift 2 ;;
    --bundle) BUNDLE="$2"; shift 2 ;;
    --app)    APP_PATH="$2"; shift 2 ;;
    --out)    OUT="$2"; shift 2 ;;
    --list)   xcrun simctl list devices available; exit 0 ;;
    --help|-h) usage; exit 0 ;;
    *) echo "unknown option: $1" >&2; usage; exit 1 ;;
  esac
done

mkdir -p "$OUT"

if ! xcrun simctl list devices available | grep -q "$DEVICE"; then
  echo "Device '$DEVICE' not available. Available devices:" >&2
  xcrun simctl list devices available >&2
  echo >&2
  echo "Create one with: xcrun simctl create \"$DEVICE\" \"$DEVICE\"" >&2
  exit 1
fi

echo "==> Booting $DEVICE"
xcrun simctl boot "$DEVICE" 2>/dev/null || true
# bootstatus blocks until the device is genuinely ready. Skipping this is how
# you end up with a folder of springboard screenshots.
xcrun simctl bootstatus "$DEVICE" -b
open -a Simulator || true

if [[ -n "$APP_PATH" ]]; then
  echo "==> Installing $APP_PATH"
  xcrun simctl install "$DEVICE" "$APP_PATH"
fi

# 9:41 with full battery and signal is Apple's own marketing convention and
# reads as deliberate rather than as someone's actual phone.
echo "==> Pinning status bar to 9:41, full battery, full signal"
xcrun simctl status_bar "$DEVICE" override \
  --time "9:41" \
  --batteryState charged --batteryLevel 100 \
  --dataNetwork wifi --wifiMode active --wifiBars 3 \
  --cellularMode active --cellularBars 4 \
  --operatorName "" 2>/dev/null || echo "    (status bar override unsupported on this device; continuing)"

if [[ -n "$BUNDLE" ]]; then
  echo "==> Launching $BUNDLE"
  xcrun simctl launch "$DEVICE" "$BUNDLE" || echo "    (launch failed; open the app manually)"
fi

cleanup() {
  xcrun simctl status_bar "$DEVICE" clear 2>/dev/null || true
  echo
  echo "==> Status bar restored. Captures in: $OUT"
}
trap cleanup EXIT

cat <<'EOF'

------------------------------------------------------------------
Navigate the app to each state you want, then press Enter to shoot.
Type 'q' + Enter when finished.

Remember the story: shot 01 is the hero (never a login or an empty
state), and the first three sell the app before anyone taps.
------------------------------------------------------------------
EOF

n=1
while true; do
  printf "Shot %02d — Enter to capture (q to quit): " "$n"
  read -r reply || break
  [[ "$reply" == "q" ]] && break
  f=$(printf "%s/%02d.png" "$OUT" "$n")
  xcrun simctl io "$DEVICE" screenshot "$f"
  dims=$(sips -g pixelWidth -g pixelHeight "$f" | awk '/pixelWidth|pixelHeight/{printf "%s ", $2}')
  echo "    saved $f  (${dims}px)"
  n=$((n + 1))
done
