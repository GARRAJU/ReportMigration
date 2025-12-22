# import requests
# import pandas as pd
# import os
# import json

# # =====================================================
# # CONFIGURATION
# # =====================================================


# TENANT_ID = os.getenv("POWERBI_TENANT_ID")
# CLIENT_ID = os.getenv("POWERBI_CLIENT_ID")
# CLIENT_SECRET = os.getenv("POWERBI_CLIENT_SECRET")

# if not TENANT_ID or not CLIENT_ID or not CLIENT_SECRET:
#     raise Exception("Power BI credentials missing in App Settings")


# # ✅ EXISTING WORKSPACE
# WORKSPACE_ID = "90062faa-3344-4bf4-8dc9-f5f54f38d8bf"

# # ✅ EXCEL FILE PATH
# EXCEL_PATH = r"C:\Users\GarrajuNaralasetti(Q\Downloads\updated_candidate_data.xlsx"

# DATASET_NAME = "Excel_Push_Dataset"
# TABLE_NAME = "MainTable"

# POWERBI_SCOPE = "https://analysis.windows.net/powerbi/api/.default"

# # =====================================================
# # STEP 1: VERIFY EXCEL FILE
# # =====================================================

# if not os.path.exists(EXCEL_PATH):
#     raise FileNotFoundError(f"❌ Excel file not found:\n{EXCEL_PATH}")

# print("✅ Excel file found")

# # =====================================================
# # STEP 2: AUTHENTICATION
# # =====================================================

# print("🔐 Getting Power BI access token...")

# token_url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"

# payload = {
#     "grant_type": "client_credentials",
#     "client_id": CLIENT_ID,
#     "client_secret": CLIENT_SECRET,
#     "scope": POWERBI_SCOPE
# }

# token_response = requests.post(token_url, data=payload)
# token_response.raise_for_status()

# access_token = token_response.json()["access_token"]

# headers = {
#     "Authorization": f"Bearer {access_token}",
#     "Content-Type": "application/json"
# }

# print("✅ Access token acquired")

# # =====================================================
# # STEP 3: READ EXCEL DATA
# # =====================================================

# print("📊 Reading Excel data...")

# df = pd.read_excel(EXCEL_PATH)

# print("✅ Excel loaded successfully")
# print(df.head())
# print(df.dtypes)

# # =====================================================
# # STEP 4: BUILD DATASET SCHEMA
# # =====================================================

# def map_dtype(dtype):
#     dtype = str(dtype).lower()
#     if "int" in dtype:
#         return "Int64"
#     if "float" in dtype:
#         return "Double"
#     if "datetime" in dtype:
#         return "DateTime"
#     return "String"

# columns = [
#     {"name": col, "dataType": map_dtype(df[col].dtype)}
#     for col in df.columns
# ]

# dataset_payload = {
#     "name": DATASET_NAME,
#     "defaultMode": "Push",
#     "tables": [
#         {
#             "name": TABLE_NAME,
#             "columns": columns
#         }
#     ]
# }

# # =====================================================
# # STEP 5: CREATE DATASET
# # =====================================================

# print("📦 Creating Push Dataset in Power BI...")

# dataset_url = f"https://api.powerbi.com/v1.0/myorg/groups/{WORKSPACE_ID}/datasets"

# dataset_response = requests.post(
#     dataset_url,
#     headers=headers,
#     json=dataset_payload
# )

# dataset_response.raise_for_status()

# DATASET_ID = dataset_response.json()["id"]

# print(f"✅ Dataset created successfully")
# print(f"🆔 Dataset ID: {DATASET_ID}")

# # =====================================================
# # STEP 6: DATA SANITIZATION (CRITICAL)
# # =====================================================

# print("🧹 Sanitizing data for JSON compliance...")

# # Convert datetime columns to ISO string
# for col in df.columns:
#     if pd.api.types.is_datetime64_any_dtype(df[col]):
#         df[col] = df[col].dt.strftime("%Y-%m-%dT%H:%M:%S")

# # Replace all NaN / INF values
# df = df.replace({pd.NA: None})
# df = df.replace({float("nan"): None})
# df = df.replace({float("inf"): None, float("-inf"): None})

# # Ensure object dtype and clean None values
# df = df.astype(object).where(pd.notnull(df), None)

# print("✅ Data sanitization completed")

# # =====================================================
# # STEP 7: PUSH DATA INTO DATASET
# # =====================================================

# print("⬆️ Pushing rows into Power BI dataset...")

# rows_payload = {
#     "rows": df.to_dict(orient="records")
# }


# json.dumps(rows_payload)

# push_url = (
#     f"https://api.powerbi.com/v1.0/myorg/groups/{WORKSPACE_ID}"
#     f"/datasets/{DATASET_ID}/tables/{TABLE_NAME}/rows"
# )

# push_response = requests.post(
#     push_url,
#     headers=headers,
#     json=rows_payload
# )

# push_response.raise_for_status()

# print("🎉 DATA PUSH COMPLETED SUCCESSFULLY")




#---------------------------------------------------------------------------------------------

import requests
import pandas as pd
import os
import json
from msal import ConfidentialClientApplication

# =====================================================
# CONFIGURATION
# =====================================================

TENANT_ID = os.getenv("POWERBI_TENANT_ID")
CLIENT_ID = os.getenv("POWERBI_CLIENT_ID")
CLIENT_SECRET = os.getenv("POWERBI_CLIENT_SECRET")

# TARGET WORKSPACE (DATA + REPORT WILL GO HERE)
WORKSPACE_ID = "f529bc3a-dfdc-49fc-99cc-94a61985480b"

# MASTER TEMPLATE
TEMPLATE_WORKSPACE_ID = "90062faa-3344-4bf4-8dc9-f5f54f38d8bf"
TEMPLATE_REPORT_ID = "3cf615ca-6afb-4259-bda1-b91a8848892e"

# EXCEL FILE
EXCEL_PATH = r"C:\Users\GarrajuNaralasetti(Q\Downloads\updated_candidate_data.xlsx"

DATASET_NAME = "Excel_Push_Dataset"
TABLE_NAME = "MainTable"

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["https://analysis.windows.net/powerbi/api/.default"]
API_ROOT = "https://api.powerbi.com/v1.0/myorg"

# =====================================================
# STEP 1: AUTHENTICATION
# =====================================================

print("🔐 Authenticating with Power BI...")

app = ConfidentialClientApplication(
    CLIENT_ID,
    authority=AUTHORITY,
    client_credential=CLIENT_SECRET
)

token = app.acquire_token_for_client(scopes=SCOPE)

if "access_token" not in token:
    raise Exception(f"Authentication failed: {token}")

access_token = token["access_token"]

HEADERS = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

print("✅ Authentication successful")

# =====================================================
# STEP 2: READ EXCEL
# =====================================================

if not os.path.exists(EXCEL_PATH):
    raise FileNotFoundError(f"Excel not found: {EXCEL_PATH}")

print("📊 Reading Excel file...")
df = pd.read_excel(EXCEL_PATH)

# =====================================================
# STEP 3: BUILD DATASET SCHEMA
# =====================================================

def map_dtype(dtype):
    dtype = str(dtype).lower()
    if "int" in dtype:
        return "Int64"
    if "float" in dtype:
        return "Double"
    if "datetime" in dtype:
        return "DateTime"
    return "String"

columns = [
    {"name": col, "dataType": map_dtype(df[col].dtype)}
    for col in df.columns
]

dataset_payload = {
    "name": DATASET_NAME,
    "defaultMode": "Push",
    "tables": [
        {
            "name": TABLE_NAME,
            "columns": columns
        }
    ]
}

# =====================================================
# STEP 4: CREATE DATASET
# =====================================================

print("📦 Creating dataset...")

dataset_response = requests.post(
    f"{API_ROOT}/groups/{WORKSPACE_ID}/datasets",
    headers=HEADERS,
    json=dataset_payload
)

dataset_response.raise_for_status()
DATASET_ID = dataset_response.json()["id"]

print("✅ Dataset created:", DATASET_ID)

# =====================================================
# STEP 5: DATA SANITIZATION
# =====================================================

for col in df.columns:
    if pd.api.types.is_datetime64_any_dtype(df[col]):
        df[col] = df[col].dt.strftime("%Y-%m-%dT%H:%M:%S")

df = df.astype(object).where(pd.notnull(df), None)

# =====================================================
# STEP 6: PUSH DATA
# =====================================================

print("⬆️ Pushing data...")

rows_payload = {
    "rows": df.to_dict(orient="records")
}

push_response = requests.post(
    f"{API_ROOT}/groups/{WORKSPACE_ID}/datasets/{DATASET_ID}/tables/{TABLE_NAME}/rows",
    headers=HEADERS,
    json=rows_payload
)

push_response.raise_for_status()

print("✅ Data pushed successfully")

# =====================================================
# STEP 7: CLONE TEMPLATE REPORT
# =====================================================

print("📄 Cloning template report...")

clone_payload = {
    "name": "blankreport_withdataset",
    "targetWorkspaceId": WORKSPACE_ID,
    "targetModelId": DATASET_ID
}

clone_response = requests.post(
    f"{API_ROOT}/groups/{TEMPLATE_WORKSPACE_ID}/reports/{TEMPLATE_REPORT_ID}/Clone",
    headers=HEADERS,
    json=clone_payload
)

if clone_response.status_code != 200:
    print("⚠️ Clone failed (likely due to Push dataset limitation)")
    print(clone_response.text)
else:
    NEW_REPORT_ID = clone_response.json()["id"]
    print("✅ Report cloned:", NEW_REPORT_ID)

    # =====================================================
    # STEP 8: REBIND (SAFE)
    # =====================================================

    rebind_payload = {"datasetId": DATASET_ID}

    requests.post(
        f"{API_ROOT}/groups/{WORKSPACE_ID}/reports/{NEW_REPORT_ID}/Rebind",
        headers=HEADERS,
        json=rebind_payload
    )

    print("✅ Report rebound")

# =====================================================
# DONE
# =====================================================

print("\n🎉 PIPELINE COMPLETED")
print("➡️ Dataset created")
print("➡️ Data pushed")
print("➡️ Report cloned (if supported)")





