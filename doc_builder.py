import os
import importlib
import manage_file
from glob import glob
import shutil

class EnvVariableError(Exception):
	pass

# Load the correct config file
def load_config():
	try: 
		config_name = os.environ.get('DOC_CONFIG')
		config_folder = 'configs.'
		config = importlib.import_module(config_folder+config_name)
	except AttributeError:
		raise EnvVariableError('You need to set the DOC_CONFIG environment variable. \
			Use the bash command `export DOC_CONFIG_PATH="config_path"`')
	return config


def quickstart_sphinx(config, doc_folder):
	# Create and move to the documentation holder folder
	manage_file.make_folder(doc_folder)
	os.chdir(doc_folder)

	# Quickstart the sphinx documentation project
	sphinx_command = f'sphinx-quickstart "{doc_folder}" -q --sep -p {config.PROJECT} -a {config.AUTHOR} -v {config.VERSION} -l {config.LANGUAGE} --master {config.MASTER} --suffix {config.SUFFIX} --makefile'

	print(sphinx_command)
	os.system(sphinx_command)

	# Apply ReadTheDoc template
	if config.USE_RTD_TEMPLATE:
		apply_rtd_template()
	return


def apply_rtd_template():
	# Prepare necessary information
	file_path = './source/conf.py'
	rtd_theme = """import sphinx_rtd_theme; html_theme="sphinx_rtd_theme"; html_theme_path=[sphinx_rtd_theme.get_html_theme_path()]"""
	init_theme = "html_theme = 'alabaster'"

	# Replace the target string
	manage_file.replace_file_content(file_path, init_theme, rtd_theme)
	return

def apply_extensions(config):
	file_path = './source/conf.py'
	init_extensions = 'extensions = [\n]'
	extensions = '"' +'",\n"'.join(config.EXTENSIONS) + '"'
	final_extensions = f"""extensions = [{extensions}]"""#\nexclude_patterns = ['_build', '**.ipynb_checkpoints']"
	print(final_extensions)

	# Replace the target string
	manage_file.replace_file_content(file_path, init_extensions, final_extensions)
	return


def generate_rst_files(config_path, doc_folder):
	notebooks_paths = glob(config_path+'/*.ipynb')
	notebooks_names = [os.path.basename(x) for x in notebooks_paths]
	rst_paths = [f"{doc_folder}source/{x.replace('ipynb', 'rst')}" for x in notebooks_names]
	for srcpath, destpath in zip(notebooks_paths, rst_paths):
		os.system(f"""jupyter-nbconvert --to rst "{srcpath}" --output "{destpath}" """)
	rst_paths = glob(doc_folder+'source/*.rst')
	return rst_paths


def update_index(notebook_paths, doc_folder, config):
	index_path = doc_folder + 'source/' + config.MASTER+'.rst'
	notebook_names = [os.path.basename(x).replace('.ipynb','') for x in notebook_paths]
	notebook_names.sort()

	# Increase documentation depth
	manage_file.replace_file_content(index_path, ":maxdepth: 2", f":maxdepth: {config.MAX_DEPTH}")

	# Add the notebooks names in the right order
	notebook_names = '\n   '.join(notebook_names)
	notebook_names = '\n\n   '+notebook_names
	manage_file.replace_file_content(index_path, ":caption: Contents:", ":caption: Contents:"+notebook_names)
	return


def notebooks_to_source(notebook_folder, doc_folder):
	notebooks = glob(notebook_folder+'/*.ipynb')
	notebooks_names = [os.path.basename(x) for x in notebooks]
	for notebook in notebooks_names:
		shutil.copy(notebook_folder+'/'+notebook, doc_folder)
	return

def make_html(doc_folder):
	os.chdir(doc_folder)
	os.system('make html')

def make_html_(doc_folder):
	os.chdir(doc_folder)
	os.system(f"""python -m sphinx {doc_folder+'source/'} {doc_folder+'build/'}""")


if __name__=="__main__":
	# Prepare config elements
	config = load_config()
	doc_folder = os.path.abspath(os.path.join(config.NOTEBOOKS_FOLDER, os.pardir))+'/'+config.PROJECT.lower()+'_doc/'
	print(doc_folder)

	# Prepare the Sphinx project holder
	manage_file.remove_folder(doc_folder)
	quickstart_sphinx(config, doc_folder)

	# Convert notebooks to rst files and place them in the desired location
	ipynb_paths = notebooks_to_source(config.NOTEBOOKS_FOLDER, doc_folder+'source/')

	# Apply the desired extensions
	apply_extensions(config)

	# rst_paths = generate_rst_files(config.NOTEBOOKS_FOLDER, doc_folder)

	# Insert rst files into the index file in the correct order and build the project's HTML
	notebook_paths = glob(doc_folder+'source/*.ipynb')
	update_index(notebook_paths, doc_folder, config)

	make_html_(doc_folder)