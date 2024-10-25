# Here are the steps on how to make a new release

1. run: rm -rf dist/; py -m build; py -m twine check dist/pytest-item-dict*.whl;
2. Create a commit on branch `upstream/main`.
3. Create a version tag. Version should be in the form of "vx.y.z". ex: v1.0.9
4. Add version tag to commit
5. Push commit and tag: git push --atomic origin main v1.0.9
