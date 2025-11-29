from datetime import datetime
import re

def normalize_date(value):
    value = value.strip()
    val_lower = value.lower()

    # Handle "Please Inquire"
    if val_lower == "please inquire":
        return None   # or pd.NaT if using pandas

    # Handle "Early/Mid/Late Month Year"
    match = re.match(r"(early|mid|late)\s+([A-Za-z]+)\s+(\d{4})", value, re.IGNORECASE)
    if match:
        position, month, year = match.groups()
        # Decide day based on position
        if position.lower() == "early":
            day = 5
        elif position.lower() == "mid":
            day = 15
        elif position.lower() == "late":
            day = 25
        try:
            dt = datetime.strptime(f"{day} {month} {year}", "%d %b %Y")
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            return None

    # Handle standard formats like "Apr 7, 2025"
    try:
        dt = datetime.strptime(value, "%b %d, %Y")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return None

if __name__ == "__main__":
    # --tests--
    t1 = normalize_date("Early Nov 2025")
    t2 = normalize_date("Mid Oct 2025")
    t3 = normalize_date("Late Nov 2025")
    t4 = normalize_date("Apr 7, 2025")
    t5 = normalize_date("Please Inquire")

    print(f"{t1}\n{t2}\n{t3}\n{t4}\n{t5}")