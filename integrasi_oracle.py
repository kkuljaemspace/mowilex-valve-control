import requests
from requests.auth import HTTPBasicAuth
import json

# Kredensial dan API Key untuk live
LIVE_USERNAME = "dkp.rfid"
LIVE_PASSWORD = "KPX_Y0A@mwl25"
LIVE_API_KEY = "zeOCUvyYrMSn2WrRFhnoFPbCTDldqej3AullXpQdfwQju"

# Base URL untuk live
LIVE_BASE_URL = "https://mowilex-live.epicorsaas.com/server/api/v2/odata/mwl/BaqSvc"



def get_po_check_live(ponum: int):
    url = f"{LIVE_BASE_URL}/MWL_POCheck/Data?PONum={ponum}"
    headers = {
        "X-Api-Key": LIVE_API_KEY
    }
    response = requests.get(url, auth=HTTPBasicAuth(LIVE_USERNAME, LIVE_PASSWORD), headers=headers)
    response.raise_for_status()
    return response.json()


def get_po_check_summary_live(ponum: int):
    url = f"{LIVE_BASE_URL}/MWL_POCheckSummary/Data?PONum={ponum}"
    headers = {
        "X-Api-Key": LIVE_API_KEY
    }
    response = requests.get(url, auth=HTTPBasicAuth(LIVE_USERNAME, LIVE_PASSWORD), headers=headers)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    po_number_live = 23343

    # Mendapatkan detail PO Check dari live
    live_detail = get_po_check_live(po_number_live)
    print("Live - PO Check Detail (Pretty Print):")
    print(json.dumps(live_detail, indent=4))

    # Simpan ke file JSON
    with open("live_po_check_detail.json", "w") as f:
        json.dump(live_detail, f, indent=4)

    # Mendapatkan summary PO Check dari live
    live_summary = get_po_check_summary_live(po_number_live)
    print("Live - PO Check Summary (Pretty Print):")
    print(json.dumps(live_summary, indent=4))

    # Simpan ke file JSON
    with open("live_po_check_summary.json", "w") as f:
        json.dump(live_summary, f, indent=4)
