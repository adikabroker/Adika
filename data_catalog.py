# ==============================================================================
# data_catalog.py — Ethiopian Automotive, Banking & Real Estate Ground-Truth
# ==============================================================================
import re
from typing import Dict, Any, Optional, List

# ------------------------------------------------------------------------------
# 1. ETHIOPIA_VEHICLES_DATABASE (Admin Verified Baseline Specifications & Prices)
# ------------------------------------------------------------------------------
ETHIOPIA_VEHICLES_DATABASE: Dict[str, Dict[str, Any]] = {
    # --- BYD Electric & Hybrid Models ---
    "byd seagull": {
        "name": "BYD Seagull EV (2023 - 2025)",
        "full_model": "BYD Seagull",
        "brand": "BYD",
        "category": "Compact Electric Hatchback",
        "current_price_range_etb": "2,800,000 - 4,200,000 ETB",
        "core_advantage": "በጣም አነስተኛ የመነሻ ዋጋ፣ ዜሮ የነዳጅ ወጪ፣ የ5% ዝቅተኛ ጉምሩክ ቀረጥ እና ዘመናዊ ገጽታ",
        "bank_collateral_appeal": "ጥሩ የባንክ ዋስትና ተቀባይነት (Green Financing)",
        "fuel_economy": "305 - 405 KM በአንድ ሙሉ ቻርጅ (~80-120 ብር የኤሌክትሪክ ወጪ)",
        "ground_clearance": "150 mm",
        "primary_use_case": "ለከተማ ውስጥ አነስተኛ ወጪ ጉዞ እና ለግል/ቤተሰብ አገልግሎት",
        "spare_parts_availability": "3.8/5 — በአዲስ አበባ የኤሌክትሪክ መኪና ጋራዦች በስፋት እየተስፋፋ",
        "resale_liquidity": "በከተማ ወጣቶችና ባለሙያዎች ዘንድ እጅግ ተወዳጅና ፈጣን ሽያጭ"
    },
    "byd dolphin": {
        "name": "BYD Dolphin EV (2023 - 2025)",
        "full_model": "BYD Dolphin",
        "brand": "BYD",
        "category": "Compact Electric Hatchback",
        "current_price_range_etb": "3,500,000 - 5,200,000 ETB",
        "core_advantage": "ሰፊ የውስጥ ክፍል፣ የላቀ የባትሪ ደህንነት (Blade Battery) እና ረጅም የጉዞ ርቀት",
        "bank_collateral_appeal": "ከፍተኛ የባንክ ብድር ዋስትና ተቀባይነት",
        "fuel_economy": "405 - 420 KM በአንድ ሙሉ ቻርጅ",
        "ground_clearance": "145 mm",
        "primary_use_case": "ለከተማ መጓጓዣ እና ለቤተሰብ ምቹ ጉዞ",
        "spare_parts_availability": "4/5 — በአዲስ አበባ የሚገኝ",
        "resale_liquidity": "እጅግ ፈጣን የገበያ ዝውውር"
    },
    "byd song plus": {
        "name": "BYD Song Plus (EV / DM-i Hybrid 2022 - 2025)",
        "full_model": "BYD Song Plus",
        "brand": "BYD",
        "category": "Mid-Size Electric / Hybrid SUV",
        "current_price_range_etb": "5,500,000 - 8,500,000 ETB",
        "core_advantage": "ፕሪሚየም የውስጥ ምቾት፣ የላቀ የኤሌክትሪክ/ሀይብሪድ ቴክኖሎጂ እና ረጅም የጉዞ ርቀት",
        "bank_collateral_appeal": "ከፍተኛ የባንክ ዋስትና ተቀባይነት",
        "fuel_economy": "EV 505 KM / DM-i Hybrid 1000+ KM Comprehensive Range",
        "ground_clearance": "170 mm",
        "primary_use_case": "ለቤተሰብ ምቾት፣ ለከተማና ለክልል የረጅም ጉዞ",
        "spare_parts_availability": "4.2/5 — በአዲስ አበባ በስፋት የሚገኝ",
        "resale_liquidity": "ከፍተኛ ተፈላጊነት ያለው"
    },
    "byd yuan plus": {
        "name": "BYD Yuan Plus / Atto 3 (2023 - 2025)",
        "full_model": "BYD Yuan Plus (Atto 3)",
        "brand": "BYD",
        "category": "Compact Electric Crossover SUV",
        "current_price_range_etb": "4,800,000 - 7,200,000 ETB",
        "core_advantage": "ዘመናዊ ዲዛይን፣ ጠንካራ ሞተር እና 5-ኮከብ የደህንነት ደረጃ",
        "bank_collateral_appeal": "ከፍተኛ የባንክ ዋስትና",
        "fuel_economy": "430 - 510 KM በአንድ ሙሉ ቻርጅ",
        "ground_clearance": "175 mm",
        "primary_use_case": "ለከተማና ለሀገር አቋራጭ ምቹ ጉዞ",
        "spare_parts_availability": "4/5",
        "resale_liquidity": "በጣም ተፈላጊ"
    },
    "byd han": {
        "name": "BYD Han EV (Flagship Luxury Sedan)",
        "full_model": "BYD Han",
        "brand": "BYD",
        "category": "Executive Luxury Electric Sedan",
        "current_price_range_etb": "7,500,000 - 11,500,000 ETB",
        "core_advantage": "የላቀ የቅንጦት ደረጃ፣ ከፍተኛ ፍጥነት እና ፕሪሚየም ቴክኖሎጂ",
        "bank_collateral_appeal": "ፕሪሚየም የባንክ ዋስትና",
        "fuel_economy": "505 - 605 KM Range",
        "ground_clearance": "140 mm",
        "primary_use_case": "ለከፍተኛ የንግድና የድርጅት ኃላፊዎች አገልግሎት",
        "spare_parts_availability": "3.5/5",
        "resale_liquidity": "መካከለኛ/ከፍተኛ"
    },
    "byd tang": {
        "name": "BYD Tang EV (7-Seat Luxury SUV)",
        "full_model": "BYD Tang",
        "brand": "BYD",
        "category": "7-Seat Luxury Electric SUV",
        "current_price_range_etb": "8,000,000 - 12,500,000 ETB",
        "core_advantage": "ባለ 7 ወንበር ሰፊ የቤተሰብ መኪና፣ ባለ 4 ጎማ ተሽከርካሪ (AWD)",
        "bank_collateral_appeal": "ከፍተኛ ዋጋ ያለው የባንክ ዋስትና",
        "fuel_economy": "505 - 565 KM Range",
        "ground_clearance": "180 mm",
        "primary_use_case": "ለትልቅ ቤተሰብ እና ለረጅም የጉዞ ምቾት",
        "spare_parts_availability": "3.5/5",
        "resale_liquidity": "ከፍተኛ"
    },
    "byd qin plus": {
        "name": "BYD Qin Plus (EV / DM-i Sedan)",
        "full_model": "BYD Qin Plus",
        "brand": "BYD",
        "category": "Compact Electric / Hybrid Sedan",
        "current_price_range_etb": "3,800,000 - 5,600,000 ETB",
        "core_advantage": "ውብ የሴዳን ቅርጽ፣ የላቀ ኢኮኖሚ እና ምቹ የከተማ አያያዝ",
        "bank_collateral_appeal": "ጥሩ የባንክ ዋስትና",
        "fuel_economy": "420 - 510 KM (EV) / 1000+ KM (DM-i)",
        "ground_clearance": "145 mm",
        "primary_use_case": "ለከተማ መጓጓዣ እና ለቤተሰብ",
        "spare_parts_availability": "3.8/5",
        "resale_liquidity": "ፈጣን"
    },
    "byd e2": {
        "name": "BYD e2 EV (Compact Hatchback)",
        "full_model": "BYD e2",
        "brand": "BYD",
        "category": "Compact Electric Hatchback",
        "current_price_range_etb": "3,200,000 - 4,600,000 ETB",
        "core_advantage": "ቀላልና ቆጣቢ የከተማ መጓጓዣ",
        "bank_collateral_appeal": "ጥሩ የባንክ ዋስትና",
        "fuel_economy": "305 - 405 KM Range",
        "ground_clearance": "150 mm",
        "primary_use_case": "ለከተማ እንቅስቃሴና ለቢሮ ሰራተኞች",
        "spare_parts_availability": "3.6/5",
        "resale_liquidity": "ፈጣን"
    },

    # --- TOYOTA Lineup ---
    "toyota vitz": {
        "name": "Toyota Vitz (2000 - 2020 Models)",
        "full_model": "Toyota Vitz",
        "brand": "Toyota",
        "category": "Subcompact Hatchback",
        "current_price_range_etb": "1,400,000 - 2,800,000 ETB",
        "core_advantage": "በኢትዮጵያ በብዛት የሚገኝ መለዋወጫ፣ ዝቅተኛ የጥገና ወጪ እና ፈጣን ዳግም ሽያጭ",
        "bank_collateral_appeal": "እጅግ ከፍተኛ የገበያ ተቀባይነትና ዋስትና",
        "fuel_economy": "14 - 18 KM/L (1.0L / 1.3L Engine)",
        "ground_clearance": "140 - 145 mm",
        "primary_use_case": "ለከተማ ውስጥ እንቅስቃሴ፣ ለጀማሪ አሽከርካሪዎች እና ለኪራይ/ራይድ",
        "spare_parts_availability": "5/5 — በማንኛውም የኢትዮጵያ ከተማ በቀላሉ የሚገኝ",
        "resale_liquidity": "በጣም ፈጣን (በሰዓታት ውስጥ የሚሸጥ)"
    },
    "toyota yaris": {
        "name": "Toyota Yaris (Sedan / Hatchback 2006 - 2022)",
        "full_model": "Toyota Yaris",
        "brand": "Toyota",
        "category": "Subcompact Sedan / Hatchback",
        "current_price_range_etb": "1,600,000 - 3,400,000 ETB",
        "core_advantage": "አስተማማኝ የቶዮታ ሞተር፣ ዘላቂነት እና የነዳጅ ቁጠባ",
        "bank_collateral_appeal": "እጅግ ከፍተኛ የባንክ ዋስትና",
        "fuel_economy": "15 - 19 KM/L",
        "ground_clearance": "145 mm",
        "primary_use_case": "ለቤተሰብ እና ለዕለታዊ የስራ ጉዞ",
        "spare_parts_availability": "5/5 — የተትረፈረፈ መለዋወጫ",
        "resale_liquidity": "እጅግ ፈጣን"
    },
    "toyota belta": {
        "name": "Toyota Belta (2006 - 2012)",
        "full_model": "Toyota Belta",
        "brand": "Toyota",
        "category": "Compact Sedan",
        "current_price_range_etb": "1,650,000 - 2,600,000 ETB",
        "core_advantage": "ሰፊ የሻንጣ መያዣ ቦክስ፣ አነስተኛ የነዳጅ ወጪ እና ቀላል ጥገና",
        "bank_collateral_appeal": "ከፍተኛ የባንክ ዋስትና",
        "fuel_economy": "16 - 20 KM/L (1.0L / 1.3L)",
        "ground_clearance": "145 mm",
        "primary_use_case": "ለቤተሰብና ለከተማ መጓጓዣ",
        "spare_parts_availability": "4.8/5",
        "resale_liquidity": "ፈጣን"
    },
    "toyota ist": {
        "name": "Toyota IST (2002 - 2014)",
        "full_model": "Toyota IST",
        "brand": "Toyota",
        "category": "Compact Crossover Hatchback",
        "current_price_range_etb": "1,550,000 - 2,500,000 ETB",
        "core_advantage": "ጥንካሬ፣ ወጣ ያለ ውበት እና አስተማማኝ አፈጻጸም",
        "bank_collateral_appeal": "ከፍተኛ የባንክ ተቀባይነት",
        "fuel_economy": "13 - 16 KM/L (1.3L / 1.5L)",
        "ground_clearance": "155 mm",
        "primary_use_case": "ለግል እና ለከተማ ጉዞ",
        "spare_parts_availability": "4.8/5",
        "resale_liquidity": "በጣም ፈጣን"
    },
    "toyota corolla": {
        "name": "Toyota Corolla (Executive / NZE / 1.8 Sedan)",
        "full_model": "Toyota Corolla",
        "brand": "Toyota",
        "category": "Compact / Mid-Size Sedan",
        "current_price_range_etb": "2,200,000 - 6,500,000 ETB",
        "core_advantage": "የኢትዮጵያ ገበያ መሪ፣ የማይበላሽ ጥንካሬ እና ቋሚ የዋጋ ጭማሪ",
        "bank_collateral_appeal": "ፕሪሚየም የባንክ ዋስትና ተቀባይነት (Tier 1 Asset)",
        "fuel_economy": "13 - 17 KM/L",
        "ground_clearance": "150 mm",
        "primary_use_case": "ለቤተሰብ ክብር፣ ለቢሮ እና ለንግድ ስራ",
        "spare_parts_availability": "5/5 — በየትኛውም የኢትዮጵያ ጋራዥ የሚጠገን",
        "resale_liquidity": "ፈጣን ሽያጭ"
    },
    "toyota corolla cross": {
        "name": "Toyota Corolla Cross (Hybrid / Gasoline 2021 - 2025)",
        "full_model": "Toyota Corolla Cross",
        "brand": "Toyota",
        "category": "Compact Crossover SUV",
        "current_price_range_etb": "6,500,000 - 9,500,000 ETB",
        "core_advantage": "ከፍተኛ የመሬት ከፍታ፣ የላቀ የሃይብሪድ ነዳጅ ቁጠባ እና ምቾት",
        "bank_collateral_appeal": "ከፍተኛ የባንክ ብድር ዋስትና",
        "fuel_economy": "18 - 23 KM/L (Hybrid)",
        "ground_clearance": "161 mm",
        "primary_use_case": "ለቤተሰብ ምቾት እና ለረጅም የከተማና የክልል ጉዞ",
        "spare_parts_availability": "4.2/5",
        "resale_liquidity": "በጣም ከፍተኛ"
    },
    "toyota rav4": {
        "name": "Toyota RAV4 (Gasoline / Hybrid 2016 - 2024)",
        "full_model": "Toyota RAV4",
        "brand": "Toyota",
        "category": "Compact / Mid-Size SUV",
        "current_price_range_etb": "4,800,000 - 11,500,000 ETB",
        "core_advantage": "ሁለገብ የ4-ጎማ ጉልበት (AWD)፣ ከፍተኛ የመሬት ከፍታ እና የረጅም ጊዜ ጥንካሬ",
        "bank_collateral_appeal": "ከፍተኛ የባንክ ዋስትና ተቀባይነት",
        "fuel_economy": "12 - 17 KM/L (Gasoline) / 18-22 KM/L (Hybrid)",
        "ground_clearance": "190 - 210 mm",
        "primary_use_case": "ለቤተሰብ ምቾት፣ ለከተማና ለገጠር መንገዶች",
        "spare_parts_availability": "4.8/5",
        "resale_liquidity": "እጅግ ከፍተኛ"
    },
    "toyota hilux": {
        "name": "Toyota Hilux (Single / Double Cab / Revo)",
        "full_model": "Toyota Hilux",
        "brand": "Toyota",
        "category": "Rugged Commercial / Passenger Pickup",
        "current_price_range_etb": "5,200,000 - 14,500,000 ETB",
        "core_advantage": "የማይበገር ጥንካሬ፣ ከፍተኛ የመጫን አቅም እና ለየትኛውም አስቸጋሪ መንገድ ተስማሚነት",
        "bank_collateral_appeal": "እጅግ ከፍተኛ የባንክ ዋስትና",
        "fuel_economy": "9 - 13 KM/L (2.4L / 2.8L / 3.0L Turbo Diesel)",
        "ground_clearance": "215 - 286 mm",
        "primary_use_case": "ለኮንስትራክሽን፣ ለንግድ፣ ለግብርና እና ለፕሮጀክት ስራ",
        "spare_parts_availability": "5/5 — በስፋት የሚገኝ",
        "resale_liquidity": "እጅግ ፈጣን ሽያጭ"
    },
    "toyota land cruiser prado": {
        "name": "Toyota Land Cruiser Prado (TX / VX / VXL)",
        "full_model": "Toyota Land Cruiser Prado",
        "brand": "Toyota",
        "category": "Premium Mid-Size 4WD SUV",
        "current_price_range_etb": "8,000,000 - 22,000,000 ETB",
        "core_advantage": "የላቀ ማዕረግ፣ አስደናቂ ጥንካሬ፣ ለኢትዮጵያ መንገዶች ፍጹም ተስማሚነት",
        "bank_collateral_appeal": "ፕሪሚየም የባንክ ዋስትና (Tier 1 Prime Collateral)",
        "fuel_economy": "8 - 11 KM/L (2.7L Petrol / 2.8L/3.0L Diesel)",
        "ground_clearance": "215 - 220 mm",
        "primary_use_case": "ለከፍተኛ ባለስልጣናት፣ ለድርጅቶች እና ለቤተሰብ የቅንጦት ጉዞ",
        "spare_parts_availability": "4.8/5",
        "resale_liquidity": "እጅግ ፈጣን"
    },
    "toyota land cruiser 70": {
        "name": "Toyota Land Cruiser 70 (Hardtop / Troop Carrier / Pickup)",
        "full_model": "Toyota Land Cruiser 70 Series (Hardtop)",
        "brand": "Toyota",
        "category": "Heavy-Duty Off-Road 4x4",
        "current_price_range_etb": "9,500,000 - 18,500,000 ETB",
        "core_advantage": "የማይበገር ወታደራዊና የመስክ ጥንካሬ፣ 1HZ/1VD አስተማማኝ ሞተር",
        "bank_collateral_appeal": "እጅግ ከፍተኛ የባንክ ዋስትና",
        "fuel_economy": "7 - 10 KM/L (4.2L 6-Cylinder Diesel)",
        "ground_clearance": "235 mm",
        "primary_use_case": "ለክልል፣ ለማዕድን፣ ለግብርና፣ ለቱሪዝም እና ለአስቸጋሪ መንገዶች",
        "spare_parts_availability": "4.8/5",
        "resale_liquidity": "በጣም ከፍተኛ"
    },
    "toyota land cruiser 200": {
        "name": "Toyota Land Cruiser 200 (V8 Luxury SUV)",
        "full_model": "Toyota Land Cruiser 200 Series (V8)",
        "brand": "Toyota",
        "category": "Full-Size Luxury 4WD SUV",
        "current_price_range_etb": "14,000,000 - 28,000,000 ETB",
        "core_advantage": "የ V8 ሞተር ሃይል፣ ከፍተኛ ክብርና ምቾት፣ የማይበገር ጥንካሬ",
        "bank_collateral_appeal": "ፕሪሚየም የባንክ ዋስትና",
        "fuel_economy": "6 - 9 KM/L (V8 4.5L Twin Turbo Diesel / 4.6L Petrol)",
        "ground_clearance": "225 - 230 mm",
        "primary_use_case": "ለቪአይፒ (VIP) እና ለከፍተኛ አመራሮች አገልግሎት",
        "spare_parts_availability": "4.5/5",
        "resale_liquidity": "ከፍተኛ"
    },
    "toyota land cruiser 300": {
        "name": "Toyota Land Cruiser 300 (LC300 2022 - 2025)",
        "full_model": "Toyota Land Cruiser 300 Series",
        "brand": "Toyota",
        "category": "Ultra-Luxury Flagship SUV",
        "current_price_range_etb": "26,000,000 - 48,000,000 ETB",
        "core_advantage": "የአዲሱ ትውልድ ቴክኖሎጂ፣ Twin-Turbo ሞተር፣ ወደር የለሽ ክብርና ምቾት",
        "bank_collateral_appeal": "ልዕለ-ፕሪሚየም ዋስትና",
        "fuel_economy": "8 - 11 KM/L (3.3L V6 Twin-Turbo Diesel / 3.5L Petrol)",
        "ground_clearance": "235 mm",
        "primary_use_case": "ለከፍተኛ ባለሀብቶች፣ ኤምባሲዎችና ድርጅቶች",
        "spare_parts_availability": "4/5",
        "resale_liquidity": "ከፍተኛ"
    },
    "toyota fortuner": {
        "name": "Toyota Fortuner (2016 - 2024)",
        "full_model": "Toyota Fortuner",
        "brand": "Toyota",
        "category": "7-Seat Mid-Size 4WD SUV",
        "current_price_range_etb": "7,500,000 - 15,000,000 ETB",
        "core_advantage": "ባለ 7 ወንበር ሰፊ የቤተሰብ SUV፣ በ Hilux ቻሲ ላይ የተገነባ ጥንካሬ",
        "bank_collateral_appeal": "ከፍተኛ የባንክ ዋስትና",
        "fuel_economy": "9 - 12 KM/L",
        "ground_clearance": "220 mm",
        "primary_use_case": "ለቤተሰብ ምቾት እና ለረጅም ጉዞ",
        "spare_parts_availability": "4.8/5",
        "resale_liquidity": "በጣም ከፍተኛ"
    },
    "toyota 4runner": {
        "name": "Toyota 4Runner (TRD / SR5 / Limited)",
        "full_model": "Toyota 4Runner",
        "brand": "Toyota",
        "category": "Mid-Size Rugged SUV",
        "current_price_range_etb": "8,500,000 - 17,000,000 ETB",
        "core_advantage": "የ 4.0L V6 ሞተር ጥንካሬ፣ አስደናቂ የመስክ ብቃት",
        "bank_collateral_appeal": "ከፍተኛ የባንክ ዋስትና",
        "fuel_economy": "7 - 10 KM/L",
        "ground_clearance": "240 mm",
        "primary_use_case": "ለአስቸጋሪ መንገዶች እና ለቅንጦት ጉዞ",
        "spare_parts_availability": "4.5/5",
        "resale_liquidity": "ጠንካራ"
    },
    "toyota hiace": {
        "name": "Toyota HiAce (High Roof / Commuter / Minivan)",
        "full_model": "Toyota HiAce",
        "brand": "Toyota",
        "category": "Commercial Passenger / Cargo Van",
        "current_price_range_etb": "4,500,000 - 10,500,000 ETB",
        "core_advantage": "በጣም አስተማማኝ የህዝብና የሰራተኞች ትራንስፖርት ንግድ መኪና",
        "bank_collateral_appeal": "ከፍተኛ የንግድ ባንክ ብድር ተቀባይነት",
        "fuel_economy": "10 - 13 KM/L (Diesel)",
        "ground_clearance": "165 mm",
        "primary_use_case": "ለትራንስፖርት ንግድ፣ ለሆቴሎችና ለድርጅቶች",
        "spare_parts_availability": "5/5",
        "resale_liquidity": "እጅግ ፈጣን"
    },
    "toyota noah": {
        "name": "Toyota Noah (7-8 Seat Minivan)",
        "full_model": "Toyota Noah",
        "brand": "Toyota",
        "category": "Compact Family / Passenger Minivan",
        "current_price_range_etb": "2,800,000 - 5,500,000 ETB",
        "core_advantage": "ባለ 8 ወንበር ሰፊ ምቾት፣ ለከተማና ለክልል ተጓዥ ተመራጭ",
        "bank_collateral_appeal": "ከፍተኛ የባንክ ዋስትና",
        "fuel_economy": "12 - 15 KM/L",
        "ground_clearance": "160 mm",
        "primary_use_case": "ለትልቅ ቤተሰብ እና ለከተማ ትራንስፖርት",
        "spare_parts_availability": "4.7/5",
        "resale_liquidity": "ፈጣን"
    },
    "toyota voxy": {
        "name": "Toyota Voxy (7-8 Seat Minivan)",
        "full_model": "Toyota Voxy",
        "brand": "Toyota",
        "category": "Compact Family Minivan",
        "current_price_range_etb": "3,000,000 - 5,800,000 ETB",
        "core_advantage": "ዘመናዊ ስፖርቲ ገጽታ፣ ሰፊ ምቾት እና ጥሩ የነዳጅ ቁጠባ",
        "bank_collateral_appeal": "ከፍተኛ የባንክ ዋስትና",
        "fuel_economy": "12 - 15 KM/L",
        "ground_clearance": "160 mm",
        "primary_use_case": "ለቤተሰብ እና ለትራንስፖርት",
        "spare_parts_availability": "4.7/5",
        "resale_liquidity": "ፈጣን"
    },
    "toyota rush": {
        "name": "Toyota Rush (7-Seat Mini SUV)",
        "full_model": "Toyota Rush",
        "brand": "Toyota",
        "category": "Compact 7-Seat SUV",
        "current_price_range_etb": "3,800,000 - 6,200,000 ETB",
        "core_advantage": "ባለ 7 ወንበር፣ 220 ሚሜ ከፍተኛ የመሬት ከፍታ እና 1.5L ቆጣቢ ሞተር",
        "bank_collateral_appeal": "ከፍተኛ የባንክ ዋስትና",
        "fuel_economy": "13 - 16 KM/L",
        "ground_clearance": "220 mm",
        "primary_use_case": "ለቤተሰብና ለአዲስ አበባ ያልተስተካከሉ መንገዶች",
        "spare_parts_availability": "4.6/5",
        "resale_liquidity": "ፈጣን"
    },
    "toyota urban cruiser": {
        "name": "Toyota Urban Cruiser (Compact SUV)",
        "full_model": "Toyota Urban Cruiser",
        "brand": "Toyota",
        "category": "Compact Crossover SUV",
        "current_price_range_etb": "3,600,000 - 5,800,000 ETB",
        "core_advantage": "ዘመናዊ ገጽታ፣ አነስተኛ የነዳጅ ወጪ እና ከፍተኛ ምቾት",
        "bank_collateral_appeal": "ከፍተኛ የባንክ ዋስትና",
        "fuel_economy": "15 - 19 KM/L",
        "ground_clearance": "180 mm",
        "primary_use_case": "ለከተማ መጓጓዣ እና ለቤተሰብ",
        "spare_parts_availability": "4.6/5",
        "resale_liquidity": "ፈጣን"
    },
    "toyota axio": {
        "name": "Toyota Corolla Axio (2007 - 2020)",
        "full_model": "Toyota Corolla Axio",
        "brand": "Toyota",
        "category": "Compact Sedan",
        "current_price_range_etb": "2,400,000 - 3,900,000 ETB",
        "core_advantage": "ቆጣቢ 1.5L ሞተር፣ ምቹ የሴዳን አያያዝ እና ዘላቂ ጥንካሬ",
        "bank_collateral_appeal": "ከፍተኛ የባንክ ዋስትና",
        "fuel_economy": "15 - 19 KM/L (Hybrid 22-26 KM/L)",
        "ground_clearance": "150 mm",
        "primary_use_case": "ለዕለታዊ መጓጓዣ፣ ለቤተሰብ እና ለራይድ",
        "spare_parts_availability": "4.8/5",
        "resale_liquidity": "በጣም ፈጣን"
    },
    "toyota premio": {
        "name": "Toyota Premio (2002 - 2018)",
        "full_model": "Toyota Premio",
        "brand": "Toyota",
        "category": "Mid-Size Sedan",
        "current_price_range_etb": "2,600,000 - 4,500,000 ETB",
        "core_advantage": "የውስጥ የቅንጦት ገጽታ (የእንጨት ማስዋቢያ) እና ለስላሳ የማሽከርከር ምቾት",
        "bank_collateral_appeal": "ከፍተኛ የባንክ ዋስትና",
        "fuel_economy": "13 - 16 KM/L (1.5L / 1.8L / 2.0L)",
        "ground_clearance": "150 mm",
        "primary_use_case": "ለክብር፣ ለቤተሰብ እና ለቢሮ እንቅስቃሴ",
        "spare_parts_availability": "4.8/5",
        "resale_liquidity": "በጣም ፈጣን"
    },
    "toyota probox": {
        "name": "Toyota Probox (Commercial Van)",
        "full_model": "Toyota Probox",
        "brand": "Toyota",
        "category": "Commercial Station Wagon / Van",
        "current_price_range_etb": "1,450,000 - 2,400,000 ETB",
        "core_advantage": "እጅግ ሰፊ የመጫን አቅም፣ ጥንካሬ እና ቆጣቢ ሞተር",
        "bank_collateral_appeal": "ጥሩ የባንክ ዋስትና",
        "fuel_economy": "14 - 18 KM/L",
        "ground_clearance": "155 mm",
        "primary_use_case": "ለእቃ ማመላለሻ እና ለንግድ ድርጅቶች",
        "spare_parts_availability": "4.9/5",
        "resale_liquidity": "ፈጣን"
    },
    "toyota coaster": {
        "name": "Toyota Coaster (30-Seat Passenger Bus)",
        "full_model": "Toyota Coaster",
        "brand": "Toyota",
        "category": "Commercial Mid-Bus",
        "current_price_range_etb": "8,500,000 - 18,000,000 ETB",
        "core_advantage": "ከፍተኛ ዕለታዊ ገቢ የሚያስገኝ አስተማማኝ የህዝብ ማመላለሻ አውቶቡስ",
        "bank_collateral_appeal": "ከፍተኛ የባንክ ንግድ ብድር ዋስትና",
        "fuel_economy": "7 - 10 KM/L (4.0L/4.2L Diesel)",
        "ground_clearance": "185 mm",
        "primary_use_case": "ለሀገር አቋራጭ ትራንስፖርት እና ለሰራተኞች ሰርቪስ",
        "spare_parts_availability": "4.8/5",
        "resale_liquidity": "በጣም ፈጣን"
    },

    # --- SUZUKI Lineup ---
    "suzuki dzire": {
        "name": "Suzuki Dzire (2018 - 2024 Models)",
        "full_model": "Suzuki Dzire",
        "brand": "Suzuki",
        "category": "Compact Sedan",
        "current_price_range_etb": "2,400,000 - 3,400,000 ETB",
        "core_advantage": "አዲስ የሞዴል ዓመት፣ ዘመናዊ የውስጥ ገጽታ እና የላቀ የነዳጅ ቁጠባ (20-22 KM/L)",
        "bank_collateral_appeal": "እጅግ ከፍተኛ — አብዛኞቹ ባንኮች በ 20-30% ቅድመ ክፍያ ብድር ይሰጡበታል",
        "fuel_economy": "20 - 22 KM/L (DualJet 1.2L Engine)",
        "ground_clearance": "163 mm (ለአዲስ አበባ መንገዶች ተስማሚ)",
        "primary_use_case": "ለከተማ መጓጓዣ፣ ለፕሪሚየም ራይድ እና ለንግድ ድርጅት ሰራተኞች",
        "spare_parts_availability": "4.8/5 — በአዲስ አበባ በስፋት የሚገኝ ኦሪጅናል መለዋወጫ",
        "resale_liquidity": "በጣም ፈጣን የገበያ ዝውውር እና የተረጋጋ ዋጋ"
    },
    "suzuki swift": {
        "name": "Suzuki Swift (2018 - 2024)",
        "full_model": "Suzuki Swift",
        "brand": "Suzuki",
        "category": "Subcompact Hatchback",
        "current_price_range_etb": "2,350,000 - 3,200,000 ETB",
        "core_advantage": "ቀልጣፋ የመሪ ቁጥጥር፣ ዘመናዊ መልክ እና አነስተኛ የነዳጅ ወጪ",
        "bank_collateral_appeal": "ከፍተኛ የባንክ ብድር ተቀባይነት ያለው ንብረት",
        "fuel_economy": "20 - 23 KM/L",
        "ground_clearance": "163 mm",
        "primary_use_case": "ለግልና ለቤተሰብ የከተማ ጉዞ እንዲሁም ለተቀላጠፈ የቢሮ እንቅስቃሴ",
        "spare_parts_availability": "4.7/5 — የተሟላ የገበያ አቅርቦት",
        "resale_liquidity": "ከፍተኛ ተፈላጊነት ያለው"
    },
    "suzuki alto": {
        "name": "Suzuki Alto 800 / K10 (2015 - 2024)",
        "full_model": "Suzuki Alto",
        "brand": "Suzuki",
        "category": "Entry Subcompact Hatchback",
        "current_price_range_etb": "1,450,000 - 2,150,000 ETB",
        "core_advantage": "በጣም አነስተኛ የመግዣ ዋጋ፣ ወደር የለሽ የነዳጅ ቆጣቢነት (22-25 KM/L)",
        "bank_collateral_appeal": "ጥሩ የባንክ ዋስትና",
        "fuel_economy": "22 - 25 KM/L",
        "ground_clearance": "160 mm",
        "primary_use_case": "ለጀማሪ አሽከርካሪዎች፣ ለከተማ አነስተኛ ወጪ ጉዞ",
        "spare_parts_availability": "4.6/5",
        "resale_liquidity": "በጣም ፈጣን"
    },
    "suzuki baleno": {
        "name": "Suzuki Baleno (2020 - 2024)",
        "full_model": "Suzuki Baleno",
        "brand": "Suzuki",
        "category": "Premium Subcompact Hatchback",
        "current_price_range_etb": "2,800,000 - 3,900,000 ETB",
        "core_advantage": "ሰፊ የውስጥ ክፍል፣ 1.5L ጠንካራ ሞተር፣ የቅንጦት ገጽታ",
        "bank_collateral_appeal": "ከፍተኛ የባንክ ዋስትና",
        "fuel_economy": "18 - 21 KM/L",
        "ground_clearance": "165 mm",
        "primary_use_case": "ለቤተሰብ ምቾት እና ለቢሮ እንቅስቃሴ",
        "spare_parts_availability": "4.5/5",
        "resale_liquidity": "ፈጣን"
    },
    "suzuki jimny": {
        "name": "Suzuki Jimny (Compact 4x4 Off-Road SUV)",
        "full_model": "Suzuki Jimny",
        "brand": "Suzuki",
        "category": "Compact 4x4 Off-Road SUV",
        "current_price_range_etb": "4,200,000 - 6,800,000 ETB",
        "core_advantage": "እውነተኛ ባለ 4-ጎማ መጎተቻ (4WD)፣ ከፍተኛ የመሬት ከፍታ እና ማራኪ ዲዛይን",
        "bank_collateral_appeal": "ከፍተኛ የባንክ ዋስትና",
        "fuel_economy": "14 - 17 KM/L (1.5L)",
        "ground_clearance": "210 mm",
        "primary_use_case": "ለከተማና ለአስቸጋሪ የመስክ መንገዶች",
        "spare_parts_availability": "4.3/5",
        "resale_liquidity": "እጅግ ተፈላጊ"
    },
    "suzuki celerio": {
        "name": "Suzuki Celerio (2018 - 2024)",
        "full_model": "Suzuki Celerio",
        "brand": "Suzuki",
        "category": "Compact City Hatchback",
        "current_price_range_etb": "1,650,000 - 2,400,000 ETB",
        "core_advantage": "አነስተኛ የነዳጅ ፍጆታ፣ ቀላል አያያዝ",
        "bank_collateral_appeal": "ጥሩ የባንክ ዋስትና",
        "fuel_economy": "21 - 24 KM/L",
        "ground_clearance": "165 mm",
        "primary_use_case": "ለዕለታዊ የከተማ እንቅስቃሴ",
        "spare_parts_availability": "4.5/5",
        "resale_liquidity": "ፈጣን"
    },
    "suzuki ertiga": {
        "name": "Suzuki Ertiga (7-Seat MPV)",
        "full_model": "Suzuki Ertiga",
        "brand": "Suzuki",
        "category": "7-Seat Compact MPV",
        "current_price_range_etb": "3,600,000 - 5,200,000 ETB",
        "core_advantage": "ባለ 7 ወንበር ሰፊ የቤተሰብ መኪና፣ 1.5L ቆጣቢ ሞተር",
        "bank_collateral_appeal": "ከፍተኛ የባንክ ዋስትና",
        "fuel_economy": "16 - 19 KM/L",
        "ground_clearance": "180 mm",
        "primary_use_case": "ለትልቅ ቤተሰብ እና ለንግድ ድርጅት ትራንስፖርት",
        "spare_parts_availability": "4.5/5",
        "resale_liquidity": "ፈጣን"
    },
    "suzuki spresso": {
        "name": "Suzuki S-Presso (Mini SUV / Hatchback)",
        "full_model": "Suzuki S-Presso",
        "brand": "Suzuki",
        "category": "Mini Crossover Hatchback",
        "current_price_range_etb": "1,500,000 - 2,300,000 ETB",
        "core_advantage": "180 ሚሜ ከፍተኛ የመሬት ከፍታ፣ ዜሮ የነዳጅ ጭንቀት",
        "bank_collateral_appeal": "ጥሩ የባንክ ዋስትና",
        "fuel_economy": "21 - 24 KM/L",
        "ground_clearance": "180 mm",
        "primary_use_case": "ለከተማና ለአካባቢ መጓጓዣ",
        "spare_parts_availability": "4.6/5",
        "resale_liquidity": "በጣም ፈጣን"
    },

    # --- HYUNDAI Lineup ---
    "hyundai tucson": {
        "name": "Hyundai Tucson (2018 - 2024)",
        "full_model": "Hyundai Tucson",
        "brand": "Hyundai",
        "category": "Compact Crossover SUV",
        "current_price_range_etb": "5,000,000 - 8,200,000 ETB",
        "core_advantage": "ከፍተኛ የመሬት ከፍታ፣ ምቹ የውስጥ ክፍል እና ዘመናዊ የደህንነት ሲስተም",
        "bank_collateral_appeal": "ከፍተኛ ዋጋ ያለው የባንክ ዋስትና ንብረት",
        "fuel_economy": "11 - 13 KM/L (Benzine / Diesel)",
        "ground_clearance": "172 - 181 mm (ለኢትዮጵያ መንገዶች ምርጥ)",
        "primary_use_case": "ለቤተሰብ ምቾት፣ ለከተማና ለገጠር መንገዶች",
        "spare_parts_availability": "4.5/5 — በአዲስ አበባ በስፋት የሚገኝ",
        "resale_liquidity": "ጠንካራ የገበያ ተቀባይነት"
    },
    "hyundai accent": {
        "name": "Hyundai Accent (2012 - 2022)",
        "full_model": "Hyundai Accent",
        "brand": "Hyundai",
        "category": "Subcompact Sedan",
        "current_price_range_etb": "2,100,000 - 3,600,000 ETB",
        "core_advantage": "ዘመናዊ ገጽታ፣ ዝቅተኛ የጥገና ወጪ እና ምቹ አያያዝ",
        "bank_collateral_appeal": "ከፍተኛ የባንክ ዋስትና",
        "fuel_economy": "14 - 18 KM/L",
        "ground_clearance": "150 mm",
        "primary_use_case": "ለከተማ መጓጓዣ፣ ለቤተሰብ እና ለራይድ",
        "spare_parts_availability": "4.6/5",
        "resale_liquidity": "ፈጣን"
    },
    "hyundai elantra": {
        "name": "Hyundai Elantra (2014 - 2023)",
        "full_model": "Hyundai Elantra",
        "brand": "Hyundai",
        "category": "Compact Sedan",
        "current_price_range_etb": "2,800,000 - 5,200,000 ETB",
        "core_advantage": "ሰፊ ምቹ የውስጥ ክፍል፣ ስፖርቲ ገጽታ",
        "bank_collateral_appeal": "ከፍተኛ የባንክ ዋስትና",
        "fuel_economy": "13 - 17 KM/L",
        "ground_clearance": "150 mm",
        "primary_use_case": "ለቤተሰብ እና ለቢሮ እንቅስቃሴ",
        "spare_parts_availability": "4.5/5",
        "resale_liquidity": "ፈጣን"
    },
    "hyundai creta": {
        "name": "Hyundai Creta (2018 - 2024)",
        "full_model": "Hyundai Creta",
        "brand": "Hyundai",
        "category": "Subcompact Crossover SUV",
        "current_price_range_etb": "4,200,000 - 6,800,000 ETB",
        "core_advantage": "190 ሚሜ የመሬት ከፍታ፣ ምቹ የውስጥ ክፍል እና ዘመናዊ መልክ",
        "bank_collateral_appeal": "ከፍተኛ የባንክ ዋስትና",
        "fuel_economy": "13 - 16 KM/L",
        "ground_clearance": "190 mm",
        "primary_use_case": "ለከተማና ለገጠር መንገዶች",
        "spare_parts_availability": "4.4/5",
        "resale_liquidity": "ከፍተኛ"
    },
    "hyundai santa fe": {
        "name": "Hyundai Santa Fe (7-Seat SUV)",
        "full_model": "Hyundai Santa Fe",
        "brand": "Hyundai",
        "category": "Mid-Size 7-Seat SUV",
        "current_price_range_etb": "6,200,000 - 11,500,000 ETB",
        "core_advantage": "ባለ 7 ወንበር ሰፊ የቅንጦት SUV፣ ከፍተኛ ጥንካሬ",
        "bank_collateral_appeal": "ፕሪሚየም የባንክ ዋስትና",
        "fuel_economy": "10 - 13 KM/L (Diesel/Petrol)",
        "ground_clearance": "185 mm",
        "primary_use_case": "ለቤተሰብ ምቾት እና ለረጅም ጉዞ",
        "spare_parts_availability": "4.3/5",
        "resale_liquidity": "ከፍተኛ"
    },
    "hyundai atos": {
        "name": "Hyundai Atos / Prime (Vintage / City Hatchback)",
        "full_model": "Hyundai Atos",
        "brand": "Hyundai",
        "category": "Entry City Hatchback",
        "current_price_range_etb": "950,000 - 1,750,000 ETB",
        "core_advantage": "ከ1 ሚሊዮን ብር በታች የሚገኝ አነስተኛ የመግዣ ዋጋና ቀላል ጥገና",
        "bank_collateral_appeal": "መካከለኛ የባንክ ዋስትና",
        "fuel_economy": "16 - 19 KM/L",
        "ground_clearance": "150 mm",
        "primary_use_case": "ለጀማሪ አሽከርካሪዎችና ለአነስተኛ በጀት ግዢ",
        "spare_parts_availability": "4.5/5",
        "resale_liquidity": "ፈጣን"
    },

    # --- VOLKSWAGEN ID Series ---
    "volkswagen id4": {
        "name": "Volkswagen ID.4 (Crozz / X EV 2022 - 2025)",
        "full_model": "Volkswagen ID.4",
        "brand": "Volkswagen",
        "category": "Pure Electric Compact SUV",
        "current_price_range_etb": "4,800,000 - 7,800,000 ETB",
        "core_advantage": "የጀርመን ምህንድስና ጥራት፣ 550-600 KM የጉዞ ርቀት፣ ዜሮ የነዳጅ ወጪ",
        "bank_collateral_appeal": "ከፍተኛ የባንክ ዋስትና",
        "fuel_economy": "550 - 600 KM በአንድ ሙሉ ቻርጅ (~120 ብር የኤሌክትሪክ ወጪ)",
        "ground_clearance": "170 mm",
        "primary_use_case": "ለከተማና ለክልል ምቹ የኤሌክትሪክ ጉዞ",
        "spare_parts_availability": "4/5 — በአዲስ አበባ ጋራዦች በስፋት የሚገኝ",
        "resale_liquidity": "በጣም ከፍተኛ"
    },
    "volkswagen id6": {
        "name": "Volkswagen ID.6 (Crozz / X 7-Seat EV)",
        "full_model": "Volkswagen ID.6",
        "brand": "Volkswagen",
        "category": "7-Seat Pure Electric SUV",
        "current_price_range_etb": "6,500,000 - 9,800,000 ETB",
        "core_advantage": "ባለ 7 ወንበር ሰፊ የቅንጦት ኤሌክትሪክ SUV፣ 580 KM የጉዞ ርቀት",
        "bank_collateral_appeal": "ፕሪሚየም የባንክ ዋስትና",
        "fuel_economy": "560 - 588 KM Range",
        "ground_clearance": "180 mm",
        "primary_use_case": "ለትልቅ ቤተሰብ እና ለረጅም ጉዞ",
        "spare_parts_availability": "3.8/5",
        "resale_liquidity": "ከፍተኛ"
    },

    # --- CHANGAN Lineup ---
    "changan e-star": {
        "name": "Changan Benni E-Star EV (2021 - 2024)",
        "full_model": "Changan E-Star",
        "brand": "Changan",
        "category": "City Electric Hatchback",
        "current_price_range_etb": "2,200,000 - 3,200,000 ETB",
        "core_advantage": "በጣም ተመጣጣኝ የኤሌክትሪክ መኪና ዋጋ፣ 301 KM የጉዞ ርቀት",
        "bank_collateral_appeal": "ጥሩ የባንክ ዋስትና",
        "fuel_economy": "301 KM በአንድ ሙሉ ቻርጅ",
        "ground_clearance": "150 mm",
        "primary_use_case": "ለከተማ እንቅስቃሴና ለዕለታዊ የስራ ጉዞ",
        "spare_parts_availability": "4/5",
        "resale_liquidity": "በጣም ፈጣን"
    },
    "changan cs35": {
        "name": "Changan CS35 Plus (2020 - 2024)",
        "full_model": "Changan CS35 Plus",
        "brand": "Changan",
        "category": "Compact Crossover SUV",
        "current_price_range_etb": "3,200,000 - 4,800,000 ETB",
        "core_advantage": "ዘመናዊ ገጽታ፣ 180 ሚሜ የመሬት ከፍታ እና ምቹ የውስጥ ክፍል",
        "bank_collateral_appeal": "ከፍተኛ የባንክ ዋስትና",
        "fuel_economy": "14 - 17 KM/L",
        "ground_clearance": "180 mm",
        "primary_use_case": "ለቤተሰብና ለከተማ መጓጓዣ",
        "spare_parts_availability": "4.2/5",
        "resale_liquidity": "ፈጣን"
    },

    # --- NETA Lineup ---
    "neta v": {
        "name": "Neta V / Neta Aya (Compact EV 2022 - 2025)",
        "full_model": "Neta V",
        "brand": "Neta",
        "category": "Compact Electric Crossover",
        "current_price_range_etb": "2,400,000 - 3,500,000 ETB",
        "core_advantage": "ተመጣጣኝ የመግዣ ዋጋ፣ 301-401 KM ርቀት፣ ትልቅ የንክኪ ስክሪን",
        "bank_collateral_appeal": "ጥሩ የባንክ ዋስትና",
        "fuel_economy": "301 - 401 KM በአንድ ሙሉ ቻርጅ",
        "ground_clearance": "155 mm",
        "primary_use_case": "ለከተማ መጓጓዣ እና ለወጣቶች",
        "spare_parts_availability": "3.9/5",
        "resale_liquidity": "ፈጣን"
    },

    # --- ISUZU Lineup ---
    "isuzu d-max": {
        "name": "Isuzu D-Max (Single / Double Cab Pickup)",
        "full_model": "Isuzu D-Max",
        "brand": "Isuzu",
        "category": "Commercial & Passenger Pickup",
        "current_price_range_etb": "4,800,000 - 11,500,000 ETB",
        "core_advantage": "አስደናቂ የናፍጣ ሞተር ጥንካሬ፣ ከፍተኛ የመጎተትና የመጫን አቅም",
        "bank_collateral_appeal": "እጅግ ከፍተኛ የባንክ ዋስትና",
        "fuel_economy": "11 - 14 KM/L (Diesel)",
        "ground_clearance": "225 - 235 mm",
        "primary_use_case": "ለኮንስትራክሽን፣ ለንግድ፣ ለፕሮጀክት እና ለቤተሰብ",
        "spare_parts_availability": "4.8/5",
        "resale_liquidity": "እጅግ ፈጣን"
    },
    "isuzu npr": {
        "name": "Isuzu NPR (Medium Cargo Truck)",
        "full_model": "Isuzu NPR",
        "brand": "Isuzu",
        "category": "Medium Commercial Truck",
        "current_price_range_etb": "4,500,000 - 9,500,000 ETB",
        "core_advantage": "የኢትዮጵያ የጭነት ንግድ የጀርባ አጥንት፣ አስተማማኝ የቀን ገቢ",
        "bank_collateral_appeal": "ከፍተኛ የባንክ ብድር ዋስትና",
        "fuel_economy": "7 - 10 KM/L (Diesel)",
        "ground_clearance": "210 mm",
        "primary_use_case": "ለከተማና ለክልል የጭነት ንግድ",
        "spare_parts_availability": "5/5",
        "resale_liquidity": "በጣም ፈጣን"
    },

    # --- MITSUBISHI Lineup ---
    "mitsubishi pajero": {
        "name": "Mitsubishi Pajero (GLS / Exceed 4WD SUV)",
        "full_model": "Mitsubishi Pajero",
        "brand": "Mitsubishi",
        "category": "Full-Size 4WD SUV",
        "current_price_range_etb": "4,200,000 - 12,500,000 ETB",
        "core_advantage": "Super Select 4WD ሲስተም፣ ጥንካሬ እና የመስክ ብቃት",
        "bank_collateral_appeal": "ከፍተኛ የባንክ ዋስትና",
        "fuel_economy": "8 - 11 KM/L",
        "ground_clearance": "215 mm",
        "primary_use_case": "ለቤተሰብና ለአስቸጋሪ መንገዶች",
        "spare_parts_availability": "4.5/5",
        "resale_liquidity": "ጠንካራ"
    },
    "mitsubishi l200": {
        "name": "Mitsubishi L200 (Double Cab Pickup)",
        "full_model": "Mitsubishi L200",
        "brand": "Mitsubishi",
        "category": "Rugged Commercial Pickup",
        "current_price_range_etb": "3,800,000 - 8,500,000 ETB",
        "core_advantage": "ጠንካራ የናፍጣ ሞተር፣ ሰፊ የመጫኛ አካል",
        "bank_collateral_appeal": "ከፍተኛ የባንክ ዋስትና",
        "fuel_economy": "10 - 13 KM/L",
        "ground_clearance": "205 - 220 mm",
        "primary_use_case": "ለስራ፣ ለንግድ እና ለቤተሰብ",
        "spare_parts_availability": "4.5/5",
        "resale_liquidity": "ፈጣን"
    },

    # --- NISSAN Lineup ---
    "nissan patrol": {
        "name": "Nissan Patrol (Y61 / Y62 V8 Flagship SUV)",
        "full_model": "Nissan Patrol",
        "brand": "Nissan",
        "category": "Full-Size Luxury 4WD SUV",
        "current_price_range_etb": "9,500,000 - 26,000,000 ETB",
        "core_advantage": "የ V8 ሞተር ኃይል፣ ከፍተኛ ክብርና ምቾት፣ የማይበገር ጥንካሬ",
        "bank_collateral_appeal": "ፕሪሚየም የባንክ ዋስትና",
        "fuel_economy": "6 - 9 KM/L",
        "ground_clearance": "270 mm",
        "primary_use_case": "ለቪአይፒ እና ለቅንጦት የመስክ ጉዞ",
        "spare_parts_availability": "4.4/5",
        "resale_liquidity": "ከፍተኛ"
    },

    # --- BAJAJ & MOTORCYCLES ---
    "bajaj": {
        "name": "Bajaj RE 4-Stroke (Auto Rickshaw)",
        "full_model": "Bajaj RE Compact",
        "brand": "Bajaj",
        "category": "3-Wheeler Passenger Commercial",
        "current_price_range_etb": "350,000 - 520,000 ETB",
        "core_advantage": "በጣም አነስተኛ የመነሻ ካፒታል፣ የቀን ገቢ (1,200 - 2,200 ብር/ቀን)፣ ቆጣቢ ነዳጅ",
        "bank_collateral_appeal": "ጥሩ አነስተኛ ዋስትና",
        "fuel_economy": "30 - 36 KM/L",
        "ground_clearance": "180 mm",
        "primary_use_case": "ለከተማ ውስጥ አነስተኛ ትራንስፖርት ንግድ",
        "spare_parts_availability": "5/5 — በማንኛውም ጋራዥ የሚገኝ",
        "resale_liquidity": "እጅግ ፈጣን"
    }
}

# ------------------------------------------------------------------------------
# 2. AMHARIC_VEHICLE_SYNONYMS (Phonetic & Name Variations Mapping)
# ------------------------------------------------------------------------------
AMHARIC_VEHICLE_SYNONYMS: Dict[str, str] = {
    # BYD
    "ቢዋይዲ": "byd", "ቢ ዋይ ዲ": "byd", "ባይድ": "byd",
    "ሲጋል": "byd seagull", "ሲገል": "byd seagull", "ሲጎል": "byd seagull", "ሲጋልስ": "byd seagull", "seagull": "byd seagull",
    "ዶልፊን": "byd dolphin", "ዶልፊንት": "byd dolphin", "dolphin": "byd dolphin",
    "ሶንግ": "byd song plus", "ሶንግ ፕላስ": "byd song plus", "ሶንግፕላስ": "byd song plus", "song": "byd song plus", "song plus": "byd song plus",
    "ዩዋን": "byd yuan plus", "ዩዋን ፕላስ": "byd yuan plus", "አቶ 3": "byd yuan plus", "atto 3": "byd yuan plus",
    "ሃን": "byd han", "ታንግ": "byd tang", "ቺን ፕላስ": "byd qin plus", "ኢ2": "byd e2",

    # TOYOTA
    "ቶዮታ": "toyota", "ቶዮታስ": "toyota", "ቶዮታው": "toyota",
    "ቪትዝ": "toyota vitz", "ቪትስ": "toyota vitz", "ቪትዞ": "toyota vitz", "ቪትዚ": "toyota vitz", "vitz": "toyota vitz",
    "ያሪስ": "toyota yaris", "ያሪስስ": "toyota yaris", "yaris": "toyota yaris",
    "ቤልታ": "toyota belta", "ቤልታስ": "toyota belta", "belta": "toyota belta",
    "ኢስት": "toyota ist", "ist": "toyota ist",
    "ኮሮላ": "toyota corolla", "ኮሮላስ": "toyota corolla", "ኮሮላው": "toyota corolla", "corolla": "toyota corolla", "ኮሮላ ክሮስ": "toyota corolla cross",
    "ራቭ4": "toyota rav4", "ራቭ 4": "toyota rav4", "ራቭ": "toyota rav4", "rav4": "toyota rav4",
    "ሀይሉክስ": "toyota hilux", "ሃይሉክስ": "toyota hilux", "ሃይለክስ": "toyota hilux", "ሬቮ": "toyota hilux", "hilux": "toyota hilux",
    "ፕራዶ": "toyota land cruiser prado", "ፕራዶስ": "toyota land cruiser prado", "ቲኤክስ": "toyota land cruiser prado", "prado": "toyota land cruiser prado",
    "ላንድ ክሩዘር": "toyota land cruiser 70", "ላንድክሩዘር": "toyota land cruiser 70", "ሀርድቶፕ": "toyota land cruiser 70", "ሃርድቶፕ": "toyota land cruiser 70", "hardtop": "toyota land cruiser 70",
    "ቪ8": "toyota land cruiser 200", "v8": "toyota land cruiser 200", "ላንድ ክሩዘር 200": "toyota land cruiser 200", "lc200": "toyota land cruiser 200",
    "ላንድ ክሩዘር 300": "toyota land cruiser 300", "lc300": "toyota land cruiser 300",
    "ፎርቹን": "toyota fortuner", "ፎርቹንር": "toyota fortuner", "fortuner": "toyota fortuner",
    "ፎር ራነር": "toyota 4runner", "ፎርራነር": "toyota 4runner", "4runner": "toyota 4runner",
    "ሀያይስ": "toyota hiace", "ሃያይስ": "toyota hiace", "ሃይስ": "toyota hiace", "ዶልፊን ሃይስ": "toyota hiace", "hiace": "toyota hiace",
    "ኖህ": "toyota noah", "noah": "toyota noah", "ቮክሲ": "toyota voxy", "voxy": "toyota voxy",
    "ረሽ": "toyota rush", "ራሽ": "toyota rush", "rush": "toyota rush",
    "አርባን ክሩዘር": "toyota urban cruiser", "ኡርባን ክሩዘር": "toyota urban cruiser", "urban cruiser": "toyota urban cruiser",
    "አክሲዮ": "toyota axio", "axio": "toyota axio", "ፕሪሚዮ": "toyota premio", "premio": "toyota premio",
    "ፕሮቦክስ": "toyota probox", "probox": "toyota probox", "ኮስተር": "toyota coaster", "coaster": "toyota coaster",

    # SUZUKI
    "ሱዙኪ": "suzuki", "ሱዙኪስ": "suzuki",
    "ዲዛየር": "suzuki dzire", "ዲዛይር": "suzuki dzire", "ደዛየር": "suzuki dzire", "ዲዛየርን": "suzuki dzire", "dzire": "suzuki dzire",
    "ስዊፍት": "suzuki swift", "ስዊፍቲ": "suzuki swift", "swift": "suzuki swift",
    "አልቶ": "suzuki alto", "alto": "suzuki alto", "ባሌኖ": "suzuki baleno", "baleno": "suzuki baleno",
    "ጂምኒ": "suzuki jimny", "jimny": "suzuki jimny", "ሴሌሪዮ": "suzuki celerio", "celerio": "suzuki celerio",
    "ኤርቲጋ": "suzuki ertiga", "ertiga": "suzuki ertiga", "ስፕሬሶ": "suzuki spresso", "spresso": "suzuki spresso",

    # HYUNDAI
    "ሀዩንዳይ": "hyundai", "ሃዩንዳይ": "hyundai", "ሂዩንዳይ": "hyundai",
    "ቱክሰን": "hyundai tucson", "ቱክሶን": "hyundai tucson", "ቱክሰንት": "hyundai tucson", "tucson": "hyundai tucson",
    "አክሰንት": "hyundai accent", "accent": "hyundai accent", "ኤላንትራ": "hyundai elantra", "elantra": "hyundai elantra",
    "ክሬታ": "hyundai creta", "creta": "hyundai creta", "ሳንታፌ": "hyundai santa fe", "santa fe": "hyundai santa fe",
    "አቶስ": "hyundai atos", "atos": "hyundai atos",

    # VOLKSWAGEN
    "ቮልስዋገን": "volkswagen", "ፎልክስዋገን": "volkswagen", "vw": "volkswagen",
    "አይዲ4": "volkswagen id4", "አይዲ 4": "volkswagen id4", "id4": "volkswagen id4", "id.4": "volkswagen id4",
    "አይዲ6": "volkswagen id6", "id6": "volkswagen id6", "id.6": "volkswagen id6",

    # CHANGAN & NETA
    "ቻንጋን": "changan", "ኢ ስታር": "changan e-star", "ኢስታር": "changan e-star", "e-star": "changan e-star", "estar": "changan e-star",
    "ሲኤስ35": "changan cs35", "cs35": "changan cs35",
    "ኔታ": "neta", "ኔታ ቪ": "neta v", "neta v": "neta v",

    # ISUZU & MITSUBISHI & NISSAN
    "ኢሱዙ": "isuzu", "ዲማክስ": "isuzu d-max", "d-max": "isuzu d-max", "dmax": "isuzu d-max",
    "ኤንፒአር": "isuzu npr", "npr": "isuzu npr",
    "ሚትሱቢሺ": "mitsubishi", "ፓጄሮ": "mitsubishi pajero", "pajero": "mitsubishi pajero",
    "ኤል200": "mitsubishi l200", "l200": "mitsubishi l200",
    "ኒሳን": "nissan", "ፓትሮል": "nissan patrol", "patrol": "nissan patrol",

    # BAJAJ
    "ባጃጅ": "bajaj", "ባጃጅስ": "bajaj", "bajaj": "bajaj", "ሞተርሳይክል": "bajaj"
}

# ------------------------------------------------------------------------------
# 3. KNOWLEDGE_BASE_STORE (Banking, Land, Real Estate, Legal & Customs Facts)
# ------------------------------------------------------------------------------
KNOWLEDGE_BASE_STORE: Dict[str, Dict[str, Any]] = {
    "banking_loan": {
        "title": "የባንክ ብድር፣ የወለድ ምጣኔ እና የቅድመ ክፍያ አሰራር (Bank Loan & Interest Policy)",
        "keywords": ["ባንክ", "ብድር", "ወለድ", "ቅድመ ክፍያ", "ዋስትና", "loan", "interest", "bank", "cbe", "አዋሽ", "ዳሽን", "አቢሲኒያ", "dti"],
        "content": (
            "1. የወለድ ምጣኔ (Interest Rates): በኢትዮጵያ ንግድ ባንኮች (CBE, Awash, Dashen, Abyssinia) የወለድ መጠን እንደ ብድሩ አይነት ከ16% እስከ 22%+ ይደርሳል።\n"
            "2. የቅድመ ክፍያ (Down Payment): ለመኪና ወይም ለቤት ግዢ ባንኮች ከ20% እስከ 30% የራስዎን ቅድመ ክፍያ ይጠይቃሉ። ቀሪው 70%-80% በባንክ ይሸፈናል።\n"
            "3. የገቢና ወርሃዊ ክፍያ ሬሾ (DTI): ወርሃዊ የብድር መክፈያዎ ከጠቅላላ ወርሃዊ ገቢዎ ከ35% - 40% እንዳይበልጥ ባንኮች ይቆጣጠራሉ።\n"
            "4. የሲፒኦ (CPO) አሰራር: ለንብረት ግዢ ክፍያ በባንክ የተረጋገጠ የክፍያ ማዘዣ (Certified Payment Order) በሻጩ ስም ማዘጋጀት ግዴታ ነው።"
        )
    },
    "land_real_estate": {
        "title": "የመሬት፣ የይዞታ ካርታ እና የሪል እስቴት አሰራር (Land Lease & Property Transfer)",
        "keywords": ["መሬት", "ቦታ", "ካርታ", "ሊዝ", "ቪላ", "አፓርትመንት", "ኮንዶሚኒየም", "40/60", "20/80", "ሪል እስቴት", "ካሬ", "land", "real estate", "house"],
        "content": (
            "1. የይዞታ ካርታና ሰነድ ማረጋገጫ: ማንኛውንም መሬት ወይም ቤት ከመግዛትዎ በፊት በክፍለ-ከተማ የመሬት አስተዳደር ኦሪጅናል ካርታ፣ የዕዳ ነፃ ማስረጃና የይዞታ ማረጋገጫ መፈተሽ አለበት።\n"
            "2. የሊዝ ክፍያ (Lease Payment): የሊዝ መሬቶች ዓመታዊ የሊዝ ክፍያ ያለባቸው መሆኑንና ቀሪ የሊዝ ዕዳን ከሻጩ ጋር በግልጽ በውል ማስፈር ያስፈልጋል።\n"
            "3. የኮንዶሚኒየም ዝውውር (40/60 እና 20/80): የባንክ ቀሪ ዕዳ ያለበት ከሆነ በባንክ በኩል ዕዳውን ማዛወር ወይም ሙሉ በሙሉ ከፍሎ የዕዳ ነፃ ማስረጃ ማውጣት ይጠይቃል።\n"
            "4. የካፒታል ጌይን ታክስ (15%): ንብረት በሚሸጥበት ጊዜ ሻጩ ከተገኘው ትርፍ ላይ የ15% የካፒታል ገቢ ግብር ይከፍላል።"
        )
    },
    "legal_documents": {
        "title": "የሰነዶች ማረጋገጫ፣ ውክልና እና የባለቤትነት ስም ዝውውር (Legal Contracts & DARA)",
        "keywords": ["ውክልና", "ፖዋ", "ውል", "ሰነዶች", "ስም ዝውውር", "dara", "ውልና ማስረጃ", "ሊብሬ", "ቦሎ", "legal", "transfer"],
        "content": (
            "1. የውልና ማስረጃ ማረጋገጫ (DARA): የመኪና ወይም የቤት ሽያጭ ውል በሰነዶች ማረጋገጫና ምዝገባ አገልግሎት (DARA) ፊት ካልተፈረመ በህግ ተቀባይነት የለውም።\n"
            "2. ህጋዊ ውክልና (Power of Attorney): በውክልና የሚሸጥ ንብረት ከሆነ የውክልናው ሰነድ 'ለመሸጥ እና ገንዘብ ለመቀበል' የሚል ግልጽ ስልጣን መስጠቱንና አለመሻሩን ማረጋገጥ ወሳኝ ነው።\n"
            "3. የተሽከርካሪ ሊብሬና ቦሎ: የተሽከርካሪው ሊብሬ ከሻሲውና ከሞተሩ ቁጥር ጋር መመሳከሩን እንዲሁም ከትራፊክ ፖሊስ የዕገዳ ነፃ መሆኑን ማረጋገጥ ያስፈልጋል።"
        )
    },
    "customs_duty": {
        "title": "የጉምሩክ ቀረጥ፣ ታክስ እና የኤሌክትሪክ ተሽከርካሪ ፖሊሲ (Customs Duty & EV Incentives)",
        "keywords": ["ቀረጥ", "ታክስ", "ጉምሩክ", "ዲዩቲ", "ኤክሳይስ", "ቫት", "ሱር", "cif", "duty", "tax", "customs", "ev tax"],
        "content": (
            "1. የኤሌክትሪክ ተሽከርካሪዎች (EV): በመንግስት የልማት ፖሊሲ መሰረት የተሟላ የቀረጥ ማበረታቻ ያላቸው ሲሆን 15% ቫት (VAT) እና 5% ዝቅተኛ የጉምሩክ ቀረጥ ብቻ ይከፈልባቸዋል።\n"
            "2. የቤንዚንና ናፍጣ ተሽከርካሪዎች: እንደ ሞተራቸው ሲሲ (CC) እና እንደ እድሜያቸው የጉምሩክ ቀረጥ (35%)፣ ኤክሳይስ ታክስ (እስከ 100%+)፣ ሱር ታክስ (10%) እና ቫት (15%) ይታሰባል።\n"
            "3. ትክክለኛ የቀረጥ ስሌት: በአዲካ የገበያ መተግበሪያ ውስጥ ያለውን 'የቀረጥ ማስያ' በመጠቀም የ CIF ዋጋ በማስገባት የወደብ ቀረጥን በትክክል ማስላት ይቻላል።"
        )
    }
}


def normalize_search_query(text: str) -> str:
    """Normalize text replacing Amharic synonyms with standardized vehicle keys."""
    if not text:
        return ""
    q = text.lower()
    for amh, eng in AMHARIC_VEHICLE_SYNONYMS.items():
        if amh in q:
            q = q.replace(amh, f" {eng} ")
    q = re.sub(r'[፣፤፥፦!\?,\.\(\)\[\]"\'/\\-]', ' ', q)
    tokens = q.split()
    cleaned = []
    for t in tokens:
        stripped = re.sub(r'^(የ|ለ|በ|ከ|ስለ|ደግሞ)', '', t).strip()
        if stripped and stripped not in {"ዋጋ", "ዋጋው", "ስንት", "ነው", "መኪና", "ተሽከርካሪ", "car", "price", "ብር", "etb"}:
            cleaned.append(stripped)
        elif t and t not in {"ዋጋ", "ዋጋው", "ስንት", "ነው", "መኪና", "ተሽከርካሪ", "car", "price", "ብር", "etb"}:
            cleaned.append(t)
    return " ".join(cleaned).strip()
