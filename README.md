# OMERO-ARC

A plugin for [omero-cli-transfer](https://github.com/ome/omero-cli-transfer) to export imaging projects from the [OMERO](https://www.openmicroscopy.org/omero/) database to an [ARC](https://nfdi4plants.github.io/nfdi4plants.knowledgebase/start-here/) locally.

## Usage

Once installed, your can "pack" omero projects to an ARC. The project metadata is mapped to studies in an ARC along with investigation metadata and the datasets are mapped to the assays. If there exits [ISA](https://isa-specs.readthedocs.io/en/latest/isamodel.html#) metadata mapped to projects and datasets as described, with proper namespaces in omero key-value pair, the (meta)data is transfered from omero to the local ARC.

If the ARC repository already exists, the OMERO project is added as a new study and connected assays. If the ARC repo does not exist, a new ARC repository is created.

Examples:
```
omero transfer pack --plugin arc Dataset:111 path/to/my/new/arc_repo
omero transfer pack --plugin arc Dataset:111 path/to/my/already/existing/arc_repo
```

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

### Installation
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
sudo .omero/compose up
```

### Run tests
```
OMERODIR="." ICE_CONFIG="test/ice.config" pytest
```
