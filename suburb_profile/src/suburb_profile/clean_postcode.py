import pandas as pd

URL_BASE = "https://www.domain.com.au/suburb-profile/"

# Load CSV
df = pd.read_csv("postcode_raw.csv")

# Remove PO Boxes
df = df[df['category'] != "Post Office Boxes"]

# Drop unnecessary columns
df = df.drop(columns=["category","url"])

# Remove duplicates
df = df.drop_duplicates(subset=["suburb","state", "postcode"])

# Convert to lowercase, strip whitespace
df["suburb"] = df["suburb"].str.lower().str.strip()
df["state"] = df["state"].str.lower().str.strip()
df["details"] = df["details"].str.lower().str.strip()

# Normalize postcode to 4 digits (pad with leading zeros)
df["postcode"] = df["postcode"].astype(str).str.zfill(4)

# Clean suburb: replace space to hyphen
df["suburb_hyphen"] = df["suburb"].str.replace(" ", "-", regex=False)

#Create new link column
df["link"] = URL_BASE + df["suburb_hyphen"] + "-" + df["state"] + "-" + df["postcode"]

# Save to CSV
df.to_csv("url_domain.csv", index=False)