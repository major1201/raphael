# !!!! MAKE SURE YOU PUT THIS PROJECT DIRECTLY UNDER /opt BEFORE YOU RUN ANY MAKE COMMANDS !!!!

ver = "0.1.0"

package:
	# install requirements
	pyvenv venv
	. venv/bin/activate; pip install -r requirements.txt
	# packaging
	mkdir dist /tmp/raphael-$(ver)
	cp -ar * /tmp/raphael-$(ver)
	rm -rf "/tmp/raphael-$(ver){build,dist,.git}"
	tar -czf "dist/raphael-$(ver).tar.gz" -C /tmp "raphael-$(ver)"

rpm:
	mkdir -p build/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
	cp "dist/raphael-$(ver).tar.gz" build/rpmbuild/SOURCES/
	cp scripts/raphael.spec build/rpmbuild/SPECS/
	rpmbuild --define "debug_package %{nil}" --define "_topdir /opt/raphael/build/rpmbuild/" -bb build/rpmbuild/SPECS/raphael.spec
	mv build/rpmbuild/RPMS/x86_64/* dist/

clean:
	rm -rf build/ dist/ /tmp/raphael-$(ver)/

cleanall:
	rm -rf build/ dist/ venv/ /tmp/raphael-$(ver)/

.PHONY: clean cleanall
