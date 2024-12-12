from abstract_arc_test import AbstractArcTest

from omero_arc.arc_mapping import IsaAssayMapper


class TestIsaAssayMapper(AbstractArcTest):
    def test_assay_isa_attributes(
        self, dataset_with_arc_assay_annotation_obj, dataset_1
    ):
        mapper_1 = IsaAssayMapper(
            dataset_1,
            study_identifier="my-first-study",
            image_filename_getter=None,
        )

        assert (
            mapper_1.isa_attributes["metadata"]["values"][0]["Assay Identifier"]
            == "my-first-assay"
        )

        assert mapper_1.isa_attributes["contacts"]["values"][0]["Last Name"] is not None

        da = dataset_with_arc_assay_annotation_obj

        mapper_2 = IsaAssayMapper(
            da, study_identifier="my-other-study", image_filename_getter=None
        )

        assert (
            mapper_2.isa_attributes["metadata"]["values"][0]["Assay Identifier"]
            == "my-custom-assay-id"
        )

        for i in range(2):
            assert mapper_2.isa_attributes["contacts"]["values"][i]["Last Name"] in ["Laura", "Doe"]
