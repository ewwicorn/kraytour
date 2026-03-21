#!/usr/bin/env bash
# ============================================================
# test_api.sh — smoke-test every endpoint of the Kraytour API
#
# Usage:
#   chmod +x test_api.sh
#   ./test_api.sh                     # default: http://localhost:8000
#   ./test_api.sh http://my-host:8000
#
# Requirements: curl, jq
# ============================================================

BASE=${1:-http://localhost:8000}
API="$BASE/api/v1"

# ── colours ──────────────────────────────────────────────────
GREEN='\033[0;32m'; RED='\033[0;31m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

PASS=0; FAIL=0

# ── helpers ──────────────────────────────────────────────────
check() {
  local label="$1" expected="$2" actual="$3" body="$4"
  if [ "$actual" = "$expected" ]; then
    echo -e "  ${GREEN}✓${RESET} $label (HTTP $actual)"
    PASS=$((PASS+1))
  else
    echo -e "  ${RED}✗${RESET} $label — expected ${expected}, got ${actual}"
    echo -e "    ${YELLOW}body: $(echo "$body" | head -c 300)${RESET}"
    FAIL=$((FAIL+1))
  fi
}

section() { echo -e "\n${CYAN}${BOLD}▶ $1${RESET}"; }

# ── health ───────────────────────────────────────────────────
section "Health"
r=$(curl -s -o /tmp/t_body -w "%{http_code}" "$BASE/health")
check "GET /health" 200 "$r" "$(cat /tmp/t_body)"

# ── auth/register ────────────────────────────────────────────
section "Auth — register"

BUYER_EMAIL="buyer_test_$$@example.com"
SELLER_EMAIL="seller_test_$$@example.com"
ADMIN_EMAIL="admin_test_$$@example.com"
PASSWORD="Testpass123"

# Register buyer
r=$(curl -s -o /tmp/t_body -w "%{http_code}" -X POST "$API/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$BUYER_EMAIL\",\"password\":\"$PASSWORD\",\"first_name\":\"Test\",\"last_name\":\"Buyer\",\"role\":\"buyer\"}")
check "POST /auth/register (buyer)" 201 "$r" "$(cat /tmp/t_body)"
BUYER_ID=$(cat /tmp/t_body | jq -r '.id // empty')

# Register seller
r=$(curl -s -o /tmp/t_body -w "%{http_code}" -X POST "$API/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$SELLER_EMAIL\",\"password\":\"$PASSWORD\",\"first_name\":\"Test\",\"last_name\":\"Seller\",\"role\":\"seller\"}")
check "POST /auth/register (seller)" 201 "$r" "$(cat /tmp/t_body)"

# Register admin
r=$(curl -s -o /tmp/t_body -w "%{http_code}" -X POST "$API/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$ADMIN_EMAIL\",\"password\":\"$PASSWORD\",\"first_name\":\"Test\",\"last_name\":\"Admin\",\"role\":\"admin\"}")
check "POST /auth/register (admin)" 201 "$r" "$(cat /tmp/t_body)"

# Duplicate email should 400
r=$(curl -s -o /tmp/t_body -w "%{http_code}" -X POST "$API/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$BUYER_EMAIL\",\"password\":\"$PASSWORD\",\"first_name\":\"Dup\",\"last_name\":\"User\",\"role\":\"buyer\"}")
check "POST /auth/register duplicate → 400" 400 "$r" "$(cat /tmp/t_body)"

# ── auth/login ───────────────────────────────────────────────
section "Auth — login"

r=$(curl -s -o /tmp/t_body -w "%{http_code}" -X POST "$API/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$BUYER_EMAIL\",\"password\":\"$PASSWORD\"}")
check "POST /auth/login (buyer)" 200 "$r" "$(cat /tmp/t_body)"
BUYER_TOKEN=$(cat /tmp/t_body | jq -r '.access_token // empty')

r=$(curl -s -o /tmp/t_body -w "%{http_code}" -X POST "$API/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$SELLER_EMAIL\",\"password\":\"$PASSWORD\"}")
check "POST /auth/login (seller)" 200 "$r" "$(cat /tmp/t_body)"
SELLER_TOKEN=$(cat /tmp/t_body | jq -r '.access_token // empty')

r=$(curl -s -o /tmp/t_body -w "%{http_code}" -X POST "$API/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$ADMIN_EMAIL\",\"password\":\"$PASSWORD\"}")
check "POST /auth/login (admin)" 200 "$r" "$(cat /tmp/t_body)"
ADMIN_TOKEN=$(cat /tmp/t_body | jq -r '.access_token // empty')

# Wrong password
r=$(curl -s -o /tmp/t_body -w "%{http_code}" -X POST "$API/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$BUYER_EMAIL\",\"password\":\"wrongpass\"}")
check "POST /auth/login wrong password → 401" 401 "$r" "$(cat /tmp/t_body)"

# ── auth/me ──────────────────────────────────────────────────
section "Auth — me"

r=$(curl -s -o /tmp/t_body -w "%{http_code}" -H "Authorization: Bearer $BUYER_TOKEN" "$API/auth/me")
check "GET /auth/me (authenticated)" 200 "$r" "$(cat /tmp/t_body)"

r=$(curl -s -o /tmp/t_body -w "%{http_code}" "$API/auth/me")
check "GET /auth/me (no token) → 403" 403 "$r" "$(cat /tmp/t_body)"

# ── auth/logout ──────────────────────────────────────────────
section "Auth — logout"

# Login fresh to get a throwaway token for logout test
r=$(curl -s -o /tmp/t_body -w "%{http_code}" -X POST "$API/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$BUYER_EMAIL\",\"password\":\"$PASSWORD\"}")
THROWAWAY_TOKEN=$(cat /tmp/t_body | jq -r '.access_token // empty')

r=$(curl -s -o /tmp/t_body -w "%{http_code}" -X POST "$API/auth/logout" \
  -H "Authorization: Bearer $THROWAWAY_TOKEN")
check "POST /auth/logout" 200 "$r" "$(cat /tmp/t_body)"

# Token should now be blacklisted
r=$(curl -s -o /tmp/t_body -w "%{http_code}" -H "Authorization: Bearer $THROWAWAY_TOKEN" "$API/auth/me")
check "GET /auth/me with blacklisted token → 401" 401 "$r" "$(cat /tmp/t_body)"

# ── locations/tags ───────────────────────────────────────────
section "Locations — tags"

r=$(curl -s -o /tmp/t_body -w "%{http_code}" "$API/locations/tags")
check "GET /locations/tags (public)" 200 "$r" "$(cat /tmp/t_body)"
FIRST_TAG_ID=$(cat /tmp/t_body | jq -r '.[0].id // empty')
FIRST_TAG_SLUG=$(cat /tmp/t_body | jq -r '.[0].slug // empty')

# ── locations list ───────────────────────────────────────────
section "Locations — list"

r=$(curl -s -o /tmp/t_body -w "%{http_code}" "$API/locations")
check "GET /locations (public, all active)" 200 "$r" "$(cat /tmp/t_body)"

r=$(curl -s -o /tmp/t_body -w "%{http_code}" "$API/locations?page=1&page_size=3")
check "GET /locations?page=1&page_size=3" 200 "$r" "$(cat /tmp/t_body)"

if [ -n "$FIRST_TAG_SLUG" ]; then
  r=$(curl -s -o /tmp/t_body -w "%{http_code}" \
    "$API/locations?tags=$FIRST_TAG_SLUG")
  check "GET /locations?tags=$FIRST_TAG_SLUG" 200 "$r" "$(cat /tmp/t_body)"
fi

r=$(curl -s -o /tmp/t_body -w "%{http_code}" "$API/locations?price_max=2000")
check "GET /locations?price_max=2000" 200 "$r" "$(cat /tmp/t_body)"

r=$(curl -s -o /tmp/t_body -w "%{http_code}" \
  "$API/locations?region=%D0%9A%D1%80%D0%B0%D1%81%D0%BD%D0%BE%D0%B4%D0%B0%D1%80%D1%81%D0%BA%D0%B8%D0%B9+%D0%BA%D1%80%D0%B0%D0%B9")
check "GET /locations?region=Краснодарский край" 200 "$r" "$(cat /tmp/t_body)"

# ── locations get by slug ────────────────────────────────────
section "Locations — get by slug"

FIRST_SLUG=$(curl -s "$API/locations" | jq -r '.items[0].slug // empty')

if [ -n "$FIRST_SLUG" ]; then
  r=$(curl -s -o /tmp/t_body -w "%{http_code}" "$API/locations/$FIRST_SLUG")
  check "GET /locations/$FIRST_SLUG" 200 "$r" "$(cat /tmp/t_body)"
else
  echo -e "  ${YELLOW}⚠ No active locations found — skipping slug tests${RESET}"
fi

r=$(curl -s -o /tmp/t_body -w "%{http_code}" "$API/locations/nonexistent-slug-xyz")
check "GET /locations/nonexistent → 404" 404 "$r" "$(cat /tmp/t_body)"

# ── locations create ─────────────────────────────────────────
section "Locations — create"

LOC_SLUG="test-loc-$$"
TAG_IDS="[]"
if [ -n "$FIRST_TAG_ID" ]; then TAG_IDS="[\"$FIRST_TAG_ID\"]"; fi

LOC_PAYLOAD=$(cat <<JSON
{
  "slug": "$LOC_SLUG",
  "name": "Test Location $$",
  "lat": 45.04,
  "lng": 38.98,
  "address": "Test address",
  "region": "Краснодарский край",
  "price_from": 500,
  "tag_ids": $TAG_IDS
}
JSON
)

# Buyer cannot create
r=$(curl -s -o /tmp/t_body -w "%{http_code}" -X POST "$API/locations" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $BUYER_TOKEN" \
  -d "$LOC_PAYLOAD")
check "POST /locations as buyer → 403" 403 "$r" "$(cat /tmp/t_body)"

# Seller can create
r=$(curl -s -o /tmp/t_body -w "%{http_code}" -X POST "$API/locations" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $SELLER_TOKEN" \
  -d "$LOC_PAYLOAD")
check "POST /locations as seller → 201" 201 "$r" "$(cat /tmp/t_body)"
CREATED_LOC_ID=$(cat /tmp/t_body | jq -r '.id // empty')

# Duplicate slug
r=$(curl -s -o /tmp/t_body -w "%{http_code}" -X POST "$API/locations" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $SELLER_TOKEN" \
  -d "$LOC_PAYLOAD")
check "POST /locations duplicate slug → 400" 400 "$r" "$(cat /tmp/t_body)"

# ── locations update ─────────────────────────────────────────
section "Locations — update"

if [ -n "$CREATED_LOC_ID" ]; then
  r=$(curl -s -o /tmp/t_body -w "%{http_code}" -X PUT "$API/locations/$CREATED_LOC_ID" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $SELLER_TOKEN" \
    -d "{\"name\": \"Updated Name $$\"}")
  check "PUT /locations/:id (owner)" 200 "$r" "$(cat /tmp/t_body)"

  r=$(curl -s -o /tmp/t_body -w "%{http_code}" -X PUT "$API/locations/$CREATED_LOC_ID" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $BUYER_TOKEN" \
    -d "{\"name\": \"Should fail\"}")
  check "PUT /locations/:id (not owner) → 403" 403 "$r" "$(cat /tmp/t_body)"
fi

# ── locations activate ───────────────────────────────────────
section "Locations — activate"

if [ -n "$CREATED_LOC_ID" ]; then
  r=$(curl -s -o /tmp/t_body -w "%{http_code}" -X PATCH "$API/locations/$CREATED_LOC_ID/activate" \
    -H "Authorization: Bearer $SELLER_TOKEN")
  check "PATCH /locations/:id/activate (non-admin) → 403" 403 "$r" "$(cat /tmp/t_body)"

  r=$(curl -s -o /tmp/t_body -w "%{http_code}" -X PATCH "$API/locations/$CREATED_LOC_ID/activate" \
    -H "Authorization: Bearer $ADMIN_TOKEN")
  check "PATCH /locations/:id/activate (admin)" 200 "$r" "$(cat /tmp/t_body)"
fi

# ── locations delete ─────────────────────────────────────────
section "Locations — delete"

if [ -n "$CREATED_LOC_ID" ]; then
  r=$(curl -s -o /tmp/t_body -w "%{http_code}" -X DELETE "$API/locations/$CREATED_LOC_ID" \
    -H "Authorization: Bearer $BUYER_TOKEN")
  check "DELETE /locations/:id (not owner) → 403" 403 "$r" "$(cat /tmp/t_body)"

  r=$(curl -s -o /tmp/t_body -w "%{http_code}" -X DELETE "$API/locations/$CREATED_LOC_ID" \
    -H "Authorization: Bearer $SELLER_TOKEN")
  check "DELETE /locations/:id (owner)" 204 "$r" "$(cat /tmp/t_body)"

  r=$(curl -s -o /tmp/t_body -w "%{http_code}" -X DELETE "$API/locations/$CREATED_LOC_ID" \
    -H "Authorization: Bearer $SELLER_TOKEN")
  check "DELETE /locations/:id already deleted → 404" 404 "$r" "$(cat /tmp/t_body)"
fi

# ── files ────────────────────────────────────────────────────
section "Files"

# Create a tiny test image (1×1 white PNG)
printf '\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82' > /tmp/test_upload.png

r=$(curl -s -o /tmp/t_body -w "%{http_code}" -X POST "$API/files/upload" \
  -H "Authorization: Bearer $BUYER_TOKEN" \
  -F "file=@/tmp/test_upload.png;type=image/png")
check "POST /files/upload (authenticated)" 200 "$r" "$(cat /tmp/t_body)"
OBJECT_NAME=$(cat /tmp/t_body | jq -r '.object_name // empty')

# Verify size is not 0 (was a bug)
FILE_SIZE=$(cat /tmp/t_body | jq -r '.size // 0')
if [ "$FILE_SIZE" -gt 0 ] 2>/dev/null; then
  echo -e "  ${GREEN}✓${RESET} upload response size > 0 (was a bug: $FILE_SIZE bytes)"
  PASS=$((PASS+1))
else
  echo -e "  ${RED}✗${RESET} upload response size is 0 — double-read bug still present"
  FAIL=$((FAIL+1))
fi

# No auth
r=$(curl -s -o /tmp/t_body -w "%{http_code}" -X POST "$API/files/upload" \
  -F "file=@/tmp/test_upload.png;type=image/png")
check "POST /files/upload (no token) → 403" 403 "$r" "$(cat /tmp/t_body)"

if [ -n "$OBJECT_NAME" ]; then
  r=$(curl -s -o /tmp/t_body -w "%{http_code}" \
    -H "Authorization: Bearer $BUYER_TOKEN" \
    "$API/files/url/$OBJECT_NAME")
  check "GET /files/url/:object_name" 200 "$r" "$(cat /tmp/t_body)"

  r=$(curl -s -o /tmp/t_body -w "%{http_code}" -X DELETE \
    -H "Authorization: Bearer $BUYER_TOKEN" \
    "$API/files/$OBJECT_NAME")
  check "DELETE /files/:object_name" 200 "$r" "$(cat /tmp/t_body)"
fi

# Non-existent file
r=$(curl -s -o /tmp/t_body -w "%{http_code}" \
  -H "Authorization: Bearer $BUYER_TOKEN" \
  "$API/files/url/does-not-exist.png")
check "GET /files/url/nonexistent → 404" 404 "$r" "$(cat /tmp/t_body)"

# ── summary ──────────────────────────────────────────────────
TOTAL=$((PASS+FAIL))
echo ""
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
echo -e "${BOLD}Results: $TOTAL tests  |  ${GREEN}$PASS passed${RESET}  |  ${RED}$FAIL failed${RESET}"
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"

[ $FAIL -eq 0 ] && exit 0 || exit 1
