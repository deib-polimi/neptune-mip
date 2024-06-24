@echo off
REM Build the Docker image
echo Building Docker image neptune-mip:latest...
docker build -t neptune-mip:latest .

REM Tag the Docker container
docker tag neptune-mip:latest andreasbrummer/neptune-mip:latest

REM Push the image
echo Pushing the image to andreasbrummer/neptune-mip:latest
docker push andreasbrummer/neptune-mip:latest
