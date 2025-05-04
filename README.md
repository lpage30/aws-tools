# python aws tools

## purpose
provide a cli command set for aws api. Initial approach is s3

## contents
### cli folder
contains 1 file per cli command. setup.py contains hooks to these cli commands
- bucket_download 
  ```
  usage: s3-bucket-download [-h] [--log-level {debug,info,warning,error,critical}] [--aws-profile-name AWS_PROFILE_NAME] [--bucket BUCKET]
                          [--key-prefix KEY_PREFIX] [--output-directory OUTPUT_DIRECTORY]

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
  ```
- bucket_upload 
  ```
  usage: s3-bucket-upload [-h] [--log-level {debug,info,warning,error,critical}] [--aws-profile-name AWS_PROFILE_NAME] [--bucket BUCKET]
                        [--input-directory INPUT_DIRECTORY]

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
  ```
- list_buckets_like
  ```
  usage: s3-list-buckets-like [-h] [--log-level {debug,info,warning,error,critical}] [--aws-profile-name AWS_PROFILE_NAME] [--like-name LIKE_NAME]
                            [--output-filepath OUTPUT_FILEPATH]

  list all bucket names like provided skeleton
  
  options:
    -h, --help            show this help message and exit
    --log-level {debug,info,warning,error,critical}
                          The level of logging output by this program
    --aws-profile-name AWS_PROFILE_NAME
                          AWS profile name
    --like-name LIKE_NAME
                          skeletal name of buckets to list
    --output-filepath OUTPUT_FILEPATH
                          full path of file where names will be written

  ```
- list_objects_like
  ```
  usage: s3-list-objects-like [-h] [--log-level {debug,info,warning,error,critical}] [--aws-profile-name AWS_PROFILE_NAME] [--bucket-name BUCKET_NAME]
                            [--like-name LIKE_NAME] [--output-filepath OUTPUT_FILEPATH]

  list all object names in named bucket like provided skeleton
  
  options:
    -h, --help            show this help message and exit
    --log-level {debug,info,warning,error,critical}
                          The level of logging output by this program
    --aws-profile-name AWS_PROFILE_NAME
                          AWS profile name
    --bucket-name BUCKET_NAME
                          Name of bucket in which to search
    --like-name LIKE_NAME
                          skeletal name of objects to list
    --output-filepath OUTPUT_FILEPATH
                          full path of file where bucket/object names will be written

  ```
- list_urls_like
  ```
  usage: s3-list-urls-like [-h] [--log-level {debug,info,warning,error,critical}] [--aws-profile-name AWS_PROFILE_NAME]
                         [--bucket-like-name BUCKET_LIKE_NAME] [--object-like-name OBJECT_LIKE_NAME] [--output-filepath OUTPUT_FILEPATH]

  list all s3 urls with bucket name like provided skeleton and object name like provided skeleton
  
  options:
    -h, --help            show this help message and exit
    --log-level {debug,info,warning,error,critical}
                          The level of logging output by this program
    --aws-profile-name AWS_PROFILE_NAME
                          AWS profile name
    --bucket-like-name BUCKET_LIKE_NAME
                          skeletal name of buckets to search
    --object-like-name OBJECT_LIKE_NAME
                          skeletal name of objects to list
    --output-filepath OUTPUT_FILEPATH
                          full path of file where s3://bucket/object names will be written

  ```
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
