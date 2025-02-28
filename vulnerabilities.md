### News

- Fixed confidential news appearing in the plaintext, moved confidential news to an env file.

### Notes

- Fix SQL injection vulnerability to use prepared statements
- Fixed XSS vulnerability by replacing HTML tags with white space.
- Fixed access control vulnerability by validating the note_id to be deleted matches the current user_id.

### Document Upload

- Fixed file upload vulnerability by accepting the accepted file types only. Otherwise,
  the file will be rejected.
- Fixed DOS attack vulnerability by limiting file size uploads to 10MB.

### Captcha

- Added hChaptcha support to regitration page.

### Admin

- Allowed the default admin to change their password.
- Fixed the SQL injection for the admin login page.
- Added custom captcha to admin login page.

### 401k

- Refactored retirement 401k stuff to use the DB and added validation.

### 2FA

- Added email 2FA to registration page.

### app.py

- Moved secret code to .env file instead of in plaintext.

### Not a Vulnerability

- Added email feature to dashboard.
