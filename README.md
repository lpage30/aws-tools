# python aws tools

## purpose
provide a cli command set for aws api. Initial approach is s3

## contents
### cli folder
contains 1 file per cli command. setup.py contains hooks to these cli commands
- bucket_download 
  ```
  usage: s3-bucket-download [-h] [--log-level {debug,info,warning,error,critical}] --aws-profile-name AWS_PROFILE_NAME --bucket BUCKET --key-prefix KEY_PREFIX
                          --output-directory OUTPUT_DIRECTORY [--no-verify-ssl]

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
  usage: s3-bucket-upload [-h] [--log-level {debug,info,warning,error,critical}] --aws-profile-name AWS_PROFILE_NAME --bucket BUCKET --input-directory INPUT_DIRECTORY
                        [--no-verify-ssl]

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
  usage: s3-list-buckets-like [-h] [--log-level {debug,info,warning,error,critical}] --aws-profile-name AWS_PROFILE_NAME [--regions REGIONS [REGIONS ...]]
                            --like-name LIKE_NAME [--min-age-days MIN_AGE_DAYS] [--max-age-days MAX_AGE_DAYS] [--after-date AFTER_DATE] [--before-date BEFORE_DATE]
                            --output-filepath OUTPUT_FILEPATH [--no-verify-ssl]

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
    --after-date AFTER_DATE
                          include buckets created on or after this date
    --before-date BEFORE_DATE
                          include buckets created on or before this date
    --output-filepath OUTPUT_FILEPATH
                          full path of file where names will be written
    --no-verify-ssl       use no-verify-ssl with aws call
  ```
- list_objects_like
  ```
  usage: s3-list-objects-like [-h] [--log-level {debug,info,warning,error,critical}] --aws-profile-name AWS_PROFILE_NAME [--regions REGIONS [REGIONS ...]]
                            --bucket-name BUCKET_NAME --like-name LIKE_NAME [--min-age-days MIN_AGE_DAYS] [--max-age-days MAX_AGE_DAYS] [--after-date AFTER_DATE]
                            [--before-date BEFORE_DATE] --output-filepath OUTPUT_FILEPATH [--no-verify-ssl]

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
    --after-date AFTER_DATE
                          include objects modified on or after this date
    --before-date BEFORE_DATE
                          include objects modified on or before this date
    --output-filepath OUTPUT_FILEPATH
                          full path of file where bucket/object JSON will be written
    --no-verify-ssl       use no-verify-ssl with aws call
  ```
- list_bucket_objects_like
  ```
  usage: s3-list-bucket-objects-like [-h] [--log-level {debug,info,warning,error,critical}] --aws-profile-name AWS_PROFILE_NAME [--regions REGIONS [REGIONS ...]]
                                   --bucket-like-name BUCKET_LIKE_NAME [--bucket-min-age-days BUCKET_MIN_AGE_DAYS] [--bucket-max-age-days BUCKET_MAX_AGE_DAYS]
                                   [--bucket-after-date BUCKET_AFTER_DATE] [--bucket-before-date BUCKET_BEFORE_DATE] --object-like-name OBJECT_LIKE_NAME
                                   [--object-min-age-days OBJECT_MIN_AGE_DAYS] [--object-max-age-days OBJECT_MAX_AGE_DAYS] [--object-after-date OBJECT_AFTER_DATE]
                                   [--object-before-date OBJECT_BEFORE_DATE] --output-filepath OUTPUT_FILEPATH [--no-verify-ssl]

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
    --bucket-after-date BUCKET_AFTER_DATE
                          include buckets created on or after this date
    --bucket-before-date BUCKET_BEFORE_DATE
                          include buckets created on or before this date
    --object-like-name OBJECT_LIKE_NAME
                          skeletal name of objects to list
    --object-min-age-days OBJECT_MIN_AGE_DAYS
                          exclude objects younger than this many days.
    --object-max-age-days OBJECT_MAX_AGE_DAYS
                          exclude objects older than this many days.
    --object-after-date OBJECT_AFTER_DATE
                          include objects modified on or after this date
    --object-before-date OBJECT_BEFORE_DATE
                          include objects modified on or before this date
    --output-filepath OUTPUT_FILEPATH
                          full path of file where bucket/object JSON will be written
    --no-verify-ssl       use no-verify-ssl with aws call
  ```
- objects_json_to_url
  ```
  usage: s3-objects-json-to-url [-h] [--log-level {debug,info,warning,error,critical}] [--top-count TOP_COUNT] --input-filepath INPUT_FILEPATH
                              [--s3-url-template S3_URL_TEMPLATE] --output-filepath OUTPUT_FILEPATH

  Convert top x S3 Objects s3 urls

  options:
    -h, --help            show this help message and exit
    --log-level {debug,info,warning,error,critical}
                          The level of logging output by this program
    --top-count TOP_COUNT
                          convert the most recent this many objects.
    --input-filepath INPUT_FILEPATH
                          full path of file containing bucket/object JSON
    --s3-url-template S3_URL_TEMPLATE
                          A string containing fields expressed within '{}': {region}, {bucket_name}, {object_full_path}
                          ie. http://s3.{region}.amazonaws.com/{bucket_name}/{object_full_path}
                          {region} - region in which bucket was found
                          {bucket_name} - name of bucket for object
                          {object_full_path} - full path of object in bucket ie. folder/subfolder/object_name, or, if no folder, object_name
    --output-filepath OUTPUT_FILEPATH
                          full path of file where s3://bucket/object names will be written
  ```
- download_objects
  ```
  usage: s3-download-objects [-h] [--log-level {debug,info,warning,error,critical}] --aws-profile-name AWS_PROFILE_NAME [--top-count TOP_COUNT]
                           --input-filepath INPUT_FILEPATH --output-dirpath OUTPUT_DIRPATH

  Download top X S3 Objects listed in input file to directory

  options:
    -h, --help            show this help message and exit
    --log-level {debug,info,warning,error,critical}
                          The level of logging output by this program
    --aws-profile-name AWS_PROFILE_NAME
                          AWS profile name
    --top-count TOP_COUNT
                          download the most recent this many objects.
    --input-filepath INPUT_FILEPATH
                          full path of file containing bucket/object JSON
    --output-dirpath OUTPUT_DIRPATH
                          full path of directory under which <bucket-name>(as subdirectory)/<object-name>(as file) will be stored
  ```
- aws_sso_login
  ```
  usage: aws-sso-login [-h] --aws-profile-name AWS_PROFILE_NAME

  aws sso login --profile

  options:
    -h, --help            show this help message and exit
    --aws-profile-name AWS_PROFILE_NAME
                          AWS profile name
  (3.13.2) larry@Larrys-MacBook-Pro aws-tools %
  ```
### s3
contains an S3 client structured class used to do basic S3 things
### util
- `aws_account_-_api.py` - contain code that is needed to parse aws-account-name, credentials etc... along with boto3 session
- `aws_login.py` - contain code used for logging in
- logging is simply logging
- `json_helpers.py` read/write jsont with datetme objects

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
