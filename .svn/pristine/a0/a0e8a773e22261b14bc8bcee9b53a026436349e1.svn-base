ifeq "$(ROOTDIR)" "" 
export ROOTDIR=$(shell while true; do if [ -f BuildEnv.mk ]; then pwd;exit; else cd ..;fi;done;)
endif
include $(ROOTDIR)/BuildEnv.mk

PY_TARGET=com_host

APP_SUBDIR=app

install-file += shell/com_host.sh@/wns/shell@.install
install-file += shell/sdregistry_util.sh@/wns/shell/@.install
install-file += shell/rsync.sh@/wns/shell/@.install

include $(ROOTDIR)/Rules.make

