from abstract_arc_test import AbstractArcTest

from omero_arc.arc_mapping import IsaInvestigationMapper


class TestIsaInvestigationMapper(AbstractArcTest):
    def test_investigation_isa_attributes(
        self, project_with_arc_assay_annotation, project_1
    ):
        p = project_1
        pa = project_with_arc_assay_annotation

        m = IsaInvestigationMapper(p)
        ma = IsaInvestigationMapper(pa)

        assert len(ma.isa_attributes["investigation"]["values"]) == 1
        assert len(m.isa_attributes["investigation"]["values"]) == 1

        assert (
            m.isa_attributes["investigation"]["values"][0]["Investigation Identifier"]
            == "default-investigation-id"
        )

        assert (
            ma.isa_attributes["investigation"]["values"][0]["Investigation Identifier"]
            == "my-custom-investigation-id"
        )

        assert (
            ma.isa_attributes["investigation"]["values"][0]["Investigation Title"]
            == "Mitochondria in HeLa Cells"
        )
