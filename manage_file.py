from datetime import datetime
import os
import shutil
from glob import glob

class BackupError(Exception):
	pass

def rename_file(file_path):
	"""Add a time information to the file received"""

	# Separate the folder_path from the file_name
	file_name = file_path.split("/")[-1]
	folder_path = "/".join(file_path.split("/")[:-1])

	# Add a time indication to the file_name and reconstruct the path
	now = datetime.now()
	extension = file_name.split(".")[1]
	file_name = file_name.split(".")[0]
	file_name += now.strftime("_%Y%m%d_%H%M%S") + "." + extension
	new_file_path = folder_path + "/" + file_name


	# Rename the file at the destination folder
	os.rename(file_path, new_file_path)

	return new_file_path, file_name


def remove_file(file_path):
	try:
	    os.remove(file_path)
	except OSError:
	    pass

def replace_file_content(file_path, src, dest):
	# Read in the file
	with open(file_path, 'r') as file:
		filedata = file.read()

	# Replace the target string
	filedata = filedata.replace(src, dest)

	# Write the file out again
	with open(file_path, 'w') as file:
		file.write(filedata)
	return

def clean_folder(folder_path, extension=None):
	"""Remove all files within a folder with a given extension. If None, then remove all files"""
	if extension is None:
		glober = f'{folder_path}*'
	else:
		glober = f'{folder_path}*{extension}'
	files = glob(glober)
	for file_path in files:
		remove_file(file_path)
	return

def remove_folder(folder_path):
	try:
		shutil.rmtree(folder_path)
	except FileNotFoundError:
		pass

def make_folder(folder_path):
	if not os.path.exists(os.path.dirname(folder_path)):
		os.makedirs(os.path.dirname(folder_path))
	return

def move_file(old_path, new_path):
	# If the new folder does not exist, create it
	make_folder(new_path)

	# Move the file
	try:
		os.rename(old_path, new_path)
	except OSError:
	    pass


def get_file_modified_date(path):
    dt = os.path.getmtime(path)
    return datetime.fromtimestamp(dt).isoformat().split('T')[0]


def allowed_file(filename, allowed_extensions):
	return '.' in filename and \
		filename.rsplit('.', 1)[1].lower() in allowed_extensions


def clean_backup(backup_folder, nb_backups):
	path = './' + backup_folder + "*.db"

	# Remove oldest backup when more than a week of backups
	files = sorted(glob(path), key=os.path.getctime)
	if len(files) > nb_backups:
		oldest = files[0]
		remove_file(oldest)
		return True
	return False


def save_db(db_path, backup_folder):
	now = datetime.now()
	new_path = './' + backup_folder + "fraude_" + now.strftime("%Y%m%d_%H%M%S") + ".db"

	if not os.path.exists(os.path.dirname(new_path)):
		os.makedirs(os.path.dirname(new_path))

	try:
		shutil.copy(db_path, new_path)
	except:
		raise BackupError('Failed to save a copy of the database')
	