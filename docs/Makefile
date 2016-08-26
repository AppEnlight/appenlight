PROJECTS = Appenlight-docs

BLOG 	= blog
MKDOCS 	= ../result/bin/mkdocs

help:
	@echo ""
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  all       		build all projects"
	@echo "  bootstrap 		build tools needed to build projects"
	@echo "  ci-docs 		Trigger by CI server to build the documentation."
	@echo "  ci-docs-publish	Trigger by CI server to publish the"
	@echo "  			documentation. Requires CI_TARGET to be set."
	@echo "  bootstrap 		build tools needed to build projects"
	@echo "  <project>		build one project. list of projects you can find below"
	@echo ""
	@echo "Current projects:"
	@for project in $(PROJECTS); do echo "  - $$project"; done
	@echo ""

all: bootstrap
	for item in $(PROJECTS); do \
		cd $$item && $(MAKE) html && cd ..; \
		mkdir -p www/$$item; \
		cp -R $$item/_build/html/* www/$$item/; \
	done

blog: bootstrap
	for item in $(BLOG) ; do \
		echo $$item ; \
		echo "Building blog" ; \
		nix-build && cd blog && ../result/bin/mkdocs build --clean && cd .. ; \
		echo "blog build" ; \
		echo "it's in the blog/site folder. Moving to www folder" ; \
		mkdir -p www/$$item; \
		cp -R $$item/site/* www/$$item; \
	done

clean:
	rm -rf result www
	rm -f common.pyc
	for item in $(PROJECTS); do \
		cd $$item && $(MAKE) clean && cd ..; \
	done

bootstrap:
	nix-build default.nix -o result

$(PROJECTS): bootstrap
	cd $@ && $(MAKE) html


# CI Integration targets

ci-docs: all


ci-docs-publish:
	$(if $(value CI_TARGET),, $(error CI_TARGET has to be defined))

	@echo "Cleaning up $(CI_TARGET)"
	for item in $(PROJECTS); do \
		item_dir=$(CI_TARGET)/$$item; \
		if [ -d $$item_dir ]; then \
			echo "Removing $$item"; \
			rm -fr $$item_dir; \
		fi; \
	done

	@echo "Publishing built documentation"
	for item in $(PROJECTS); do \
		item_dir=$(CI_TARGET)/$$item; \
		echo "Publishing $$item to $$item_dir"; \
		cp -R www/$$item $$item_dir; \
	done

#	@echo "Publishing the blog internally"
#	for item in $(BLOG); do \
#		item_dir=$(CI_TARGET)/$$item; \
#		echo "Publishing $$item to $$item_dir"; \
#		cp -R www/$$item $$item_dir; \
#	done
