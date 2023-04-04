# Monarch API

![](https://github.com/monarch-initiative/monarch-api/actions/workflows/test-backend.yaml/badge.svg)
![](https://github.com/monarch-initiative/monarch-api/actions/workflows/test-frontend.yaml/badge.svg)
![](https://github.com/monarch-initiative/monarch-api/actions/workflows/deploy-documentation.yaml/badge.svg)
![](https://github.com/monarch-initiative/monarch-api/actions/workflows/build-image.yaml/badge.svg)

`monarch-api` is a FastAPI for browsing the knowledge graph produced by the Monarch Initiative.

[Documentation](https://monarch-initiative.github.io/monarch-api/)


### For developers

You can install monarch-api from GitHub as follows:

```
# clone the repo
git clone https://github.com/monarch-initiative/monarch-api

# cd into the folder
cd monarch-api

# install
poetry -C backend/ install
cd frontend && yarn build
```
