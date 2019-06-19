import os
import importlib
import manage_file
from glob import glob
import shutil
import pdfkit

class EnvVariableError(Exception):
	pass


def quickstart_sphinx(documentation_folder, project, author, version, language, master, suffix, template='rtd'):
	# Create and move to the documentation holder folder
	manage_file.make_folder(documentation_folder)
	os.chdir(documentation_folder)

	# Quickstart the sphinx documentation project
	sphinx_command = \
		f'sphinx-quickstart "{documentation_folder}" -q --sep -p {project} -a {author} -v {version} -l {language} --master {master} --suffix {suffix} --makefile'

	# print(sphinx_command)
	os.system(sphinx_command)

	# Apply ReadTheDoc template
	if template=='rtd':
		apply_rtd_template(documentation_folder)
	else:
		pass
	return


def apply_rtd_template(documentation_folder):
	# Prepare necessary information
	file_path = f'{documentation_folder}source/conf.py'
	rtd_theme = """import sphinx_rtd_theme; html_theme="sphinx_rtd_theme"; html_theme_path=[sphinx_rtd_theme.get_html_theme_path()]"""
	init_theme = "html_theme = 'alabaster'"

	# Replace the target string within the file
	manage_file.replace_file_content(file_path, init_theme, rtd_theme)
	return


def apply_extensions(documentation_folder, extensions):
	file_path = f'{documentation_folder}source/conf.py'
	init_extensions = 'extensions = [\n]'
	extensions = '"' +'",\n"'.join(extensions) + '"'
	final_extensions = f"""extensions = [{extensions}]"""#\nexclude_patterns = ['_build', '**.ipynb_checkpoints']"

	# Replace the target string within the file
	manage_file.replace_file_content(file_path, init_extensions, final_extensions)
	return


def generate_rst_files(documentation_folder, notebooks_folder):
	notebooks_paths = glob(f'{notebooks_folder}*.ipynb')
	notebooks_names = [os.path.basename(x) for x in notebooks_paths]
	print(f'NOTEBOOK NAMES : {notebooks_names}')
	rst_paths = [f"{documentation_folder}source/{x.replace('ipynb', 'rst')}" for x in notebooks_names]
	print(f'RST PATHS : {rst_paths}')
	for srcpath, destpath in zip(notebooks_paths, rst_paths):
		os.system(f"""jupyter-nbconvert --to rst "{srcpath}" --output "{destpath}" """)
	rst_paths = glob(f'{documentation_folder}source/*.rst')
	return rst_paths


def update_index(documentation_folder, notebooks_paths, master, max_depth):
	index_path = f'{documentation_folder}source/{master}.rst'
	notebook_names = [os.path.basename(x).replace('.ipynb','') for x in notebooks_paths]
	notebook_names.sort()

	# Increase documentation depth
	manage_file.replace_file_content(index_path, ":maxdepth: 2", f":maxdepth: {max_depth}")

	# Add the notebooks names in the right order
	notebook_names = '\n   '.join(notebook_names)
	notebook_names = f'\n\n   {notebook_names}'
	manage_file.replace_file_content(index_path, ":caption: Contents:", f":caption: Contents: {notebook_names}")
	return


def notebooks_to_source(notebooks_folder, documentation_folder):
	notebooks_paths = glob(f'{notebooks_folder}*.ipynb')
	notebooks_names = [os.path.basename(x) for x in notebooks_paths]
	print(f'NOTEBOOK NAMES 2 : {notebooks_names}')
	for notebook in notebooks_names:
		shutil.copy(f'{notebooks_folder}{notebook}', documentation_folder)
	return


def make_html(documentation_folder):
	os.chdir(documentation_folder)
	os.system(f"""python -m sphinx {documentation_folder}source/ {documentation_folder}build/""")


if __name__=="__main__":
	##########################################
	# Build the documentation for this project
	##########################################

	# Get the absolute paths for the documentation
	current_folder = os.getcwd()
	documentation_folder = f'{current_folder}/../documentation/documentation/'
	notebooks_folder = f'{current_folder}/../documentation/notebooks/'

	# Get other important variables
	project ='DocMakerDocumentation'
	author ='Yohan'
	version ='0.0.1'
	language ='en'
	suffix ='.rst'
	master ='index'
	max_depth = 2
	extensions = ['nbsphinx','sphinx.ext.mathjax','sphinx.ext.imgmath']

	# Prepare the Sphinx project holder
	manage_file.remove_folder(documentation_folder)
	quickstart_sphinx(documentation_folder, project, author, version, language, master, suffix, template='rtd')

	# Convert notebooks to rst files and place them in the desired location
	ipynb_paths = notebooks_to_source(notebooks_folder, f'{documentation_folder}source')

	# Apply the desired extensions
	apply_extensions(documentation_folder, extensions)

	rst_paths = generate_rst_files(documentation_folder, notebooks_folder)

	# Insert rst files into the index file in the correct order and build the project's HTML
	notebooks_paths = glob(f'{documentation_folder}source/*.ipynb')
	update_index(documentation_folder, notebooks_paths, master, max_depth)

	make_html(documentation_folder)

	html_paths = glob(f'{documentation_folder}build/*html')
	#print(html_paths)
	pdfkit.from_file('C:/Users/yohan/Desktop/BDF/docmaker/documentation/documentation/build/02_documentation.html', 'out.pdf')
_