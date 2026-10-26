# Upgrade: photos and histories

Back up `/home/YOUR_CPANEL_USER/assetdesk/assets.sqlite3` before upgrading (stop the Python app while making the backup). Keep the backup outside the public web directory.

Upload the updated ZIP to `/home/YOUR_CPANEL_USER`, extract it so application files replace those under `/home/YOUR_CPANEL_USER/assetdesk`, and preserve `.hosting.json` and the existing database. The package contains neither of these files.

In cPanel Terminal run:

```bash
source /home/YOUR_CPANEL_USER/virtualenv/assetdesk/3.12/bin/activate
cd /home/YOUR_CPANEL_USER/assetdesk
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py check
```

Restart Assetdesk in Setup Python App. Keep the startup file set to `app_wsgi.py`.

Open an asset to manage its photo, add a service record, or add/update assignment history. Existing assignees receive a history entry with an unknown original date. Editing an asset's Assigned to field records the change with today's date; use User history for dated assignments and returns. Only one assignment can remain active per asset.

Photos are validated, resized, and stored privately in the database. Include the database in regular backups. Images are served through authenticated list-permission checks, never a public upload folder.

Multiple administrators are supported through People: create a user, then enable Active, Staff status and Superuser status. Superusers have organization-wide access; use list Editor memberships for restricted access.
