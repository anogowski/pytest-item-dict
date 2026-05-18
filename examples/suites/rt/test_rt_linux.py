import pytest


class Test_RT_Linux:

	@classmethod
	def setup_class(cls) -> None:
		print("\n\n>>> Setup class: Test_RT_Linux")

	@classmethod
	def teardown_class(cls) -> None:
		print("\n>>> Teardown class: Test_RT_Linux")

	@pytest.mark.rt
	@pytest.mark.linux
	def test_rt_linux_1(self) -> None:
		pass

	@pytest.mark.rt
	@pytest.mark.linux
	def test_rt_linux_2(self) -> None:
		pass
