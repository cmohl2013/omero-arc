from omero_cli_transfer import TransferControl
from omero.gateway import BlitzGateway
from omero.model import MapAnnotationI, NamedValue
from omero.rtypes import rstring
import pytest
from pathlib import Path
from ome_types import from_xml
from generate_xml import list_file_ids
import tarfile
import os
import shutil
from omero_cli_transfer import ArcPacker
from omero.testlib import ITest
from omero.cli import CLI
from omero.plugins.sessions import SessionsControl


class AbstractCLITest(ITest):
    @classmethod
    def setup_class(cls):
        super(AbstractCLITest, cls).setup_class()
        cls.cli = CLI()
        cls.cli.register("sessions", SessionsControl, "TEST")

    def setup_mock(self):
        self.mox = mox.Mox()

    def teardown_mock(self):
        self.mox.UnsetStubs()
        self.mox.VerifyAll()


class AbstractArcTest(AbstractCLITest):
    def setup_method(self, method):
        self.args = self.login_args()
        self.cli.register("transfer", TransferControl, "TEST")
        self.args += ["transfer"]
        self.gw = BlitzGateway(client_obj=self.client)
        self.session = self.client.getSessionId()

    def create_mapped_annotation(
        self, name=None, map_values=None, namespace=None, parent_object=None
    ):
        map_annotation = self.new_object(MapAnnotationI, name=name)
        if map_values is not None:
            map_value_ls = [
                NamedValue(str(key), str(map_values[key])) for key in map_values
            ]
            map_annotation.setMapValue(map_value_ls)
        if namespace is not None:
            map_annotation.setNs(rstring(namespace))

        map_annotation = self.client.sf.getUpdateService().saveAndReturnObject(
            map_annotation
        )
        if parent_object is not None:
            self.link(parent_object, map_annotation)

        return map_annotation

    @pytest.fixture(scope="function")
    def dataset_1(self):
        dataset_1 = self.make_dataset(name="My First Assay")

        for i in range(3):
            img_name = f"assay 2 image {i}"
            image = self.create_test_image(
                80, 40, 3, 4, 2, self.client.getSession(), name=img_name
            )
            self.link(dataset_1, image)

        return self.gw.getObject("Dataset", dataset_1.id._val)

    @pytest.fixture(scope="function")
    def dataset_1_obj(self):
        dataset_1 = self.make_dataset(name="My First Assay")

        for i in range(3):
            img_name = f"assay 2 image {i}"
            image = self.create_test_image(
                80, 40, 3, 4, 2, self.client.getSession(), name=img_name
            )
            self.link(dataset_1, image)

        return dataset_1

    @pytest.fixture(scope="function")
    def dataset_2(self):
        dataset_2 = self.make_dataset(name="My Second Assay")

        for i in range(3):
            img_name = f"assay 2 image {i}"
            image = self.create_test_image(
                100, 100, 1, 1, 1, self.client.getSession(), name=img_name
            )
            self.link(dataset_2, image)

        return dataset_2

    @pytest.fixture(scope="function")
    def project_1(self, dataset_1, dataset_2):
        project_1 = self.make_project(name="My First Study")

        self.link(project_1, dataset_1)
        self.link(project_1, dataset_2)

        return self.gw.getObject("Project", project_1.id._val)

    @pytest.fixture(scope="function")
    def project_2(self, dataset_2):
        project_2 = self.make_project(name="My Second Study")

        self.link(project_2, dataset_2)

        return self.gw.getObject("Project", project_2.id._val)

    @pytest.fixture(scope="function")
    def dataset_czi_1(self):
        dataset = self.make_dataset(name="My Assay with CZI Images")

        def _add_local_image_file(path_to_img_file):
            assert path_to_img_file.exists()
            target_str = f"Dataset:{dataset.id._val}"
            self.import_image(path_to_img_file, extra_args=["--target", target_str])

        path_to_img_file = (
            Path(__file__).parent / "data/img_files/CD_s_1_t_3_c_2_z_5.czi"
        )
        _add_local_image_file(path_to_img_file=path_to_img_file)

        image_tif = self.create_test_image(
            100,
            100,
            1,
            1,
            1,
            self.client.getSession(),
            name="another pixel image",
        )
        self.link(dataset, image_tif)

        path_to_img_file = Path(__file__).parent / "data/img_files/sted-confocal.lif"
        _add_local_image_file(path_to_img_file=path_to_img_file)

        return dataset

    @pytest.fixture(scope="function")
    def dataset_with_arc_assay_annotation(self):
        dataset = self.make_dataset(name="My Assay with Annotations")

        annotation_namespace = "ARC:ISA:ASSAY:ASSAY METADATA"
        annotations = {
            "Assay Identifier": "my-custom-assay-id",
            "Measurement Type": ("High resolution transmission electron micrograph"),
            "Measurement Type Term Accession Number": (
                "http://purl.obolibrary.org/obo/CHMO_0002125"
            ),
            "Measurement Type Term Source REF": "CHMO",
            "Technology Type": "transmission electron microscopy",
            "Technology Type Term Accession Number": (
                "http://www.bioassayontology.org/bao#BAO_0000455"
            ),
            "Technology Type Term Source Ref": "BAO",
            "Technolology Platform": "JEOL JEM2100Plus",
        }
        self.create_mapped_annotation(
            name=annotation_namespace,
            map_values=annotations,
            namespace=annotation_namespace,
            parent_object=dataset,
        )

        annotation_namespace = "ARC:ISA:ASSAY:ASSAY PERFORMERS"
        annotations = {
            "Last Name": "Doe",
            "First Name": "John",
            "Email": "john.doe@email.com",
            "Phone": "+49 (0)221 12345",
            "Fax": "+49 (0)221 12347",
            "Address": "Cologne University, Cologne",
            "Affiliation": "Institute of Plant Science, Cologne University",
            "orcid": "789897890ß6",
            "Roles": "researcher",
            "Roles Term Accession Number": ("http://purl.org/spar/scoro/researcher"),
            "Roles Term Source REF": "SCoRO",
        }
        self.create_mapped_annotation(
            name=annotation_namespace,
            map_values=annotations,
            namespace=annotation_namespace,
            parent_object=dataset,
        )

        annotation_namespace = "ARC:ISA:ASSAY:ASSAY PERFORMERS"
        annotations = {
            "Last Name": "Laura",
            "First Name": "Langer",
            "Mid Initials": "L",
            "Email": "laura.l.langer@email.com",
            "Phone": "0211-12345",
            "Roles": "researcher",
            "Roles Term Accession Number": ("http://purl.org/spar/scoro/researcher"),
            "Roles Term Source REF": "SCoRO",
        }
        self.create_mapped_annotation(
            name=annotation_namespace,
            map_values=annotations,
            namespace=annotation_namespace,
            parent_object=dataset,
        )

        # image 1
        image_tif = self.create_test_image(
            100,
            100,
            1,
            1,
            1,
            self.client.getSession(),
            name="pixel image 1",
        )
        self.link(dataset, image_tif)

        # annotation_namespace = "ARC:ISA:ASSAY:my-assay-with-annotations"
        # annotations = {
        #     "Source Name": 8894,
        #     "Protocol Type": "assay protocol",
        #     "Term Source Ref": "DPBO",
        #     "Term Accesssion Number": ("https://purl.obolibrary.org/obo/DPBO_1000177"),
        #     "Protocol REF": "image_acquisition.md",
        #     "Parameter[OperationMode]": "IMAGING",
        #     "Parameter[IndicatedMagnification]": 10000,
        #     "Parameter[Voltage]": 80000,
        #     "Parameter[scanrate]": 1.13,
        #     "Unit": "nm",
        # }
        # self.create_mapped_annotation(
        #     name=annotation_namespace,
        #     map_values=annotations,
        #     namespace=annotation_namespace,
        #     parent_object=image_tif,
        # )

        def _add_local_image_file(path_to_img_file):
            assert path_to_img_file.exists()
            target_str = f"Dataset:{dataset.id._val}"
            pix_ids = self.import_image(
                path_to_img_file, extra_args=["--target", target_str]
            )
            return pix_ids

        path_to_img_file = (
            Path(__file__).parent.parent
            / "data/arc_test_data/img_files/CD_s_1_t_3_c_2_z_5.czi"
        )
        pix_ids = _add_local_image_file(path_to_img_file=path_to_img_file)
        # image_czi = self.gw.getObject("Image", int(pix_ids[0]))

        # annotation_namespace = "ARC:ISA:ASSAY:my-assay-with-annotations"
        # annotations = {
        #     "Source Name": 7777,
        #     "Protocol Type": "assay protocol",
        #     "Term Source Ref": "DPBO",
        #     "TermA ccesssion Number": ("https://purl.obolibrary.org/obo/DPBO_1000177"),
        #     "Protocol REF": "image_acquisition.md",
        #     "Parameter[OperationMode]": "IMAGING",
        #     "Parameter[IndicatedMagnification]": 5000,
        #     "Parameter[Voltage]": 60000,
        #     "Parameter[scanrate]": 1.17,
        #     "Unit": "nm",
        # }
        # self.create_mapped_annotation(
        #     name=annotation_namespace,
        #     map_values=annotations,
        #     namespace=annotation_namespace,
        #     parent_object=image_czi,
        # )

        path_to_img_file = (
            Path(__file__).parent.parent
            / "data/arc_test_data/img_files/sted-confocal.lif"
        )
        _add_local_image_file(path_to_img_file=path_to_img_file)

        return dataset

    @pytest.fixture(scope="function")
    def dataset_with_arc_assay_annotation_obj(self, dataset_with_arc_assay_annotation):
        return self.gw.getObject("Dataset", dataset_with_arc_assay_annotation.id._val)

    @pytest.fixture(scope="function")
    def project_with_arc_assay_annotation(
        self, dataset_1, dataset_with_arc_assay_annotation
    ):
        project = self.make_project(name="My Study with Annotations")
        self.link(project, dataset_1)
        self.link(project, dataset_with_arc_assay_annotation)

        annotation_namespace = "These Values are not relevant for ARCs"
        annotations = {"color 1": "red", "color 2": "blue"}
        self.create_mapped_annotation(
            name=annotation_namespace,
            map_values=annotations,
            namespace=annotation_namespace,
            parent_object=project,
        )

        annotation_namespace = "ARC:ISA:INVESTIGATION:ONTOLOGY SOURCE REFERENCE"
        annotations = {
            "Term Source Name": "EFO",
            "Term Source File": ("http://www.ebi.ac.uk/efo/releases/v3.14.0/efo.owl"),
            "Term Source Description": "Experimental Factor Ontology",
        }
        self.create_mapped_annotation(
            name=annotation_namespace,
            map_values=annotations,
            namespace=annotation_namespace,
            parent_object=project,
        )

        annotation_namespace = "ARC:ISA:INVESTIGATION:INVESTIGATION"
        annotations = {
            "Investigation Identifier": "my-custom-investigation-id",
            "Investigation Title": "Mitochondria in HeLa Cells",
            "Investigation Description": (
                "Observation of MDV formation in Mitochondria"
            ),
            "Investigation Submission Date": "8/11/2022",
            "Investigation Public Release Date": "1/12/2022",
        }
        self.create_mapped_annotation(
            name=annotation_namespace,
            map_values=annotations,
            namespace=annotation_namespace,
            parent_object=project,
        )

        annotation_namespace = "ARC:ISA:INVESTIGATION:INVESTIGATION CONTACTS"
        annotations = {
            "Investigation Person Last Name": "Mueller",
            "Investigation Person First Name": "Arno",
            "Investigation Person Email": "arno.mueller@email.com",
            "Investigation Person Roles": "researcher",
            "Investigation Person Roles Term Accession Number": (
                "http://purl.org/spar/scoro/researcher"
            ),
            "Investigation Person Roles Term Source REF": "SCoRO",
        }
        self.create_mapped_annotation(
            name=annotation_namespace,
            map_values=annotations,
            namespace=annotation_namespace,
            parent_object=project,
        )

        annotation_namespace = "ARC:ISA:INVESTIGATION:INVESTIGATION PUBLICATIONS"
        annotations = {
            "Investigation Publication DOI": "10.1038/s41467-022-34205-9",
            "Investigation Publication PubMed ID": 678978,
            "Investigation Publication Author List": "Mueller M, Langer L L",
            "Investigation Publication Title": (
                "HJKIH P9 orchestrates JKLKinase " "trafficking in mesenchymal cells."
            ),
            "Investigation Publication Status": "published",
            "Investigation Publication Status Term Accession Number": (
                "http://www.ebi.ac.uk/efo/EFO_0001796"
            ),
            "Investigation Publication Status Term Source REF": "EFO",
        }
        self.create_mapped_annotation(
            name=annotation_namespace,
            map_values=annotations,
            namespace=annotation_namespace,
            parent_object=project,
        )

        annotation_namespace = "ARC:ISA:STUDY:STUDY METADATA"
        annotations = {
            "Study Identifier": "my-custom-study-id",
            "Study Title": "My Custom Study Title",
            "Study Description": "My custom description.",
            "Study Submission Date": "8/11/2022",
            "Study Public Release Date": "3/3/2023",
        }
        self.create_mapped_annotation(
            name=annotation_namespace,
            map_values=annotations,
            namespace=annotation_namespace,
            parent_object=project,
        )

        annotation_namespace = "ARC:ISA:STUDY:STUDY PUBLICATIONS"
        annotations = {
            "Study Publication DOI": "10.1038/s41467-022-34205-9",
            "Study Publication PubMed ID": 678978,
            "Study Publication Author List": "Mueller M, Langer L L",
            "Study Publication Title": (
                "HJKIH P9 orchestrates " "JKLKinase trafficking in mesenchymal cells."
            ),
            "Study Publication Status": "published",
            "Study Publication Status Term Accession Number": (
                "http://www.ebi.ac.uk/efo/EFO_0001796"
            ),
            "Study Publication Status Term Source REF": "EFO",
        }
        self.create_mapped_annotation(
            name=annotation_namespace,
            map_values=annotations,
            namespace=annotation_namespace,
            parent_object=project,
        )
        annotation_namespace = "ARC:ISA:STUDY:STUDY PUBLICATIONS"
        annotations = {
            "Study Publication DOI": "10.567/s56878-890890-330-3",
            "Study Publication PubMed ID": 7898961,
            "Study Publication Author List": "Mueller M, Langer L L, Berg J",
            "Study Publication Title": ("HELk reformation in activated Hela Cells"),
            "Study Publication Status": "published",
            "Study Publication Status Term Accession Number": (
                "http://www.ebi.ac.uk/efo/EFO_0001796"
            ),
            "Study Publication Status Term Source REF": "EFO",
        }
        self.create_mapped_annotation(
            name=annotation_namespace,
            map_values=annotations,
            namespace=annotation_namespace,
            parent_object=project,
        )

        annotation_namespace = "ARC:ISA:STUDY:STUDY DESIGN DESCRIPTORS"
        annotations = {
            "Study Design Type": "Transmission Electron Microscopy",
            "Study Design Type Term Accession Number": (
                "http://www.ebi.ac.uk/efo/EFO_0001796"
            ),
            "Study Design Type Term Source REF": "EFO",
        }
        self.create_mapped_annotation(
            name=annotation_namespace,
            map_values=annotations,
            namespace=annotation_namespace,
            parent_object=project,
        )

        annotation_namespace = "ARC:ISA:STUDY:STUDY FACTORS"
        annotations = {
            "Study Factor Name": "My Factor",
            "Study Factor Type": "Factor for test reasons",
            "Study Design Type Term Accession Number": (
                "http://www.ebi.ac.uk/efo/EFO_0001796"
            ),
            "Study Design Type Term Source REF": "EFO",
        }
        self.create_mapped_annotation(
            name=annotation_namespace,
            map_values=annotations,
            namespace=annotation_namespace,
            parent_object=project,
        )

        annotation_namespace = "ARC:ISA:STUDY:STUDY FACTORS"
        annotations = {
            "Study Factor Name": "My Second Factor",
            "Study Factor Type": "Factor Number 2 for test reasons",
            "Study Design Type Term Accession Number": (
                "http://www.ebi.ac.uk/efo/EFO_0001796"
            ),
            "Study Design Type Term Source REF": "EFO",
        }
        self.create_mapped_annotation(
            name=annotation_namespace,
            map_values=annotations,
            namespace=annotation_namespace,
            parent_object=project,
        )

        annotation_namespace = "ARC:ISA:STUDY:STUDY PROTOCOLS"
        annotations = {
            "Study Protocol Name": "Cell embedding for electron microscopy",
            "Study Protocol Type": "Test Protocol Type",
            "Study Protocol Type Term Accession Number": (
                "http://www.ebi.ac.uk/efo/EFO_0001796"
            ),
            "Study Protocol Type Term Source REF": "EFO",
            "Study Protocol Description": "A protocol for test reasons.",
            "Study Protocol URI": (
                "urn:oasis:names:specification:docbook:dtd:xml:4.1.2"
            ),
            "Study Protocol Version": "0.0.1",
            "Study Protocol Parameters Name": ("temperature;" "glucose concentration"),
            "Study Protocol Parameters Term Accession Number": (
                "http://www.ebi.ac.uk/efo/EFO_0001796;"
                "http://www.ebi.ac.uk/efo/EFO_0001796"
            ),
            "Study Protocol Parameters Term Source REF": "EFO;EFO",
            "Study Protocol Components Name": (
                "SuperEmeddingMediumX;" "SuperEmeddingMediumY"
            ),
            "Study Protocol Components Type": "reagent;reagent",
            "Study Protocol Components Type Term Accession Number": (
                "http://www.ebi.ac.uk/efo/EFO_0001796;"
                "http://www.ebi.ac.uk/efo/EFO_0001796"
            ),
            "Study Protocol Components Type Term Source REF": "EFO;EFO",
        }
        self.create_mapped_annotation(
            name=annotation_namespace,
            map_values=annotations,
            namespace=annotation_namespace,
            parent_object=project,
        )

        annotation_namespace = "ARC:ISA:STUDY:STUDY CONTACTS"
        annotations = {
            "Study Person Last Name": "Mueller",
            "Study Person First Name": "Arno",
            "Study Person Email": "arno.mueller@email.com",
            "Study Person Roles": "researcher",
            "Study Person Roles Term Accession Number": (
                "http://purl.org/spar/scoro/researcher"
            ),
            "Study Person Roles Term Source REF": "SCoRO",
        }
        self.create_mapped_annotation(
            name=annotation_namespace,
            map_values=annotations,
            namespace=annotation_namespace,
            parent_object=project,
        )

        return self.gw.getObject("Project", project.id._val)

    @pytest.fixture(scope="function")
    def project_czi(self, dataset_czi_1, dataset_1):
        project_czi = self.make_project(name="My Study with a CZI Image")

        self.link(project_czi, dataset_czi_1)
        self.link(project_czi, dataset_1)

        return self.gw.getObject("Project", project_czi.id._val)

    @pytest.fixture(scope="function")
    def path_arc_test_data(self, project_1, project_czi, request):
        path_to_arc_test_data = (
            Path(__file__).parent.parent / "data/arc_test_data/packed_projects"
        )
        os.makedirs(path_to_arc_test_data, exist_ok=True)

        if request.config.option.skip_create_arc_test_data:
            # if pytest is used with option --not-create-arc-test-data
            return path_to_arc_test_data

        shutil.rmtree(path_to_arc_test_data)
        os.makedirs(path_to_arc_test_data, exist_ok=True)

        for project, project_name in [
            (project_1, "project_1"),
            (project_czi, "project_czi"),
        ]:
            project_identifier = f"Project:{project.getId()}"
            path_to_arc_test_dataset = path_to_arc_test_data / project_name
            args = self.args + [
                "pack",
                project_identifier,
                str(path_to_arc_test_dataset),
            ]
            self.cli.invoke(args)

            with tarfile.open(path_to_arc_test_dataset.with_suffix(".tar")) as f:
                f.extractall(path_to_arc_test_dataset)
            os.remove(path_to_arc_test_dataset.with_suffix(".tar"))

        return path_to_arc_test_data

    @pytest.fixture(scope="function")
    def path_omero_data_1(self, path_arc_test_data):
        return path_arc_test_data / "project_1"

    @pytest.fixture(scope="function")
    def path_omero_data_czi(self, path_arc_test_data):
        return path_arc_test_data / "project_czi"

    @pytest.fixture(scope="function")
    def omero_data_czi_image_filenames_mapping(self, path_omero_data_czi):
        with open(path_omero_data_czi / "transfer.xml") as f:
            xmldata = f.read()
        ome = from_xml(xmldata)
        return list_file_ids(ome)

    @pytest.fixture()
    def arc_repo_1(
        self,
        project_czi,
        omero_data_czi_image_filenames_mapping,
        path_omero_data_czi,
        tmp_path,
    ):
        path_to_arc_repo = tmp_path / "my_arc"

        ap = ArcPacker(
            ome_object=project_czi,
            path_to_arc_repo=path_to_arc_repo,
            path_to_image_files=path_omero_data_czi,
            image_filenames_mapping=omero_data_czi_image_filenames_mapping,
            conn=self.gw,
        )

        ap.create_arc_repo()
        return ap
