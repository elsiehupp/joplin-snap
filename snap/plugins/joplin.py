from snapcraft.plugins.v2 import PluginV2
from typing import Any, Dict, List, Set


class PluginImpl(PluginV2):

	@classmethod
	def get_schema(cls) -> Dict[str, Any]:
		return {
			"$schema": "http://json-schema.org/draft-04/schema#",
			"type": "object",
			"additionalProperties": False,
			"properties": {"node-version": {"type": "string"}},
			"required": ["node-version"]
		}

	def get_build_snaps(self) -> Set[str]:
		return set()

	def get_build_packages(self) -> Set[str]:
		return {"python", "rsync", "libsecret-1-dev", "curl"}

	def get_build_environment(self) -> Dict[str, str]:
		return dict(
			PATH="${SNAPCRAFT_PART_BUILD}/NodeJS/bin:${PATH}",
			npm_config_unsafe_perm="true",
			SUDO_UID="0",
			SUDO_GID="0",
			SUDO_USER="root",
			npm_config_prefer_offline="true"
		)

	def _setup_npm(self) -> List[str]:
		_NodeJSVersion = self.options.node_version
		return [
			"if [ ! -f ${SNAPCRAFT_PART_BUILD}/NodeJS/bin/node ]; then ",
				"mkdir -p $SNAPCRAFT_PART_BUILD/NodeJS",
				f"curl -s 'https://nodejs.org/dist/v{_NodeJSVersion}/node-v{_NodeJSVersion}-linux-x64.tar.xz' -o NodeJS.tar.xz",
				"tar xf $SNAPCRAFT_PART_BUILD/NodeJS.tar.xz -C $SNAPCRAFT_PART_BUILD/NodeJS --strip-components 1",
			"fi"
		]

	@staticmethod
	def _apply_patches() -> List[str]:
		return [
			"patch -i $SNAPCRAFT_PROJECT_DIR/patches/disable_updates.patch -p 1",
			"patch -i $SNAPCRAFT_PROJECT_DIR/patches/hide_dev_command.patch -p 1",
			"patch -i $SNAPCRAFT_PROJECT_DIR/patches/detect_updates.patch -p 1",
			"patch -i $SNAPCRAFT_PROJECT_DIR/patches/force_custom_xdg-open.patch -p 1"
		]

	@staticmethod
	def _build_commands() -> List[str]:
		return [
			"unset PYTHONPATH",
			"npm cache verify",
			"npm install",
			"cd packages/app-desktop",
			"npm run dist",
			"cp -r dist/linux-unpacked ${SNAPCRAFT_PART_INSTALL}",
			"mv ${SNAPCRAFT_PART_INSTALL}/linux-unpacked/@joplinapp-desktop ${SNAPCRAFT_PART_INSTALL}/linux-unpacked/joplin"
		]

	def get_build_commands(self) -> List[str]:
		return self._apply_patches() + self._setup_npm() + self._build_commands()
