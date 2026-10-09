# (name, category, place)
PARTS = {
    # outside: body
    "front_bumper":     ("front bumper", "body_panel", "outside"),
    "rear_bumper":      ("rear bumper", "body_panel", "outside"),
    "bonnet":           ("bonnet", "body_panel", "outside"),
    "boot_lid":         ("boot lid", "body_panel", "outside"),
    "roof":             ("roof", "body_panel", "outside"),
    "door":             ("door", "body_panel", "outside"),
    "fender":           ("front fender", "body_panel", "outside"),
    "quarter_panel":    ("rear quarter panel", "body_panel", "outside"),
    "body_other":       ("other body part", "body_panel", "outside"),
    # outside: glass and lights
    "windshield":       ("windshield", "glass", "outside"),
    "rear_glass":       ("rear glass", "glass", "outside"),
    "side_window":      ("side window", "glass", "outside"),
    "sunroof":          ("sunroof", "glass", "outside"),
    "headlamp":         ("headlamp", "lamp", "outside"),
    "tail_lamp":        ("tail lamp", "lamp", "outside"),
    "fog_lamp":         ("fog lamp", "lamp", "outside"),
    # outside: fittings and wheels
    "side_mirror":      ("side mirror", "fitting", "outside"),
    "grille":           ("grille", "fitting", "outside"),
    "wiper":            ("wiper", "fitting", "outside"),
    "door_handle":      ("door handle", "fitting", "outside"),
    "number_plate":     ("number plate", "fitting", "outside"),
    "wheel":            ("alloy wheel or wheel cover", "fitting", "outside"),
    "tyre":             ("tyre", "tyre", "outside"),
    # inside: seats and trim
    "seat":             ("seat", "trim", "inside"),
    "seat_cover":       ("seat cover", "trim", "inside"),
    "dashboard":        ("dashboard", "trim", "inside"),
    "door_trim":        ("door trim", "trim", "inside"),
    "roof_lining":      ("roof lining", "trim", "inside"),
    "floor_carpet":     ("floor carpet or mat", "trim", "inside"),
    # inside: controls and electronics
    "steering_wheel":   ("steering wheel", "control", "inside"),
    "gear_lever":       ("gear lever", "control", "inside"),
    "handbrake":        ("handbrake", "control", "inside"),
    "pedals":           ("pedals", "control", "inside"),
    "seat_belt":        ("seat belt", "control", "inside"),
    "inside_mirror":    ("inside rear-view mirror", "control", "inside"),
    "instrument_cluster": ("instrument cluster", "control", "inside"),
    "infotainment":     ("infotainment screen", "control", "inside"),
    "ac_vent":          ("AC vent or controls", "control", "inside"),
    "interior_other":   ("other inside part", "control", "inside"),
    # under the bonnet
    "engine_bay":       ("engine bay", "engine_bay", "under the bonnet"),
}

CATEGORIES = {   # category -> what severity 1, 2 and 3 mean as a repair
    "body_panel": ("polish or touch-up", "repair and repaint the panel", "replace and paint the panel"),
    "glass":      ("chip or small crack repair", "replace the glass", "replace the glass and its surround or mechanism"),
    "lamp":       ("polish or repair the lens", "replace a standard lamp unit", "replace an LED or projector lamp unit"),
    "fitting":    ("minor repair or refit", "replace the part (basic version)", "replace the part (powered or premium version)"),
    "tyre":       ("replace one tyre", "replace two tyres", "replace four tyres"),
    "trim":       ("deep clean or small repair", "repair or re-upholster a section", "replace the part"),
    "control":    ("minor fix or clean", "replace the part", "replace the whole assembly"),
    "engine_bay": ("clean up or fix a small part", "repair a leak or replace a small component", "major repair"),
}
