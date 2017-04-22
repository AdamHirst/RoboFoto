VENV_NAME=venv
REQUIREMENTS=requirements.txt

.PHONY: clean

venv: ${REQUIREMENTS}
	virtualenv -p python3 --system-site-packages ${VENV_NAME}
	${VENV_NAME}/bin/pip3 install -r ${REQUIREMENTS}

clean:
	rm -rf ${VENV_NAME}
