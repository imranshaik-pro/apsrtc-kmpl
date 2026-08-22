#!/usr/bin/env python3
"""
Build depot_mapping.json from the master depot list with alias keys.
"""

import json

REGION_MAP = {
    "Srikakulam": "SRIKAKULAM",
    "Vizianagaram": "VIZIANAGARAM",
    "Parvathipuram Manyam": "PPMMANYAM",
    "Anakapalli": "ANAKAPALLI",
    "Alluri Sitharama Raju": "ASR",
    "Visakhapatnam": "VISAKHAPATNAM",
    "Kakinada": "KAKINADA",
    "Dr. B.R. Ambedkar Konaseema": "KONASEEMA",
    "East Godavari": "EASTGODAVARI",
    "West Godavari": "WESTGODAVARI",
    "Eluru": "ELURU",
    "NTR": "NTR",
    "Krishna": "KRISHNA",
    "Guntur": "GUNTUR",
    "Palnadu": "PALNADU",
    "Bapatla": "BAPATLA",
    "Prakasam": "PRAKASAM",
    "Markapuram Jurisdiction": "MARKAPURAM",
    "Sri Potti Sriramulu Nellore": "SPSNELLORE",
    "Tirupati": "TIRUPATI",
    "Chittoor": "CHITTOR",
    "Annamayya": "ANNAMAIAH",
    "YSR Kadapa": "YSRKADAPA",
    "Kurnool": "KURNOOL",
    "Nandyal": "NANDYAL",
    "Ananthapuramu": "ANANTAPUR",
    "Sri Sathya Sai": "SRISATYASAI"
}

DEPOTS = [
    ("TKL", "Tekkali", "Srikakulam"),
    ("SKLM1", "Srikakulam-1", "Srikakulam"),
    ("SKLM2", "Srikakulam-2", "Srikakulam"),
    ("PLS", "Palasa", "Srikakulam"),
    ("SKT", "Srungavarapukota / S.Kota", "Vizianagaram"),
    ("VZM", "Vizianagaram", "Vizianagaram"),
    ("PLKD", "Palakonda", "Parvathipuram Manyam"),
    ("PPM", "Parvathipuram", "Parvathipuram Manyam"),
    ("SLR", "Salur", "Parvathipuram Manyam"),
    ("AKP", "Anakapalli", "Anakapalli"),
    ("NRPM", "Narsipatnam", "Anakapalli"),
    ("PDR", "Paderu", "Alluri Sitharama Raju"),
    ("VSP", "Visakhapatnam", "Visakhapatnam"),
    ("MDWD", "Madhavadhara", "Visakhapatnam"),
    ("WLTR", "Waltair", "Visakhapatnam"),
    ("GWK", "Gajuwaka", "Visakhapatnam"),
    ("SML", "Simhachalam", "Visakhapatnam"),
    ("VSCD", "Visakha Steel City Depot", "Visakhapatnam"),
    ("MDP", "Maddilapalem", "Visakhapatnam"),
    ("KKD", "Kakinada", "Kakinada"),
    ("ELSM", "Eleswaram", "Kakinada"),
    ("TUNI", "Tuni", "Kakinada"),
    ("RVM", "Ravulapalem", "Dr. B.R. Ambedkar Konaseema"),
    ("RZL", "Razole", "Dr. B.R. Ambedkar Konaseema"),
    ("AMP", "Amalapuram", "Dr. B.R. Ambedkar Konaseema"),
    ("RCPM", "Ramachandrapuram", "Dr. B.R. Ambedkar Konaseema"),
    ("RJY", "Rajamahendravaram / Rajahmundry", "East Godavari"),
    ("GKRM", "Gokavaram", "East Godavari"),
    ("KVR", "Kovvur", "East Godavari"),
    ("NDD", "Nidadavole", "East Godavari"),
    ("NSP", "Narsapuram", "West Godavari"),
    ("BVRM", "Bhimavaram", "West Godavari"),
    ("TNK", "Tanuku", "West Godavari"),
    ("TPG", "Tadepalligudem", "West Godavari"),
    ("ELR", "Eluru", "Eluru"),
    ("JRG", "Jangareddygudem", "Eluru"),
    ("NZD", "Nuzvid", "Eluru"),
    ("JPT", "Jaggaiahpeta", "NTR"),
    ("TVR", "Tiruvuru", "NTR"),
    ("VJA", "Vijayawada / Vidyadharapuram", "NTR"),
    ("ATNR", "Autonagar", "NTR"),
    ("IBM", "Ibrahimpatnam", "NTR"),
    ("GVPT1", "Governorpet-1", "NTR"),
    ("GVPT2", "Governorpet-2", "NTR"),
    ("GVRM", "Gannavaram", "Krishna"),
    ("MTM", "Machilipatnam", "Krishna"),
    ("GDV", "Gudivada", "Krishna"),
    ("AVG", "Avanigadda", "Krishna"),
    ("VYR", "Vuyyuru", "Krishna"),
    ("GNT1", "Guntur-1", "Guntur"),
    ("TNL", "Tenali", "Guntur"),
    ("PNR", "Ponnur", "Guntur"),
    ("MGLR", "Mangalagiri", "Guntur"),
    ("PDRL", "Piduguralla", "Palnadu"),
    ("MCL", "Macherla", "Palnadu"),
    ("NRT", "Narasaraopet", "Palnadu"),
    ("CPT", "Chilakaluripeta", "Palnadu"),
    ("SAP", "Sattenapalli", "Palnadu"),
    ("VNK", "Vinukonda", "Palnadu"),
    ("BPTL", "Bapatla", "Bapatla"),
    ("RPL", "Repalle", "Bapatla"),
    ("CRL", "Chirala", "Bapatla"),
    ("OGL", "Ongole", "Prakasam"),
    ("ADK", "Addanki", "Prakasam"),
    ("KDKR", "Kandukur", "Prakasam"),
    ("PDL", "Podili", "Markapuram Jurisdiction"),
    ("MRKP", "Markapur", "Markapuram Jurisdiction"),
    ("KNGR", "Kanigiri", "Markapuram Jurisdiction"),
    ("GDLR", "Giddalur", "Markapuram Jurisdiction"),
    ("NLR1", "Nellore-1", "Sri Potti Sriramulu Nellore"),
    ("ATKN", "Atmakur - Nellore", "Sri Potti Sriramulu Nellore"),
    ("UDGR", "Udayagiri", "Sri Potti Sriramulu Nellore"),
    ("KVL", "Kavali", "Sri Potti Sriramulu Nellore"),
    ("RPR", "Rapur", "Sri Potti Sriramulu Nellore"),
    ("GDT", "Gudur", "Sri Potti Sriramulu Nellore"),
    ("VKD", "Vakapadu", "Tirupati"),
    ("SLPT", "Sullurpeta", "Tirupati"),
    ("VGR", "Venkatagiri", "Tirupati"),
    ("TPT", "Tirupati Main", "Tirupati"),
    ("MGLM", "Mangalam", "Tirupati"),
    ("ALPR", "Alipiri", "Tirupati"),
    ("TML", "Tirumala", "Tirupati"),
    ("SKHT", "Srikalahasti", "Tirupati"),
    ("STVD", "Satyavedu", "Tirupati"),
    ("PTR", "Puttur", "Tirupati"),
    ("CTR1", "Chittoor-1", "Chittoor"),
    ("CTR2", "Chittoor-2", "Chittoor"),
    ("PLMR", "Palamaner", "Chittoor"),
    ("KPM", "Kuppam", "Chittoor"),
    ("PLR", "Pileru", "Annamayya"),
    ("MPL1", "Madanapalle-1", "Annamayya"),
    ("MPL2", "Madanapalle-2", "Annamayya"),
    ("RCTY", "Rayachoty", "Annamayya"),
    ("PNGR", "Punganur", "Annamayya"),
    ("KDP", "Kadapa", "YSR Kadapa"),
    ("BDVL", "Badvel", "YSR Kadapa"),
    ("MYDK", "Mydukur", "YSR Kadapa"),
    ("JMD", "Jammalamadugu", "YSR Kadapa"),
    ("PDTR", "Proddatur", "YSR Kadapa"),
    ("PLVD", "Pulivendula", "YSR Kadapa"),
    ("RJPT", "Rajampeta", "YSR Kadapa"),
    ("KNL1", "Kurnool-1", "Kurnool"),
    ("KNL2", "Kurnool-2", "Kurnool"),
    ("ADONI", "Adoni", "Kurnool"),
    ("PTKD", "Pattikonda", "Kurnool"),
    ("YMG", "Yemmiganur", "Kurnool"),
    ("ALG", "Allagadda", "Nandyal"),
    ("ATKK", "Atmakur - Kurnool/Nandyal", "Nandyal"),
    ("BPL", "Banaganapalli", "Nandyal"),
    ("DHN", "Dhone", "Nandyal"),
    ("KKL", "Koilakuntla", "Nandyal"),
    ("NDK", "Nandikotkur", "Nandyal"),
    ("NDL", "Nandyal", "Nandyal"),
    ("ATP", "Anantapur", "Ananthapuramu"),
    ("KLDG", "Kalyandurgam", "Ananthapuramu"),
    ("RDG", "Rayadurgam", "Ananthapuramu"),
    ("TDP", "Tadipatri", "Ananthapuramu"),
    ("GTKL", "Guntakal", "Ananthapuramu"),
    ("UKD", "Uravakonda", "Ananthapuramu"),
    ("GTY", "Gooty", "Ananthapuramu"),
    ("DMM", "Dharmavaram", "Sri Sathya Sai"),
    ("HDP", "Hindupur", "Sri Sathya Sai"),
    ("KDR", "Kadiri", "Sri Sathya Sai"),
    ("MDKS", "Madakasira", "Sri Sathya Sai"),
    ("PNKD", "Penukonda", "Sri Sathya Sai"),
    ("PTP", "Puttaparthi", "Sri Sathya Sai"),
]

def normalize_display(raw):
    name = raw.upper()
    name = name.replace(" / ", "/")
    name = name.replace(" - ", "-")
    name = name.replace(" ", "")
    return name

def build_alias(display):
    alias = display.lower()
    alias = alias.replace(" ", "").replace("-", "").replace("/", "").replace("(", "").replace(")", "")
    return alias

def main():
    mapping = {}
    for code, display, district in DEPOTS:
        norm = normalize_display(display)
        vehicle_depot = f"{code}/{norm}"
        region = REGION_MAP.get(district, "UNKNOWN")
        # Primary key: code (lowercase, no special)
        key = code.lower().replace("-", "").replace("(", "").replace(")", "")
        mapping[key] = {
            "vehicle_depot": vehicle_depot,
            "region_code": region,
            "display_name": norm
        }
        # Alias from display name
        alias = build_alias(display)
        if alias != key:
            mapping[alias] = {
                "vehicle_depot": vehicle_depot,
                "region_code": region,
                "display_name": norm,
                "_alias_of": key
            }
    with open("depot_mapping.json", "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)
    print(f"Generated depot_mapping.json with {len(mapping)} entries.")

if __name__ == "__main__":
    main()
