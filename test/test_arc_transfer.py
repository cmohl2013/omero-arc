from abstract_arc_test import AbstractArcTest
import pytest


class TestArcTransfer(AbstractArcTest):
    # def test_pack_arc_fails_for_dataset_cli(self, dataset_1, tmp_path):
    #     # only projects can be packed as arc
    #     dataset_identifier = f"Dataset:{dataset_1.id}"
    #     path_to_arc = tmp_path / "my_arc"
    #     args = self.args + [
    #         "pack",
    #         "--plugin","arc",
    #         dataset_identifier,
    #         str(path_to_arc),
    #     ]

    #     with pytest.raises(AssertionError):
    #         self.cli.invoke(args)

    def test_pack_arc(self, project_1, tmp_path):
        project_identifier = f"Project:{project_1.getId()}"
        path_to_arc = tmp_path / "my_arc"
        args = self.args + [
            "pack",
            "--plugin","arc",
            project_identifier,
            str(path_to_arc),
        ]
        self.cli.invoke(args)

        assert path_to_arc.exists()
        assert (path_to_arc / "assays").exists()
        assert (path_to_arc / "studies").exists()

    def test_pack_arc_existing_repo(self, arc_repo_1, project_2):
        project_identifier = f"Project:{project_2.getId()}"
        path_to_arc = arc_repo_1.path_to_arc_repo

        assert path_to_arc.exists()

        assert (path_to_arc / "studies/my-study-with-a-czi-image").exists()
        assert (path_to_arc / "assays/my-first-assay").exists()
        assert not (path_to_arc / "assays/my-second-assay").exists()
        assert not (path_to_arc / "studies/my-second-study").exists()

        args = self.args + [
            "pack",
             "--plugin","arc",
            project_identifier,
            str(path_to_arc),
        ]
        self.cli.invoke(args)

        assert (path_to_arc / "studies/my-study-with-a-czi-image").exists()
        assert (path_to_arc / "assays/my-first-assay").exists()
        assert (path_to_arc / "assays/my-second-assay").exists()
        assert (path_to_arc / "studies/my-second-study").exists()
