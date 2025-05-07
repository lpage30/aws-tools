# python aws tools

## purpose
provide a cli command set for aws api. Initial approach is s3

## contents
### cli folder
contains 1 file per cli command. setup.py contains hooks to these cli commands
- bucket_download 
  ```
  usage: s3-bucket-download [-h] [--log-level {debug,info,warning,error,critical}] --aws-profile-name AWS_PROFILE_NAME
                            --bucket BUCKET --key-prefix KEY_PREFIX --output-directory OUTPUT_DIRECTORY
                            [--no-verify-ssl]

  Export bucket records to csv.

  options:
    -h, --help            show this help message and exit
    --log-level {debug,info,warning,error,critical}
                          The level of logging output by this program
    --aws-profile-name AWS_PROFILE_NAME
                          AWS profile name
    --bucket BUCKET       bucket from which to download
    --key-prefix KEY_PREFIX
                          key-prefix of objects to download
    --output-directory OUTPUT_DIRECTORY
                          directory in which all objects will be downloaded
    --no-verify-ssl       use no-verify-ssl with aws call  
  ```
- bucket_upload 
  ```
  usage: s3-bucket-upload [-h] [--log-level {debug,info,warning,error,critical}] --aws-profile-name AWS_PROFILE_NAME
                          --bucket BUCKET --input-directory INPUT_DIRECTORY [--no-verify-ssl]

  Import csv records to bucket.

  options:
    -h, --help            show this help message and exit
    --log-level {debug,info,warning,error,critical}
                          The level of logging output by this program
    --aws-profile-name AWS_PROFILE_NAME
                          AWS profile name
    --bucket BUCKET       bucket to upload into
    --input-directory INPUT_DIRECTORY
                          directory from which all files will uploaded into bucket
    --no-verify-ssl       use no-verify-ssl with aws call
  ```
- list_buckets_like
  ```
  usage: s3-list-buckets-like [-h] [--log-level {debug,info,warning,error,critical}] --aws-profile-name AWS_PROFILE_NAME
                              [--regions REGIONS [REGIONS ...]] --like-name LIKE_NAME [--min-age-days MIN_AGE_DAYS]
                              [--max-age-days MAX_AGE_DAYS] --output-filepath OUTPUT_FILEPATH [--no-verify-ssl]

  list all bucket names like provided skeleton

  options:
    -h, --help            show this help message and exit
    --log-level {debug,info,warning,error,critical}
                          The level of logging output by this program
    --aws-profile-name AWS_PROFILE_NAME
                          AWS profile name
    --regions REGIONS [REGIONS ...]
                          list of regions to search
    --like-name LIKE_NAME
                          skeletal name of buckets to list
    --min-age-days MIN_AGE_DAYS
                          exclude buckets younger than this many days.
    --max-age-days MAX_AGE_DAYS
                          exclude buckets older than this many days.
    --output-filepath OUTPUT_FILEPATH
                          full path of file where names will be written
    --no-verify-ssl       use no-verify-ssl with aws call
  ```
- list_objects_like
  ```
  usage: s3-list-objects-like [-h] [--log-level {debug,info,warning,error,critical}] --aws-profile-name AWS_PROFILE_NAME
                              [--regions REGIONS [REGIONS ...]] --bucket-name BUCKET_NAME --like-name LIKE_NAME
                              [--min-age-days MIN_AGE_DAYS] [--max-age-days MAX_AGE_DAYS] --output-filepath
                              OUTPUT_FILEPATH [--no-verify-ssl]

  list all object names in named bucket like provided skeleton

  options:
    -h, --help            show this help message and exit
    --log-level {debug,info,warning,error,critical}
                          The level of logging output by this program
    --aws-profile-name AWS_PROFILE_NAME
                          AWS profile name
    --regions REGIONS [REGIONS ...]
                          list of regions to search
    --bucket-name BUCKET_NAME
                          Name of bucket in which to search
    --like-name LIKE_NAME
                          skeletal name of objects to list
    --min-age-days MIN_AGE_DAYS
                          exclude objects younger than this many days.
    --max-age-days MAX_AGE_DAYS
                          exclude objects older than this many days.
    --output-filepath OUTPUT_FILEPATH
                          full path of file where bucket/object JSON will be written
    --no-verify-ssl       use no-verify-ssl with aws call
  ```
- list_bucket_objects_like
  ```
  usage: s3-list-bucket-objects-like [-h] [--log-level {debug,info,warning,error,critical}] --aws-profile-name
                                    AWS_PROFILE_NAME [--regions REGIONS [REGIONS ...]] --bucket-like-name
                                    BUCKET_LIKE_NAME [--bucket-min-age-days BUCKET_MIN_AGE_DAYS]
                                    [--bucket-max-age-days BUCKET_MAX_AGE_DAYS] --object-like-name OBJECT_LIKE_NAME
                                    [--object-min-age-days OBJECT_MIN_AGE_DAYS]
                                    [--object-max-age-days OBJECT_MAX_AGE_DAYS] --output-filepath OUTPUT_FILEPATH
                                    [--no-verify-ssl]

  list all objects with bucket name like provided skeleton and object name like provided skeleton

  options:
    -h, --help            show this help message and exit
    --log-level {debug,info,warning,error,critical}
                          The level of logging output by this program
    --aws-profile-name AWS_PROFILE_NAME
                          AWS profile name
    --regions REGIONS [REGIONS ...]
                          list of regions to search
    --bucket-like-name BUCKET_LIKE_NAME
                          skeletal name of buckets to search
    --bucket-min-age-days BUCKET_MIN_AGE_DAYS
                          exclude buckets younger than this many days.
    --bucket-max-age-days BUCKET_MAX_AGE_DAYS
                          exclude buckets older than this many days.
    --object-like-name OBJECT_LIKE_NAME
                          skeletal name of objects to list
    --object-min-age-days OBJECT_MIN_AGE_DAYS
                          exclude objects younger than this many days.
    --object-max-age-days OBJECT_MAX_AGE_DAYS
                          exclude objects older than this many days.
    --output-filepath OUTPUT_FILEPATH
                          full path of file where bucket/object JSON will be written
    --no-verify-ssl       use no-verify-ssl with aws call
  ```
- objects_json_to_url
  ```
  usage: s3-objects-json-to-url [-h] [--log-level {debug,info,warning,error,critical}] --input-filepath INPUT_FILEPATH
                                --output-filepath OUTPUT_FILEPATH

  Convert JSON file array of S3 Objects to array of S3 urls

  options:
    -h, --help            show this help message and exit
    --log-level {debug,info,warning,error,critical}
                          The level of logging output by this program
    --input-filepath INPUT_FILEPATH
                          full path of file containing bucket/object JSON
    --output-filepath OUTPUT_FILEPATH
                          full path of file where s3://bucket/object names will be written
  ```
- aws_sso_login
  ```
  usage: aws-sso-login [-h] [--aws-profile-name AWS_PROFILE_NAME]
  
  aws sso login --profile
  
  options:
    -h, --help            show this help message and exit
    --aws-profile-name AWS_PROFILE_NAME
                          AWS profile name
  ```
### s3
contains an S3 client structured class used to do basic S3 things
### util
- `aws_account_-_api.py` - contain code that is needed to parse aws-account-name, credentials etc... along with boto3 session
- `aws_login.py` - contain code used for logging in
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
