"""
Global intervention tree defining category → action → detail structure.
Aligned with NREMT patient assessment model.
"""

TREE = {
    "Scene": {
        "Scene Safety": {
            "BSI/PPE": {},
            "Scene Safe?": {}
        },
        "Determine nature of Illness": {},
        "Determine the number of patients": {},
        "Additional Resources": {
            "ALS Request": {},
            "Police/Fire": {},
            "HAZMAT": {},
            "Utility Company": {}
        },
        "Spine stabilization": {
            "Stabilize spine": {},
            "Don't stabilize spine": {}
        }
    },

    "Primary Assessment": {
        "General Impression": {},
        "Determine responsiveness/level of consciousness (AVPU)": {},
        "Airway": {
            "Open Airway": {
                "Head Tilt-Chin Lift": {},
                "Jaw Thrust": {}
            },
        },
        "Breathing": {
            "Assess Breathing": {
                "Rate/Quality": {}
            },
            "Administer O2": {
                "NC": {},
                "NRB": {},
                "BVM Ventilation": {},
                "CPAP": {}
            }
        },
        "Circulation": {
            "Control Bleeding": {
                "Direct Pressure": {},
                "Pressure Dressing": {},
                "Tourniquet": {}
            },
            "Pulse Check": {}
        },
        "History Taking": {
            "History of present illness": {
                "Onset": {},
                "Provocation": {},
                "Quality": {},
                "Radiation": {},
                "Severity": {},
                "Time": {},
            },
            "Past medical history": {
                "Signs and Symptoms": {},
                "Allergies": {},
                "Medications": {},
                "Past medical history": {},
                "Last oral intake": {},
                "Events leading up to the incident": {}
            }
        }
    },

    "Secondary Assessment": {
        "Vital Signs": {
            "HR": {},
            "RR": {},
            "BP": {},
            "D-stick": {},
        }
    },

    "Medications": {
        "Oxygen": {
            "NC": {},
            "SVN": {},
            "NRB": {},
            "BVM": {},
            "CPAP": {}
        },
        "Albuterol": {
            "SVN": {},
            "MDI": {}
        },
        "Aspirin": {
            "160-325 mg"
        },
        "Nitroglycerin": {
            "0.4 mg pill/spray": {},
        },
        "Oral Glucose": {
            "1 tube PO": {}
        },
        "Glucagon": {
            "1 mg IN per nostril (max 2 mg)": {}
        },
        "Epinephrine": {
            "0.3 mg IM (Adult auto-injector)": {},
            "0.15 mg IM (Peds auto-injector)": {}
        },
        "Naloxone": {
            "2 mg IN (1 mg/nostril)": {},
            "Repeat q5 min PRN": {}
        }
    },
}
