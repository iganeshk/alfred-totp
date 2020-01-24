#!/usr/bin/env bash
# BASH script to sync alfred workflow directory and export it as workflow to releases directory (working directory).
# Parses .env for workflow UUID.
# UUID be found at $HOME/Alfred/Alfred.alfredpreferences/workflows/user.workflow.XXXXXX-XXXX-XXX-XXXXXXXXX
# SAMPLE .env
# UUID=C88D3289-A059-48D6-8FA1-D96F47205FAE

set -e
cd "$(dirname "$0")"

UUID=""

# Current Arguments:    sync     - Sync current directory to workflow directory overwriting changes
#                       revsync  - Sync workflow directory to current directory overwriting changes
#                       export   - Export the alfred workflow except values of "variablesdontexport" variables

_init_env() {
	if [ -f .env ] && [ -s .env ]; then
			export $(grep -v '^#' .env | xargs)
			export workflow_dir="$HOME/Alfred/Alfred.alfredpreferences/workflows/user.workflow.$UUID"
			export info_plist="${workflow_dir}/info.plist"
	else
			echo -e ".env not setup, please have a look at this script to giddyap!"
			exit 1
	fi
}

_export_workflow()  {
	# Create releases directory if needed
	if [[ ! -d "./releases" ]]; then
		mkdir "releases"
	fi
	readonly workflow_name="$(/usr/libexec/PlistBuddy -c 'print name' "${info_plist}")"
	readonly workflow_file="./releases/${workflow_name}.alfredworkflow"

	if /usr/libexec/PlistBuddy -c 'print variablesdontexport' "${info_plist}" &> /dev/null; then
		readonly workflow_dir_to_package="$(mktemp -d)"
		cp -R "${workflow_dir}/"* "${workflow_dir_to_package}"

		readonly tmp_info_plist="${workflow_dir_to_package}/info.plist"
		/usr/libexec/PlistBuddy -c 'Print variablesdontexport' "${tmp_info_plist}" | grep '    ' | sed -E 's/ {4}//' | xargs -I {} /usr/libexec/PlistBuddy -c "Set variables:'{}' ''" "${tmp_info_plist}"
	else
		readonly workflow_dir_to_package="${workflow_dir}"
	fi

	ditto -ck "${workflow_dir_to_package}" "${workflow_file}"
	echo -e "Exported worflow to ${workflow_file}"
}

_sync_workflow()	{
	echo -e "Copying files from:\n$(pwd -P) to $workflow_dir"
	read -r -p "Are you sure? [y/N] " response
	if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
		# cp -rf * "$workflow_dir"
		rsync -avr --exclude='releases' --exclude=".*" --exclude="assets" --exclude="info.plist" . "$workflow_dir"
	fi
}

_revsync_workflow()    {
	echo -e "Copying files from:\n$workflow_dir to $(pwd -P) "
	read -r -p "Are you sure? [y/N] " response
	if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
		# cp -rf "$workflow_dir" .
		rsync -avr --exclude='releases' --exclude=".*" --exclude="assets" "$workflow_dir" .
	fi
}

while [ "$1" != "" ]; do
	PARAM=`echo $1 | awk -F= '{print $1}'`
	VALUE=`echo $1 | awk -F= '{print $2}'`
	case $PARAM in
			sync | --sync)
					_init_env
					_sync_workflow
					exit
					;;
			revsync | --revsync)
					_init_env
					exit
					;;
			export| --export)
					_init_env
					_export_workflow
					exit
					;;
			*)
					echo -e "ERROR: unknown argument \"$PARAM\""
					exit 1
					;;
	esac
	shift
done
