#------------------------------------------------------------------------------

PACKAGE_NAME=cygport

default : build
# test

#-----------------------------------------------------------------------------

ifeq ($(OS),Windows_NT)
  SHL_PRE :=
  SHL_EXT := dll
  EXE_SUFFIX := .exe
else
  SHL_PRE := lib
  SHL_EXT := so
  EXE_SUFFIX :=
endif

#------------------------------------------------------------------------------

PYTHON	:= $(if $(version),python${version},python)
PIP	:= $(if $(version),pip${version},pip)

#------------------------------------------------------------------------------

# Note: Installation done by both 'develop' and 'build' but differently.

.PHONY: default build test develop install clean distclean

REQUIREMENTS_SATISFIED = .requirements_satisfied
BUILD_SENTINELS = .build .develop .test
SENTINELS = ${REQUIREMENTS_SATISFIED} ${BUILD_SENTINELS}

USER := $(if $(NO_USER), , --user)

#------------------------------------------------------------------------------

req = requirements.txt
${REQUIREMENTS_SATISFIED} :
	@ if [ -e ${req} -a -s ${req} ] ; then \
	      echo ${PIP} install -r ${req} ; \
	      ${PIP} --disable-pip-version-check install -r ${req} ; \
	      echo ; \
	  fi
	@ touch $@

init :	${REQUIREMENTS_SATISFIED}

#------------------------------------------------------------------------------

SOURCE = $(shell find ${PACKAGE_NAME} -name '*.py' )

build : .build

.build : ${SOURCE}
	${PYTHON} setup.py build
	@ touch $@
	@ sleep 1
	@ echo

#------------------------------------------------------------------------------

TESTS = $(shell find tests -type f )

test : .test

.test :	.build ${TESTS}
	PYTHONPATH=.:${PYTHONPATH} ${PYTHON} -munittest discover --start-directory tests -p 'test_*.py'
	@ # touch .test
	@ echo

test-as-is test-as-installed :
	export PYTHON_TEST_AS_INSTALLED=true ; make --no-print-directory test

#------------------------------------------------------------------------------

develop : .develop

.develop : .${LIB_NAME} ${REQUIREMENTS_SATISFIED}
	cd $(shell cygpath -w -a .) \
	  && python setup.py develop ${USER}
	@ touch $@
	@ sleep 1
	@ echo

#------------------------------------------------------------------------------

# install : test
install : .build
	cd $(shell cygpath -u -a $(shell cygpath -w -a .)) \
	  && ${PIP} --disable-pip-version-check -v install --upgrade . ${USER}
	@ echo

#	${PYTHON} setup.py install --user

#------------------------------------------------------------------------------

uninstall :
	${PIP} --disable-pip-version-check -v uninstall ${PACKAGE_NAME}
	@ echo

#------------------------------------------------------------------------------

clean :
	rm -f ${BUILD_SENTINELS}
	rm -f {.,${LIB_NAME}}{,/*}/_${LIB_NAME}*.{c,o,so,dll,${SHL_EXT}}
	rm -f {.,${LIB_NAME}}{,/*}/{lex,yacc}tab.py
	rm -rf build dist ${PACKAGE_NAME}.egg-info
	find . -depth -name __pycache__ -exec rm -rf \{\} \;
	find . -name '*.pyc' -delete

distclean : clean
	rm -f ${SENTINELS}
	@ echo

#------------------------------------------------------------------------------

re :	quiet-clean
	@ echo "+ make build"
	@ make --no-print-directory build
	@ echo
	@ echo "+ make test"
	@ make --no-print-directory test

#------------------------------------------------------------------------------

quiet-clean :
	@ echo ": Quietly wipe the slate clean ..."
	@ echo "+ make clean > /dev/null"
	@ make --no-print-directory clean 2>&1 > /dev/null
	@ echo

#------------------------------------------------------------------------------

configuration :
	@ echo "Configuration"
	@ echo "-------------"
	@ echo
	@ ( cmd='python --version' ; echo "+ $$cmd" ; echo ; $$cmd 2>&1 \
	  ; echo \
	  ; cmd='eargs PYTHONPATH' ; echo "+ $$cmd" ; echo ; $$cmd \
	  ; echo \
	  ; echo "+ ${PIP} list --format=columns | grep 'cffi '" \
	  ; echo \
	  ; ${PIP} --disable-pip-version-check list --format=columns | grep 'cffi ' \
	  ; echo \
	  ; which-module cffi \
	  ; echo \
	  ) | sed -e 's/^/    /'

#------------------------------------------------------------------------------

error-details : quiet-clean configuration
	@ export PATH=$(shell pwd)/scripts:"$$PATH" \
	    && make --no-print-directory  __error-details

__error-details :
	@ echo "+ make build"
	-@ make --no-print-directory build
	@ echo
	@ echo
	@ echo "The problematic text :"
	@ echo
	@ logfile=`gcc --log-file ` \
	  && cat "$$logfile" \
	  && echo ::: "$$logfile"
	@ echo

#------------------------------------------------------------------------------
