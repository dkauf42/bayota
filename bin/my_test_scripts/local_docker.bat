:: John Massey
:: ASRC Federal
:: 6/24/2019
:: Usage: Get local users AWS Access Keys, Requires AWS CLI tools to be installed
:: Add these keys to the docker container call to provide
:: AWS Credentials to the docker container and all software installed
:: THIS PROCESS IS NOT NECESSARY IN AWS as Keys are provided by AWS Account Roles 

:: Required Paramaters
::   1. Docker Image Name, and Tag
SET imageName=%~1

:: Get Local AWS_ACCESS_KEYS's from %UserProfile%\.aws\configure
FOR /F "tokens=* USEBACKQ" %%F IN (`aws configure get aws_access_key_id`) DO (
SET AwsAccessKey=%%F
)

FOR /F "tokens=* USEBACKQ" %%F IN (`aws configure get aws_secret_access_key`) DO (
SET AwsAccessSecretKey=%%F
)

:: Run Docker Image with Keys Injected as EnvVars
:: Running the image without adding the interactive option will perform the command configured in the Dockerfile [CMD]
:: To run Container interactively, add /bin/bash to the end of the command below.
:: While running interactively you will need to run your code manually python /app/<progName> options...
docker run -e "AWS_ACCESS_KEY_ID=%AwsAccessKey%" -e "AWS_SECRET_ACCESS_KEY=%AwsAccessSecretKey%" -i -t %imageName%