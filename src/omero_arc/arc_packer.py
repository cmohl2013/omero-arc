import importlib
import json
import os
import shutil
import subprocess
from pathlib import Path

from omero_arc.arc_mapping import (IsaAssayMapper, IsaInvestigationMapper,
                                   IsaStudyMapper)

if importlib.util.find_spec("pandas"):
    import pandas as pd
else:
    raise ImportError(
        "Could not import pandas library. Make sure to "
        "install omero-cli-transfer with the optional "
        "[arc] addition"
    )


def fmt_identifier(title: str) -> str:
    return title.lower().replace(" ", "-")


def is_arc_repo(path: Path) -> bool:
    if (path / ".arc").exists():
        return True
    return False


def original_image_metadata(image):
    _, series_metadata, global_metadata = image.loadOriginalMetadata()

    series_metadata = dict(series_metadata) if len(series_metadata) > 0 else None
    global_metadata = dict(global_metadata) if len(global_metadata) > 0 else None

    out = {
        "series_metadata": series_metadata,
        "global_metadata": global_metadata,
    }

    return out


class ArcPacker(object):
    def __init__(
        self,
        ome_object,
        path_to_arc_repo: Path,
        path_to_image_files,
        image_filenames_mapping,
        conn,
    ):
        self.obj = ome_object  # must be a project
        self.path_to_arc_repo = path_to_arc_repo
        self.conn = conn
        self.image_filenames_mapping = image_filenames_mapping
        self.path_to_image_files = path_to_image_files

        self.isa_assay_mappers = []
        self.ome_dataset_for_isa_assay = {}

    def create_arc_repo(self):
        self.initialize_arc_repo()
        self.add_data_to_arc_repo()

    def add_data_to_arc_repo(self):
        self._create_study()
        self._create_assays()
        for assay_mapper in self.isa_assay_mappers:
            assay_identifier = assay_mapper.assay_identifier()
            self._add_image_data_for_assay(assay_identifier)
            self._add_original_metadata_for_assay(assay_identifier)
        self._add_isa_assay_sheets()

    def initialize_arc_repo(self):
        os.makedirs(self.path_to_arc_repo, exist_ok=False)

        subprocess.run(["arc", "init"], cwd=self.path_to_arc_repo)
        ome_project = self.obj
        mapper = IsaInvestigationMapper(ome_project)
        for command in mapper.arccommander_commands():
            if len(command) > 0:
                subprocess.run(command, cwd=self.path_to_arc_repo)

    def _create_study(self):
        ome_project = self.obj

        mapper = IsaStudyMapper(ome_project)
        for command in mapper.arccommander_commands():
            if len(command) > 0:
                subprocess.run(command, cwd=self.path_to_arc_repo)
        self.study_mapper = mapper

    def _create_assays(self):
        ome_project = self.obj
        project_id = ome_project.getId()

        def _filename_for_image(image_id):
            return self.image_filenames_mapping[f"Image:{image_id}"].name

        ome_datasets = self.conn.getObjects("Dataset", opts={"project": project_id})
        for dataset in ome_datasets:
            mapper = IsaAssayMapper(
                dataset,
                study_identifier=self.study_mapper.study_identifier(),
                image_filename_getter=_filename_for_image,
            )
            self.isa_assay_mappers.append(mapper)
            for command in mapper.arccommander_commands():
                if len(command) > 0:
                    subprocess.run(command, cwd=self.path_to_arc_repo)

            self.ome_dataset_for_isa_assay[mapper.assay_identifier()] = dataset

    def isa_assay_filename(self, assay_identifier):
        assert assay_identifier in self.assay_identifiers
        path = self.path_to_arc_repo / f"assays/{assay_identifier}/isa.assay.xlsx"
        assert path.exists()
        return path

    def image_filename(self, image_id, abspath=True):
        image_id_str = f"Image:{image_id}"

        rel_path = Path(self.image_filenames_mapping[image_id_str])

        if not abspath:
            return rel_path
        return self.path_to_image_files / rel_path

    def _add_image_data_for_assay(self, assay_identifier):
        # ome_dataset_id = self.assay_identifiers[assay_identifier]

        assert assay_identifier in self.ome_dataset_for_isa_assay
        dest_image_folder = self.path_to_arc_repo / f"assays/{assay_identifier}/dataset"
        ds = self.ome_dataset_for_isa_assay[assay_identifier]

        for image in self.conn.getObjects("Image", opts={"dataset": ds.getId()}):
            img_filepath_abs = self.image_filename(image.getId(), abspath=True)
            img_fileppath_rel = self.image_filename(image.getId(), abspath=False)
            target_path = dest_image_folder / img_fileppath_rel.name
            os.makedirs(target_path.parent, exist_ok=True)
            shutil.copy2(img_filepath_abs, target_path)

    def isa_assay_tables(self, assay_identifier):
        dataset = self.ome_dataset_for_isa_assay[assay_identifier]
        assay_mapper = IsaAssayMapper(
            dataset, self.study_mapper.study_identifier(), self.image_filename
        )
        tables = []
        images = self.conn.getObjects("Image", opts={"dataset": dataset.getId()})
        images = [im for im in images]
        for sheet_mapper in assay_mapper.isa_sheets:
            tables.append(sheet_mapper.tbl(self.conn))
        return tables

    def _add_isa_assay_sheets(self):
        for assay_identifier in self.ome_dataset_for_isa_assay.keys():
            isa_assay_file = (
                self.path_to_arc_repo / f"assays/{assay_identifier}/isa.assay.xlsx"
            )
            with pd.ExcelWriter(isa_assay_file, engine="openpyxl", mode="a") as writer:
                tables = self.isa_assay_tables(assay_identifier)
                for table in tables:
                    table.to_excel(writer, sheet_name=table.name, index=False)

    def _add_original_metadata_for_assay(self, assay_identifier):
        """writes json files with original metadata"""

        dataset = self.ome_dataset_for_isa_assay[assay_identifier]
        images = self.conn.getObjects("Image", opts={"dataset": dataset.getId()})
        for image in images:
            metadata = original_image_metadata(image)
            metadata["image_id"] = image.getId()
            metadata["image_filename"] = self.image_filename(
                image.getId(), abspath=False
            ).name

            savepath = self.path_to_arc_repo / (
                f"assays/{assay_identifier}"
                f"/protocols/ImageID{image.getId()}_metadata.json"
            )
            with open(savepath, "w") as f:
                json.dump(metadata, f, indent=4)
