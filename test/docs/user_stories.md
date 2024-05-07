# Omero->ARC One-Way "Snapshot" Export Via Command Line

## Background
Marie is a PhD student in a cell biology lab. For her research project she collects 3D multichannel confocal microscopy images with a Zeiss microscope and regularly uploads the raw data in czi format to an omero database which is managed by the institute's light microscopy core facility. She stores all data in a project named "lysosome_trafficing_fibroblasts". Within the folder structure, she organizes the image data in different datasets, where each dataset refers to a certain experimental condition. The four datasets are named "Knockdown AFK-1", "Knockdown AFK-1 + Blebbistatin", "WT", "WT + Blebbistatin". Each dataset contains 10 to 30 images.

## Objective
Marie aims to publish her results in a research paper. She wants to make her raw data including metadata publicly available as an arc repository. The link to the repository will be included as a link in the publication.

## User Journey

* Marie creates an account on the website of a publicly available GitLab dedicated to ARC repositories. The creates an empty project named "Lysosome Trafficing in Fibroblasts".

* On the command line of her Laptop she clones the repository into a local folder (using `git`).

* Next she exports all OMERO datasets of her project "lysosome_trafficing_fibroblasts" to her local ARC repository using `omero-cli-transfer` with the plugin `omero-arc`.

```sh
omero transfer pack --plugin arc Dataset:111 path/to/my/arc/repo/lysosome_trafficing_in_fibroblasts

omero transfer pack --plugin arc Dataset:112 path/to/my/arc/repo/lysosome_trafficing_in_fibroblasts

omero transfer pack --plugin arc Dataset:113 path/to/my/arc/repo/lysosome_trafficing_in_fibroblasts
```
* Finally she pushes the updated repository to Remote using `git`
