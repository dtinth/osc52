#!/bin/sh
# Decide the version of the next release from the Conventional Commits made
# since the last one. Prints the tag to create, or nothing at all when the
# commits do not warrant a release.
set -eu

previous=$(git tag --list 'v*' --sort=-v:refname | head -n 1)
if [ -z "$previous" ]; then
	echo v0.1.0 # nothing has been released yet
	exit 0
fi

subjects=$(git log --format=%s "$previous"..HEAD)
bodies=$(git log --format=%b "$previous"..HEAD)

if printf '%s\n%s\n' "$subjects" "$bodies" |
	grep -qE '^([a-z]+(\(.+\))?!:|BREAKING CHANGE)'; then
	bump=major
elif printf '%s\n' "$subjects" | grep -qE '^feat(\(.+\))?:'; then
	bump=minor
elif printf '%s\n' "$subjects" | grep -qE '^(fix|perf)(\(.+\))?:'; then
	bump=patch
else
	exit 0 # docs, chores, refactors and the like: nothing to release
fi

major=$(echo "${previous#v}" | cut -d. -f1)
minor=$(echo "${previous#v}" | cut -d. -f2)
patch=$(echo "${previous#v}" | cut -d. -f3)

# While the major is 0 nothing is stable yet, so a breaking change is a minor.
if [ "$major" = 0 ] && [ "$bump" = major ]; then
	bump=minor
fi

case $bump in
major) major=$((major + 1)) minor=0 patch=0 ;;
minor) minor=$((minor + 1)) patch=0 ;;
patch) patch=$((patch + 1)) ;;
esac

echo "v$major.$minor.$patch"
