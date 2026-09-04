# Paste this into app.py (or webapp.py) and reuse your existing `app` + `supabase` clients.
# Requires: service-role or a policy that allows DELETE on listings.

from flask import jsonify

@app.route("/api/items/<item_id>", methods=["DELETE"])
@app.route("/api/listings/<item_id>", methods=["DELETE"])
def delete_item(item_id):
    try:
        raw = str(item_id or "").strip()
        digits = "".join(ch for ch in raw if ch.isdigit())
        candidates = []
        if digits:
            try:
                candidates.append(int(digits))
            except Exception:
                pass
            candidates.append(digits)
        candidates.append(raw)
        seen = set()
        last_data = []
        for cid in candidates:
            key = (type(cid).__name__, str(cid))
            if key in seen:
                continue
            seen.add(key)
            response = supabase.table("listings").delete().eq("id", cid).execute()
            last_data = getattr(response, "data", None) or []
            if last_data:
                return jsonify({
                    "status": "success",
                    "success": True,
                    "deleted": True,
                    "message": "Record permanently deleted",
                    "rows": last_data,
                }), 200

        # Soft-delete fallback if hard delete matched 0 rows (optional column)
        try:
            supabase.table("listings").update({"status": "deleted", "is_deleted": True}).eq("id", raw).execute()
        except Exception:
            pass

        return jsonify({
            "status": "error",
            "success": False,
            "deleted": False,
            "message": "No matching listing row was deleted",
        }), 404
    except Exception as e:
        print("PERMANENT DELETE ERROR:", str(e))
        return jsonify({"status": "error", "success": False, "message": str(e)}), 500
