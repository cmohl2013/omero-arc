# OMERO-ARC

## Installation


### Install Dependencies

* Install `ARCCommander` (and Git and Git LFS) as described [here](https://nfdi4plants.org/nfdi4plants.knowledgebase/docs/ArcCommanderManual/index-setup.html)
* Install `omero-cli-transfer` as described [here](https://github.com/ome/omero-cli-transfer)

### Install omero-arc plugin

```
pip install omero-arc
```

## Development Environment Setup
```
conda create -n myenv -c conda-forge python=3.8 zeroc-ice=3.6.5
conda activate myvenv
```

### Install omero-arc
```
git clone git@github.com:cmohl2013/omero-arc.git
cd omero-arc
pip install -e .[dev] # installs optional dependencies including omero-cli-transfer
conda install pytest

```

### Start OMERO test database

Launch OMERO test environment with docker-compose.
```
sudo chmod a+x .omero/compose # enure that compose is executable
sudo .omoero/compose up
```

### Run tests
```
OMERODIR="." ICE_CONFIG="test/ice.config" pytest
```
