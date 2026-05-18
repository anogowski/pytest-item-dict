import pytest


class Test_RT_Windows:

	def setup_method(self) -> None:
		print("\n\n>>> Setup method")

	def teardown_method(self) -> None:
		print("\n>>> Teardown method")

	@pytest.mark.rt
	@pytest.mark.windows
	def test_rt_windows_1(self) -> None:
		pass

	@pytest.mark.rt
	@pytest.mark.windows
	def test_rt_windows_2(self) -> None:
		pass
