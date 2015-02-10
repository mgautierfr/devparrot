

import pytest
from devparrot.core.configLoader import Config
import itertools


@pytest.mark.parametrize(("keys","value"), [
(None, "value"),
([], "value"),
([None], "value"),
(["key"], "value"),
(["key", None], "value"),
([None, "key"], "value"),
(["key", "key2"], "value")
])
def test_config_0_level(keys, value):
    config = Config()
    config.add_option("option", default="value")
    assert config.get("option", keys) == value


@pytest.mark.parametrize(("keys","value"), [
(None, "value"),
([], "value"),
([None], "value"),
(["key"], "other"),
(["key", None], "other"),
([None, "key"], "value"),
(["key", "key2"], "other")
])
def test_config_1_level(keys, value):
    config = Config()
    config.add_option("option", default="value")
    config["option"].set("other", ["key"])
    assert config.get("option", keys) == value


@pytest.mark.parametrize(("keys","value"), [
(None, "none"),
([], "none"),
([None], "none"),
(["key1"], "key1"),
(["key1", None], "key1"),
([None, "key1"], "none"),
(["key2"], "key2"),
(["key2", "key1"], "key2"),
(["key3"], "key3"),
(["key3", "key1"], "key3.key1"),
(["key3", "key2"], "key3"),
(["key4"], "none"),
(["key4", "key1"], "key4.key1"),
(["key4", "key2"], "key2"),
])
def test_config_2_level(keys, value):
    config = Config()
    config.add_option("option", default="none")
    config["option"].set("key1", ["key1"])
    config["option"].set("key2", ["key2"])
    config["option"].set("key3", ["key3"])
    config["option"].set("key3.key1", ["key3", "key1"])
    config["option"].set("key4.key1", ["key4", "key1"])
    assert config.get("option", keys) == value



@pytest.mark.parametrize(("keys","value"), [
(None, "none"),
([], "none"),
([None], "none"),
(["key1"], "key1"),
(["key1", None], "key1"),
([None, "key1"], "none"),
(["key2"], "key2"),
(["key2", "key1"], "key2"),
(["key3"], "key3"),
(["key3", "key1"], "key3.key1"),
(["key3", "key2"], "key3"),
(["key4"], "none"),
(["key4", "key1"], "key4.key1"),
(["key4", "key2"], "key2"),
])
def test_config_2_level_with_update(keys, value):
    config = Config()
    config.add_option("option", default="none")
    config.update({"option":{"key1": "key1",
                             "key2": "key2",
                             "key3": {None:"key3",
                                      "key1":"key3.key1"},
                             "key4": {"key1":"key4.key1"}
                            }
                  })
    assert config.get("option", keys) == value


@pytest.mark.parametrize(("keys","value"), [
(None, "none"),
([], "none"),
([None], "none"),
(["key1"], "key1"),
(["key1", None], "key1"),
([None, "key1"], "none"),
(["key2"], "key2"),
(["key2", "key1"], "key2"),
(["key3"], "key3"),
(["key3", "key1"], "key3.key1"),
(["key3", "key2"], "key3"),
(["key4"], "none"),
(["key4", "key1"], "key4.key1"),
(["key4", "key2"], "key2"),
])
def test_config_2_level_with_update_sub_key(keys, value):
    config = Config()
    config.add_option("option", default="none")
    config.update({"option":{"key1": "key1",
                             "key2": "key2",
                             "key3": "key3"}
                  })
    config.update({"option":{"key1":"key3.key1"}}, ["key3"])
    config.update({"option":"key4.key1"}, ["key4", "key1"])
    assert config.get("option", keys) == value


@pytest.mark.parametrize(("keys","value"), [
(["A", "B", "E"], "none"),
(["A", "B", "E", "K1"], "K1"),
(["A", "B", "E", "K2"], "none"),
(["A", "B", "C", "F", "K1"], "A/B/C.K1"),
(["A", "B", "D", "K1"], "A/B/D"),
(["A", "B", "D", "K2"], "A/B/D.K2"),
])
def test_config_3_level_missing_key_in_request(keys, value):
    config = Config()
    config.add_option("option", default="none")
    config["option"].set("K1", ["K1"])
    config["option"].set("A/B/C.K1", ["A", "B", "C", "K1"])
    config["option"].set("A/B/C.K2", ["A", "B", "C", "K2"])
    config["option"].set("A/B/D", ["A", "B", "D"])
    config["option"].set("A/B/D.K2", ["A", "B", "D", "K2"])
    assert config.get("option", keys) == value
