# Assetdesk user guide

Version 1.1.0

Assetdesk is a private web application for recording an organization’s IT equipment. It combines an asset register with list-based access, spreadsheet imports, private pictures, service records, assignment history, and an activity log.

This guide is for three audiences:

- **Viewers** who search, review, and export assets in permitted lists.
- **Editors** who also add and update assets and their records in permitted lists.
- **Administrators** who manage the whole application, including users, lists, and access.

## 1. Roles and access

Access is granted by asset list. A list can represent a department, site, company, security boundary, or other grouping such as “Head Office,” “Finance,” or “Warehouse.”

| Capability | Viewer | Editor | Administrator |
| --- | --- | --- | --- |
| See assets in an assigned list | Yes | Yes | All lists |
| Search and filter accessible assets | Yes | Yes | Yes |
| Export accessible asset rows | Yes | Yes | Yes |
| Add or edit assets | No | Assigned lists | All lists |
| Import spreadsheets | No | Assigned lists | All lists |
| Manage pictures, service records, and user history | No | Assigned lists | All lists |
| Create users and lists | No | No | Yes |
| Grant or revoke access | No | No | Yes |

An Editor role on one list does not give access to another list. A user can be a Viewer on one list and an Editor on another. Users without any memberships see no assets. Administrators are superusers and have organization-wide access.

The **Assigned to** value and User history describe possession of equipment. They do not create an application account or grant access.

## 2. Signing in and account security

Open the Assetdesk address supplied by your administrator. Enter your username and password, then select **Sign in**.

After five unsuccessful attempts, Assetdesk temporarily locks sign-in for that username and address for approximately 15 minutes. If you are locked out or forget your password, contact an administrator. Assetdesk has no public password-reset or account-registration page.

To change your password after signing in:

1. Select **Change password** at the bottom of the sidebar.
2. Enter your current password.
3. Enter and confirm the new password.
4. Select **Update password**.

Use a unique password of at least 12 characters. Sign out when you finish using a shared computer.

## 3. Understanding the asset register

The Asset register is the home page. It only includes assets that your account is permitted to see.

The summary cards show:

- **Total assets:** all assets across your accessible lists.
- **Assigned:** assets whose status is Assigned.
- **Available:** assets ready for assignment.
- **Warranty ending:** non-retired assets whose warranty ends within the next 30 days.

The equipment table shows each asset’s name, tag, category, status, current assignee, location, list, and warranty date. Select an asset name to open its details.

### Search and filters

The search box matches asset name, tag, serial number, and assigned employee. You can combine it with the List and Status filters, then select **Apply**. Select **Reset** to clear the current search and filters.

Results are displayed 20 per page. Use **Previous** and **Next** at the bottom of the table.

### Exporting records

Select **Export CSV** to download the rows matching the current search and filters. The export contains:

- Tag
- Asset name
- List
- Category
- Status
- Serial number
- Assigned to
- Location
- Purchase date
- Warranty expiration

The export does not include pictures, notes, service history, user history, or the activity log. Your access rules also apply to exports; inaccessible lists cannot be exported.

## 4. Creating an asset

Editors and administrators can select **Add asset**. Complete the form and select **Save asset**.

| Field | Purpose |
| --- | --- |
| Tag | Unique organization-wide identifier, such as `IT-00421` |
| Name | Clear equipment name, such as `Accounts laptop` |
| Asset list | Determines who can see and edit the asset |
| Category | Laptop, Desktop, Monitor, Server, Network equipment, Printer, Phone, or Other |
| Status | Available, Assigned, In repair, or Retired |
| Manufacturer and Model | Hardware identification |
| Serial number | Manufacturer serial number |
| Assigned to | Current employee name or email; required when status is Assigned |
| Location | Office, floor, room, rack, branch, or other useful location |
| Purchase date | Acquisition date |
| Warranty expires | Warranty end date; cannot precede purchase date |
| Notes | Additional operational information, up to 5,000 characters |

Asset tags must be unique across every list. If a tag cannot be used, choose another tag or ask an administrator to locate the existing record.

Choose the asset list carefully. Moving an asset later is allowed only when you have Editor access to both its current and destination lists. Its details and history move with it.

## 5. Editing an asset

Open an asset and select **Edit asset**. Update the required fields and save.

Every successful creation and edit adds an entry to **Recent activity**, including the responsible account and timestamp. Activity entries are read-only in the administration area.

Changing **Assigned to** through the main asset form automatically closes any current open assignment using today’s date, then creates a new assignment for the new employee using today’s date. For accurate historical dates and return notes, use the User history controls described below.

To remove equipment from active circulation, set its status to **Retired**. Assetdesk does not provide routine asset deletion, preserving the record and history.

## 6. Importing an existing spreadsheet

Editors and administrators can import `.xlsx` or `.csv` files. Each import places every row into one selected destination list.

### Prepare the spreadsheet

Use the first row for column headings. These two columns are required:

- **Tag**
- **Asset** or **Name**

Supported optional headings are:

- Category or Type
- Status
- Manufacturer or Brand
- Model
- Serial number or Serial
- Assigned to or Owner
- Location
- Purchase date
- Warranty expires or Warranty end
- Notes, Description, or Comments

Column headings are not case-sensitive. Extra columns are ignored. Blank rows are skipped.

Use one of these category values: `Laptop`, `Desktop`, `Monitor`, `Server`, `Network`, `Network equipment`, `Printer`, `Phone`, or `Other`. Unrecognized categories are imported as Other.

Use these status values: `available`, `assigned`, `repair`, or `retired`. Unrecognized or blank statuses become Available.

Use real spreadsheet date cells where possible. Text dates may use `YYYY-MM-DD`, `DD/MM/YYYY`, `MM/DD/YYYY`, or `DD-MM-YYYY`. `YYYY-MM-DD` is recommended because it is unambiguous.

### Run the import

1. Select **Import spreadsheet** from the Asset register.
2. Choose the destination list.
3. Select the `.xlsx` or `.csv` file.
4. Select **Import assets**.

Every imported asset receives an “Imported from spreadsheet” activity entry. The import is all-or-nothing: a missing required value, invalid date, or duplicate tag stops the import and prevents partial rows from being saved. Correct the indicated row and upload the file again.

For assigned rows, include an Assigned to value. Review the imported records after a large import, especially categories, statuses, and dates.

## 7. Asset pictures

An asset can have one current picture. Pictures are stored privately and are only returned to signed-in users who can see the asset.

To add or replace a picture:

1. Open the asset.
2. Under **Asset picture**, select **Manage picture**.
3. Choose a JPEG, PNG, or WebP file.
4. Select **Save**.

The original file must be 5 MB or smaller and under 20 megapixels. Assetdesk corrects camera orientation, resizes large pictures to fit within 1600 × 1600 pixels, and stores the result as JPEG.

To remove the current picture, open **Manage picture**, select **Remove current picture**, and save. Removing a picture does not remove the asset or its histories.

Good asset pictures show the whole device and its identifying label without exposing passwords, personal messages, access cards, or other sensitive material.

## 8. Service history

Use service history to document repairs, inspections, upgrades, and preventive maintenance.

1. Open the asset.
2. Under **Service history**, select **Add service**.
3. Enter the service date, issue, and work performed.
4. Optionally enter the provider, cost, three-letter currency code, and next service date.
5. Select **Save**.

The service date, issue, and work performed are required. Cost cannot be negative; when a cost is entered, currency is required. Use codes such as `BDT`, `USD`, or `EUR`. The next service date cannot precede the service date.

Service records appear newest first. Write one record per service event and include replaced components, warranty claims, ticket or invoice references, test results, and unresolved issues where relevant.

## 9. User assignment and return history

User history records who held an asset and when it was returned.

### Assign an asset

1. Open the asset.
2. Under **User history**, select **Add assignment**.
3. Enter the employee name or email and assignment date.
4. Add handover notes if needed.
5. Leave Returned date empty while the employee holds the asset.
6. Select **Save**.

Only one assignment can remain open for an asset. Adding an open assignment updates the asset’s Assigned to field and status.

### Record a return

1. Open the asset.
2. Find the current assignment under **User history**.
3. Select **Edit / record return**.
4. Enter the return date and any condition or handover notes.
5. Select **Save**.

The return date cannot precede the assignment date. When no open assignment remains, Assetdesk clears Assigned to and changes an Assigned asset to Available.

Assets already assigned when assignment history was introduced have a generated history entry with an unknown original assignment date.

## 10. Administrator guide

Administrators see **Lists & access** and **People** in the sidebar. Administrator accounts are Django superusers and can see every asset and list.

### Create a user

1. Select **People**.
2. Select **Add user**.
3. Enter a username and temporary password, then save.
4. Open the new user and add their name and email if required.
5. Leave **Staff status** and **Superuser status** disabled for ordinary users.
6. Ensure **Active** is enabled.
7. Save, then assign the user to the required lists.

Deliver temporary credentials through a trusted channel and have the user change the password after signing in.

### Create another administrator

Follow the user steps, then enable **Staff status** and **Superuser status** for the account. Superuser status gives full organization-wide access, so grant it only to authorized administrators. Keep at least two working administrator accounts to reduce lockout risk, with each administrator using a separate account.

### Create a list and grant access

1. Select **Lists & access**.
2. Add or open an asset list.
3. Enter its name and description.
4. In the membership rows, choose each user and their Viewer or Editor role.
5. Save.

Changes take effect immediately. Removing a membership removes that user’s access to the list. Deactivating a user prevents sign-in. Avoid using superuser status as a substitute for list membership when the person only needs selected lists.

### Reset a password

Open **People**, select the user, and use the password-change control in the administration page. Share the new temporary password securely. Administrators cannot view an existing password because passwords are stored as hashes.

### Review activity

The administration area contains Asset events. These show asset creation, edits, imports, and record updates. They cannot be added, changed, or deleted through the application. This is an operational audit trail, not a tamper-proof compliance archive; a server or database administrator can still alter the database.

## 11. Recommended operating practices

- Give each person an individual account; do not share administrator credentials.
- Use Viewer access for people who only need reports.
- Grant Editor access only to the lists a person maintains.
- Use stable tag conventions and never reuse a retired asset’s tag.
- Record returns before reassigning equipment.
- Add service records promptly and use consistent currency codes.
- Keep pictures focused on equipment, without confidential information in the background.
- Review inactive accounts and list memberships regularly.
- Back up the application database before upgrades and on a regular schedule.
- Test that backups can be restored. Pictures and all histories are part of the database.

## 12. Troubleshooting

### I cannot see an expected asset

Clear the search and filters. If it is still absent, ask an administrator to confirm that the asset is in the expected list and that you have an active membership for that list.

### I cannot add, edit, or import assets

You probably have Viewer access. An administrator must grant Editor access to the required list. Editors can only move an asset between lists where they have Editor access to both.

### My import failed

Check the row number in the error. Confirm the first row includes Tag and Asset/Name, every data row contains both values, tags are unique across the organization, and dates use a supported format. Because imports are transactional, corrected files can be retried without cleaning up partial rows.

### A picture will not upload

Confirm it is JPEG, PNG, or WebP, no larger than 5 MB, and below 20 megapixels. Exporting a fresh JPEG copy from a photo application often fixes malformed image files.

### I cannot add an assignment

The asset may already have an assignment without a return date. Open that record, enter its return date, save, and then add the new assignment.

### Sign-in is temporarily locked

Wait approximately 15 minutes or ask an administrator to unlock the account from the server. Confirm the username before retrying to avoid extending the lockout.

### The website is unavailable

Report the time, browser message, and page address to the hosting administrator. The administrator should check the application process, disk capacity, TLS certificate, recent server logs, and whether the database is writable. Do not send passwords or database files in ordinary email or chat.

## 13. Data protection and limitations

Assetdesk stores account records, permissions, asset details, pictures, service records, assignment history, sessions, and activity entries in its database. Access is enforced on the server using the user’s list memberships.

The application is designed for one organization and one application instance. It does not currently provide SSO, MFA, email invitations, barcode scanning, automated email reminders, or a tamper-proof audit store. Hosting administrators can access server-side data. Choose hosting, backups, and retention rules appropriate for your organization.

For installation, upgrades, backup commands, and server administration, see [DEPLOYMENT.md](DEPLOYMENT.md), [CPANEL.md](CPANEL.md), and [README.md](README.md).
