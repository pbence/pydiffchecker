# PyDiffChecker

**Wrappers for git diff**

## LineShiftChecker

This tool provides an API for checking shifted but not modified lines in changed files of a Git diff. The tool will collect the lines where the content did not change into dict-like objects with source->destination line number mapping per changed file. File renames are detected as well.

The behavior is very similar to unified diff on Github or output of [git-diffn](https://github.com/ElectricRCAircraftGuy/eRCaGuy_dotfiles/blob/master/useful_scripts/git-diffn.sh). There are green (added), red (remove) and white (unmodified) lines. The return value of the API will contain these "white" lines with the source/destination line number for the whole file.

### Example

Let's assume this is the output of git-diffn:
```diff
diff --git a/pydiffchecker/helper.py b/pydiffchecker/helper.py
index f9d4e08..6a6c214 100644
--- a/pydiffchecker/helper.py
+++ b/pydiffchecker/helper.py
@@ -3,14 +3,13 @@ from typing import Iterator
    3,   3:
    4,   4:
    5,   5: def subprocess_readlines(cmd, cwd=None) -> Iterator[str]:
-   6     :-    process = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE)
+        6:+    process = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, text=True)
    7,   7:
    8,   8:     for line in process.stdout:
-   9     :-        line = line.decode().rstrip(r'\n')
-  10     :-
+        9:+        line = line.rstrip('\n')
   11,  10:         yield line
   12,  11:
-  13     :-    process.wait()
+       12:+    process.communicate()
   14,  13:
   15,  14:     if process.returncode != 0:
   16,  15:         raise subprocess.CalledProcessError(process.returncode, cmd)
```

Here the lines 3-5, 7-8, 11-12 and 14-16 are unmodified, but some of them are shifted. Of course, "white" lines that are not shown above are also unmodified. The API fill return the following data (visualized for simplicity, see Usage how to access the data programatically):
```
* pydiffchecker/helper.py->pydiffchecker/helper.py:
    1->1
    2->2
    3->3
    4->4
    5->5
    6->None
    7->7
    8->8
    9->None
    10->None
    11->10
    12->11
    13->None
    14->13
    15->14
    16->15
```

### Usage
```python
from pydiffchecker.line_shift_checker import LineShiftChecker

line_shift_checker = LineShiftChecker('HEAD~', 'HEAD')
all_shifted_lines = line_shift_checker.get_all_shifted_lines()

# Iterate through shifted lines
for src_path, shifted_lines in all_shifted_lines.items():
    renamed_to = shifted_lines.dst_path
    for src_line_index, dst_line_index in shifted_lines:
        print(f'{src_line_index}->{dst_line_index}')

# Find if lines are shifted (and to where) in a file
if 'your/file.cpp' in all_shifted_lines:
    shifted_lines = all_shifted_lines['your/file.cpp']
    renamed_to = shifted_lines.dst_path
    if 12 in shifted_lines:
        # line 12 was shifted, to where?
        shifted_to = shifted_lines[12]
```
