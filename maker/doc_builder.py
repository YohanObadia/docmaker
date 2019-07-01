import os
import importlib
import manage_file
from glob import glob
from pathlib import Path
import shutil
import pdfkit
import numpy as np

class EnvVariableError(Exception):
	pass


def apply_rtd_template(documentation_folder):
	# Prepare necessary information
	file_path = f'{documentation_folder}source/conf.py'
	rtd_theme = """import sphinx_rtd_theme; html_theme="sphinx_rtd_theme"; html_theme_path=[sphinx_rtd_theme.get_html_theme_path()]"""
	init_theme = "html_theme = 'alabaster'"

	# Replace the target string within the file
	manage_file.replace_file_content(file_path, init_theme, rtd_theme)
	return


def apply_extensions(documentation_folder, extensions):
	
	# Prepare the two strings
	init_extensions = 'extensions = [\n]'
	extensions = '"' +'",\n"'.join(extensions) + '"'
	final_extensions = f"""extensions = [{extensions}]"""#\nexclude_patterns = ['_build', '**.ipynb_checkpoints']"

	# Replace the target string within the file
	file_path = f'{documentation_folder}source/conf.py'
	manage_file.replace_file_content(file_path, init_extensions, final_extensions)

	return


def quickstart_sphinx(documentation_folder, project, author, version, language, master, suffix, extensions, template='rtd'):
	# Create and move to the documentation holder folder
	manage_file.make_folder(documentation_folder)
	os.chdir(documentation_folder)

	# Quickstart the sphinx documentation project
	sphinx_command = \
		f'sphinx-quickstart "{documentation_folder}" -q --sep -p {project} -a {author} -v {version} -l {language} --master {master} --suffix {suffix} --makefile'
	os.system(sphinx_command)

	# Modify the conf.py file to add extensions
	apply_extensions(documentation_folder, extensions)

	# Apply ReadTheDoc template
	if template=='rtd':
		apply_rtd_template(documentation_folder)
	else:
		pass
	return


def notebooks_to_source(notebooks_folder, documentation_folder):
	notebooks_paths = glob(f'{notebooks_folder}/*/*.ipynb')
	notebooks_names = [os.path.basename(x) for x in notebooks_paths]
	for path in notebooks_paths:
		parent = manage_file.get_parent_folder(path)
		manage_file.copy_file(path, f'{documentation_folder}/{parent}/')
	return


def get_toctree(notebook_folder, max_depth=2, hidden=True):
	notebooks_paths = glob(f'{notebook_folder}/*ipynb')
	notebook_names = [os.path.basename(x).replace('.ipynb','') for x in notebooks_paths]
	notebook_names.sort()
	parent_folder = manage_file.get_parent_folder(notebooks_paths[0])
	caption = parent_folder.split('_')[1]
	toctree = f'.. toctree::\n\t:maxdepth: {max_depth}\n\t' + (":hidden:\n\t" if hidden else "") + f':caption: {caption}\n\n'
	for name in notebook_names:
		toctree += f'\t{parent_folder}/{name}\n'
	return toctree


def get_description(folder):
	description_path = glob(f'{folder}/*.rst')[0]
	description = ''
	try:
		with open(description_path, 'r') as f:
			description = f.read()
	except:
		pass
	return description


def get_section(notebook_folder, max_depth=2, hidden=True):
	description = get_description(notebook_folder)
	toctree = get_toctree(notebook_folder, max_depth, hidden)
	section = f'{description} \n {toctree} \n'
	return section


def create_master(documentation_folder, notebooks_folder, master='index', max_depth=2, hidden=True):
	master_path = f'{documentation_folder}source/{master}.rst'
	notebooks_paths = glob(f'{notebooks_folder}/*/*ipynb')
	notebooks_parents = np.unique([manage_file.get_parent_folder(x) for x in notebooks_paths])
	notebooks_folders = [f'{notebooks_folder}/{parent}' for parent in notebooks_parents]

	master = get_description(notebooks_folder)
	for folder in notebooks_folders:
		master += get_section(folder, max_depth, hidden)

	with open(master_path, 'w') as f:
		f.write(master)
	return


def make_doc(documentation_folder, format):
	os.chdir(documentation_folder)
	os.system(f"""python -m sphinx -b {format} {documentation_folder}source/ {documentation_folder}build/""")


if __name__=="__main__":
	##########################################
	# Build the documentation for this project
	##########################################

	# Get the absolute paths for the documentation
	current_folder = os.getcwd()
	documentation_folder = f'{current_folder}/../doc/documentation/'
	notebooks_folder = f'{current_folder}/../doc/notebooks/'

	# Get other important variables
	project ='Criblage'
	author ='Yohan'
	version ='0.0.1'
	language ='en'
	suffix ='.rst'
	master ='index'
	max_depth = 2
	hidden = True
	extensions = ['nbsphinx','sphinx.ext.mathjax']#,'sphinx.ext.imgmath']

	# Prepare the Sphinx project holder
	manage_file.remove_folder(documentation_folder)
	quickstart_sphinx(documentation_folder, project, author, version, language, master, suffix, extensions, template='rtd')

	# Place the notebooks in the source folder
	ipynb_paths = notebooks_to_source(notebooks_folder, f'{documentation_folder}source')

	# Create the master file with the toctrees used for making the documentation
	create_master(documentation_folder, notebooks_folder, master, max_depth, hidden)

	# Make the documentation in the desired format (html, latex, srt, etc...)
	make_doc(documentation_folder, 'html')