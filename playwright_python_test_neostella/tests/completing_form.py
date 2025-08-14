import csv
import re
from math import hypot
from playwright.sync_api import Page

# ---------- Data Drive Execution ----------

def get_csv_data():

    """
    Load test data from a CSV file.
    The CSV should have a header row and the following fields per row:
        EIN, company name, sector, address, automation tool, annual saving,
        date of first project, username, password
    """
    data = []
    with open("./ddt/ddt_5iterations.csv", newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # skip header
        for row in reader:
            data.append(row)
    return data

# ---------- Text helpers ----------

def norm(text: str) -> str:

    """Lowercase + remove non-alphanumerics for fuzzy match."""

    return re.sub(r'[^a-z0-9]', '', text.lower())

def text_matches_keywords(text: str, keywords: list[str]) -> bool:

    """
    Return True if all keywords appear in text (case-insensitive, alphanumeric-only).
    This allows us to survive slight text changes, extra spaces, or punctuation.
    """

    nt = norm(text)
    return all(norm(k) in nt for k in keywords)

# ---------- Element helpers ----------

def visible_bounding_box(locator):

    """Returns bounding box dict or None if not visible.
    Checks if an element is visible on the page and, if so, returns its geometric coordinates.
    """
    try:
        bb = locator.bounding_box()
        return bb  # None if not visible
    except Exception:
        return None

def center(bb):
    
    """Return the (x, y) center point of a bounding box.
    Takes the top-left corner (x, y) and adds half the width and height:
    When we are looking for the nearest input to a label, we compare distances between their centers.

    """

    return (bb["x"] + bb["width"]/2.0, bb["y"] + bb["height"]/2.0)

def manhattan(a, b):

    """Return Manhattan distance between two (x, y) points.
    This is different from straight-line (Euclidean) distance — Manhattan distance is like counting blocks in 
    a grid (no diagonals).
    For form layouts, the nearest element is often visually closest in grid alignment, 
    so Manhattan distance tends to work better for matching labels and inputs than Euclidean.
    """

    return abs(a[0]-b[0]) + abs(a[1]-b[1])

# ---------- Core: find nearest input to label text ----------

def fill_by_near_text(page: Page, keywords: list[str], value: str, used_indexes: set[int]) -> bool:

    """
    1) Find a label-like text element whose text contains all 'keywords'
    2) Find the nearest input to that text (by geometry Manhattan method)
    3) Fill it. Avoid reusing the same input within the same iteration via used_indexes.
    Returns True if filled, else False.

    This approach survives DOM reshuffles after form submission
    by re-locating fresh elements each time.

    """
    # All candidate text elements that might act as labels
    label_els = page.locator("//label | //div | //span | //p")

    label_count = label_els.count()
    best_label_idx = None
    best_label_bb = None

    # Pick the first visible label whose text matches keywords (you can add tie-breaks if needed)
    for i in range(label_count):
        lab = label_els.nth(i)
        bb = visible_bounding_box(lab)
        if not bb:
            continue
        text = lab.inner_text(timeout=1000).strip()
        if not text:
            continue
        if text_matches_keywords(text, keywords):
            best_label_idx = i
            best_label_bb = bb
            break

    if best_label_idx is None:
        # No label matched — caller can decide to fallback to next empty input
        return False

    label_center = center(best_label_bb)

    # Candidate inputs: include <input>, <textarea>, and contenteditable elements
    inputs = page.locator("//input")
    inputs_count = inputs.count()

    best_input_idx = None
    best_dist = float("inf")

    for j in range(inputs_count):
        inp = inputs.nth(j)
        bb = visible_bounding_box(inp)
        if not bb:
            continue

        # Skip disabled inputs
        try:
            disabled = inp.evaluate("el => el.disabled === true")
            if disabled:
                continue
        except Exception:
            pass

        # Avoid reusing an input in the same iteration
        if j in used_indexes:
            continue

        d = manhattan(center(bb), label_center)
        if d < best_dist:
            best_dist = d
            best_input_idx = j

    if best_input_idx is None:
        return False

    # Fill the chosen input
    target = inputs.nth(best_input_idx)

    # Try input_value() where possible; fallback to type/fill
    try:
        target.fill(value)
    except Exception:
        # contenteditable fallbacks
        try:
            target.click()
            target.press("Control+A")
            target.type(value, delay=0)
        except Exception:
            return False

    used_indexes.add(best_input_idx)
    return True

# ---------- Fallback: fill next visible empty input ----------

def fill_next_empty_input(page: Page, value: str, used_indexes: set[int]) -> bool:

    """
    If no label match is found, fill the next visible and empty <input>.
    This is a last-resort safety net for unexpected label changes.
    """

    inputs = page.locator("//input")
    count = inputs.count()

    for j in range(count):
        if j in used_indexes:
            continue
        el = inputs.nth(j)
        if not visible_bounding_box(el):
            continue

        # Check if empty (best-effort across inputs)
        is_empty = False
        try:
            # For standard inputs/textareas
            current = el.input_value(timeout=500)
            is_empty = (current or "").strip() == ""
        except Exception: pass

        if is_empty:
            try:
                el.fill(value)
            except Exception:
                try:
                    el.click()
                    el.press("Control+A")
                    el.type(value, delay=0)
                except Exception:
                    continue
            used_indexes.add(j)
            return True
    return False

# ---------- Test: re-scan + map by label-nearest every iteration ----------

def test_dynamic_form(page: Page):

    """
    Main test:
        - Loads CSV data
        - Logs in once
        - Iterates through all rows
        - Fills all 8 fields using label proximity or fallback
        - Clicks submit, survives DOM reshuffles
        - Optionally clicks reCAPTCHA popup if present
    """

    rows = get_csv_data()
    page.goto("https://www.theautomationchallenge.com/")

    for idx, row in enumerate(rows, start=1):
        (
            employer_identification_number,
            company_name,
            sector,
            company_address,
            automation_tool,
            annual_automation_saving,
            date_of_first_project,
            user_name,
            password
        ) = row

        # Login only once
        if idx == 1:
            page.get_by_role("button", name="SIGN UP OR LOGIN").click()
            page.get_by_role("button", name="OR LOGIN", exact=True).click()
            page.get_by_role("textbox", name="Email").fill(user_name)
            page.get_by_role("textbox", name="Password").fill(password)
            page.get_by_role("button", name="LOG IN").click()
            page.wait_for_timeout(3000)
            page.get_by_role("button", name="Start").click()
            page.wait_for_timeout(3000)


        print(f"=== Processing row {idx}/{len(rows)}: {company_name} ===")

        # Re-scan & fill: do NOT reuse locators across submissions
        used_inputs = set()

        # Define your field → keyword mapping (use multiple tokens to survive label merges)
        fields = [
            (["ein", "employer"], employer_identification_number),
            (["company", "name"], company_name),
            (["sector"], sector),
            (["company", "address"], company_address),
            (["automation", "tool"], automation_tool),
            (["annual", "automation", "saving"], annual_automation_saving),
            (["date"], date_of_first_project),
            # If there’s an 8th custom field, add keywords here:
            # (["some", "label"], some_value),
        ]

        for keywords, value in fields:
            ok = fill_by_near_text(page, keywords, value, used_inputs)
            if not ok:
                # Last-resort fallback: fill next empty visible input
                filled = fill_next_empty_input(page, value, used_inputs)
                if not filled:
                    print(f"⚠️ Could not place value for keywords {keywords}")


        
        # Submit and wait for the reshuffle
        page.get_by_role("button", name="Submit").click()
