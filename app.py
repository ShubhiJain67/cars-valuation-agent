"""
Web UI for the car valuation tool.

Run: streamlit run app.py
"""
from datetime import date

import pandas as pd
import streamlit as st

from constants.car import BODY_TYPES, FUELS, MAX_KM, MAX_OWNERS, SEVERITIES, TRANSMISSIONS
from constants.parts import CATEGORIES, PARTS
from main import validate_request
from services.images import MAX_IMAGES, process_images
from services.nearest_cars import LISTINGS
from services.valuation import get_valuation

OTHER_MODEL = "Other model (type it)"

st.set_page_config(page_title="Car Valuation", layout="wide")


def inr(amount: int) -> str:
    """Indian digit grouping: 1234567 -> ₹12,34,567"""
    digits = str(int(round(amount)))
    if len(digits) > 3:
        head, tail = digits[:-3], digits[-3:]
        head = ",".join([head[max(i - 2, 0):i] for i in range(len(head), 0, -2)][::-1])
        digits = f"{head},{tail}"
    return f"₹{digits}"


def lakh(amount: int) -> str:
    return f"₹{amount / 100_000:.2f} L"


def severity_label(part: str, severity: str) -> str:
    level = int(severity[-1])
    return f"{level} · {CATEGORIES[PARTS[part][1]][level - 1]}"


@st.cache_data
def models_by_name() -> pd.DataFrame:
    """Most common body type, fuel and transmission per model, for sensible defaults."""
    return LISTINGS.groupby("name").agg(
        body_type=("body_type", lambda s: s.mode()[0]),
        fuel=("fuel", lambda s: s.mode()[0]),
        transmission=("transmission", lambda s: s.mode()[0]),
        listings=("name", "size"),
    )


# ---------------------------------------------------------------- inputs
st.title("Car Valuation")
st.caption("Market value from comparable Cars24 listings, minus the cost of repairing visible damage.")

models = models_by_name()
details, condition = st.columns([1, 1.25], gap="large")

with details:
    st.subheader("Car details")
    choice = st.selectbox("Model", sorted(models.index) + [OTHER_MODEL], index=None,
                          placeholder="Start typing, e.g. Maruti Swift", key="model")
    car = st.text_input("Model name (make first, e.g. Maruti Fronx)", key="custom_model") \
        if choice == OTHER_MODEL else choice
    known = models.loc[choice] if choice in models.index else None

    c1, c2 = st.columns(2)
    year = c1.number_input("Registration year", 2000, date.today().year, 2020, key="year")
    km = c2.number_input("Kilometres driven", 0, MAX_KM - 1, 30_000, step=1_000, key="km")
    c1, c2 = st.columns(2)
    owners = c1.number_input("Owners so far", 1, MAX_OWNERS, 1, key="owners")
    state = c2.text_input("Registration state (optional)", max_chars=2, placeholder="DL", key="state")

    def pick(column, label, options, default, key):
        options = list(options)
        index = options.index(default) if default in options else 0
        return column.selectbox(label, options, index=index, key=f"{key}_{choice}")

    c1, c2, c3 = st.columns(3)
    fuel = pick(c1, "Fuel", FUELS, known["fuel"].upper() if known is not None else None, "fuel")
    transmission = pick(c2, "Transmission", [t.title() for t in TRANSMISSIONS],
                        known["transmission"].title() if known is not None else None, "transmission")
    body_type = pick(c3, "Body type", BODY_TYPES, known["body_type"] if known is not None else None, "body")
    if known is not None:
        st.caption(f"{known['listings']} listings of this model in the data.")

with condition:
    st.subheader("Condition")
    photos_tab, manual_tab = st.tabs(["Upload photos", "Enter damage manually"])
    with photos_tab:
        st.markdown(
            f"Upload up to {MAX_IMAGES} photos. **At least one must show the number plate**, and every photo "
            "must show the same registration number, on the plate or written on paper. Photos without it "
            "are discarded."
        )
        uploads = st.file_uploader("Car photos", type=["jpg", "jpeg", "png", "webp"],
                                   accept_multiple_files=True, label_visibility="collapsed")
        if uploads:
            st.image([u.getvalue() for u in uploads], width=110, caption=[u.name for u in uploads])
    with manual_tab:
        parts = st.multiselect("Damaged parts", list(PARTS), format_func=lambda p: PARTS[p][0])
        manual_damages = {}
        for part in parts:
            manual_damages[part] = st.radio(
                PARTS[part][0].capitalize(), SEVERITIES, horizontal=True, key=f"sev_{part}",
                format_func=lambda s, p=part: severity_label(p, s),
            )

use_photos = bool(uploads)
button_label = "Check photos and value the car" if use_photos else "Value the car"
run = st.button(button_label, type="primary", disabled=not car)
if not car:
    st.caption("Choose a model to continue.")
elif use_photos and manual_damages:
    st.caption("Photos are uploaded, so damage comes from the photos and the manual entries are ignored.")

# ---------------------------------------------------------------- run
if run:
    request = {
        "car": car, "year": int(year), "km_driven": int(km), "owner_count": int(owners), "fuel": fuel,
        "transmission": transmission, "body_type": body_type, "state": state.upper() or None,
        "damages": manual_damages,
    }
    photo_result = None
    try:
        if use_photos:
            with st.spinner("Reading number plates and checking for damage…"):
                photo_result = process_images([(u.name, u.getvalue()) for u in uploads])
            request["damages"] = photo_result["damages"]
        with st.spinner("Checking the model and finding comparable cars…"):
            errors = [] if use_photos and not photo_result["accepted"] else validate_request(**request)
            valuation = None if errors or (use_photos and not photo_result["accepted"]) else get_valuation(**request)
        st.session_state.result = {"request": request, "photos": photo_result, "errors": errors,
                                   "valuation": valuation, "previews": {u.name: u.getvalue() for u in uploads or []}}
    except ValueError as e:  # e.g. not enough comparable cars
        st.session_state.result = {"notice": str(e)}
    except Exception as e:  # LLM or network failures should show up in the page, not crash it
        st.session_state.result = {"failure": str(e)}

# ---------------------------------------------------------------- results
result = st.session_state.get("result")
if result:
    st.divider()
    if "notice" in result:
        st.warning(result["notice"])
        st.stop()
    if "failure" in result:
        st.error(f"Something went wrong: {result['failure']}")
        st.stop()

    photos = result["photos"]
    if photos:
        st.subheader("Photo check")
        if photos["registration_number"]:
            st.markdown(f"Registration number from the plate: **{photos['registration_number']}**")
        cards = [(a["image"], "Used", f"number on {a['shown_on'].replace('_', ' ')}") for a in photos["accepted"]]
        cards += [(r["image"], "Discarded", r["reason"]) for r in photos["rejected"]]
        for row_start in range(0, len(cards), 4):
            for column, (name, status, note) in zip(st.columns(4), cards[row_start:row_start + 4]):
                with column:
                    if name in result["previews"]:
                        st.image(result["previews"][name], width="stretch")
                    (st.success if status == "Used" else st.error)(f"**{status}** · {name}\n\n{note}")
        if not photos["accepted"]:
            st.error("No usable photos. Include at least one clear photo of the number plate.")
            st.stop()
        if photos["findings"]:
            st.markdown("**Damage found in the photos**")
            st.dataframe(pd.DataFrame([{
                "Part": PARTS[f["part"]][0].capitalize(),
                "Repair needed": severity_label(f["part"], f["severity"]),
                "What we see": f["description"],
                "Confidence": f"{f['confidence']:.0%}",
                "Priced": "Yes" if f["priced"] else "No (low confidence)",
                "Photos": ", ".join(f["images"]),
            } for f in photos["findings"]]), hide_index=True, width="stretch")
        else:
            st.info("No visible damage found in the photos.")
        if photos.get("unclear_areas"):
            st.caption("Could not judge from these photos: " + ", ".join(photos["unclear_areas"]))

    if result["errors"]:
        st.error("Please fix these details:\n\n" + "\n".join(f"- {e}" for e in result["errors"]))
        st.stop()

    v = result["valuation"]
    st.subheader("Valuation")
    m1, m2, m3 = st.columns(3)
    m1.metric("Final price", lakh(v["final_price"]))
    m2.metric("Market value in good condition", lakh(v["base_price"]))
    m3.metric("Repairs", inr(v["repair_total"]))
    st.markdown(f"Likely range **{inr(v['final_low'])} – {inr(v['final_high'])}**, "
                f"from {len(v['comparables'])} comparable {v.get('car_class', '')} listings ({v['exact_matches']} exact "
                "matches on model, fuel and transmission).")

    left, right = st.columns([1.6, 1], gap="large")
    with left:
        st.markdown("**Comparable listings**")
        st.caption("Listed on Cars24 in 2023; the last column ages each price to your car's age today.")
        st.dataframe(pd.DataFrame([{
            "Model": c["name"].title(), "Fuel": c["fuel"].title(), "Gearbox": c["transmission"].title(),
            "Year": c["year"], "Km": f"{c['km']:,}", "Owners": c["owner"], "State": c["state"],
            "Listed at": inr(c["listed_price"]), "Worth now": inr(c["price_at_your_age"]),
            "Distance": c["distance"],
        } for c in v["comparables"]]), hide_index=True, width="stretch")
    with right:
        st.markdown("**Repair costs**")
        if v["repair_breakdown"]:
            damages = result["request"]["damages"]
            st.dataframe(pd.DataFrame([{
                "Part": PARTS[p][0].capitalize(), "Repair": severity_label(p, damages[p]), "Cost": inr(cost),
            } for p, cost in v["repair_breakdown"].items()]), hide_index=True, width="stretch")
        else:
            st.caption("No damage entered.")
