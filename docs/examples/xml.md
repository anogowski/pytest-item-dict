# XML Examples

All three XML files are produced by a single `pytest` invocation from the
`examples/` directory.  The root element is `<pytest>`.  Attributes such as
`outcome`, `duration`, and `markers` are stored as XML element attributes;
`@counts` and `@total_duration` are serialized as `counts` and `total_duration`
attributes on parent elements.

---

## collect_hierarchy.xml

Captured at `pytest_collection_finish`.  Pure structure with `markers` attributes
(`set_collect_dict_markers = true`) — no `outcome`, `duration`, or `counts`.

```xml
<pytest>
	<examples>
		<suites>
			<it>
				<linux>
					<test_linux.py>
						<Test_Linux>
							<test_i_linux markers="['linux', 'it']" />
						</Test_Linux>
					</test_linux.py>
				</linux>
				<windows>
					<test_windows.py>
						<Test_Windows>
							<test_i_windows markers="['windows', 'it']" />
						</Test_Windows>
					</test_windows.py>
				</windows>
			</it>
			<rt>
				<test_rt_linux.py>
					<Test_RT_Linux>
						<test_rt_linux_1 markers="['linux', 'rt']" />
						<test_rt_linux_2 markers="['linux', 'rt']" />
					</Test_RT_Linux>
				</test_rt_linux.py>
				<test_rt_windows.py>
					<Test_RT_Windows>
						<test_rt_windows_1 markers="['windows', 'rt']" />
						<test_rt_windows_2 markers="['windows', 'rt']" />
					</Test_RT_Windows>
				</test_rt_windows.py>
			</rt>
			<vt>
				<linux>
					<test_v_linux.py>
						<Test_Linux>
							<test_v_linux markers="['linux', 'vt']" />
							<test_v_linux_2 markers="['linux', 'vt']" />
							<test_v_linux_3 markers="['linux', 'vt']" />
						</Test_Linux>
					</test_v_linux.py>
					<test_v_posix.py>
						<Test_Linux>
							<test_v_posix markers="['linux', 'vt']" />
							<test_v_posix_2 markers="['linux', 'vt']" />
						</Test_Linux>
					</test_v_posix.py>
				</linux>
				<windows>
					<test_v_windows.py>
						<Test_Windows>
							<test_v_windows_10 markers="['windows', 'vt']" />
							<test_v_windows_11 markers="['windows', 'vt']" />
						</Test_Windows>
					</test_v_windows.py>
				</windows>
			</vt>
		</suites>
	</examples>
</pytest>
```

---

## test_unexecuted_hierarchy.xml

Captured at `pytest_collection_finish` from a deep-copy of `test_dict` before
any tests run.  Every test element carries `outcome="unexecuted"`.  Parent
elements carry `counts` (the full dict serialised as a string) and
`total_duration` attributes.

```xml
<pytest counts="{'unexecuted': 13, 'total': 13, 'passed': 0, 'failed': 0, 'skipped': 0, 'executed': 0}" total_duration="0.0">
	<examples counts="{'unexecuted': 13, 'total': 13, 'passed': 0, 'failed': 0, 'skipped': 0, 'executed': 0}" total_duration="0.0">
		<suites counts="{'unexecuted': 13, 'total': 13, 'passed': 0, 'failed': 0, 'skipped': 0, 'executed': 0}" total_duration="0.0">
			<it counts="{'unexecuted': 2, 'total': 2, 'passed': 0, 'failed': 0, 'skipped': 0, 'executed': 0}" total_duration="0.0">
				<linux counts="{'unexecuted': 1, 'total': 1, 'passed': 0, 'failed': 0, 'skipped': 0, 'executed': 0}" total_duration="0.0">
					<test_linux.py counts="{'unexecuted': 1, 'total': 1, 'passed': 0, 'failed': 0, 'skipped': 0, 'executed': 0}" total_duration="0.0">
						<Test_Linux counts="{'unexecuted': 1, 'total': 1, 'passed': 0, 'failed': 0, 'skipped': 0, 'executed': 0}" total_duration="0.0">
							<test_i_linux outcome="unexecuted" />
						</Test_Linux>
					</test_linux.py>
				</linux>
				<windows counts="{'unexecuted': 1, 'total': 1, 'passed': 0, 'failed': 0, 'skipped': 0, 'executed': 0}" total_duration="0.0">
					<test_windows.py counts="{'unexecuted': 1, 'total': 1, 'passed': 0, 'failed': 0, 'skipped': 0, 'executed': 0}" total_duration="0.0">
						<Test_Windows counts="{'unexecuted': 1, 'total': 1, 'passed': 0, 'failed': 0, 'skipped': 0, 'executed': 0}" total_duration="0.0">
							<test_i_windows outcome="unexecuted" />
						</Test_Windows>
					</test_windows.py>
				</windows>
			</it>
			<rt counts="{'unexecuted': 4, 'total': 4, 'passed': 0, 'failed': 0, 'skipped': 0, 'executed': 0}" total_duration="0.0">
				<test_rt_linux.py counts="{'unexecuted': 2, 'total': 2, 'passed': 0, 'failed': 0, 'skipped': 0, 'executed': 0}" total_duration="0.0">
					<Test_RT_Linux counts="{'unexecuted': 2, 'total': 2, 'passed': 0, 'failed': 0, 'skipped': 0, 'executed': 0}" total_duration="0.0">
						<test_rt_linux_1 outcome="unexecuted" />
						<test_rt_linux_2 outcome="unexecuted" />
					</Test_RT_Linux>
				</test_rt_linux.py>
				<test_rt_windows.py counts="{'unexecuted': 2, 'total': 2, 'passed': 0, 'failed': 0, 'skipped': 0, 'executed': 0}" total_duration="0.0">
					<Test_RT_Windows counts="{'unexecuted': 2, 'total': 2, 'passed': 0, 'failed': 0, 'skipped': 0, 'executed': 0}" total_duration="0.0">
						<test_rt_windows_1 outcome="unexecuted" />
						<test_rt_windows_2 outcome="unexecuted" />
					</Test_RT_Windows>
				</test_rt_windows.py>
			</rt>
			<vt counts="{'unexecuted': 7, 'total': 7, 'passed': 0, 'failed': 0, 'skipped': 0, 'executed': 0}" total_duration="0.0">
				<linux counts="{'unexecuted': 5, 'total': 5, 'passed': 0, 'failed': 0, 'skipped': 0, 'executed': 0}" total_duration="0.0">
					<test_v_linux.py counts="{'unexecuted': 3, 'total': 3, 'passed': 0, 'failed': 0, 'skipped': 0, 'executed': 0}" total_duration="0.0">
						<Test_Linux counts="{'unexecuted': 3, 'total': 3, 'passed': 0, 'failed': 0, 'skipped': 0, 'executed': 0}" total_duration="0.0">
							<test_v_linux outcome="unexecuted" />
							<test_v_linux_2 outcome="unexecuted" />
							<test_v_linux_3 outcome="unexecuted" />
						</Test_Linux>
					</test_v_linux.py>
					<test_v_posix.py counts="{'unexecuted': 2, 'total': 2, 'passed': 0, 'failed': 0, 'skipped': 0, 'executed': 0}" total_duration="0.0">
						<Test_Linux counts="{'unexecuted': 2, 'total': 2, 'passed': 0, 'failed': 0, 'skipped': 0, 'executed': 0}" total_duration="0.0">
							<test_v_posix outcome="unexecuted" />
							<test_v_posix_2 outcome="unexecuted" />
						</Test_Linux>
					</test_v_posix.py>
				</linux>
				<windows counts="{'unexecuted': 2, 'total': 2, 'passed': 0, 'failed': 0, 'skipped': 0, 'executed': 0}" total_duration="0.0">
					<test_v_windows.py counts="{'unexecuted': 2, 'total': 2, 'passed': 0, 'failed': 0, 'skipped': 0, 'executed': 0}" total_duration="0.0">
						<Test_Windows counts="{'unexecuted': 2, 'total': 2, 'passed': 0, 'failed': 0, 'skipped': 0, 'executed': 0}" total_duration="0.0">
							<test_v_windows_10 outcome="unexecuted" />
							<test_v_windows_11 outcome="unexecuted" />
						</Test_Windows>
					</test_v_windows.py>
				</windows>
			</vt>
		</suites>
	</examples>
</pytest>
```

---

## test_hierarchy.xml

Captured at `pytest_sessionfinish`.  Contains final `outcome`, per-test
`duration` and `markers` attributes, `setup_method`/`teardown_method` child
elements (`set_test_dict_setup_teardown = true`), `setup_class`/`teardown_class`
where defined, and `counts`/`total_duration` on every parent element.

```xml
<pytest counts="{'passed': 13, 'total': 13, 'failed': 0, 'skipped': 0, 'unexecuted': 0, 'executed': 13}" total_duration="0.0030058000702410936">
	<examples counts="{'passed': 13, 'total': 13, 'failed': 0, 'skipped': 0, 'unexecuted': 0, 'executed': 13}" total_duration="0.0030058000702410936">
		<suites counts="{'passed': 13, 'total': 13, 'failed': 0, 'skipped': 0, 'unexecuted': 0, 'executed': 13}" total_duration="0.0030058000702410936">
			<it counts="{'passed': 2, 'total': 2, 'failed': 0, 'skipped': 0, 'unexecuted': 0, 'executed': 2}" total_duration="0.00047960004303604364">
				<linux counts="{'passed': 1, 'total': 1, 'failed': 0, 'skipped': 0, 'unexecuted': 0, 'executed': 1}" total_duration="0.0002831000601872802">
					<test_linux.py counts="{'passed': 1, 'total': 1, 'failed': 0, 'skipped': 0, 'unexecuted': 0, 'executed': 1}" total_duration="0.0002831000601872802">
						<Test_Linux counts="{'passed': 1, 'total': 1, 'failed': 0, 'skipped': 0, 'unexecuted': 0, 'executed': 1}" total_duration="0.0002831000601872802">
							<test_i_linux outcome="passed" markers="['linux', 'it']" duration="0.0002831000601872802">
								<setup_method outcome="passed" />
								<teardown_method outcome="passed" />
							</test_i_linux>
						</Test_Linux>
					</test_linux.py>
				</linux>
				<windows counts="{'passed': 1, 'total': 1, 'failed': 0, 'skipped': 0, 'unexecuted': 0, 'executed': 1}" total_duration="0.00019649998284876347">
					<test_windows.py counts="{'passed': 1, 'total': 1, 'failed': 0, 'skipped': 0, 'unexecuted': 0, 'executed': 1}" total_duration="0.00019649998284876347">
						<Test_Windows counts="{'passed': 1, 'total': 1, 'failed': 0, 'skipped': 0, 'unexecuted': 0, 'executed': 1}" total_duration="0.00019649998284876347">
							<test_i_windows outcome="passed" markers="['windows', 'it']" duration="0.00019649998284876347">
								<setup_method outcome="passed" />
								<teardown_method outcome="passed" />
							</test_i_windows>
						</Test_Windows>
					</test_windows.py>
				</windows>
			</it>
			<rt counts="{'passed': 4, 'total': 4, 'failed': 0, 'skipped': 0, 'unexecuted': 0, 'executed': 4}" total_duration="0.0015302000101655722">
				<test_rt_linux.py counts="{'passed': 2, 'total': 2, 'failed': 0, 'skipped': 0, 'unexecuted': 0, 'executed': 2}" total_duration="0.0007338001159951091">
					<Test_RT_Linux counts="{'passed': 2, 'total': 2, 'failed': 0, 'skipped': 0, 'unexecuted': 0, 'executed': 2}" total_duration="0.0007338001159951091">
						<test_rt_linux_1 outcome="passed" markers="['linux', 'rt']" duration="0.0004681000718846917">
							<setup_method outcome="passed" />
							<teardown_method outcome="passed" />
						</test_rt_linux_1>
						<test_rt_linux_2 outcome="passed" markers="['linux', 'rt']" duration="0.00026570004411041737">
							<setup_method outcome="passed" />
							<teardown_method outcome="passed" />
						</test_rt_linux_2>
						<setup_class outcome="passed" />
						<teardown_class outcome="passed" />
					</Test_RT_Linux>
				</test_rt_linux.py>
				<test_rt_windows.py counts="{'passed': 2, 'total': 2, 'failed': 0, 'skipped': 0, 'unexecuted': 0, 'executed': 2}" total_duration="0.0007963998941704631">
					<Test_RT_Windows counts="{'passed': 2, 'total': 2, 'failed': 0, 'skipped': 0, 'unexecuted': 0, 'executed': 2}" total_duration="0.0007963998941704631">
						<test_rt_windows_1 outcome="passed" markers="['windows', 'rt']" duration="0.0004784999182447791">
							<setup_method outcome="passed" />
							<teardown_method outcome="passed" />
						</test_rt_windows_1>
						<test_rt_windows_2 outcome="passed" markers="['windows', 'rt']" duration="0.000317899975925684">
							<setup_method outcome="passed" />
							<teardown_method outcome="passed" />
						</test_rt_windows_2>
					</Test_RT_Windows>
				</test_rt_windows.py>
			</rt>
			<vt counts="{'passed': 7, 'total': 7, 'failed': 0, 'skipped': 0, 'unexecuted': 0, 'executed': 7}" total_duration="0.0009960000170394778">
				<linux counts="{'passed': 5, 'total': 5, 'failed': 0, 'skipped': 0, 'unexecuted': 0, 'executed': 5}" total_duration="0.0007232001516968012">
					<test_v_linux.py counts="{'passed': 3, 'total': 3, 'failed': 0, 'skipped': 0, 'unexecuted': 0, 'executed': 3}" total_duration="0.00046220002695918083">
						<Test_Linux counts="{'passed': 3, 'total': 3, 'failed': 0, 'skipped': 0, 'unexecuted': 0, 'executed': 3}" total_duration="0.00046220002695918083">
							<test_v_linux outcome="passed" markers="['linux', 'vt']" duration="0.00014949985779821873">
								<setup_method outcome="passed" />
								<teardown_method outcome="passed" />
							</test_v_linux>
							<test_v_linux_2 outcome="passed" markers="['linux', 'vt']" duration="0.00014600006397813559">
								<setup_method outcome="passed" />
								<teardown_method outcome="passed" />
							</test_v_linux_2>
							<test_v_linux_3 outcome="passed" markers="['linux', 'vt']" duration="0.00016670010518282652">
								<setup_method outcome="passed" />
								<teardown_method outcome="passed" />
							</test_v_linux_3>
						</Test_Linux>
					</test_v_linux.py>
					<test_v_posix.py counts="{'passed': 2, 'total': 2, 'failed': 0, 'skipped': 0, 'unexecuted': 0, 'executed': 2}" total_duration="0.00026100012473762035">
						<Test_Linux counts="{'passed': 2, 'total': 2, 'failed': 0, 'skipped': 0, 'unexecuted': 0, 'executed': 2}" total_duration="0.00026100012473762035">
							<test_v_posix outcome="passed" markers="['linux', 'vt']" duration="0.00012990005780011415">
								<setup_method outcome="passed" />
								<teardown_method outcome="passed" />
							</test_v_posix>
							<test_v_posix_2 outcome="passed" markers="['linux', 'vt']" duration="0.0001311000669375062">
								<setup_method outcome="passed" />
								<teardown_method outcome="passed" />
							</test_v_posix_2>
						</Test_Linux>
					</test_v_posix.py>
				</linux>
				<windows counts="{'passed': 2, 'total': 2, 'failed': 0, 'skipped': 0, 'unexecuted': 0, 'executed': 2}" total_duration="0.00027279986534267664">
					<test_v_windows.py counts="{'passed': 2, 'total': 2, 'failed': 0, 'skipped': 0, 'unexecuted': 0, 'executed': 2}" total_duration="0.00027279986534267664">
						<Test_Windows counts="{'passed': 2, 'total': 2, 'failed': 0, 'skipped': 0, 'unexecuted': 0, 'executed': 2}" total_duration="0.00027279986534267664">
							<test_v_windows_10 outcome="passed" markers="['windows', 'vt']" duration="0.0001374998828396201">
								<setup_method outcome="passed" />
								<teardown_method outcome="passed" />
							</test_v_windows_10>
							<test_v_windows_11 outcome="passed" markers="['windows', 'vt']" duration="0.00013529998250305653">
								<setup_method outcome="passed" />
								<teardown_method outcome="passed" />
							</test_v_windows_11>
						</Test_Windows>
					</test_v_windows.py>
				</windows>
			</vt>
		</suites>
	</examples>
</pytest>
```
