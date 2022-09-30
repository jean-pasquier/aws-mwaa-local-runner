## Technical information

- `python` as language
- `GitHub Action` to deploy

## How it works

Write your own dag into `dags/team/project/` folder.<br/>

### Local test

As MWAA is a managed Aiflow service with many Python dependencies, it is not trivial to simulate a production
environment locally. This is why Amazon open sourced a container-based solution to handle
it: [aws-mwaa-local-runner@2.2](github.com/aws/aws-mwaa-local-runner/tree/v2.2.2). This includes a Docker image (
see `docker/Dockerfile`) and a set of services (postgres database handling metadata, etc.). We added some new services
that mock common uses cases, such as [min.io](https://min.io/) for `S3` and `posgres` for Redshift (
see `docker/docker-compose-local.yml`) and moved some Docker volumes to match DPS Airflow template.

#### Prerequisites (see [AWS documentation](https://docs.aws.amazon.com/mwaa/latest/userguide/airflow-versions.html) and [aws-mwaa-local-runner@2.2](github.com/aws/aws-mwaa-local-runner/tree/v2.2.2))

* `Python 3.7`
* `docker` daemon with `docker-compose`

Create a `.env` file at the root of this project, this will add environment variables to local Airflow instance. This a
way to create connections to mocked services (
see [Airflow connection documentation](https://airflow.apache.org/docs/apache-airflow/stable/howto/connection.html)).
For example:

```text
AIRFLOW_CONN_AWS_CONN_TEST=s3://?host=http://dlk:9000&region_name=eu-west-1&aws_access_key_id=airflow_minio_key&aws_secret_access_key=airflow_minio_secret
AIRFLOW_CONN_RSH_CONN_TEST='postgresql+psycopg2://airflow:airflow@dwh:5432/airflow'
```

Have in mind that connection created through environment variables are not stored in the metabase and thus are not
visible in the UI -> Admin -> Connections.<br/>
But you can test the connection within an Operator or Hook with `aws_conn_id="aws_conn_test"`
or `redshift_conn_id="redshift_team"`.

#### Commands

```shell
$ ./mwaa-local-env help
$ ./mwaa-local-env build-image
$ ./mwaa-local-env start
```

Open the Apache Airlfow UI: http://localhost:8080/. You can connect with Admin user (Username: `admin`,
Password: `test`).<br/>
If there is an issue with Aiflow `metabase` at some point, it may be mandatory to reset it
running `$ ./mwaa-local-env reset-db`

#### IDE

You can set up your IDE (i.e. IntelliJ) for autocompletion, error highlights, etc. with Python plugin and proper virtual
environment handling:

```shell
$ python3 -m venv .venv
$ source .venv/bin/activate
$ which pip
$ pip install -r docker/config/requirements.txt -r docker/config/mwaa-base-providers-requirements.txt -r requirements.txt -c docker/config/constraints.txt
```

Configure your IDE to use relevant Python SDK: `.venv/bin/python`.

### Deployment

git push to `main` to deploy in `preprod` (see `.github/workflows/deploy-preprod-on-push.yml` and `Makefile`).<br/>
Release a new version to deploy in `prod` (see `.github/workflows/deploy-prod-on-release.yml` and `Makefile`).

## Project structure

```
.github                     <- github actions
    |-- workflows
    |   |-- deploy-preprod-on-push.yml <- deploy to preprod
    |   |-- deploy-prod-on-release.yml <- deploy to prod

dags                        <- directory copied to S3 and parsed by Aiflow   
    |-- team
    |   |-- project
    |   |   |-- conf
    |   |   |   |-- config.py
    |   |   |   |-- confs
    |   |   |   |   |-- base
    |   |   |   |   |   |-- parameters.yml
    |   |   |   |   |-- local
    |   |   |   |   |   |-- parameters.yml
    |   |   |   |   |-- preprod
    |   |   |   |   |   |-- parameters.yml
    |   |   |   |   |-- prod
    |   |   |   |   |   |-- parameters.yml
    |   |   |-- hooks
    |   |   |   |-- custom_hook_1.py
    |   |   |-- operators
    |   |   |   |-- operator1.py
    |   |   |-- dag_1.py
    |   |   |-- dag_2.py
    |   |   |-- dag_n.py

docker                      <- local aiflow containers management   
    |-- config
    |   |-- airflow.cfg
    |   |-- constraints.txt
    |   |-- mwaa-base-providers-requirements.txt
    |   |-- requirements.txt
    |   |-- webserver_config.py
    |-- script
    |   |-- bootstrap.sh
    |   |-- entrypoint.sh
    |   |-- generate_key.sh
    |   |-- systemlibs.sh
    |-- docker-compose-local.yml
    |-- docker-compose-resetdb.yml
    |-- Dockerfile

dps-airflow-operators       <- clone of dps operators (aim to be removed and included in requirements.txt)   
    |-- ...

log4j.properties
Makefile
mwaa-local-env              <- entrypoint to handle local airflow instance
requirements.txt            <- custom dags Python requirements            
```




