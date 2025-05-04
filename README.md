# python aws tools

## purpose
provide a cli command set for aws api. Initial approach is s3

## contents
### cli folder
contains 1 file per cli command. setup.py contains hooks to these cli commands
- bucket_download 
  ```
  s3-bucket-download --aws-account-name <account-name> --bucket <bucket> [--key-prefix <prefix> --log-level <debug|info|warning|error|critical>] --output-directory <directory-for-objects>
  ```
  downloads all objects from provided s3 bucket with provided optional key-prefix into provided directory
- bucket_upload 
  ```
  s3-bucket-upload --aws-account-name <account-name> --bucket <bucket> [---log-level <debug|info|warning|error|critical>] --input-directory <directory-of-objects-to-upload>
  ```
  uploads all objects from provided input directory to provided s3 bucket. s3 key will be the filename of the object.

### s3
contains an S3 client structured class used to do basic S3 things
### util
- `aws-account-api.py` - contain code that is needed to parse aws-account-name, credentials etc... along with boto3 session
- logging is simply logging

## build scripts
Scripts were created in both bash and batch so as to work in windows or linux-based systems
- `clean` `clean.bat`  
cleans up results of any prior builds
- `build-project` `build-project.bat`
calls clean and then builds project using python -m build
- `install` `install.bat` 
calls build-project and then installs built project using python pip install
- `uninstall` `uninstall.bat`
uninstalls project using python pip uninstall and then calls clean
