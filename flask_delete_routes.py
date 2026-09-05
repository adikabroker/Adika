# ========== Adika DELETE routes (add to app.py) ==========
# Requires: from flask import jsonify, request
#           supabase client already initialized as `supabase`

@app.route("/api/delete-listing/<item_id>", methods=["DELETE", "POST"])
@app.route("/api/delete-listing/<int:item_id>", methods=["DELETE", "POST"])
def delete_listing(item_id):
    """Delete a marketplace row from adika_clean_market (fallback: listings).
    Auth: Telegram user id from JSON body or headers; admin 7030641737 can delete any.
    """
    try:
        body = {}
        try:
            body = request.get_json(silent=True) or {}
        except Exception:
            body = {}

        admin_ids = set([7030641737])
        # optional extra admins from env/config
        try:
            extra = app.config.get("ADMIN_IDS") or []
            for a in extra:
                admin_ids.add(int(a))
        except Exception:
            pass

        requester = (
            body.get("telegram_id")
            or body.get("user_id")
            or request.headers.get("X-Telegram-User-Id")
            or ""
        )
        requester = str(requester).strip()
        is_admin = False
        try:
            if requester and int(requester) in admin_ids:
                is_admin = True
        except Exception:
            pass

        # Resolve id (int or uuid string)
        target_id = item_id
        try:
            target_id = int(item_id)
        except Exception:
            target_id = str(item_id)

        tables_try = ["adika_clean_market", "listings", "market"]
        deleted = False
        last_error = None
        used_table = None

        for table in tables_try:
            try:
                q = supabase.table(table).delete().eq("id", target_id)
                # Non-admin: restrict to owner
                if not is_admin and requester:
                    # try common owner columns
                    # PostgREST can't OR easily in delete filter chain; fetch then check
                    sel = supabase.table(table).select("id,user_id,telegram_id,user_chat_id").eq("id", target_id).limit(1).execute()
                    rows = (sel.data or []) if sel else []
                    if not rows:
                        continue
                    row = rows[0]
                    owners = {
                        str(row.get("user_id") or ""),
                        str(row.get("telegram_id") or ""),
                        str(row.get("user_chat_id") or ""),
                    }
                    if requester not in owners and not is_admin:
                        last_error = "forbidden"
                        continue
                res = q.execute()
                # consider success if no exception
                deleted = True
                used_table = table
                break
            except Exception as e:
                last_error = str(e)
                continue

        if deleted:
            # cascade photos (best-effort)
            try:
                for col in ("listing_id", "market_id", "item_id"):
                    try:
                        supabase.table("listing_photos").delete().eq(col, target_id).execute()
                    except Exception:
                        pass
            except Exception:
                pass
            return jsonify({
                "success": True,
                "message": "Listing deleted successfully",
                "id": target_id,
                "table": used_table,
            }), 200

        if last_error == "forbidden":
            return jsonify({"success": False, "error": "forbidden"}), 403
        return jsonify({
            "success": False,
            "error": last_error or "not_found",
            "id": target_id,
        }), 404

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/delete-buyer/<item_id>", methods=["DELETE", "POST"])
def delete_buyer(item_id):
    """Delete from buyers / buyer_requests tables."""
    try:
        body = request.get_json(silent=True) or {}
        requester = str(body.get("telegram_id") or body.get("user_id") or "")
        admin_ids = {7030641737}
        is_admin = False
        try:
            if requester and int(requester) in admin_ids:
                is_admin = True
        except Exception:
            pass

        target_id = item_id
        try:
            target_id = int(item_id)
        except Exception:
            target_id = str(item_id)

        for table in ("buyers", "buyer_requests"):
            try:
                if not is_admin and requester:
                    sel = supabase.table(table).select("id,user_id,telegram_id").eq("id", target_id).limit(1).execute()
                    rows = (sel.data or []) if sel else []
                    if not rows:
                        continue
                    row = rows[0]
                    owners = {str(row.get("user_id") or ""), str(row.get("telegram_id") or "")}
                    if requester not in owners:
                        continue
                supabase.table(table).delete().eq("id", target_id).execute()
                return jsonify({"success": True, "message": "Buyer request deleted", "table": table}), 200
            except Exception:
                continue
        return jsonify({"success": False, "error": "not_found"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/delete", methods=["POST", "DELETE"])
def delete_generic():
    """Body: { id, table?, telegram_id? } — routes to market or buyers."""
    body = request.get_json(silent=True) or {}
    item_id = body.get("id") or body.get("listing_id")
    if item_id is None:
        return jsonify({"success": False, "error": "missing id"}), 400
    table = (body.get("table") or body.get("table_name") or "adika_clean_market")
    if table in ("buyers", "buyer_requests"):
        return delete_buyer(item_id)
    return delete_listing(item_id)
