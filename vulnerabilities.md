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

### Admin

- Moved default admin information to .env instead of in the plaintext.
1. Gitignore was not set to ignore database folder, so it would publish your db to github

2. Added hCaptcha to registration form

3. Refactored retirement 401k stuff to use the DB and added validation