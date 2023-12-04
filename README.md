# NEPTUNE Mixed Integer Programming
<p align="center">
  <img width="100%" src="https://i.imgur.com/tm9mSuM.png" alt="Politecnico di Milano" />
</p>

This repository contains the python version of the MIP solver used for NEPTUNE.

## Getting Started
This repository has been dockerized. It's possible to run a plug&play image at `systemautoscaler/allocation-algorithm-rest:dev`

To build a new Docker image, run:
```
docker build -t {IMAGE}:{TAG} .
```

Run the container:
```
docker run -it -p 5000:5000 {IMAGE}:{TAG} 
```

To run the test, execute in another terminal:
```
python test.py
```
