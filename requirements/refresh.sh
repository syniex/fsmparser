# Rebuild lockfiles from scratch, updating all dependencies

command -v pip-compile >/dev/null 2>&1 || {
  echo >&2 "pip-compile is not installed. Install with 'pip install pip-tools'."
  exit 1
}

echo "Updating requirements/*.txt files using pip-compile"
# refresh the constraints / all lockfile
pip-compile -q --resolver backtracking -o requirements/all.txt --strip-extras requirements/all.in

# update all of the other lockfiles
pip-compile -q --resolver backtracking -o requirements/linting.txt requirements/linting.in
pip-compile -q --resolver backtracking -o requirements/testing.txt  requirements/testing.in
pip-compile -q --resolver backtracking -o requirements/testing-extra.txt requirements/testing-extra.in
pip-compile -q --resolver backtracking -o requirements/pyproject.txt pyproject.toml

# confirm we can do an install
pip install --dry-run -r requirements/all.txt
