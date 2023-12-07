from abstract_arc_test import AbstractArcTest

from omero_arc.arc_mapping import IsaStudyMapper


class TestIsaStudyMapper(AbstractArcTest):
    def test_isa_attributes(self, project_with_arc_assay_annotation, project_1):
        p = project_1
        pa = project_with_arc_assay_annotation

        mapper_1 = IsaStudyMapper(p)
        assert (
            mapper_1.isa_attributes["metadata"]["values"][0]["Study Identifier"]
            == "my-first-study"
        )
        assert (
            mapper_1.isa_attributes["metadata"]["values"][0]["Study Title"]
            == "My First Study"
        )

        mapper_2 = IsaStudyMapper(pa)
        assert (
            mapper_2.isa_attributes["metadata"]["values"][0]["Study Identifier"]
            == "my-custom-study-id"
        )
        assert (
            mapper_2.isa_attributes["metadata"]["values"][0]["Study Title"]
            == "My Custom Study Title"
        )

        assert (
            mapper_2.isa_attributes["publications"]["values"][0]
            != mapper_2.isa_attributes["publications"]["values"][1]
        )
        assert mapper_2.isa_attributes["publications"]["values"][0][
            "Study Publication PubMed ID"
        ] in ("678978", "7898961")
        assert mapper_2.isa_attributes["publications"]["values"][1][
            "Study Publication PubMed ID"
        ] in ("678978", "7898961")

    def test_arccommander_cmds(self, project_with_arc_assay_annotation, project_1):
        p = project_1
        pa = project_with_arc_assay_annotation

        mapper_1 = IsaStudyMapper(p)

        cmds = mapper_1.arccommander_commands()
        assert len(cmds) == 2
        expected = [
            "arc",
            "study",
            "add",
            "--identifier",
            "my-first-study",
            "--title",
            "My First Study",
            "--description",
            "",
        ]
        assert cmds[0] == expected

        mapper_2 = IsaStudyMapper(pa)

        cmds = mapper_2.arccommander_commands()
        assert len(cmds) == 8
        expected = [
            "arc",
            "study",
            "add",
            "--identifier",
            "my-custom-study-id",
            "--title",
            "My Custom Study Title",
            "--description",
            "My custom description.",
            "--submissiondate",
            "8/11/2022",
            "--publicreleasedate",
            "3/3/2023",
        ]
        assert cmds[0] == expected

        expected_1 = [
            "arc",
            "study",
            "publication",
            "register",
            "--studyidentifier",
            "my-custom-study-id",
            "--doi",
            "10.1038/s41467-022-34205-9",
            "--pubmedid",
            "678978",
            "--authorlist",
            "Mueller M, Langer L L",
            "--title",
            ("HJKIH P9 orchestrates JKLKinase trafficking " "in mesenchymal cells."),
            "--status",
            "published",
            "--statustermaccessionnumber",
            "http://www.ebi.ac.uk/efo/EFO_0001796",
            "--statustermsourceref",
            "EFO",
        ]

        expected_2 = [
            "arc",
            "study",
            "publication",
            "register",
            "--studyidentifier",
            "my-custom-study-id",
            "--doi",
            "10.567/s56878-890890-330-3",
            "--pubmedid",
            "7898961",
            "--authorlist",
            "Mueller M, Langer L L, Berg J",
            "--title",
            "HELk reformation in activated Hela Cells",
            "--status",
            "published",
            "--statustermaccessionnumber",
            "http://www.ebi.ac.uk/efo/EFO_0001796",
            "--statustermsourceref",
            "EFO",
        ]

        assert cmds[1] != cmds[2]
        assert cmds[1] in (expected_1, expected_2)
        assert cmds[2] in (expected_1, expected_2)

    def test_annotation_data(self, project_1, project_with_arc_assay_annotation):
        p = project_1
        pa = project_with_arc_assay_annotation

        mapper_1 = IsaStudyMapper(p)
        annotation_data = mapper_1._annotation_data("metadata")
        assert len(annotation_data) == 0

        mapper_2 = IsaStudyMapper(pa)
        annotation_data = mapper_2._annotation_data("metadata")
        assert len(annotation_data) == 1
        assert annotation_data[0]["Study Title"] == "My Custom Study Title"

        annotation_data = mapper_2._annotation_data("publications")
        assert len(annotation_data) == 2
        assert (
            annotation_data[0]["Study Publication PubMed ID"]
            != annotation_data[1]["Study Publication PubMed ID"]
        )
        assert annotation_data[0]["Study Publication PubMed ID"] in (
            "678978",
            "7898961",
        )
        assert annotation_data[1]["Study Publication PubMed ID"] in (
            "678978",
            "7898961",
        )
