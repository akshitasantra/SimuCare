# logic/intervention_tree.py
"""
Global intervention tree defining category → action → detail structure.
"""

# Example tree; expand with full EMT intervention options as needed
TREE = {
    "Scene": {
        "Wear PPE": {
            "Gloves": {},
            "Gloves + Goggles": {},
            "Gloves + Mask": {}
        },
    },
    "Primary Assessment": {
        "General Impression": {
            "Major Bleed": {},
            "No Major Bleed": {}
        },
        "Airway Management": {
            "Insert OPA": {
                "Size_6": {},
                "Size_8": {}
            },
            "Jaw Thrust": {}
        },
        "Breathing Support": {
            "Administer_O2": {
                "6L_NC": {},
                "15L_NRB": {}
            },
            "BVM": {}
        }
    },
    "Circulation": {
        "Control Bleeding": {
            "Pressure Dressing": {},
            "Tourniquet": {}
        },
        "IV Access": {
            "Start IV": {}
        }
    },
    "Meds": {
        "Epinephrine": {
            "0.3mg_IM": {},
            "0.15mg_IM": {}
        },
        "Naloxone": {
            "2mg_IN": {},
            "0.4mg_IM": {}
        },
        "Oral Glucose": {
            "15g_PO": {}
        },
        "Aspirin": {
            "324mg_PO": {}
        }
    },
    "Triage": {
        "Immediate": {},
        "Delayed": {},
        "Expectant": {}
    },
    "Transport": {
        "Go to ED": {},
        "Wait for ALS": {}
    }
}
