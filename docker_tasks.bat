@echo off
REM Stop all running containers
echo Stopping all running containers...
for /f "tokens=*" %%i in ('docker ps -q') do docker stop %%i

REM Build the Docker image
echo Building Docker image neptune-mip:latest...
docker build -t neptune-mip:latest .

REM Run the Docker container
echo Running Docker container from neptune-mip:latest...
docker run -it -p 5000:5000 neptune-mip:latest
