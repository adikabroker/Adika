# Paste into app.py / webapp.py.
# SINGLE source of truth: table `listings`
# Related photos: table `listing_photos` (listing_id FK) — delete first, then listing.
# Do NOT read home feed from `adika_clean_market` if you delete from `listings`.

import os
from flask import jsonify, request
from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = (
    os.getenv("SUPABASE_SERVICE_KEY")
    or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    or os.getenv("SERVICE_ROLE_KEY")
)

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_KEY are required")

supabase_admin = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

LISTINGS_TABLE = "listings"
PHOTOS_TABLE = "listing_photos"


def _rows(res):
    data = getattr(res, "data", None) if res is not None else None
    return data if isinstance(data, list) else []


def _ids(item_id):
    raw = str(item_id or "").strip()
    digits = "".join(ch for ch in raw if ch.isdigit())
    out = []
    if digits:
        try:
            out.append(int(digits))
        except Exception:
            pass
        out.append(digits)
    if raw not in out:
        out.append(raw)
    return out


@app.route("/api/listings", methods=["GET"])
def get_listings():
    """Same table as DELETE."""
    try:
        limit = int(request.args.get("limit", 20))
        offset = int(request.args.get("offset", 0))
        res = (
            supabase_admin.table(LISTINGS_TABLE)
            .select("*")
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )
        return jsonify({"status": "success", "data": _rows(res)}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/items/<item_id>", methods=["DELETE"])
@app.route("/api/listings/<item_id>", methods=["DELETE"])
def delete_item(item_id):
    try:
        deleted = []
        for candidate in _ids(item_id):
            try:
                supabase_admin.table(PHOTOS_TABLE).delete().eq("listing_id", candidate).execute()
            except Exception as photo_err:
                print("PHOTO DELETE WARN:", photo_err)

            last = supabase_admin.table(LISTINGS_TABLE).delete().eq("id", candidate).execute()
            deleted = _rows(last)
            if deleted:
                break

        if deleted:
            return jsonify({
                "status": "success",
                "success": True,
                "deleted": True,
                "message": "Deleted permanently",
                "rows": deleted,
            }), 200

        return jsonify({
            "status": "error",
            "success": False,
            "deleted": False,
            "message": "በዚህ ID የተመዘገበ መረጃ ዳታቤዝ ውስጥ አልተገኘም",
        }), 404

    except Exception as e:
        print("DELETE EXCEPTION:", str(e))
        return jsonify({
            "status": "error",
            "success": False,
            "deleted": False,
            "message": str(e),
        }), 500
