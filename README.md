# APSRTC-KMPL

Automated APSRTC vehicle and regional KMPL reporting application.

## Project Status

- Phase A — Data Discovery — COMPLETE
- Phase B — Calculation & Reporting — COMPLETE
- Phase C — End-to-End Integration — COMPLETE
- Phase D — Final Validation & Testing — COMPLETE
- Phase E — Production Daily Workflow — COMPLETE
- Phase F — Documentation & Finalization — IN PROGRESS
- Phase G — WhatsApp Group Delivery — FUTURE

WhatsApp delivery has not yet been implemented.

## Technology

- Python
- requests
- BeautifulSoup
- Decimal
- python-dotenv

Project commands must use:

    .\.venv\Scripts\python.exe

PowerShell virtual-environment activation is not required.

## Environment Configuration

Create a local `.env` file:

    APSRTC_USERNAME=your_username
    APSRTC_PASSWORD=your_password

Never commit `.env`.

Never hard-code APSRTC credentials.

`.env.example` contains only configuration placeholders.

## Production Daily Report

Run:

    .\.venv\Scripts\python.exe .\run_daily_report.py --date 2026-08-18 --depot PRODDUTUR --vehicle-depot "PDTR/PRODDUTUR" --region-code YSRKADAPA

The runner:

1. Validates the report date.
2. Authenticates using the existing login module.
3. Retrieves the vehicle report.
4. Parses vehicle records.
5. Calculates For-Day KMPL.
6. Calculates Up-To-Day KMPL independently.
7. Builds the vehicle summary.
8. Retrieves the Region report.
9. Parses Region records.
10. Builds the final Telugu report.
11. Saves the report as UTF-8.
12. Displays the report.
13. Returns a non-zero status on failure.

## Report Output

Reports are saved under:

    reports\

Example:

    reports\PRODDUTUR_2026-08-18.txt

For reliable Telugu display in PowerShell:

    Get-Content -Encoding UTF8 .\reports\PRODDUTUR_2026-08-18.txt

## KMPL Calculation

KMPL is calculated as:

    Total Kms / HSD

For-Day and Up-To-Day calculations are independent.

Individual vehicle KMPL values are never averaged.

Duplicate vehicle records are consolidated by:

    Vehicle Number
        |
        v
    Sum Total Kms
        |
        v
    Sum HSD
        |
        v
    Calculate KMPL

Production rounding uses Decimal with ROUND_HALF_UP.

Python `round()` is not used for production APSRTC presentation.

## KMPL Slabs

| Slab | Rule |
|------|------|
| 1 | KMPL <= 5.00 |
| 2 | KMPL > 5.00 and <= 5.10 |
| 3 | KMPL > 5.10 and <= 5.20 |
| 4 | KMPL > 5.20 and <= 5.30 |
| 5 | KMPL > 5.30 |

5.30 belongs to Slab 4.

## Regional Reporting

Regional reporting preserves:

- TOT
- NAC
- AC

The final report uses one aligned table containing:

- Target
- ఈ రోజు
- ఈ రోజు వరకు
- గత నెల
- గత ఇయర్ నెల

Column alignment is generated programmatically.

## Testing

Tests are executed using:

    .\.venv\Scripts\python.exe -m tests.<test_module>

The project contains tests for:

- calculation pipeline
- application integration
- daily workflow
- region formatter
- region parser
- region reporting
- reporting
- Telugu report
- vehicle summary

## Diagnostic Files

`inspect_report.py` is retained as a diagnostic utility for APSRTC vehicle-report troubleshooting.

`region_response.html` is a captured diagnostic APSRTC response.

These are not part of the production execution path.

Generated reports under `reports\` are runtime output.

## Security

The repository must never contain:

    .env

or real APSRTC credentials.

Before committing, verify:

    git ls-files .env

This command must return no output.

`.gitignore` protects:

- `.env`
- `.venv`
- Python cache files
- generated reports
- diagnostic Region HTML
- log files

## Future WhatsApp Integration

WhatsApp delivery is not currently implemented.

Future Phase G will cover:

    Generated validated report
            |
            v
    WhatsApp delivery integration
            |
            v
    Intended WhatsApp group
            |
            v
    Error handling
            |
            v
    Retry behavior
            |
            v
    End-to-end delivery test

A WhatsApp provider/API will be selected only after evaluating its capabilities, authentication, cost, reliability, group-delivery support, and security implications.

## Development Principle

The project follows:

    Simple
    Reliable
    Maintainable
    Accurate
    Low Cost

Established APSRTC endpoints, business rules, calculation rules, rounding rules, slab rules, reporting structure, and Telugu report design must not be changed silently.

