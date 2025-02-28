### News

- Fixed confidential news appearing in the plaintext, moved confidential news to an env file.

### Notes

- Fix SQL injection vulnerability to use prepared statements
- Fixed XSS vulnerability by replacing HTML tags with white space.
- Fixed access control vulnerability by validating the note_id to be deleted matches the current user_id.

### Document Upload

- Fixed file upload vulnerability by accepting the accepted file types only. Otherwise,
  the file will be rejected.
