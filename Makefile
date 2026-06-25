# Convenience targets for the literate-repo skill.

.PHONY: help package demo check test clean

help:
	@echo "Targets:"
	@echo "  make package   Build dist/literate-repo.skill (the installable skill)"
	@echo "  make demo      Regenerate the demo notebooks from demo/sample_repo"
	@echo "  make check     Validate the demo notebooks are well-formed"
	@echo "  make test      Run the sample repo's unit tests"
	@echo "  make clean     Remove build artifacts and caches"

package:
	python3 tools/package_skill.py

demo:
	cd demo && python3 build_demo.py

check:
	python3 scripts/litnb.py --check demo/calc-literate

test:
	cd demo/sample_repo && python3 -m pytest tests/ -q

clean:
	rm -rf dist
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
	find . -name .ipynb_checkpoints -type d -prune -exec rm -rf {} +
	find . -name '*.pyc' -delete
