import os
import sys

parent_dir = os.path.abspath(os.path.join(os.getcwd(), ".."))
folder_a_path = os.path.join(parent_dir, "scripts")
sys.path.append(folder_a_path)
