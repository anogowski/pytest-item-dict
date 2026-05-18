# JSON Examples

All three JSON files are produced by a single `pytest` invocation from the
`examples/` directory.

---

## collect_hierarchy.json

Captured at `pytest_collection_finish`.  Pure structure with marker annotations
(`set_collect_dict_markers = true`) — no `@outcome`, `@duration`, or `@counts`.

```json
{
  "examples": {
    "suites": {
      "it": {
        "linux": {
          "test_linux.py": {
            "Test_Linux": {
              "test_i_linux": {
                "@markers": [
                  "linux",
                  "it"
                ]
              }
            }
          }
        },
        "windows": {
          "test_windows.py": {
            "Test_Windows": {
              "test_i_windows": {
                "@markers": [
                  "windows",
                  "it"
                ]
              }
            }
          }
        }
      },
      "rt": {
        "test_rt_linux.py": {
          "Test_RT_Linux": {
            "test_rt_linux_1": {
              "@markers": [
                "linux",
                "rt"
              ]
            },
            "test_rt_linux_2": {
              "@markers": [
                "linux",
                "rt"
              ]
            }
          }
        },
        "test_rt_windows.py": {
          "Test_RT_Windows": {
            "test_rt_windows_1": {
              "@markers": [
                "windows",
                "rt"
              ]
            },
            "test_rt_windows_2": {
              "@markers": [
                "windows",
                "rt"
              ]
            }
          }
        }
      },
      "vt": {
        "linux": {
          "test_v_linux.py": {
            "Test_Linux": {
              "test_v_linux": {
                "@markers": [
                  "linux",
                  "vt"
                ]
              },
              "test_v_linux_2": {
                "@markers": [
                  "linux",
                  "vt"
                ]
              },
              "test_v_linux_3": {
                "@markers": [
                  "linux",
                  "vt"
                ]
              }
            }
          },
          "test_v_posix.py": {
            "Test_Linux": {
              "test_v_posix": {
                "@markers": [
                  "linux",
                  "vt"
                ]
              },
              "test_v_posix_2": {
                "@markers": [
                  "linux",
                  "vt"
                ]
              }
            }
          }
        },
        "windows": {
          "test_v_windows.py": {
            "Test_Windows": {
              "test_v_windows_10": {
                "@markers": [
                  "windows",
                  "vt"
                ]
              },
              "test_v_windows_11": {
                "@markers": [
                  "windows",
                  "vt"
                ]
              }
            }
          }
        }
      }
    }
  }
}
```

---

## test_unexecuted_hierarchy.json

Captured at `pytest_collection_finish` from a deep-copy of `test_dict` before
any tests run.  Every test carries `@outcome: "unexecuted"` and `@counts` /
`@total_duration` are fully aggregated at every parent node.

```json
{
  "examples": {
    "suites": {
      "it": {
        "linux": {
          "test_linux.py": {
            "Test_Linux": {
              "test_i_linux": {
                "@outcome": "unexecuted"
              },
              "@counts": {
                "unexecuted": 1,
                "total": 1,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "executed": 0
              },
              "@total_duration": 0.0
            },
            "@counts": {
              "unexecuted": 1,
              "total": 1,
              "passed": 0,
              "failed": 0,
              "skipped": 0,
              "executed": 0
            },
            "@total_duration": 0.0
          },
          "@counts": {
            "unexecuted": 1,
            "total": 1,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "executed": 0
          },
          "@total_duration": 0.0
        },
        "windows": {
          "test_windows.py": {
            "Test_Windows": {
              "test_i_windows": {
                "@outcome": "unexecuted"
              },
              "@counts": {
                "unexecuted": 1,
                "total": 1,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "executed": 0
              },
              "@total_duration": 0.0
            },
            "@counts": {
              "unexecuted": 1,
              "total": 1,
              "passed": 0,
              "failed": 0,
              "skipped": 0,
              "executed": 0
            },
            "@total_duration": 0.0
          },
          "@counts": {
            "unexecuted": 1,
            "total": 1,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "executed": 0
          },
          "@total_duration": 0.0
        },
        "@counts": {
          "unexecuted": 2,
          "total": 2,
          "passed": 0,
          "failed": 0,
          "skipped": 0,
          "executed": 0
        },
        "@total_duration": 0.0
      },
      "rt": {
        "test_rt_linux.py": {
          "Test_RT_Linux": {
            "test_rt_linux_1": {
              "@outcome": "unexecuted"
            },
            "test_rt_linux_2": {
              "@outcome": "unexecuted"
            },
            "@counts": {
              "unexecuted": 2,
              "total": 2,
              "passed": 0,
              "failed": 0,
              "skipped": 0,
              "executed": 0
            },
            "@total_duration": 0.0
          },
          "@counts": {
            "unexecuted": 2,
            "total": 2,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "executed": 0
          },
          "@total_duration": 0.0
        },
        "test_rt_windows.py": {
          "Test_RT_Windows": {
            "test_rt_windows_1": {
              "@outcome": "unexecuted"
            },
            "test_rt_windows_2": {
              "@outcome": "unexecuted"
            },
            "@counts": {
              "unexecuted": 2,
              "total": 2,
              "passed": 0,
              "failed": 0,
              "skipped": 0,
              "executed": 0
            },
            "@total_duration": 0.0
          },
          "@counts": {
            "unexecuted": 2,
            "total": 2,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "executed": 0
          },
          "@total_duration": 0.0
        },
        "@counts": {
          "unexecuted": 4,
          "total": 4,
          "passed": 0,
          "failed": 0,
          "skipped": 0,
          "executed": 0
        },
        "@total_duration": 0.0
      },
      "vt": {
        "linux": {
          "test_v_linux.py": {
            "Test_Linux": {
              "test_v_linux": {
                "@outcome": "unexecuted"
              },
              "test_v_linux_2": {
                "@outcome": "unexecuted"
              },
              "test_v_linux_3": {
                "@outcome": "unexecuted"
              },
              "@counts": {
                "unexecuted": 3,
                "total": 3,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "executed": 0
              },
              "@total_duration": 0.0
            },
            "@counts": {
              "unexecuted": 3,
              "total": 3,
              "passed": 0,
              "failed": 0,
              "skipped": 0,
              "executed": 0
            },
            "@total_duration": 0.0
          },
          "test_v_posix.py": {
            "Test_Linux": {
              "test_v_posix": {
                "@outcome": "unexecuted"
              },
              "test_v_posix_2": {
                "@outcome": "unexecuted"
              },
              "@counts": {
                "unexecuted": 2,
                "total": 2,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "executed": 0
              },
              "@total_duration": 0.0
            },
            "@counts": {
              "unexecuted": 2,
              "total": 2,
              "passed": 0,
              "failed": 0,
              "skipped": 0,
              "executed": 0
            },
            "@total_duration": 0.0
          },
          "@counts": {
            "unexecuted": 5,
            "total": 5,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "executed": 0
          },
          "@total_duration": 0.0
        },
        "windows": {
          "test_v_windows.py": {
            "Test_Windows": {
              "test_v_windows_10": {
                "@outcome": "unexecuted"
              },
              "test_v_windows_11": {
                "@outcome": "unexecuted"
              },
              "@counts": {
                "unexecuted": 2,
                "total": 2,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "executed": 0
              },
              "@total_duration": 0.0
            },
            "@counts": {
              "unexecuted": 2,
              "total": 2,
              "passed": 0,
              "failed": 0,
              "skipped": 0,
              "executed": 0
            },
            "@total_duration": 0.0
          },
          "@counts": {
            "unexecuted": 2,
            "total": 2,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "executed": 0
          },
          "@total_duration": 0.0
        },
        "@counts": {
          "unexecuted": 7,
          "total": 7,
          "passed": 0,
          "failed": 0,
          "skipped": 0,
          "executed": 0
        },
        "@total_duration": 0.0
      },
      "@counts": {
        "unexecuted": 13,
        "total": 13,
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "executed": 0
      },
      "@total_duration": 0.0
    },
    "@counts": {
      "unexecuted": 13,
      "total": 13,
      "passed": 0,
      "failed": 0,
      "skipped": 0,
      "executed": 0
    },
    "@total_duration": 0.0
  },
  "@counts": {
    "unexecuted": 13,
    "total": 13,
    "passed": 0,
    "failed": 0,
    "skipped": 0,
    "executed": 0
  },
  "@total_duration": 0.0
}
```

---

## test_hierarchy.json

Captured at `pytest_sessionfinish`.  Contains final `@outcome`, per-test
`@duration`, `@markers`, `setup_method`/`teardown_method` nodes
(`set_test_dict_setup_teardown = true`), `setup_class`/`teardown_class` where
defined, and `@counts` / `@total_duration` bubbled to every parent node.

```json
{
  "examples": {
    "suites": {
      "it": {
        "linux": {
          "test_linux.py": {
            "Test_Linux": {
              "test_i_linux": {
                "@outcome": "passed",
                "setup_method": {
                  "@outcome": "passed"
                },
                "teardown_method": {
                  "@outcome": "passed"
                },
                "@markers": [
                  "linux",
                  "it"
                ],
                "@duration": 0.0002831000601872802
              },
              "@counts": {
                "passed": 1,
                "total": 1,
                "failed": 0,
                "skipped": 0,
                "unexecuted": 0,
                "executed": 1
              },
              "@total_duration": 0.0002831000601872802
            },
            "@counts": {
              "passed": 1,
              "total": 1,
              "failed": 0,
              "skipped": 0,
              "unexecuted": 0,
              "executed": 1
            },
            "@total_duration": 0.0002831000601872802
          },
          "@counts": {
            "passed": 1,
            "total": 1,
            "failed": 0,
            "skipped": 0,
            "unexecuted": 0,
            "executed": 1
          },
          "@total_duration": 0.0002831000601872802
        },
        "windows": {
          "test_windows.py": {
            "Test_Windows": {
              "test_i_windows": {
                "@outcome": "passed",
                "setup_method": {
                  "@outcome": "passed"
                },
                "teardown_method": {
                  "@outcome": "passed"
                },
                "@markers": [
                  "windows",
                  "it"
                ],
                "@duration": 0.00019649998284876347
              },
              "@counts": {
                "passed": 1,
                "total": 1,
                "failed": 0,
                "skipped": 0,
                "unexecuted": 0,
                "executed": 1
              },
              "@total_duration": 0.00019649998284876347
            },
            "@counts": {
              "passed": 1,
              "total": 1,
              "failed": 0,
              "skipped": 0,
              "unexecuted": 0,
              "executed": 1
            },
            "@total_duration": 0.00019649998284876347
          },
          "@counts": {
            "passed": 1,
            "total": 1,
            "failed": 0,
            "skipped": 0,
            "unexecuted": 0,
            "executed": 1
          },
          "@total_duration": 0.00019649998284876347
        },
        "@counts": {
          "passed": 2,
          "total": 2,
          "failed": 0,
          "skipped": 0,
          "unexecuted": 0,
          "executed": 2
        },
        "@total_duration": 0.00047960004303604364
      },
      "rt": {
        "test_rt_linux.py": {
          "Test_RT_Linux": {
            "test_rt_linux_1": {
              "@outcome": "passed",
              "setup_method": {
                "@outcome": "passed"
              },
              "teardown_method": {
                "@outcome": "passed"
              },
              "@markers": [
                "linux",
                "rt"
              ],
              "@duration": 0.0004681000718846917
            },
            "test_rt_linux_2": {
              "@outcome": "passed",
              "setup_method": {
                "@outcome": "passed"
              },
              "teardown_method": {
                "@outcome": "passed"
              },
              "@markers": [
                "linux",
                "rt"
              ],
              "@duration": 0.00026570004411041737
            },
            "setup_class": {
              "@outcome": "passed"
            },
            "teardown_class": {
              "@outcome": "passed"
            },
            "@counts": {
              "passed": 2,
              "total": 2,
              "failed": 0,
              "skipped": 0,
              "unexecuted": 0,
              "executed": 2
            },
            "@total_duration": 0.0007338001159951091
          },
          "@counts": {
            "passed": 2,
            "total": 2,
            "failed": 0,
            "skipped": 0,
            "unexecuted": 0,
            "executed": 2
          },
          "@total_duration": 0.0007338001159951091
        },
        "test_rt_windows.py": {
          "Test_RT_Windows": {
            "test_rt_windows_1": {
              "@outcome": "passed",
              "setup_method": {
                "@outcome": "passed"
              },
              "teardown_method": {
                "@outcome": "passed"
              },
              "@markers": [
                "windows",
                "rt"
              ],
              "@duration": 0.0004784999182447791
            },
            "test_rt_windows_2": {
              "@outcome": "passed",
              "setup_method": {
                "@outcome": "passed"
              },
              "teardown_method": {
                "@outcome": "passed"
              },
              "@markers": [
                "windows",
                "rt"
              ],
              "@duration": 0.000317899975925684
            },
            "@counts": {
              "passed": 2,
              "total": 2,
              "failed": 0,
              "skipped": 0,
              "unexecuted": 0,
              "executed": 2
            },
            "@total_duration": 0.0007963998941704631
          },
          "@counts": {
            "passed": 2,
            "total": 2,
            "failed": 0,
            "skipped": 0,
            "unexecuted": 0,
            "executed": 2
          },
          "@total_duration": 0.0007963998941704631
        },
        "@counts": {
          "passed": 4,
          "total": 4,
          "failed": 0,
          "skipped": 0,
          "unexecuted": 0,
          "executed": 4
        },
        "@total_duration": 0.0015302000101655722
      },
      "vt": {
        "linux": {
          "test_v_linux.py": {
            "Test_Linux": {
              "test_v_linux": {
                "@outcome": "passed",
                "setup_method": {
                  "@outcome": "passed"
                },
                "teardown_method": {
                  "@outcome": "passed"
                },
                "@markers": [
                  "linux",
                  "vt"
                ],
                "@duration": 0.00014949985779821873
              },
              "test_v_linux_2": {
                "@outcome": "passed",
                "setup_method": {
                  "@outcome": "passed"
                },
                "teardown_method": {
                  "@outcome": "passed"
                },
                "@markers": [
                  "linux",
                  "vt"
                ],
                "@duration": 0.00014600006397813559
              },
              "test_v_linux_3": {
                "@outcome": "passed",
                "setup_method": {
                  "@outcome": "passed"
                },
                "teardown_method": {
                  "@outcome": "passed"
                },
                "@markers": [
                  "linux",
                  "vt"
                ],
                "@duration": 0.00016670010518282652
              },
              "@counts": {
                "passed": 3,
                "total": 3,
                "failed": 0,
                "skipped": 0,
                "unexecuted": 0,
                "executed": 3
              },
              "@total_duration": 0.00046220002695918083
            },
            "@counts": {
              "passed": 3,
              "total": 3,
              "failed": 0,
              "skipped": 0,
              "unexecuted": 0,
              "executed": 3
            },
            "@total_duration": 0.00046220002695918083
          },
          "test_v_posix.py": {
            "Test_Linux": {
              "test_v_posix": {
                "@outcome": "passed",
                "setup_method": {
                  "@outcome": "passed"
                },
                "teardown_method": {
                  "@outcome": "passed"
                },
                "@markers": [
                  "linux",
                  "vt"
                ],
                "@duration": 0.00012990005780011415
              },
              "test_v_posix_2": {
                "@outcome": "passed",
                "setup_method": {
                  "@outcome": "passed"
                },
                "teardown_method": {
                  "@outcome": "passed"
                },
                "@markers": [
                  "linux",
                  "vt"
                ],
                "@duration": 0.0001311000669375062
              },
              "@counts": {
                "passed": 2,
                "total": 2,
                "failed": 0,
                "skipped": 0,
                "unexecuted": 0,
                "executed": 2
              },
              "@total_duration": 0.00026100012473762035
            },
            "@counts": {
              "passed": 2,
              "total": 2,
              "failed": 0,
              "skipped": 0,
              "unexecuted": 0,
              "executed": 2
            },
            "@total_duration": 0.00026100012473762035
          },
          "@counts": {
            "passed": 5,
            "total": 5,
            "failed": 0,
            "skipped": 0,
            "unexecuted": 0,
            "executed": 5
          },
          "@total_duration": 0.0007232001516968012
        },
        "windows": {
          "test_v_windows.py": {
            "Test_Windows": {
              "test_v_windows_10": {
                "@outcome": "passed",
                "setup_method": {
                  "@outcome": "passed"
                },
                "teardown_method": {
                  "@outcome": "passed"
                },
                "@markers": [
                  "windows",
                  "vt"
                ],
                "@duration": 0.0001374998828396201
              },
              "test_v_windows_11": {
                "@outcome": "passed",
                "setup_method": {
                  "@outcome": "passed"
                },
                "teardown_method": {
                  "@outcome": "passed"
                },
                "@markers": [
                  "windows",
                  "vt"
                ],
                "@duration": 0.00013529998250305653
              },
              "@counts": {
                "passed": 2,
                "total": 2,
                "failed": 0,
                "skipped": 0,
                "unexecuted": 0,
                "executed": 2
              },
              "@total_duration": 0.00027279986534267664
            },
            "@counts": {
              "passed": 2,
              "total": 2,
              "failed": 0,
              "skipped": 0,
              "unexecuted": 0,
              "executed": 2
            },
            "@total_duration": 0.00027279986534267664
          },
          "@counts": {
            "passed": 2,
            "total": 2,
            "failed": 0,
            "skipped": 0,
            "unexecuted": 0,
            "executed": 2
          },
          "@total_duration": 0.00027279986534267664
        },
        "@counts": {
          "passed": 7,
          "total": 7,
          "failed": 0,
          "skipped": 0,
          "unexecuted": 0,
          "executed": 7
        },
        "@total_duration": 0.0009960000170394778
      },
      "@counts": {
        "passed": 13,
        "total": 13,
        "failed": 0,
        "skipped": 0,
        "unexecuted": 0,
        "executed": 13
      },
      "@total_duration": 0.0030058000702410936
    },
    "@counts": {
      "passed": 13,
      "total": 13,
      "failed": 0,
      "skipped": 0,
      "unexecuted": 0,
      "executed": 13
    },
    "@total_duration": 0.0030058000702410936
  },
  "@counts": {
    "passed": 13,
    "total": 13,
    "failed": 0,
    "skipped": 0,
    "unexecuted": 0,
    "executed": 13
  },
  "@total_duration": 0.0030058000702410936
}
```
