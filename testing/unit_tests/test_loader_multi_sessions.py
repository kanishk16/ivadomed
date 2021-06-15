import os
import csv_diff
import numpy as np
import pandas as pd

import ivadomed.loader.tools.bids_dataframe
import ivadomed.loader.tools.utils
from ivadomed.loader.bids_dataset import get_unique_session_list
from testing.unit_tests.t_utils import path_temp, download_data_multi_sessions_contrasts_test_files
from testing.common_testing_util import remove_tmp_dir, path_data_multi_sessions_contrasts_source, path_data_multi_sessions_contrasts_tmp
from pytest_cases import parametrize_with_cases
import shutil
from testing.unit_tests.test_loader_multi_sessions_cases import case_data_target_specific_session_contrast, case_data_multi_session_contrast
from loguru import logger


def setup_function():
    # Dedicated setup function for multisession data.
    remove_tmp_dir()
    os.mkdir(path_temp)
    if os.path.exists(path_data_multi_sessions_contrasts_source):
        shutil.copytree(path_data_multi_sessions_contrasts_source,
                        path_data_multi_sessions_contrasts_tmp,
                        ignore=shutil.ignore_patterns(str(path_data_multi_sessions_contrasts_source / '.git')))


def test_get_unique_session_list():
    data = {"filename": ["ses-aaa_aaa", "ses-aaa_bbb", "aa", "ses-aaa_aaa"], "aa": [1, 2, 3, 4]}
    df = pd.DataFrame(data=data)
    assert np.array_equal(get_unique_session_list(df), ["aaa", "bbb"])


@parametrize_with_cases("loader_parameters, target_csv", cases=[
    case_data_target_specific_session_contrast,
    case_data_multi_session_contrast
])
def test_bids_multi_sessions_contrasts_dataframe_anat(download_data_multi_sessions_contrasts_test_files,
                                                      loader_parameters,
                                                      target_csv):
    """
    Test for when multi-sessions and multi-contrasts, how the filtering and ground truth identification process works.
    """

    bids_df = ivadomed.loader.tools.bids_dataframe.BidsDataframe(loader_parameters,
                                                                 str(path_data_multi_sessions_contrasts_tmp),
                                                                 derivatives=True)
    df_test = bids_df.df.drop(columns=['path'])
    df_test = df_test.sort_values(by=['filename']).reset_index(drop=True)
    csv_ref = os.path.join(loader_parameters["path_data"][0], target_csv)
    csv_test = os.path.join(loader_parameters["path_data"][0], "df_test.csv")
    df_test.to_csv(csv_test, index=False)
    diff = csv_diff.compare(csv_diff.load_csv(open(csv_ref)), csv_diff.load_csv(open(csv_test)))
    assert diff == {'added': [], 'removed': [], 'changed': [],
                    'columns_added': [], 'columns_removed': []}


def test_shutil():
    wild_card = str(path_data_multi_sessions_contrasts_source / '.*')
    shutil.copytree(path_data_multi_sessions_contrasts_source,
                    path_data_multi_sessions_contrasts_tmp,
                    ignore=shutil.ignore_patterns(wild_card))


def teardown_function():
    #remove_tmp_dir()
    pass
