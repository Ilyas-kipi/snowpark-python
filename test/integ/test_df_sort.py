#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (c) 2012-2021 Snowflake Computing Inc. All right reserved.
#

import pytest
from src.snowflake.snowpark.column import Column
from src.snowflake.snowpark.snowpark_client_exception import SnowparkClientException


def test_sort_basic(session_cnx, db_parameters):
    with session_cnx(db_parameters) as session:
        df = session.createDataFrame([(1, 1), (1, 2), (1, 3), (2, 1), (2, 2),
                                      (2, 3), (3, 1), (3, 2), (3, 3)]).toDF(["a", "b"])

        # asc with 1 column
        sorted_rows = df.sort(Column("a").asc()).collect()
        for idx in range(1, len(sorted_rows)):
            assert sorted_rows[idx-1].get_int(0) <= sorted_rows[idx].get_int(0)

        # desc with 1 column
        sorted_rows = df.sort(Column("a").desc()).collect()
        for idx in range(1, len(sorted_rows)):
            assert sorted_rows[idx-1].get_int(0) >= sorted_rows[idx].get_int(0)

        # asc with 2 columns
        sorted_rows = df.sort(Column("a").asc(), Column("b").asc()).collect()
        for idx in range(1, len(sorted_rows)):
            assert sorted_rows[idx-1].get_int(0) < sorted_rows[idx].get_int(0) or \
                   (sorted_rows[idx-1].get_int(0) == sorted_rows[idx].get_int(0) and
                    sorted_rows[idx-1].get_int(1) <= sorted_rows[idx].get_int(1))

        # desc with 2 columns
        sorted_rows = df.sort(Column("a").desc(), Column("b").desc()).collect()
        for idx in range(1, len(sorted_rows)):
            assert sorted_rows[idx-1].get_int(0) > sorted_rows[idx].get_int(0) or \
                   (sorted_rows[idx-1].get_int(0) == sorted_rows[idx].get_int(0) and
                    sorted_rows[idx-1].get_int(1) >= sorted_rows[idx].get_int(1))


def test_sort_different_inputs(session_cnx, db_parameters):
    with session_cnx(db_parameters) as session:
        df = session.createDataFrame([(1, 1), (1, 2), (1, 3), (2, 1), (2, 2),
                                      (2, 3), (3, 1), (3, 2), (3, 3)]).toDF(["a", "b"])

        # str and asc
        sorted_rows = df.sort("a", ascending=True).collect()
        for idx in range(1, len(sorted_rows)):
            assert sorted_rows[idx-1].get_int(0) <= sorted_rows[idx].get_int(0)

        # Column and desc
        sorted_rows = df.sort(Column("a"), ascending=False).collect()
        for idx in range(1, len(sorted_rows)):
            assert sorted_rows[idx-1].get_int(0) >= sorted_rows[idx].get_int(0)

        # str, str and order default (asc)
        sorted_rows = df.sort("a", "b").collect()
        for idx in range(1, len(sorted_rows)):
            assert sorted_rows[idx-1].get_int(0) < sorted_rows[idx].get_int(0) or \
                   (sorted_rows[idx-1].get_int(0) == sorted_rows[idx].get_int(0) and
                    sorted_rows[idx-1].get_int(1) <= sorted_rows[idx].get_int(1))

        # List[str] and order list
        sorted_rows = df.sort(["a", "b"], ascending=[True, False]).collect()
        for idx in range(1, len(sorted_rows)):
            assert sorted_rows[idx-1].get_int(0) < sorted_rows[idx].get_int(0) or \
                   (sorted_rows[idx-1].get_int(0) == sorted_rows[idx].get_int(0) and
                    sorted_rows[idx-1].get_int(1) >= sorted_rows[idx].get_int(1))

        # List[Union[str, Column]] and order list overwrites the column
        sorted_rows = df.sort(["a", Column("b").desc()], ascending=[1, 1]).collect()
        for idx in range(1, len(sorted_rows)):
            assert sorted_rows[idx-1].get_int(0) < sorted_rows[idx].get_int(0) or \
                   (sorted_rows[idx-1].get_int(0) == sorted_rows[idx].get_int(0) and
                    sorted_rows[idx-1].get_int(1) <= sorted_rows[idx].get_int(1))


def test_sort_invalid_inputs(session_cnx, db_parameters):
    with session_cnx(db_parameters) as session:
        df = session.createDataFrame([(1, 1), (1, 2), (1, 3), (2, 1), (2, 2),
                                      (2, 3), (3, 1), (3, 2), (3, 3)]).toDF(["a", "b"])
        # empty
        with pytest.raises(SnowparkClientException) as ex_info:
            df.sort()
        assert "sort() needs at least one sort expression" in str(ex_info)
        with pytest.raises(SnowparkClientException) as ex_info:
            df.sort([])
        assert "sort() needs at least one sort expression" in str(ex_info)

        # invalid ascending type
        with pytest.raises(SnowparkClientException) as ex_info:
            df.sort("a", ascending="ASC")
        assert "ascending can only be boolean or list" in str(ex_info)

        # inconsistent ascending length
        with pytest.raises(SnowparkClientException) as ex_info:
            df.sort("a", "b", ascending=[True, True, True])
        assert "The length of col (2) should be same with the length of ascending (3)" in str(ex_info)

        # invalid input types
        with pytest.raises(SnowparkClientException) as ex_info:
            df.sort(["a"], ["b"])
        assert "sort() only accepts one list, but got 2" in str(ex_info)