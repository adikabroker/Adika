#!/usr/bin/env python3
"""
test_all_features.py — validate Adika schema alignment across
listings, ethiopia_vehicles, knowledge_base, search_alerts, favorites
plus adika_features helpers and api_service callable surfaces.
"""
from __future__ import annotations

import json
import os
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT.parent))


SCHEMA_SQL = """
CREATE TABLE listings (
    id INTEGER PRIMARY KEY,
    user_chat_id INTEGER,
    user_name TEXT,
    req_type TEXT,
    main_category TEXT,
    sub_category TEXT,
    action_type TEXT,
    property_type TEXT,
    description TEXT,
    price TEXT,
    phone TEXT,
    created_at TEXT,
    extra_data TEXT,
    photos TEXT,
    status TEXT
);
CREATE TABLE ethiopia_vehicles (
    id INTEGER PRIMARY KEY,
    model_key TEXT UNIQUE,
    name TEXT,
    full_model TEXT,
    brand TEXT,
    category TEXT,
    current_price_range_etb TEXT,
    core_advantage TEXT,
    bank_collateral_appeal TEXT,
    fuel_economy TEXT,
    ground_clearance TEXT,
    primary_use_case TEXT,
    spare_parts_availability TEXT,
    resale_liquidity TEXT
);
CREATE TABLE knowledge_base (
    id INTEGER PRIMARY KEY,
    category TEXT,
    topic TEXT,
    keywords TEXT,
    title TEXT,
    content TEXT
);
CREATE TABLE search_alerts (
    id INTEGER PRIMARY KEY,
    user_chat_id INTEGER,
    chat_id INTEGER,
    category TEXT,
    max_price TEXT,
    model_hint TEXT,
    created_at TEXT
);
CREATE TABLE favorites (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    chat_id INTEGER,
    listing_id INTEGER,
    created_at TEXT
);
CREATE TABLE user_preferences (
    user_id INTEGER PRIMARY KEY,
    categories TEXT DEFAULT '[]',
    budget_min INTEGER DEFAULT 0,
    budget_max INTEGER DEFAULT 999999999,
    onboarding_done INTEGER DEFAULT 0,
    updated_at TEXT
);
CREATE TABLE brokers (
    id INTEGER PRIMARY KEY,
    chat_id INTEGER,
    user_chat_id INTEGER,
    telegram_id INTEGER,
    full_name TEXT,
    phone TEXT,
    status TEXT,
    categories TEXT,
    telegram_username TEXT
);
CREATE TABLE otp_codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER NOT NULL,
    code_hash TEXT NOT NULL,
    purpose TEXT DEFAULT 'verify',
    expires_at TEXT NOT NULL,
    used INTEGER DEFAULT 0,
    created_at TEXT
);
"""


class FakeCursor:
    def __init__(self, conn):
        self._conn = conn
        self._cur = conn.cursor()
        self.lastrowid = None

    def execute(self, sql, params=None):
        self._cur.execute(sql, params or ())
        self.lastrowid = self._cur.lastrowid
        return self

    def fetchone(self):
        row = self._cur.fetchone()
        return dict(row) if row is not None else None

    def fetchall(self):
        return [dict(r) for r in self._cur.fetchall()]


class FakeConn:
    def __init__(self, raw):
        self._raw = raw

    def cursor(self):
        return FakeCursor(self._raw)

    def commit(self):
        self._raw.commit()

    def close(self):
        pass


def install_fake_models(db_path):
    import types

    raw = sqlite3.connect(db_path)
    raw.row_factory = sqlite3.Row
    raw.executescript(SCHEMA_SQL)
    raw.commit()

    def get_db_connection():
        c = sqlite3.connect(db_path)
        c.row_factory = sqlite3.Row
        return FakeConn(c)

    models = types.ModuleType("models")
    models.get_db_connection = get_db_connection
    models.get_placeholder = lambda: "?"
    models.is_postgres = lambda: False
    models.add_listing = lambda *a, **k: None
    models.ensure_core_tables = lambda: None
    models.ensure_listings_columns = lambda: None
    models.LAST_DB_ERROR = ""
    sys.modules["models"] = models

    config = types.ModuleType("config")
    config.logger = __import__("logging").getLogger("test")
    config.OPENROUTER_API_KEY = ""
    config.WEBAPP_URL = ""
    sys.modules.setdefault("config", config)
    return raw


class SchemaAndHelpersTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False)
        cls.tmp.close()
        cls.raw = install_fake_models(cls.tmp.name)
        import adika_features as af
        cls.af = af
        cls.raw.executescript(
            """
            INSERT INTO listings (id, user_chat_id, user_name, req_type, main_category, sub_category,
                action_type, property_type, description, price, phone, extra_data, photos, status)
            VALUES
            (1, 111, 'Abebe', 'SELL', 'መኪና', 'Vitz', 'sell', '', 'Toyota Vitz', '2500000', '0911000000',
             '{"brand":"Toyota","model":"Vitz"}', '[]', 'active'),
            (2, 111, 'Abebe', 'SELL', 'መኪና', 'Prado', 'sell', '', 'Land Cruiser Prado', '5800000', '0911000000',
             '{"brand":"Toyota","model":"Prado"}', '[]', 'active'),
            (3, 222, 'Sara', 'SELL', 'ቤት', 'Apartment', 'sell', 'apartment', 'Bole 2BR', '4000000', '0911222333',
             '{"title":"Bole Apt"}', '[]', 'active');
            INSERT INTO ethiopia_vehicles (id, model_key, name, full_model, brand, category, current_price_range_etb)
            VALUES (1, 'byd seagull', 'BYD Seagull EV', 'Seagull', 'BYD', 'EV', '2,800,000 - 4,200,000 ETB');
            INSERT INTO knowledge_base (id, category, topic, keywords, title, content)
            VALUES (1, 'መኪና', 'duty', '["ቀረጥ","duty"]', 'የጉምሩክ ቀረጥ', 'EV duty is 5%');
            INSERT INTO search_alerts (id, user_chat_id, chat_id, category, max_price, model_hint)
            VALUES (1, 7030641737, 7030641737, 'መኪና', '4000000', 'vitz');
            """
        )
        cls.raw.commit()

    def test_listings_columns(self):
        cols = {r[1] for r in self.raw.execute("PRAGMA table_info(listings)")}
        for c in ("user_chat_id", "main_category", "extra_data", "photos", "price", "status"):
            self.assertIn(c, cols)

    def test_ethiopia_vehicles_model_key(self):
        row = self.af.query_ethiopia_vehicle("byd seagull")
        self.assertIsNotNone(row)
        self.assertEqual(row["full_model"], "Seagull")

    def test_knowledge_base(self):
        rows = self.af.query_knowledge_base("ቀረጥ")
        self.assertTrue(rows)
        self.assertIn("duty", rows[0]["title"].lower() + rows[0]["topic"])

    def test_toggle_favorite_and_subscribers(self):
        r = self.af.toggle_favorite(7030641737, 1, chat_id=7030641737, action="add")
        self.assertTrue(r["favorited"])
        subs = self.af.get_favorite_subscribers(1)
        self.assertEqual(len(subs), 1)
        self.assertEqual(subs[0]["chat_id"], 7030641737)
        r2 = self.af.toggle_favorite(7030641737, 1, chat_id=7030641737, action="remove")
        self.assertFalse(r2["favorited"])

    def test_update_listing_price(self):
        ok, old, title, cat = self.af.update_listing_price(1, "2300000")
        self.assertTrue(ok)
        self.assertEqual(str(old), "2500000")
        self.assertEqual(cat, "መኪና")
        self.assertTrue(title)

    def test_matching_alerts_respects_max_price(self):
        hits = self.af.get_matching_alerts("መኪና", "2500000", model_hint="vitz")
        self.assertTrue(hits)
        miss = self.af.get_matching_alerts("መኪና", "5800000", model_hint="vitz")
        self.assertFalse(miss)

    def test_preferences_and_score(self):
        self.assertTrue(self.af.save_user_preferences(7030641737, ["መኪና"], 1500000, 4000000))
        prefs = self.af.get_user_preferences(7030641737)
        self.assertEqual(prefs["budget_max"], 4000000)
        cheap = {"main_category": "መኪና", "price": "2500000"}
        dear = {"main_category": "መኪና", "price": "5800000"}
        self.assertGreater(self.af.score_listing_for_user(cheap, prefs), self.af.score_listing_for_user(dear, prefs))

    def test_otp(self):
        code = self.af.create_telegram_otp(7030641737, "verify")
        self.assertEqual(len(code), 6)
        self.assertTrue(self.af.verify_telegram_otp(7030641737, code, "verify"))

    def test_parse_price_text_column(self):
        self.assertEqual(self.af._parse_price("4,000,000 ETB"), 4000000.0)
        self.assertEqual(self.af._parse_price("2500000"), 2500000.0)

    def test_api_service_binds_helpers(self):
        import api_service as api
        self.assertTrue(callable(getattr(api, "toggle_favorite", None)))
        self.assertTrue(callable(getattr(api, "update_listing_price", None)))
        self.assertTrue(callable(getattr(api, "get_favorite_subscribers", None)))
        self.assertTrue(callable(getattr(api, "get_matching_alerts", None)))
        self.assertTrue(callable(getattr(api, "sanitize_and_route_url", None)))
        self.assertTrue(callable(getattr(api, "decode_qr_from_bytes", None)))
        url = api.sanitize_and_route_url("https://dead.addiscadaster.gov.et/verify/aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")
        self.assertIn("addislandfarm.gov.et", url)

    def test_advisor_fallback_vehicle_map(self):
        import api_service as api
        db = getattr(api, "ETHIOPIA_VEHICLES_DATABASE", {}) or {}
        self.assertIn("byd seagull", {k.lower() for k in db.keys()} | set(db.keys()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
