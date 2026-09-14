# Privacy Policy — APSRTC Report Automation

_Last updated: September 14, 2026_

APSRTC Report Automation is a private operational reporting utility used by its authorized owner/operator. This policy explains how the application handles information when Google account access is authorized.

## Information the application accesses

The application may access Google Drive and Google Sheets data that the authorized user permits through Google OAuth. This access is used only for the reporting functions requested by the user.

## How information is used

Google account access is used only to:

- Create, update, and read reporting spreadsheets required by the automation.
- Upload, locate, and manage generated report files in the user's Google Drive.
- Prevent duplicate report creation where the reporting workflow requires an existing-file check.

The application does not use Google account data for advertising, profiling, marketing, or sale.

## Data sharing

The application does not sell Google user data and does not intentionally share Google user data with third parties. Data is processed only as necessary to run the user's reporting automation and through the infrastructure selected by the user, including GitHub Actions and Google services.

## Data storage and credentials

OAuth credentials and refresh tokens used by the automation are stored as protected GitHub Actions secrets and are not committed to the public repository. Generated reports may be stored in the user's Google Drive and, where configured, temporarily as GitHub Actions workflow artifacts.

## Data retention

Reports remain in the user's Google Drive until the user removes them. Temporary workflow artifacts are subject to the retention period configured in the GitHub Actions workflow. The application itself does not maintain a separate commercial user database.

## Revoking access

The user may revoke the application's access to their Google account at any time through their Google Account security settings. The user may also remove or replace the OAuth credentials and refresh token used by the GitHub Actions workflows.

## Security

Reasonable measures are used to protect credentials, including storing sensitive OAuth values as GitHub Actions secrets rather than in source code. No method of electronic storage or transmission can be guaranteed to be completely secure.

## Children's privacy

This application is not intended for use by children and does not knowingly collect personal information from children.

## Changes to this policy

This policy may be updated if the application's reporting workflow or Google service usage changes. The latest version will remain available at this page.

## Contact

For privacy questions or requests related to this application, contact the developer through the support email shown on the application's Google OAuth consent screen.
