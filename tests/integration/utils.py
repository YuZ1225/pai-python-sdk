import configparser
import datetime
import os
import shutil
import uuid
from collections import namedtuple

from pai.common.utils import random_str

_test_root = os.path.dirname(os.path.abspath(__file__))

PAI_PIPELINE_RUN_ID_PLACEHOLDER = "${pai_system_run_id_underscore}"
PAI_PIPELINE_NODE_ID_PLACEHOLDER = "${pai_system_node_id_underscore}"


PaiServiceConfig = namedtuple(
    "AlibabaCloudServiceConfig",
    [
        "access_key_id",
        "access_key_secret",
        "region_id",
        "workspace_id",
        "endpoint",
    ],
)


MaxcConfig = namedtuple(
    "MaxcConfig",
    [
        "access_key_id",
        "access_key_secret",
        "endpoint",
        "project",
    ],
)

OssConfig = namedtuple(
    "OssConfig",
    [
        "access_key_id",
        "access_key_secret",
        "bucket_name",
        "endpoint",
        "role_arn",
        # ForGroupInner only，which is required for OSS dataset mount in PAI-DLC job.
        "aliyun_uid",
    ],
)


class TestContext(object):
    def __init__(self, pai_service_config, oss_config, maxc_config):
        self.pai_service_config = pai_service_config
        self.oss_config = oss_config
        self.maxc_config = maxc_config

    @property
    def has_docker(self):
        return shutil.which("docker") is not None

    @property
    def is_inner(self):
        return self.pai_service_config.region_id == "center"

    @classmethod
    def _load_test_config(cls):
        test_config = os.environ.get("PAI_TEST_CONFIG", "test_public.ini")
        cfg_parser = configparser.ConfigParser()
        cfg_parser.read(os.path.join(_test_root, test_config))

        access_key_id = cfg_parser.get("client", "access_key_id")
        access_key_secret = cfg_parser.get("client", "access_key_secret")
        region_id = cfg_parser.get("client", "region_id", fallback=None)
        endpoint = cfg_parser.get("client", "endpoint", fallback=None)
        workspace_id = cfg_parser.get("client", "workspace_id", fallback=None)

        pai_service_config = PaiServiceConfig(
            access_key_id=access_key_id,
            access_key_secret=access_key_secret,
            region_id=region_id,
            workspace_id=workspace_id,
            endpoint=endpoint,
        )

        oss_config = OssConfig(
            access_key_id=cfg_parser.get(
                "oss",
                "access_key_id",
                fallback=None,
            ),
            access_key_secret=cfg_parser.get(
                "oss",
                "access_key_secret",
                fallback=None,
            ),
            bucket_name=cfg_parser.get("oss", "bucket"),
            endpoint=cfg_parser.get("oss", "endpoint"),
            role_arn=cfg_parser.get("oss", "rolearn"),
            aliyun_uid=cfg_parser.get(
                "oss",
                "aliyun_uid",
                fallback=None,
            ),
        )

        maxc_config = MaxcConfig(
            access_key_id=access_key_id,
            access_key_secret=access_key_secret,
            endpoint=cfg_parser.get("odps", "endpoint"),
            project=cfg_parser.get("odps", "project"),
        )
        return pai_service_config, oss_config, maxc_config

    @classmethod
    def load_test_config(cls):
        pai_service_config, oss_config, maxc_config = cls._load_test_config()
        return cls(
            pai_service_config,
            oss_config,
            maxc_config,
        )

    @classmethod
    def get_context(cls):
        return t_context


t_context = TestContext.load_test_config()


def make_resource_name(case_name, resource_type=None, sep="-", time_suffix=True):
    """Make a test resource name."""
    return sep.join(
        filter(
            None,
            [
                "sdktest",
                resource_type,
                case_name,
                datetime.datetime.now().isoformat(timespec="seconds")
                if time_suffix
                else random_str(10),
            ],
        )
    )


def make_eas_service_name(case_name):
    return make_resource_name(case_name=case_name, sep="_", time_suffix=False)


def gen_temp_table(prefix="pai_temp_"):
    return "{prefix}{identifier}".format(
        prefix=prefix,
        identifier=uuid.uuid4().hex,
    )


def gen_run_node_scoped_placeholder(suffix=None):
    if suffix:
        return "{0}_{1}_{2}".format(
            PAI_PIPELINE_NODE_ID_PLACEHOLDER, PAI_PIPELINE_RUN_ID_PLACEHOLDER, suffix
        )
    else:
        return "{0}_{1}".format(
            PAI_PIPELINE_NODE_ID_PLACEHOLDER, PAI_PIPELINE_RUN_ID_PLACEHOLDER
        )
