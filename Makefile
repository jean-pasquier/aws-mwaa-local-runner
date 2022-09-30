LOCAL_PROJECT_PATH := dags/team


MWAA_BUCKET_PREPROD := preprod-bucket
MWAA_BUCKET_PROD := bucket


deploy_preprod:
	aws s3 rm --recursive s3://$(MWAA_BUCKET_PREPROD)/$(LOCAL_PROJECT_PATH)
# aws s3 sync "./" s3://$(MWAA_BUCKET_PREPROD) --delete --exclude "*" --include "requirements.txt"
	aws s3 sync $(LOCAL_PROJECT_PATH) s3://$(MWAA_BUCKET_PREPROD)/$(LOCAL_PROJECT_PATH) --exclude 'conf/confs/*'
	aws s3 sync $(LOCAL_PROJECT_PATH)/conf/confs/base s3://$(MWAA_BUCKET_PREPROD)/$(LOCAL_PROJECT_PATH)/conf/confs/base
	aws s3 sync $(LOCAL_PROJECT_PATH)/conf/confs/preprod s3://$(MWAA_BUCKET_PREPROD)/$(LOCAL_PROJECT_PATH)/conf/confs/preprod


deploy_prod:
	aws s3 rm --recursive s3://$(MWAA_BUCKET_PROD)/$(LOCAL_PROJECT_PATH)
	aws s3 sync $(LOCAL_PROJECT_PATH) s3://$(MWAA_BUCKET_PROD)/$(LOCAL_PROJECT_PATH) --exclude 'conf/confs/*'
	aws s3 sync $(LOCAL_PROJECT_PATH)/conf/confs/base s3://$(MWAA_BUCKET_PROD)/$(LOCAL_PROJECT_PATH)/conf/confs/base
	aws s3 sync $(LOCAL_PROJECT_PATH)/conf/confs/prod s3://$(MWAA_BUCKET_PROD)/$(LOCAL_PROJECT_PATH)/conf/confs/prod


