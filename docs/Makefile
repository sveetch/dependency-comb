# Minimal makefile for Sphinx documentation
#
VENV_PATH=../.venv

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= $(VENV_PATH)/bin/sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

build_command_helps:
	$(VENV_PATH)/bin/dependency_comb analyze -h > _static/command_helps/analyze.txt
	$(VENV_PATH)/bin/dependency_comb format -h > _static/command_helps/format.txt
	$(VENV_PATH)/bin/dependency_comb report -h > _static/command_helps/report.txt
.PHONY: build_command_helps

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
