import importlib
from copy import deepcopy
from functools import lru_cache

if importlib.util.find_spec("pandas"):
    import pandas as pd
else:
    raise ImportError(
        "Could not import pandas library. Make sure to "
        "install omero-cli-transfer with the optional "
        "[arc] addition"
    )


class AbstractIsaMapper:
    @lru_cache
    def _all_annotatation_objects(self):
        return [a for a in self.obj.listAnnotations()]

    def _annotation_data(self, annotation_type):
        namespace = self.isa_attribute_config[annotation_type]["namespace"]
        annotation_data = []
        for annotation in self._all_annotatation_objects():
            if annotation.getNs() == namespace:
                annotation_data.append(dict(annotation.getValue()))
        return annotation_data

    def arccommander_commands(self):
        cmds = []
        for annotation_type in self.isa_attributes:
            isa_attributes = deepcopy(self.isa_attributes[annotation_type])

            for d in isa_attributes["values"]:
                cmd = isa_attributes.get("command", []).copy()
                for key in d:
                    command_options = isa_attributes["command_options"]
                    command_option = command_options.get(key, None)
                    if command_option is not None:
                        value = d[key]
                        cmd.append(command_option)
                        cmd.append(value)
                cmds.append(cmd)
        return cmds

    def _create_isa_attributes(self):
        isa_attributes = {}
        for annotation_type in self.isa_attribute_config:
            annotation_data = self._annotation_data(annotation_type)
            config = self.isa_attribute_config[annotation_type]

            isa_attributes[annotation_type] = {}

            if annotation_type == "metadata":
                assert (
                    len(annotation_data) <= 1
                ), f"only one annotation allowed for {config['namespace']}"
                command = config.get("command", [])

            command = []
            for arg in config.get("command", []):
                if callable(arg):
                    arg = arg()
                command.append(arg)

            isa_attributes[annotation_type]["values"] = []
            isa_attributes[annotation_type]["command"] = command
            isa_attributes[annotation_type]["command_options"] = config[
                "command_options"
            ]
            values_to_set = {}
            if len(annotation_data) == 0:
                # set defaults if no annotations available
                for key in config["default_values"]:
                    value = config["default_values"][key]
                    if value is not None:
                        values_to_set[key] = value
                if len(values_to_set) > 0:
                    isa_attributes[annotation_type]["values"].append(values_to_set)
            else:
                # set annotation value if key is
                # registered in config["default_values"]
                for annotation in annotation_data:
                    for key in config["default_values"]:
                        value = annotation.get(key, None)
                        if value is not None:
                            values_to_set[key] = value
                    if len(values_to_set) > 0:
                        isa_attributes[annotation_type]["values"].append(
                            values_to_set.copy()
                        )
            if len(isa_attributes[annotation_type]["values"]) == 0:
                del isa_attributes[annotation_type]

            self.isa_attributes = isa_attributes


class AbstractIsaAssaySheetMapper:
    def __init__(self, ome_dataset):
        self.ome_dataset = ome_dataset

    def tbl(self, conn):
        objs = conn.getObjects(
            self.obj_type, opts={"dataset": self.ome_dataset.getId()}
        )
        objs = [obj for obj in objs]

        rows = [self.isa_column_mapping(obj) for obj in objs]
        df = pd.DataFrame(rows)
        df.name = self.sheet_name
        return df


class IsaInvestigationMapper(AbstractIsaMapper):
    def __init__(self, ome_project):
        """Maps data of an omero project to isa investigation attributes of
        an ARC.

        The mapping of each value is defined in isa_attribute_config.
        Values are stored in Omero
        as mapped annotations linked to the omero project.

        * namespace: Mapped annotations are be identified by their
            namespace. Only annotations that match the specified
            namespace are assigned to the respective ARC key-values.
        * default_values: Defines all keys that can be transfered
           from the mapped annotation to the ARC and defines default values,
           if the value is not set in a mapped annotation.
        * command: ARCs are manipulated with the ARCCommander CLI.
           command defines the ARCommander command that is executed to write
            the data from the mapped annotation to the ARC repository.



        """
        self.obj = ome_project
        owner = ome_project.getOwner()  # used to set default values below
        # annotation
        self.isa_attribute_config = {
            "investigation": {
                "namespace": "ARC:ISA:INVESTIGATION:INVESTIGATION",
                "default_values": {
                    "Investigation Identifier": "default-investigation-id",
                    "Investigation Title": None,
                    "Investigation Description": None,
                    "Investigation Submission Date": None,
                    "Investigation Public Release Date": None,
                },
                "command": ["arc", "investigation", "create"],
                "command_options": {
                    "Investigation Identifier": "--identifier",
                    "Investigation Title": "--title",
                    "Investigation Description": "--description",
                    "Investigation Submission Date": "--submissiondate",
                    "Investigation Public Release Date": "--publicreleasedate",
                },
            },
            "publications": {
                "namespace": ("ARC:ISA:INVESTIGATION:INVESTIGATION PUBLICATIONS"),
                "default_values": {
                    "Investigation Publication DOI": None,
                    "Investigation Publication PubMed ID": None,
                    "Investigation Publication Author List": None,
                    "Investigation Publication Title": None,
                    "Investigation Publication Status": None,
                    ("Investigation Publication Status " "Term Accession Number"): None,
                    "Investigation Publication Status Term Source REF": None,
                },
                "command": [
                    "arc",
                    "investigation",
                    "publication",
                    "register",
                ],
                "command_options": {
                    "Investigation Publication DOI": "--doi",
                    "Investigation Publication PubMed ID": "--pubmedid",
                    "Investigation Publication Author List": "--authorlist",
                    "Investigation Publication Title": "--title",
                    "Investigation Publication Status": "--status",
                    (
                        "Investigation Publication Status " "Term Accession Number"
                    ): "--statustermaccessionnumber",
                    (
                        "Investigation Publication Status " "Term Source REF"
                    ): "--statustermsourceref",
                },
            },
            "contacts": {
                "namespace": "ARC:ISA:INVESTIGATION:INVESTIGATION CONTACTS",
                "default_values": {
                    "Investigation Person Last Name": owner.getLastName(),
                    "Investigation Person First Name": owner.getFirstName(),
                    "Investigation Person Email": owner.getEmail(),
                    "Investigation Person Phone": None,
                    "Investigation Person Fax": None,
                    "Investigation Person Address": None,
                    "Investigation Person Affiliation": None,
                    "Investigation Person orcid": None,
                    "Investigation Person Roles": None,
                    "Investigation Person Roles Term Accession Number": None,
                    "Investigation Person Roles Term Source REF": None,
                },
                "command": [
                    "arc",
                    "investigation",
                    "person",
                    "register",
                ],
                "command_options": {
                    "Investigation Person Last Name": "--lastname",
                    "Investigation Person First Name": "--firstname",
                    "Investigation Person Mid Initials": "--midinitials",
                    "Investigation Person Email": "--email",
                    "Investigation Person Phone": "--phone",
                    "Investigation Person Fax": "--fax",
                    "Investigation Person Address": "--address",
                    "Investigation Person Affiliation": "--affiliation",
                    "Investigation Person orcid": "--orcid",
                    "Investigation Person Roles": "--roles",
                    (
                        "Investigation Person Roles " "Term Accession Number"
                    ): "--rolestermaccessionnumber",
                    (
                        "Investigation Person Roles " "Term Source REF"
                    ): "--rolestermsourceref",
                },
            },
        }

        self._create_isa_attributes()


class IsaStudyMapper(AbstractIsaMapper):
    def study_identifier(self):
        return self.isa_attributes["metadata"]["values"][0]["Study Identifier"]

    def __init__(self, ome_project):
        self.obj = ome_project
        owner = ome_project.getOwner()
        # annotation
        self.isa_attribute_config = {
            "metadata": {
                "namespace": "ARC:ISA:STUDY:STUDY METADATA",
                "default_values": {
                    "Study Identifier": ome_project.getName().lower().replace(" ", "-"),
                    "Study Title": ome_project.getName(),
                    "Study Description": ome_project.getDescription(),
                    "Study Submission Date": None,
                    "Study Public Release Date": None,
                },
                "command": ["arc", "study", "add"],
                "command_options": {
                    "Study Identifier": "--identifier",
                    "Study Title": "--title",
                    "Study Description": "--description",
                    "Study Submission Date": "--submissiondate",
                    "Study Public Release Date": "--publicreleasedate",
                },
            },
            "publications": {
                "namespace": "ARC:ISA:STUDY:STUDY PUBLICATIONS",
                "default_values": {
                    "Study Publication DOI": None,
                    "Study Publication PubMed ID": None,
                    "Study Publication Author List": None,
                    "Study Publication Title": None,
                    "Study Publication Status": None,
                    "Study Publication Status Term Accession Number": None,
                    "Study Publication Status Term Source REF": None,
                },
                "command": [
                    "arc",
                    "study",
                    "publication",
                    "register",
                    "--studyidentifier",
                    self.study_identifier,
                ],
                "command_options": {
                    "Study Publication DOI": "--doi",
                    "Study Publication PubMed ID": "--pubmedid",
                    "Study Publication Author List": "--authorlist",
                    "Study Publication Title": "--title",
                    "Study Publication Status": "--status",
                    "Study Publication Status Term Accession Number": (
                        "--statustermaccessionnumber"
                    ),
                    "Study Publication Status Term Source REF": (
                        "--statustermsourceref"
                    ),
                },
            },
            "design": {
                "namespace": "ARC:ISA:STUDY:STUDY DESIGN DESCRIPTORS",
                "default_values": {
                    "Study Design Type": None,
                    "Study Design Type Term Accession Number": None,
                    "Study Design Type Term Source REF": None,
                },
                "command": [
                    "arc",
                    "study",
                    "design",
                    "register",
                    "--studyidentifier",
                    self.study_identifier,
                ],
                "command_options": {
                    "Study Design Type": "--designtype",
                    "Study Design Type Term Accession Number": (
                        "--typetermaccessionnumber"
                    ),
                    "Study Design Type Term Source REF": "--typetermsourceref",
                },
            },
            "factors": {
                "namespace": "ARC:ISA:STUDY:STUDY FACTORS",
                "default_values": {
                    "Study Factor Name": None,
                    "Study Factor Type": None,
                    "Study Factor Type Term Accession Number": None,
                    "Study Factor Type Term Source REF": None,
                },
                "command": [
                    "arc",
                    "study",
                    "factor",
                    "register",
                    "--studyidentifier",
                    self.study_identifier,
                ],
                "command_options": {
                    "Study Factor Name": "--name",
                    "Study Factor Type": "--factortype",
                    "Study Factor Type Term Accession Number": (
                        "--typetermaccessionnumber"
                    ),
                    "Study Factor Type Term Source REF": "--typetermsourceref",
                },
            },
            "protocols": {
                "namespace": "ARC:ISA:STUDY:STUDY PROTOCOLS",
                "default_values": {
                    "Study Protocol Name": None,
                    "Study Protocol Type": None,
                    "Study Protocol Type Term Accession Number": None,
                    "Study Protocol Type Term Source REF": None,
                    "Study Protocol Description": None,
                    "Study Protocol URI": None,
                    "Study Protocol Version": None,
                    "Study Protocol Parameters Name": None,
                    "Study Protocol Parameters Term Accession Number": None,
                    "Study Protocol Parameters Term Source REF": None,
                    "Study Protocol Components Name": None,
                    "Study Protocol Components Type": None,
                    ("Study Protocol Components " "Type Term Accession Number"): None,
                    "Study Protocol Components Type Term Source REF": None,
                },
                "command": [
                    "arc",
                    "study",
                    "protocol",
                    "register",
                    "--studyidentifier",
                    self.study_identifier,
                ],
                "command_options": {
                    "Study Protocol Name": "--name",
                    "Study Protocol Type": "--protocoltype",
                    "Study Protocol Type Term Accession Number": (
                        "--typetermaccessionnumber"
                    ),
                    "Study Protocol Type Term Source REF": ("--typetermsourceref"),
                    "Study Protocol Description": "--description",
                    "Study Protocol URI": "--uri",
                    "Study Protocol Version": "--version",
                    "Study Protocol Parameters Name": "--parametersname",
                    "Study Protocol Parameters Term Accession Number": (
                        "--parameterstermaccessionnumber"
                    ),
                    "Study Protocol Parameters Term Source REF": (
                        "--parameterstermsourceref"
                    ),
                    "Study Protocol Components Name": "--componentsname",
                    "Study Protocol Components Type": "--componentstype",
                    "Study Protocol Components Type Term Accession Number": (
                        "--componentstypetermaccessionnumber"
                    ),
                    "Study Protocol Components Type Term Source REF": (
                        "--componentstypetermsourceref"
                    ),
                },
            },
            "contacts": {
                "namespace": "ARC:ISA:STUDY:STUDY CONTACTS",
                "default_values": {
                    "Study Person Last Name": owner.getLastName(),
                    "Study Person First Name": owner.getFirstName(),
                    "Study Person Email": owner.getEmail(),
                    "Study Person Phone": None,
                    "Study Person Fax": None,
                    "Study Person Address": None,
                    "Study Person Affiliation": None,
                    "Study Person orcid": None,
                    "Study Person Roles": None,
                    "Study Person Roles Term Accession Number": None,
                    "Study Person Roles Term Source REF": None,
                },
                "command": [
                    "arc",
                    "study",
                    "person",
                    "register",
                    "--studyidentifier",
                    self.study_identifier,
                ],
                "command_options": {
                    "Study Person Last Name": "--lastname",
                    "Study Person First Name": "--firstname",
                    "Study Person Mid Initials": "--midinitials",
                    "Study Person Email": "--email",
                    "Study Person Phone": "--phone",
                    "Study Person Fax": "--fax",
                    "Study Person Address": "--address",
                    "Study Person Affiliation": "--affiliation",
                    "Study Person orcid": "--orcid",
                    "Study Person Roles": "--roles",
                    "Study Person Roles Term Accession Number": (
                        "--rolestermaccessionnumber"
                    ),
                    "Study Person Roles Term Source REF": ("--rolestermsourceref"),
                },
            },
        }

        self._create_isa_attributes()


class IsaAssayMapper(AbstractIsaMapper):
    def assay_identifier(self):
        return self.isa_attributes["metadata"]["values"][0]["Assay Identifier"]

    def study_identifier(self):
        return self.isa_attributes["metadata"]["values"][0]["Study Identifier"]

    def __init__(self, ome_dataset, study_identifier, image_filename_getter):
        self.image_filename_getter = image_filename_getter

        self.obj = ome_dataset
        owner = ome_dataset.getOwner()

        self.isa_attribute_config = {
            "metadata": {
                "namespace": "ARC:ISA:ASSAY:ASSAY METADATA",
                "default_values": {
                    "Assay Identifier": ome_dataset.getName().lower().replace(" ", "-"),
                    "Measurement Type": None,
                    "Measurement Type Term Accession Number": None,
                    "Measurement Type Term Source REF": None,
                    "Technology Type": None,
                    "Technology Type Term Accession Number": None,
                    "Technology Type Term Source Ref": None,
                    "Technolology Platform": None,
                },
                "command": [
                    "arc",
                    "assay",
                    "add",
                    "--studyidentifier",
                    study_identifier,
                ],
                "command_options": {
                    "Assay Identifier": "--assayidentifier",
                    "Measurement Type": "--measurementtype",
                    # mixed up on purpose to deal with arc commander bug
                    # https://github.com/nfdi4plants/ARCCommander/issues/232
                    "Measurement Type Term Accession Number": (
                        "--measurementtypetermsourceref"
                    ),
                    "Measurement Type Term Source REF": (
                        "--measurementtypetermaccessionnumber"
                    ),
                    "Technology Type": "--technologytype",
                    # mixed up on purpose to deal with arc commander bug
                    "Technology Type Term Accession Number": (
                        "--technologytypetermsourceref"
                    ),
                    "Technology Type Term Source Ref": (
                        "--technologytypetermaccessionnumber"
                    ),
                    "Technolology Platform": "--technologyplatform",
                },
            },
            "contacts": {
                "namespace": "ARC:ISA:ASSAY:ASSAY PERFORMERS",
                "default_values": {
                    "Last Name": owner.getLastName(),
                    "First Name": owner.getFirstName(),
                    "Email": owner.getEmail(),
                    "Phone": None,
                    "Fax": None,
                    "Address": None,
                    "Affiliation": None,
                    "orcid": None,
                    "Roles": None,
                    "Roles Term Accession Number": None,
                    "Roles Term Source REF": None,
                },
                "command": [
                    "arc",
                    "assay",
                    "person",
                    "register",
                    "--assayidentifier",
                    self.assay_identifier,
                ],
                "command_options": {
                    "Last Name": "--lastname",
                    "First Name": "--firstname",
                    "Mid Initials": "--midinitials",
                    "Email": "--email",
                    "Phone": "--phone",
                    "Fax": "--fax",
                    "Address": "--address",
                    "Affiliation": "--affiliation",
                    "orcid": "--orcid",
                    "Roles": "--roles",
                    "Roles " "Term Accession Number": "--rolestermaccessionnumber",
                    "Roles " "Term Source REF": "--rolestermsourceref",
                },
            },
        }
        self._create_isa_attributes()
        self.isa_sheets = [
            IsaAssaySheetImageFilesMapper(ome_dataset, self.image_filename_getter),
            IsaAssaySheetImageMetadataMapper(ome_dataset),
        ]


class IsaAssaySheetImageFilesMapper(AbstractIsaAssaySheetMapper):
    def __init__(self, ome_dataset, image_filename_getter):
        self.obj_type = "Image"
        self.sheet_name = "Image Files"
        self.image_filename_getter = image_filename_getter

        super().__init__(ome_dataset)

    def isa_column_mapping(self, image):
        isa_column_mapping = {
            "Image ID": image.getId(),
            "Name": image.getName(),
            "Description": image.getDescription(),
            "Filename": self.image_filename_getter(image.getId(), abspath=False).name,
        }
        return isa_column_mapping


class IsaAssaySheetImageMetadataMapper(AbstractIsaAssaySheetMapper):
    def __init__(self, ome_dataset):
        self.obj_type = "Image"
        self.sheet_name = "Image Metadata"
        super().__init__(ome_dataset)

    def isa_column_mapping(self, image):
        def _pixel_unit(image):
            pix = image.getPixelSizeX(units=True)
            if pix is None:
                return
            return pix.getUnit()

        isa_column_mapping = {
            "Image ID": image.getId(),
            "Image Size X": image.getSizeX(),
            "Image Size Y": image.getSizeY(),
            "Image Size Z": image.getSizeZ(),
            "Pixel Size X": image.getPixelSizeX(),
            "Pixel Size Y": image.getPixelSizeY(),
            "Pixel Size Z": image.getPixelSizeZ(),
            "Pixel Size Unit": _pixel_unit(image),
        }
        return isa_column_mapping
