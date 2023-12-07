# OMERO-ARC

## Installation


### Install Dependencies

* Install `ARCCommander` (and Git and Git LFS) as described [here](https://nfdi4plants.org/nfdi4plants.knowledgebase/docs/ArcCommanderManual/index-setup.html)
* Install `omero-cli-transfer` as described [here](https://github.com/ome/omero-cli-transfer)

### Install omero-arc plugin

```
pip install omero-arc
```

## Development

### Start OMERO test database

```
sudo chmod a+x .omero/compose # enure that compose is executable
sudo .omoero/compose up
```

### Run tests
```
OMERODIR="." ICE_CONFIG="test/ice.config" pytest
```
