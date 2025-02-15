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


<br />
<br />
<br />


# CLEM variant 1
## Background

Felix is an electron microscopist. Together with his colleague Christian who is a light microscopist he is performing some CLEM experiments, which should enable the analysis of overall structure of mitochondria and endoplasmic reticulum and the ultrastructure of their contact sites. Christian acquires single plane multichannel high resolution images of cells with specific fluorescent stains for mitochondria and ER respectively. He uploads his images right away to OMERO and then exports from there into an ARC with an investigation called “mitochondrial structure in aging” with a study called “Mito-ER-contact-sites” and created an assay to contain his images called “fluorescence microscopy of mito and ER stained HeLa cells”. 
After Christian acquired the images Felix fixed the cells and contrasted them for EM imaging. By means of a coordinate system on the sample substrate he retrieves the cells imaged by Christian and collects electron micrographs as single plane images in dm4-file format of these cells highlighting the contact sites of the organelles. This way Felix obtains multiple electron micrographs from the area of one fluorescence image. He uploads them to OMERO and from there adds a new assay to the ARC called “electron microscopy of mito-er-contact sites in HeLa-cells”. 
Using a registration tool in the Icy software Felix and Christian align the electron micrographs with the corresponding fluorescence image and save it as a multichannel tif-file which now conveniently combines the fluorescence with the electron microscopy data. They store these resulting files in a new Assay called “CLEM analysis of mito-er-contact sites in HeLa-cells”. They add a companion file automatically generated by Icy to the protocol folder of the assay, which describes the transformations applied to the input images to achieve the registration of the resulting CLEM image and import the assay “CLEM analysis of mito-er-contact sites in HeLa-cells” as a new dataset into OMERO.

## Objective
Felix and Christian want to share their work with their colleagues via OMERO. They want to import the ARC, respectively the relevant study and assays into OMERO. The relationship of the original fluorescence and electron microscopy images with the combined and registered CLEM image should be documented in OMERO by Key-Value-Pairs linking the images. The metadata imported from the ARC as KVP into OMERO should also link the images in OMERO. E.g. it should be possible which images derive from the same sample. Ideally, it should also be traceable which images derive from the same sample region. Moreover, ideally the CLEM images would be annotated with the OMERO-IDs of the original EM and fluorescence images they were made of. Also the description of the transformation applied to achieve the registration should be linked with the CLEM image.


## User Journey


Import fluorescence microscopy dataset and electron microscopy dataset from OMERO into one ARC.
Use the data in the ARC for a new assay, which comprises the registration of  fluorescence and electron microscopy images.
Upload the new registration assay to OMERO so that the registered images are linked with the original images.

# CLEM variant 2
## Background

Felix is an electron microscopist. Together with his colleague Christian who is a light microscopist he is performing some CLEM experiments, which should enable the analysis of overall structure of mitochondria and endoplasmic reticulum and the ultrastructure of their contact sites. Christian acquires single plane multichannel high resolution images of cells with specific fluorescent stains for mitochondria and ER respectively. He uses an ARC with an investigation called “mitochondrial structure in aging” with a study called “Mito-ER-contact-sites” and created an assay to contain his images called “fluorescence microscopy of mito and ER stained HeLa cells”. 
After Christian acquired the images Felix fixed the cells and contrasted them for EM imaging. By means of a coordinate system on the sample substrate he retrieves the cells imaged by Christian and collects electron micrographs as single plane images in dm4-file format of these cells highlighting the contact sites of the organelles. This way Felix obtains multiple electron micrographs from the area of one fluorescence image. He added a new assay to the ARC called “electron microscopy of mito-er-contact sites in HeLa-cells”. 
Using a registration tool in the Icy software Felix and Chistian align the electron micrographs with the corresponding fluorescence image and save it as a multichannel tif-file which now conveniently combines the fluorescence with the electron microscopy data. They store these resulting files in a new Assay called “CLEM analysis of mito-er-contact sites in HeLa-cells”. They add a companion file automatically generated by Icy to the protocol folder of the assay, which describes the transformations applied to the input images to achieve the registration of the resulting CLEM image.

## Objective
Felix and Christian want to share their work with their colleagues via OMERO. They want to import the ARC, respectively the relevant study and assays into OMERO. The relationship of the original fluorescence and electron microscopy images with the combined and registered CLEM image should be documented in OMERO by Key-Value-Pairs linking the images. The metadata imported from the ARC as KVP into OMERO should also link the images in OMERO. E.g. it should be possible which images derive from the same sample. Ideally, it should also be traceable which images derive from the same sample region. Moreover, ideally the CLEM images would be annotated with the OMERO-IDs of the original EM and fluorescence images they were made of. Also the description of the transformation applied to achieve the registration should be linked with the CLEM image.


## User Journey


Create an ARC on a local machine.
Upload to OMERO using ARC-OMERO transfer plugin.
Work on the data in OMERO. 
Download the ARC back using OMERO-ARC 
Publish it to DATAPlant DataHUB.


<br />
<br />
<br />

# Use Case: Investigating Algal Changes Under Heat Stress

## Overview
This use case describes a workflow for investigating how algae respond to heat stress, using a variety of assays and imaging techniques. The workflow involves the collection and documentation of samples, performing multiple assays, and using specialized software for data analysis and visualization.

## Actors
- **Primary User (Researcher)**: Conducts the investigation and uses various software tools to document and analyze data.
- **Data scientist**: Developed object tracking workflow for cell detection and runs workflow within the ARC
- **Software Developer**: Implements software plug-in that is aware of the metadata to impose the results of two different assays (image and ROIs (Regions of Interest)).

## Main Flow
1. **Setup and Documentation**:
   - The researcher initiates an investigation into the effects of heat stress on algae.
   - Liquid culture samples are taken from a bioreactor under controlled conditions.
   - The administrative metadata for the investigation is documented in ARC according to the ISA model.
   - Details about the sample material and the sampling process are recorded in the ISA study.

2. **Performing Assays**:
   - The same sample material is used for multiple assays, including:
     - **Proteomics**: To study the protein expressions.
     - **Metabolomics**: To analyze metabolic changes.
     - **RNAseq**: To investigate gene expression changes.
   - Phenotypic changes are recorded using light microscopy.
   - Electron microscopy images are taken to detect the formation of starch granules.

3. **Data Management**:
   - Each assay produces its own dataset according to the ARC structure.
   - Light microscopy images are used as input for a workflow that performs cell object detection, resulting in ROIs without the images themselves.

4. **Data Visualization**:
   - The researcher uses OMERO software to browse through both light microscopy and electron microscopy images.
   - The ROIs generated from the object detection workflow are overlaid on the corresponding images within OMERO for detailed analysis.

## Postconditions
- The researcher successfully browses and analyzes the images and corresponding ROIs in OMERO.
- Insights into the algal response to heat stress are gained through the integrated analysis of multiple assays and imaging techniques.

## Extensions
- **Error Handling**: If there is an issue with the data import into OMERO, the system should provide clear error messages and suggestions for resolving the issues.
- **Data Export**: The researcher may need to export the combined image and ROI data for presentations or further analysis into an additional OMERO assay.

## Benefits
- **Comprehensive Analysis**: Combining various assays and imaging techniques provides a holistic view of the algal response to heat stress.
- **Efficient Data Management**: The ISA model and ARC structure ensure systematic documentation and organization of data.
- **Enhanced Visualization**: OMERO facilitates easy browsing and detailed examination of images and ROIs.

## Conclusion
This use case highlights the importance of integrating documentation, data analysis, and visualization tools in a scientific investigation. By leveraging ARC for metadata management and OMERO for image analysis, researchers can gain valuable insights into the biological effects of environmental stressors on algae.


<br />
<br />
<br />


# Use Case : Management of Data for Research Institute


## Background : 

Moritz, a data manager for his institute, wants to create a local ImageHub which will be connected to OMERO. All the data and metadata in the ImageHub remains in the local system as folders and in-place imported to OMERO.

Similarly, for ARCs he wants to create a local storage location where researchers from his institute would place and work on their ARC.  This location will be connected to OMERO and users would upload and update their ARC in OMERO and vice versa.
 

## Objective : 

In-place import of ARC to OMERO from ARC location or other configurable location.
Update of in-place imported ARC data and metadata in OMERO.
Update of data and metadata from OMERO to ARC location or other configurable location.

## Actors : 

1. Data Manager/ Steward : Manages and monitors data for the institute or facility.
2. Researchers : Creates an ARC and uses OMERO for imaging data and metadata.
3. IT department : Provides storage space for ARC location.
4. Developer :  Develops user friendly applications.


## Workflow Examples:

### User Perspective : 

1. Create an ARC in an ARC storage location.
2. Clicks a button in OMERO.web  and in-place imports the ARC or part of it (i.e. Assays, Study)
3. Draws ROI on an image in OMERO and saves it.
4. Clicks a button and updates the ARC in the ARC storage location.
5. After a week the user adds more data and metadata to the ARC in the ARC storage location.
6. Clicks a button in OMERO.web and updates the ARC in OMERO.web



### Developer Perspective:

1. Creates a user-friendly application.
2. Create an OMERO extension, for example a web-app extension.
3. Web app contains button to Upload(Link) data and metadata from an ARC in ARC storage location.
4. Web app provides a possibility to configure location of ARC (i.e. ARC storage location or other location in the local machine).
5. Web App provides buttons to Update the ARC in OMERO and Update the same ARC in ARC storage location. (i.e. on-demand syncing).

  

## Benefits:

1. With in-place import of data, duplication can be avoided.
2. Researchers can easily find, visualize and collaborate with imaging ARC linked to OMERO.
3. Bi-directional update (on-demand sync) of an ARC provides users to seamlessly utilize OMERO capabilities while being rooted in ARC at the ARC storage location.
 

