# Sublime Libsass

Build system for SASS/SCSS files in Sublime Text 2/3 with no external dependencies

It uses libsass (via the official sassc front-end) for faster compile times compared to the official Ruby implementation.

https://github.com/blitzrk/sublime-libsass

## Configuration

Flags corresponding to sassc's and a relative output directory may be specified. Otherwise reasonable defaults will be chosen, but not so reasonable that you shouldn't have a config file for anything more than a proof of concept. The defaults are:

`.libsass.json`:

```json
{
	"output_dir": "build/css",
	"options": {
		"line-comments": true,
		"line-numbers":  true,
		"style":         "nested"
	}
}
```

You can edit the config or generate an example by selecting the menu item `Tools`->`Libsass Build`->`Create/Edit Config File`.

## Usage

Configuration is entirely optional, so in the simplest case, simply build with `Ctrl+Shift+B`. If you have another SASS build system installed, you may need to select libsass in Sublime's menu.

## Troubleshooting

### Libsass isn't automatically chosen as the build system

If you have another SASS build system installed, it may be conflicting. If no build system is selected, then you may not have a SASS syntax definition installed or it may be oddly defined (i.e. not using source.sass or source.scss). Try replacing it with another syntax highlighting package such as [Sass](https://github.com/nathos/sass-textmate-bundle).

### My file compiled, but I don't know where it went!

Libsass looks up the directory structure until it finds (or doesn't find) a `.libsass.json` config file. If you're not using a config file (You really should!) then check that there isn't a config in any parent directory. E.g. if you have your project in `/home/ben/projects/app` and an extraneous config file `/home/ben/projects/.libsass.json`, the css will output relative to `/home/ben/projects` instead of to `/home/ben/projects/app/build/css`.
