# Monarch App


![](https://github.com/monarch-initiative/monarch-app/actions/workflows/test-backend.yaml/badge.svg)
![](https://github.com/monarch-initiative/monarch-app/actions/workflows/test-frontend.yaml/badge.svg)
![](https://github.com/monarch-initiative/monarch-app/actions/workflows/deploy-documentation.yaml/badge.svg)
![](https://github.com/monarch-initiative/monarch-app/actions/workflows/build-image.yaml/badge.svg)

This repository contains the source code for the Monarch Initiative website (a Vue TS frontend),  
as well as `monarch-py`, a Python library for interacting with the Monarch Initiative knowledge graph,  
which includes an optional FastAPI module that serves as the website's backend.  

[The New Website](https://monarch-app.monarchinitiative.org)

[Documentation](https://monarch-app.monarchinitiative.org/docs)

### For developers

To get started with this repo:

```
git clone https://github.com/monarch-initiative/monarch-app
cd monarch-app
```

Then see `Makefile` or the individual `/frontend` and `/backend` folders for how you can install, develop, build, test, lint, or format the frontend or backend.
