import numpy as np
import pandas as pd
from abstract_arc_test import AbstractArcTest

from omero_arc import ArcPacker
from omero_arc.arc_packer import is_arc_repo


class TestArcPacker(AbstractArcTest):
    def test_is_arc_repo(self, arc_repo_1, tmp_path):
        assert not is_arc_repo(tmp_path)
        assert is_arc_repo(arc_repo_1.path_to_arc_repo)

    def test_arc_packer_initialize(self, project_czi, tmp_path):
        path_to_arc_repo = tmp_path / "my_arc"
        ap = ArcPacker(
            ome_object=project_czi,
            path_to_arc_repo=path_to_arc_repo,
            path_to_image_files=None,
            image_filenames_mapping=None,
            conn=self.client,
        )
        ap.initialize_arc_repo()
        df = pd.read_excel(
            path_to_arc_repo / "isa.investigation.xlsx",
            index_col=0,
        )

        assert df.loc["Investigation Identifier"].iloc[0] == "default-investigation-id"
        assert df.loc["Investigation Title"].iloc[0] is np.nan

    def test_arc_packer_initialize_with_annotations(
        self, project_with_arc_assay_annotation, tmp_path
    ):
        path_to_arc_repo = tmp_path / "my_arc"
        ap = ArcPacker(
            ome_object=project_with_arc_assay_annotation,
            path_to_arc_repo=path_to_arc_repo,
            path_to_image_files=None,
            image_filenames_mapping=None,
            conn=self.client,
        )
        ap.initialize_arc_repo()
        df = pd.read_excel(
            path_to_arc_repo / "isa.investigation.xlsx",
            index_col=0,
        )

        assert (
            df.loc["Investigation Identifier"].iloc[0] == "my-custom-investigation-id"
        )
        assert df.loc["Investigation Title"].iloc[0] == "Mitochondria in HeLa Cells"

        assert df.loc["Investigation Person Last Name"].iloc[0] == "Mueller"
        assert (
            df.loc["Investigation Publication DOI"].iloc[0]
            == "10.1038/s41467-022-34205-9"
        )

    def test_arc_packer_create_study(self, project_1, tmp_path):
        path_to_arc_repo = tmp_path / "my_arc"
        ap = ArcPacker(
            ome_object=project_1,
            path_to_arc_repo=path_to_arc_repo,
            path_to_image_files=None,
            image_filenames_mapping=None,
            conn=self.gw,
        )
        ap.initialize_arc_repo()

        ap._create_study()

        assert (path_to_arc_repo / "studies/my-first-study").exists()
        assert (path_to_arc_repo / "studies/my-first-study/isa.study.xlsx").exists()

        df = pd.read_excel(
            path_to_arc_repo / "studies/my-first-study/isa.study.xlsx",
            sheet_name="Study",
            index_col=0,
        )

        assert df.loc["Study Title"].iloc[0] == "My First Study"
        assert df.loc["Study Identifier"].iloc[0] == "my-first-study"

    def test_arc_packer_create_study_with_annotations(
        self, project_with_arc_assay_annotation, tmp_path
    ):
        project = project_with_arc_assay_annotation
        path_to_arc_repo = tmp_path / "my_arc"
        ap = ArcPacker(
            ome_object=project,
            path_to_arc_repo=path_to_arc_repo,
            path_to_image_files=None,
            image_filenames_mapping=None,
            conn=self.gw,
        )
        ap.initialize_arc_repo()

        ap._create_study()

        assert (path_to_arc_repo / "studies/my-custom-study-id").exists()
        assert (path_to_arc_repo / "studies/my-custom-study-id/isa.study.xlsx").exists()

        df = pd.read_excel(
            path_to_arc_repo / "studies/my-custom-study-id/isa.study.xlsx",
            sheet_name="Study",
            index_col=0,
        )

        assert df.loc["Study Title"].iloc[0] == "My Custom Study Title"
        assert df.loc["Study Identifier"].iloc[0] == "my-custom-study-id"
        assert df.loc["Study Submission Date"].iloc[0] == "8/11/2022"
        assert df.loc["Study Public Release Date"].iloc[0] == "3/3/2023"
        df = pd.read_excel(
            path_to_arc_repo / "isa.investigation.xlsx",
            sheet_name="isa_investigation",
            index_col=0,
        )
        assert df.loc["Study Title"].iloc[0] == "My Custom Study Title"
        assert df.loc["Study Identifier"].iloc[0] == "my-custom-study-id"
        assert df.loc["Study Submission Date"].iloc[0] == "8/11/2022"
        assert df.loc["Study Public Release Date"].iloc[0] == "3/3/2023"

        assert (
            df.loc["Study Publication PubMed ID"].iloc[0]
            != df.loc["Study Publication PubMed ID"].iloc[1]
        )
        assert df.loc["Study Publication PubMed ID"].iloc[0] in (
            "678978",
            "7898961",
        )
        assert df.loc["Study Publication PubMed ID"].iloc[1] in (
            "678978",
            "7898961",
        )
        assert df.loc["Study Design Type"].iloc[0] == "Transmission Electron Microscopy"

        assert (
            df.loc["Study Factor Name"].iloc[0] != df.loc["Study Factor Name"].iloc[1]
        )
        assert df.loc["Study Factor Name"].iloc[0] in (
            "My Factor",
            "My Second Factor",
        )
        assert df.loc["Study Factor Name"].iloc[1] in (
            "My Factor",
            "My Second Factor",
        )

        assert (
            df.loc["Study Protocol Name"].iloc[0]
            == "Cell embedding for electron microscopy"
        )
        assert df.loc["Study Protocol Version"].iloc[0] == "0.0.1"

        assert df.loc["Study Person Last Name"].iloc[0] == "Mueller"

    def test_arc_packer_create_assays(self, project_1, tmp_path):
        path_to_arc_repo = tmp_path / "my_arc"
        ap = ArcPacker(
            ome_object=project_1,
            path_to_arc_repo=path_to_arc_repo,
            path_to_image_files=None,
            image_filenames_mapping=None,
            conn=self.gw,
        )
        ap.initialize_arc_repo()

        ap._create_study()
        ap._create_assays()

        assert (path_to_arc_repo / "assays/my-first-assay").exists()
        assert (path_to_arc_repo / "assays/my-second-assay").exists()

    def test_arc_packer_create_assays_with_annotations(
        self, project_with_arc_assay_annotation, tmp_path
    ):
        path_to_arc_repo = tmp_path / "my_arc"
        ap = ArcPacker(
            ome_object=project_with_arc_assay_annotation,
            path_to_arc_repo=path_to_arc_repo,
            path_to_image_files=None,
            image_filenames_mapping=None,
            conn=self.gw,
        )
        ap.initialize_arc_repo()

        ap._create_study()
        ap._create_assays()

        assert (path_to_arc_repo / "assays/my-custom-assay-id").exists()

        df = pd.read_excel(
            path_to_arc_repo / "assays/my-custom-assay-id/isa.assay.xlsx",
            sheet_name="Assay",
            index_col=0,
        )

        assert (
            df.loc["Measurement Type"].iloc[0]
            == "High resolution transmission electron micrograph"
        )
        assert df.loc["Measurement Type Term Source REF"].iloc[0] == "CHMO"
        assert df.loc["Technology Type Term Source REF"].iloc[0] == "BAO"
        assert (
            df.loc["Technology Type Term Accession Number"].iloc[0]
            == "http://www.bioassayontology.org/bao#BAO_0000455"
        )

        assert df.loc["Technology Type"].iloc[0] == "transmission electron microscopy"
        assert df.loc["Technology Platform"].iloc[0] == "JEOL JEM2100Plus"

    def test_arc_packer_add_image_data_for_assay(
        self,
        project_czi,
        path_omero_data_czi,
        omero_data_czi_image_filenames_mapping,
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
        ap.initialize_arc_repo()

        ap._create_study()
        ap._create_assays()
        ap._add_image_data_for_assay(assay_identifier="my-first-assay")
        ap._add_image_data_for_assay(assay_identifier="my-assay-with-czi-images")

        dataset = ap.ome_dataset_for_isa_assay["my-first-assay"]
        for image in self.gw.getObjects("Image", opts={"dataset": dataset.getId()}):
            relpath = ap.image_filename(image.getId(), abspath=False)
            abspath = tmp_path / "my_arc/assays/my-first-assay/dataset" / relpath.name
            assert abspath.exists()

    def test_original_metadata(self, arc_repo_1, project_czi):
        ap = arc_repo_1

        # ap._add_original_metadata()
        datasets = self.gw.getObjects("Dataset", opts={"project": project_czi.getId()})

        for dataset in datasets:
            folder = (
                ap.path_to_arc_repo
                / f"assays/{dataset.name.lower().replace(' ','-')}/protocols"
            )
            images = self.gw.getObjects("Image", opts={"dataset": dataset.getId()})
            for image in images:
                metadata_filepath = folder / f"ImageID{image.getId()}_metadata.json"
                print(metadata_filepath)
                assert metadata_filepath.exists()

    def test_generate_isa_assay_tables(
        self,
        arc_repo_1,
    ):
        ap = arc_repo_1

        dfs = ap.isa_assay_tables(assay_identifier="my-assay-with-czi-images")
        for df in dfs:
            assert not df.empty

    def test_add_isa_assay_sheets(
        self,
        arc_repo_1,
    ):
        ap = arc_repo_1
        # ap._add_isa_assay_sheets()

        for assay_identifier in ["my-assay-with-czi-images", "my-first-assay"]:
            isa_assay_file = (
                ap.path_to_arc_repo / f"assays/{assay_identifier}/isa.assay.xlsx"
            )
            for sheet_name in ["Image Files", "Image Metadata"]:
                df = pd.read_excel(isa_assay_file, sheet_name=sheet_name)
                assert not df.empty
        pass
