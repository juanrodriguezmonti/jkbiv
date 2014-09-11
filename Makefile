PREFIX=/usr
ICON_DIR=${PREFIX}/share/icons/hicolor
PWD=`pwd`
all:
	@echo "Install with 'sudo make install'"
	@echo "Uninstall with 'sudo make uninstall'"

install:
	rm -rf ${PREFIX}/share/jkbiv
	mkdir -p ${PREFIX}/share/jkbiv
	cp -av *[^~] ${PREFIX}/share/jkbiv/
	cd ${PREFIX}/share/jkbiv; \
		ln -s ${PWD}/jkbiv.py ${PREFIX}/local/bin/jkbiv; \
		mv jkbiv.desktop ${PREFIX}/share/applications; \
		cp -v ${PWD}/icons/256.png /usr/share/pixmaps/jkbiv.png; \
		ln -s ${PWD}/icons/16.png ${ICON_DIR}/16x16/apps/jkbiv.png; \
		ln -s ${PWD}/icons/22.png ${ICON_DIR}/22x22/apps/jkbiv.png; \
		ln -s ${PWD}/icons/48.png ${ICON_DIR}/48x48/apps/jkbiv.png; \
		ln -s ${PWD}/icons/256.png ${ICON_DIR}/256x256/apps/jkbiv.png;
	@echo
	@echo "Install complete!"

uninstall:
	rm -rf ${PREFIX}/share/jkbiv/
	rm -rf ${PREFIX}/local/bin/jkbiv
	rm -rf ${PREFIX}/share/applications/jkbiv.desktop
	rm -f /usr/share/pixmaps/jkbiv.png
	rm -f ${ICON_DIR}/16x16/apps/jkbiv.png
	rm -f ${ICON_DIR}/22x22/apps/jkbiv.png
	rm -f ${ICON_DIR}/48x48/apps/jkbiv.png
	rm -f ${ICON_DIR}/256x256/apps/jkbiv.png
	@echo
	@echo "Stardict-flashcard has been uninstalled from your system."

