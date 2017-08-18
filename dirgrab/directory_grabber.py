import fnmatch
import os
import shutil

def find_files(search_root, pattern):
    '''Recursively find all files matching pattern from search_root.'''
    match_files = []
    for root, dirnames, filenames in os.walk(search_root):
        for filename in fnmatch.filter(filenames, pattern):
            match_files.append(os.path.join(root, filename))
    return match_files

def find_file_paths(search_root, pattern):
    '''Get the unique paths to files matching pattern from search_root.'''
    matched_files = find_files(search_root, pattern)
    return tuple(set([os.path.dirname(x) for x in matched_files]))

def flatten_path(tree, new_separator):
    '''Flatten a directory tree by replacing path separators.'''
    return tree.strip(os.path.sep).replace(os.path.sep, new_separator)

def grab_directories(search_root, pattern, output_dir, new_separator):
    '''Recusively find all files in search_root matching pattern
     and copy them to output_dir using a flattened path name.'''
    match_dirs = find_file_paths(search_root, pattern)

    if len(match_dirs) == 0:
        print('No %s directories found.'%pattern)

    for source in match_dirs:
        print('>>> Found %s at %s'%(pattern, source))

        # Skip directories that look like outputs of this program in case
        # of multiple runs
        if os.path.abspath(output_dir) in os.path.abspath(source):
            print('SKIPPING: Source looks like an old output')
            continue

        # Name the new directory based on the source directory's path (with
        # a new symbol replacing path separators). This is to ensure unique
        # names that still have tracability to their origin path
        dest_name = flatten_path(source.lstrip(search_root), new_separator)
        destination = os.path.join(output_dir, dest_name)

        # Skip directories that look like they have already been grabbed,
        # again in case of multiple runs
        if os.path.isdir(destination):
            print('SKIPPING: Destination directory already exists')
            continue

        print('COPYING: New directory is %s'%destination)
        shutil.copytree(source, destination)

if __name__ == "__main__":
    # Using os.getcwd() displays full paths, '.' displays relative paths
    search_root = '.'
    #search_root = os.getcwd()

    # Output directory name, rooted in search_root
    output_dir = os.path.join(search_root, 'GrabbedDirs')

    # File pattern (fnmatch.filter syntax)
    search_pattern = 'trace_*.log'

    grab_directories(search_root, search_pattern, output_dir, '__')