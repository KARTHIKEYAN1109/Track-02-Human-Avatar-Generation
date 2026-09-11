.PHONY: test unit-test integration-test e2e-test validate benchmark clean lint

PYTHON := .venv/Scripts/python.exe
PYTEST := .venv/Scripts/pytest.exe

test:
	$(PYTEST) tests/ -v --cov=src/avatar_system --cov-report=term-missing

unit-test:
	$(PYTEST) tests/unit/ -v

integration-test:
	$(PYTEST) tests/integration/ -v

e2e-test:
	$(PYTEST) tests/e2e/ -v

validate-examples:
	$(PYTHON) -m avatar_system.cli validate --spec configs/example_avatar.yaml
	$(PYTHON) -m avatar_system.cli validate --spec configs/baseline_avatars.yaml
	$(PYTHON) -m avatar_system.cli validate --spec configs/strong_test_matrix.yaml

benchmark:
	$(PYTHON) -m avatar_system.cli benchmark

clean:
	$(PYTHON) -m avatar_system.cli clean
