from pprint import pprint

from pai.pipeline import PipelineParameter
from pai.operator import (
    ScriptOperator,
    PAI_PROGRAM_ENTRY_POINT_ENV_KEY,
    PAI_SOURCE_CODE_ENV_KEY,
    PAI_SCRIPT_TEMPLATE_DEFAULT_COMMAND,
)
from pai.pipeline.types import (
    PipelineArtifact,
    LocationArtifactMetadata,
    DataType,
    LocationType,
)

from pai.pipeline.types.artifact import MaxComputeTableArtifact
from tests.unit import BaseUnitTestCase
from tests.test_data import SCRIPT_DIR_PATH


class TestScriptOperator(BaseUnitTestCase):
    def test_script(self):
        entry_point = "run.py"
        script_templ = ScriptOperator(
            source_dir=SCRIPT_DIR_PATH,
            entry_file="run.py",
            inputs=[],
            env={
                "hello": "world",
            },
        )
        script_templ.prepare()
        manifest = script_templ.to_dict()
        manifest_env = manifest["spec"]["container"]["envs"]

        self.assertTrue(manifest_env.get(PAI_SOURCE_CODE_ENV_KEY).startswith("oss://"))
        self.assertEqual(
            manifest_env.get(PAI_PROGRAM_ENTRY_POINT_ENV_KEY, ""), entry_point
        )
        self.assertEqual(manifest_env.get("hello", ""), "world")

        self.assertEqual(
            manifest["spec"]["container"]["command"],
            [PAI_SCRIPT_TEMPLATE_DEFAULT_COMMAND],
        )

    def test_check_script_source_files(self):
        cases = [
            {
                "name": "oss_source_case1",
                "input": {
                    "entry_file": "oss://test_bucket/run.py",
                    "source_dir": "oss://test_bucket/hello/world",
                },
                "expectedErrorMsg": "OSS",
            },
            {
                "name": "oss_source_case2",
                "input": {
                    "entry_file": "oss://test_bucket/run.py",
                    "source_dir": "/test_bucket/hello/world",
                },
                "expectedErrorMsg": "OSS",
            },
            {
                "name": "entry_file_is_dir",
                "input": {
                    "entry_file": "oss://test_bucket/source_path/dir/",
                    "source_dir": "/test_bucket/hello/world",
                },
                "expectedErrorMsg": r"directory path",
            },
            {
                "name": "source",
                "input": {
                    "entry_file": "test_bucket/source_path/dir/run.py",
                    "source_dir": "/test_bucket/hello/world",
                },
                "expectedErrorMsg": "top-level directory",
            },
        ]

        for case in cases:
            with self.assertRaisesRegexp(ValueError, case["expectedErrorMsg"]):
                ScriptOperator.check_source_file(
                    entry_file=case["input"]["entry_file"],
                    source_dir=case["input"]["source_dir"],
                )

    def test_table_ref(self):
        templ = ScriptOperator(
            source_dir="./scripts",
            entry_file="run.py",
            inputs=[
                PipelineParameter(
                    "tableName",
                ),
                PipelineParameter("partition", default=""),
            ],
            outputs=[
                PipelineArtifact(
                    "outputTable",
                    LocationArtifactMetadata(
                        data_type=DataType.DataSet,
                        location_type=LocationType.MaxComputeTable,
                    ),
                    value=MaxComputeTableArtifact.value_from_param(
                        "tableName", "partition"
                    ),
                )
            ],
        )
        pprint(templ.to_dict())