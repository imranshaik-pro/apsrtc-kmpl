"""Google Sheets helpers using the same OAuth credentials as Drive automation."""

from googleapiclient.discovery import build

from src.integrations.google_drive import _credentials


def sheets_service():
    return build("sheets", "v4", credentials=_credentials(), cache_discovery=False)


def read_values(spreadsheet_id: str, range_name: str):
    return (
        sheets_service()
        .spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range=range_name)
        .execute()
        .get("values", [])
    )


def write_values(spreadsheet_id: str, range_name: str, values):
    return (
        sheets_service()
        .spreadsheets()
        .values()
        .update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="RAW",
            body={"values": values},
        )
        .execute()
    )


def sheet_id(spreadsheet_id: str, title: str):
    meta = (
        sheets_service()
        .spreadsheets()
        .get(spreadsheetId=spreadsheet_id, fields="sheets.properties")
        .execute()
    )
    for sheet in meta.get("sheets", []):
        props = sheet.get("properties", {})
        if props.get("title") == title:
            return props.get("sheetId")
    return None


def ensure_hidden_sheet(spreadsheet_id: str, title: str):
    sid = sheet_id(spreadsheet_id, title)
    if sid is not None:
        return sid
    result = (
        sheets_service()
        .spreadsheets()
        .batchUpdate(
            spreadsheetId=spreadsheet_id,
            body={
                "requests": [
                    {
                        "addSheet": {
                            "properties": {
                                "title": title,
                                "hidden": True,
                            }
                        }
                    }
                ]
            },
        )
        .execute()
    )
    return result["replies"][0]["addSheet"]["properties"]["sheetId"]


def format_number_rows(spreadsheet_id: str, title: str, row_formats: dict[int, str], start_col: int, end_col: int):
    """Apply number formats. row_formats uses 1-based sheet row numbers."""
    sid = sheet_id(spreadsheet_id, title)
    if sid is None:
        return
    requests = []
    for row_number, pattern in row_formats.items():
        requests.append(
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sid,
                        "startRowIndex": row_number - 1,
                        "endRowIndex": row_number,
                        "startColumnIndex": start_col - 1,
                        "endColumnIndex": end_col,
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "numberFormat": {
                                "type": "NUMBER",
                                "pattern": pattern,
                            }
                        }
                    },
                    "fields": "userEnteredFormat.numberFormat",
                }
            }
        )
    if requests:
        sheets_service().spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id, body={"requests": requests}
        ).execute()
