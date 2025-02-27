### Notes
- Fix SQL injection vulnerability to use prepared statements
- Fixed XSS vulnerability by replacing HTML tags with white space.

### Document Upload
- Fixed file upload vulnerability by accepting the accepted file types only. Otherwise,
  the file will be rejected.
