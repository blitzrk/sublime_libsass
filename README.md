Build system for SASS/SCSS files in Sublime Text 2/3 with no external dependencies

It uses libsass (via the official sassc front-end) for faster compile times compared to the official Ruby implementation.

## Configuration

Flags corresponding to sassc's and a relative output directory may be specified. Otherwise reasonable defaults will be chosen, as below:

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

## Usage

Configuration is entirely optional, so in the simplest case, simply build with `Ctrl+Shift+B`. If you have another SASS build system installed, you may need to select libsass in Sublime's menu.
